"""Async MIDI clock with high-resolution tick generation

The InternalClock runs on the asyncio event loop and maintains precise timing
using monotonic time with drift correction. It emits tick callbacks at PPQN=960
resolution and special events for bar/beat boundaries and metronome pulses.
"""

import asyncio
from time import monotonic
import logging

logger = logging.getLogger(__name__)


class InternalClock:
    """High-resolution async MIDI clock using PPQN=960

    Responsibilities:
    - Maintain precise timing using monotonic time + drift correction
    - Convert BPM → ticks per second
    - Emit tick callbacks (_on_tick, _on_bar_start, _on_beat)
    - Run on the asyncio event loop (integrates with existing architecture)

    Attributes:
        PPQN: 960 (standard MIDI timing resolution)
        sequencer: Reference to MidiSequencer for callbacks
    """

    PPQN = 960  # Pulses per quarter note

    def __init__(self, sequencer):
        """Initialize clock

        Args:
            sequencer: MidiSequencer instance to receive tick callbacks
        """
        self.sequencer = sequencer
        self.state = sequencer.state

        self._task = None
        self._last_monotonic = 0.0
        self._accumulated_ticks = 0.0
        self._is_running = False

    async def start(self):
        """Begin the clock loop"""
        if self._is_running:
            return

        self._is_running = True
        self._last_monotonic = monotonic()
        self._accumulated_ticks = 0.0

        self._task = asyncio.create_task(self._run_clock())
        logger.debug(f"Sequencer clock started (BPM={self.state.tempo})")

    async def stop(self):
        """Stop the clock"""
        if not self._is_running:
            return

        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.debug("Sequencer clock stopped")

    async def _run_clock(self):
        """Main clock loop: maintain precise timing and emit tick callbacks

        Algorithm:
        1. Measure elapsed time since last iteration using monotonic()
        2. Convert elapsed time to ticks using current BPM
        3. Accumulate fractional ticks
        4. Dispatch all complete ticks as callbacks
        5. Sleep ~1ms to avoid busy-loop CPU usage

        Drift correction: accumulating fractional ticks ensures timing stays
        synchronized even if sleep intervals are inexact.
        """
        try:
            while self._is_running:
                try:
                    now = monotonic()
                    dt = now - self._last_monotonic
                    self._last_monotonic = now

                    # Convert elapsed time to ticks
                    bpm = self.state.tempo
                    seconds_per_quarter = 60.0 / bpm
                    seconds_per_tick = seconds_per_quarter / self.PPQN
                    ticks_this_frame = dt / seconds_per_tick

                    self._accumulated_ticks += ticks_this_frame

                    # Dispatch all accumulated complete ticks
                    while self._accumulated_ticks >= 1:
                        tick_increment = int(self._accumulated_ticks)
                        self._accumulated_ticks -= tick_increment

                        # Update playhead position
                        self.state.current_tick = (
                            self.state.current_tick + tick_increment
                        ) % self.state.loop_length_ticks

                        # Fire the main tick callback (playback happens here)
                        self.sequencer._on_tick(self.state.current_tick)

                        # Check for bar start (reset to 0)
                        if (
                            self.state.current_tick == 0
                            and self.state.loop_length_ticks > 0
                        ):
                            self.sequencer._on_bar_start()

                        # Check for beat start
                        ticks_per_beat = self.PPQN * (4 / self.state.time_signature_den)
                        if (
                            ticks_per_beat > 0
                            and self.state.current_tick % ticks_per_beat == 0
                        ):
                            beat_index = (
                                int(self.state.current_tick / ticks_per_beat)
                                % self.state.time_signature_num
                            )
                            self.sequencer._on_beat(beat_index)

                    # Small sleep to prevent 100% CPU usage
                    # Vary sleep based on accumulated ticks to maintain precision
                    sleep_time = max(0.0001, 0.001 - self._accumulated_ticks * 0.0001)
                    await asyncio.sleep(sleep_time)

                except Exception as e:
                    logger.error(f"Clock tick error: {e}", exc_info=True)
                    await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.debug("Clock task cancelled")
            raise

    def is_running(self) -> bool:
        """Check if clock is actively running"""
        return self._is_running
