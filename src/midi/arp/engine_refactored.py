"""Refactored arpeggiator engine with separated concerns.

The engine orchestrates timing calculations, mode strategies, note production,
and MIDI dispatching into a cohesive real-time note generation system.
"""

import asyncio
import logging
from typing import Optional

from typing import List

from .dispatcher import MidiDispatcher
from .modes import create_mode
from .note_producer import NoteProducer
from .state_validator import ArpState
from .timing import TimingCalculator

logger = logging.getLogger(__name__)


class ArpEngine:
    """Refactored arpeggiator engine with separated concerns.

    Maintains the same public interface as the original ArpEngine while
    internally using specialized components for timing, modes, note production,
    and MIDI dispatching.
    """

    def __init__(
        self,
        arp_state: ArpState,
        midi_engine,
        event_loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """Initialize refactored arpeggiator engine.

        Args:
            arp_state: ArpState instance for configuration
            midi_engine: MIDI engine with queue for message delivery
            event_loop: Optional asyncio event loop (uses current if not provided)
        """
        self.state = arp_state
        self.midi_engine = midi_engine
        self._loop = event_loop or asyncio.get_event_loop()

        # Initialize specialized components
        self._timing_calc = TimingCalculator()
        self._note_producer = NoteProducer()
        self._dispatcher = MidiDispatcher(midi_engine)

        # Engine state
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._step = 0
        self._position = 0

    def start(self) -> None:
        """Start the arpeggiator engine.

        Creates an async task that runs the main engine loop.
        Safe to call multiple times (idempotent).
        """
        if self._running:
            return
        self._running = True
        self._step = 0
        self._position = 0
        self._task = self._loop.create_task(self._timing_loop())

    def stop(self) -> None:
        """Stop the arpeggiator engine.

        Cancels the running task if it exists.
        Safe to call even if not running.
        """
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _timing_loop(self) -> None:
        """Main timing loop that drives step generation.

        Continuously:
        1. Calculates timing metadata for current step
        2. Processes the step (generates notes)
        3. Sleeps for calculated duration
        4. Advances to next step

        Runs until stop() is called or state.enabled becomes False.
        """
        try:
            while self._running and self.state and self.state.enabled:
                try:
                    # Calculate timing for this step
                    timing = self._timing_calc.calculate_timing(
                        bpm=self.state.timing.bpm,
                        division=self.state.timing.division,
                        swing_pct=self.state.timing.swing,
                        step_number=self._step,
                        tempo_mul=self.state.timing.tempo_mul,
                    )

                    # Process this step (generate and dispatch notes)
                    await self._process_step()

                    # Sleep for calculated interval and swing
                    await asyncio.sleep(timing.total_sleep)

                    self._step += 1
                except asyncio.CancelledError:
                    raise  # Re-raise cancellation to outer handler
                except Exception:
                    logger.exception("ArpEngine step error, continuing")
                    await asyncio.sleep(0.05)  # Brief pause on error

        except asyncio.CancelledError:
            # Normal shutdown via stop()
            return
        except Exception:
            logger.exception("ArpEngine timing loop error")

    def _build_expanded_notes(self) -> List[int]:
        """Build the full note sequence by expanding held notes across octave range.

        Uses state.octave (1-4) to determine how many octaves to span,
        and state.octave_dir (UP/DOWN/BOTH) to determine direction.

        Returns:
            Sorted list of MIDI notes covering the octave range.
        """
        base_notes = list(self.state.pattern.notes)  # already sorted
        if not base_notes:
            return []

        octave_range = max(1, min(4, self.state.octave))
        if octave_range == 1:
            return base_notes

        expanded = []
        direction = (self.state.octave_dir or "UP").upper()

        if direction == "UP":
            for oct in range(octave_range):
                for note in base_notes:
                    n = note + oct * 12
                    if 0 <= n <= 127:
                        expanded.append(n)
        elif direction == "DOWN":
            for oct in range(octave_range - 1, -1, -1):
                for note in base_notes:
                    n = note - oct * 12
                    if 0 <= n <= 127:
                        expanded.append(n)
            expanded.sort()
        else:  # BOTH
            # Go down (octave_range // 2) and up (octave_range - octave_range // 2 - 1)
            down_count = (octave_range - 1) // 2
            up_count = octave_range - 1 - down_count
            for oct in range(-down_count, up_count + 1):
                for note in base_notes:
                    n = note + oct * 12
                    if 0 <= n <= 127:
                        expanded.append(n)
            expanded.sort()

        return expanded

    async def _process_step(self) -> None:
        """Process a single step: generate and dispatch note.

        If no active notes for this step, silently advances.
        Otherwise produces a note, calculates velocity, dispatches note_on
        and schedules note_off based on gate percentage.
        """
        # Build expanded notes across octave range
        expanded_notes = self._build_expanded_notes()

        if not expanded_notes:
            return

        # Get the mode strategy for current mode
        mode = create_mode(self.state.mode)

        # Build list of active note indices
        active_indices = mode.build_active_indices(expanded_notes)

        if not active_indices:
            return

        # Choose which note to play and advance position
        idx, new_pos = mode.choose_next(active_indices, self._position)
        self._position = new_pos

        # Get the actual step index in expanded notes
        step_idx = active_indices[idx]

        # Produce note and velocity
        note = expanded_notes[step_idx]
        velocity = self._note_producer.calculate_velocity(
            step_idx, len(expanded_notes), self.state
        )

        # Apply accent if enabled for this note's semitone
        if self._note_producer.should_accent(note, self.state):
            velocity = self._note_producer._apply_accent(velocity)

        # Send note_on message
        if self._dispatcher.send_note_on(note, velocity):
            # Schedule note_off after gate duration
            gate_duration = self._timing_calc.calculate_gate_duration(
                bpm=self.state.timing.bpm,
                gate_pct=self.state.gate_pct,
            )
            # If latch is HOLD, sustain notes longer
            if self.state.latch == "HOLD":
                gate_duration = max(gate_duration, 5.0)  # At least 5 seconds
            asyncio.create_task(self._schedule_note_off(note, gate_duration))

    async def _schedule_note_off(self, note: int, delay: float) -> None:
        """Schedule a note_off message after delay.

        Args:
            note: MIDI note to release
            delay: Delay in seconds before sending note_off
        """
        await asyncio.sleep(delay)
        self._dispatcher.send_note_off(note)

    def preview(self, steps: int = 8) -> None:
        """Preview the next N steps of the pattern.

        Asynchronously plays a quick preview of the pattern for UI feedback.
        Runs in the background without affecting the main engine.

        Args:
            steps: Number of steps to preview (default 8)
        """

        async def _do_preview():
            """Internal async preview generator."""
            if not self._dispatcher.has_queue():
                return

            # Build expanded notes
            expanded_notes = self._build_expanded_notes()
            if not expanded_notes:
                return

            # Get mode strategy
            mode = create_mode(self.state.mode)
            active_indices = mode.build_active_indices(expanded_notes)

            if not active_indices:
                return

            # Preview specified number of steps
            position = 0
            for _ in range(steps):
                # Choose next note
                idx, position = mode.choose_next(active_indices, position)
                step_idx = active_indices[idx]

                note = expanded_notes[step_idx]
                velocity = self._note_producer.calculate_velocity(
                    step_idx, len(expanded_notes), self.state
                )

                # Apply accent if enabled
                if self._note_producer.should_accent(note, self.state):
                    velocity = self._note_producer._apply_accent(velocity)

                # Send note_on and note_off with short delay
                if self._dispatcher.send_note_on(note, velocity):
                    await asyncio.sleep(0.08)
                    self._dispatcher.send_note_off(note)

        # Run preview in background
        asyncio.run_coroutine_threadsafe(_do_preview(), self._loop)

    # Backward compatibility methods (deprecated)
    def _build_active_order(self) -> None:
        """Deprecated: Use modes.py instead.

        Kept for backward compatibility. Do not use in new code.
        """
        expanded = self._build_expanded_notes()
        mode = create_mode(self.state.mode)
        active = mode.build_active_indices(expanded)
        # Store in a temporary attribute for any legacy code that checks it
        self._active_order = active

    def _choose_index(self) -> int:
        """Deprecated: Use modes.py instead.

        Kept for backward compatibility. Do not use in new code.
        """
        mode = create_mode(self.state.mode)
        if not hasattr(self, "_active_order"):
            self._build_active_order()

        if not self._active_order:
            return 0

        idx, new_pos = mode.choose_next(self._active_order, self._position)
        self._position = new_pos
        return idx
