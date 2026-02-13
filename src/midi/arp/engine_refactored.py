"""Refactored arpeggiator engine with separated concerns.

The engine orchestrates timing calculations, mode strategies, note production,
and MIDI dispatching into a cohesive real-time note generation system.
"""

import asyncio
import logging
from typing import Optional

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
            # Normal shutdown via stop()
            return
        except Exception:
            logger.exception("ArpEngine timing loop error")

    async def _process_step(self) -> None:
        """Process a single step: generate and dispatch note.

        If no active notes for this step, silently advances.
        Otherwise produces a note, calculates velocity, dispatches note_on
        and schedules note_off based on gate percentage.
        """
        # Get the mode strategy for current mode
        mode = create_mode(self.state.mode)

        # Build list of active note indices from pattern
        active_indices = mode.build_active_indices(self.state.pattern.mask)

        if not active_indices:
            return

        # Choose which note to play and advance position
        idx, new_pos = mode.choose_next(active_indices, self._position)
        self._position = new_pos

        # Get the actual step index in the pattern
        step_idx = active_indices[idx]

        # Check if this step is marked to play in pattern
        if not self.state.pattern.mask[step_idx]:
            return

        # Produce note and velocity
        note, velocity = self._note_producer.produce_note(step_idx, self.state)

        # Send note_on message
        if self._dispatcher.send_note_on(note, velocity):
            # Schedule note_off after gate duration
            gate_duration = self._timing_calc.calculate_gate_duration(
                bpm=self.state.timing.bpm,
                gate_pct=self.state.gate_pct,
            )
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

            # Get mode strategy
            mode = create_mode(self.state.mode)
            active_indices = mode.build_active_indices(self.state.pattern.mask)

            if not active_indices:
                return

            # Preview specified number of steps
            position = 0
            for _ in range(steps):
                # Choose next note
                idx, position = mode.choose_next(active_indices, position)
                step_idx = active_indices[idx]

                if not self.state.pattern.mask[step_idx]:
                    continue

                # Produce note for preview
                note, velocity = self._note_producer.produce_note(step_idx, self.state)

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
        mode = create_mode(self.state.mode)
        active = mode.build_active_indices(self.state.pattern.mask)
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
