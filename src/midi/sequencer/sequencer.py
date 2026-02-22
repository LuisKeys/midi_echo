"""Main MIDI Sequencer implementation

The MidiSequencer is the core control class that:
- Records fully processed MIDI output from the processor
- Plays back recorded patterns on an internal PPQN-based async clock
- Manages state (tempo, time signature, quantization, metronome)
- Handles transport control (play, stop, record, clear)
- Integrates with AppContext and MidiEngine
"""

import asyncio
import logging
import mido
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...gui.context import AppContext
    from ..engine import MidiEngine

from .sequencer_state import SequencerState
from .pattern import Pattern
from .clock import InternalClock
from ...audio import MetronomeClicker

logger = logging.getLogger(__name__)


class MidiSequencer:
    """Single-track pattern sequencer for recording and looping processed MIDI

    Architecture:
    - Records taps from MidiProcessor.process() output
    - Uses InternalClock (PPQN=960) for playback timing
    - Playback sends messages directly to output port (no processor re-entry)
    - Maintains state for sync with GUI
    - Persists patterns with presets

    Thread Safety:
    - Recording called from MidiEngine queue processor (asyncio context)
    - GUI interactions use asyncio.run_coroutine_threadsafe()
    - All async operations thread-safe via asyncio event loop
    """

    def __init__(self, engine: "MidiEngine", context: "AppContext"):
        """Initialize sequencer

        Args:
            engine: MidiEngine instance for output port access
            context: AppContext for event loop reference
        """
        self.engine = engine
        self.context = context

        # State models
        self.state = SequencerState()
        self.pattern = Pattern()
        self.clock = InternalClock(self)
        self.clicker = MetronomeClicker()  # Internal audio for metronome

        # Quantization grid in ticks
        self._quantization_grid_ticks = self._calculate_quantization_grid()

        # For tracking held notes (for all-notes-off on stop)
        self._notes_held: dict = {}  # {(channel, note): velocity}

    # ── Initialization & Setup ──

    def _calculate_quantization_grid(self) -> int:
        """Calculate grid size in ticks for current quantization setting

        Grid sizes (at PPQN=960):
        - 1/4 (quarter note): 960 ticks
        - 1/8 (eighth note): 480 ticks
        - 1/16 (sixteenth note): 240 ticks
        - 1/32 (thirty-second): 120 ticks
        """
        PPQN = InternalClock.PPQN
        quantization_map = {
            "1/4": PPQN,
            "1/8": PPQN // 2,
            "1/16": PPQN // 4,
            "1/32": PPQN // 8,
        }
        return quantization_map.get(self.state.quantization, PPQN // 4)

    # ── Recording ──

    def record_message(self, message: mido.Message):
        """Record a MIDI message from processed output

        Called from MidiEngine after MidiProcessor.process() succeeds.
        Only active when is_recording=True.

        Filters:
        - Only records note_on, note_off, control_change messages
        - Ignores system messages, clock, etc.

        Process:
        1. Filter by message type
        2. Get current tick from state
        3. Quantize to grid
        4. Store in pattern
        5. Track held notes for stop logic

        Args:
            message: mido.Message to record
        """
        if not self.state.is_recording:
            return

        # Filter: only record musical messages
        if message.type not in ("note_on", "note_off", "control_change"):
            return

        # Get current position and quantize
        tick = self.state.current_tick
        quantized_tick = self._quantize_tick(tick)

        # Add to pattern
        self.pattern.add_event(quantized_tick, message)

        # Track held notes
        if message.type == "note_on" and message.velocity > 0:
            key = (message.channel, message.note)
            self._notes_held[key] = message.velocity
        elif message.type == "note_off" or (
            message.type == "note_on" and message.velocity == 0
        ):
            key = (message.channel, message.note)
            self._notes_held.pop(key, None)

    def _quantize_tick(self, tick: int) -> int:
        """Quantize a tick to the nearest grid position

        Args:
            tick: Unquantized tick position

        Returns:
            Quantized tick (rounded to nearest grid)
        """
        grid = self._quantization_grid_ticks
        return round(tick / grid) * grid

    # ── Playback (Tick Callbacks) ──

    def _on_tick(self, tick: int):
        """Called by clock on each tick—the core playback engine

        Playback algorithm:
        1. Check if playing (safety check)
        2. Get all events due at this tick
        3. Send each event directly to output

        Thread-safe: Called from clock (asyncio task on event loop)

        Args:
            tick: Current tick position in loop
        """
        if not self.state.is_playing:
            return

        # Get all events scheduled for this tick
        for event in self.pattern.events_at_tick(tick):
            self._send_message_direct(event.message)

    def _on_bar_start(self):
        """Called at the start of each bar (when tick wraps to 0)

        Triggers:
        - Metronome downbeat click (loud) via internal audio synthesis
        """
        if self.state.metronome_enabled:
            # Trigger non-blocking audio playback directly
            try:
                self.clicker.play_downbeat()
            except Exception as e:
                logger.debug(f"Error scheduling downbeat audio: {e}")

    def _on_beat(self, beat_index: int):
        """Called at the start of each beat (except downbeat)

        Triggers:
        - Metronome beat click (softer than downbeat) via internal audio synthesis

        Args:
            beat_index: 0-based beat number within the bar
        """
        if self.state.metronome_enabled and beat_index > 0:
            # Trigger non-blocking audio playback directly
            try:
                self.clicker.play_beat()
            except Exception as e:
                logger.debug(f"Error scheduling beat audio: {e}")

    def _send_message_direct(self, message: mido.Message):
        """Send message directly to output port, bypassing processor

        This preserves recorded messages as-is (no scale snapping, arp, harmony applied).

        Implementation: Uses engine output port if available.
        Note: This is a simplified version. In full integration, this would use
        the dispatcher pattern with call_soon_threadsafe() for thread safety.

        Args:
            message: mido.Message to send
        """
        try:
            # Access the output port directly from the engine
            if (
                self.engine
                and hasattr(self.engine, "output_port")
                and self.engine.output_port
            ):
                self.engine.output_port.send(message)
            else:
                logger.debug(f"Output port not available, cannot send: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    # ── Transport Control ──

    async def start_playback(self):
        """Begin pattern playback (looping)

        Process:
        1. Check if already playing
        2. Set is_playing flag
        3. Reset playhead to 0
        4. Start the internal clock
        """
        if self.state.is_playing:
            return

        self.state.is_playing = True
        self.state.current_tick = 0

        # Emit initial downbeat immediately so playback starts in time
        # (clock beat callbacks are generated after first tick advance).
        self._on_bar_start()

        await self.clock.start()
        logger.info(f"Sequencer playback started (BPM={self.state.tempo})")

    async def stop_playback(self):
        """Stop playback and send all notes off

        Process:
        1. Clear is_playing flag
        2. Stop the clock
        3. Send All Notes Off (CC 123) on all 16 channels
        4. Clear held notes tracker
        5. Reset playhead to 0
        """
        if not self.state.is_playing:
            return

        self.state.is_playing = False
        await self.clock.stop()

        # Send All Notes Off on all channels
        for channel in range(16):
            all_notes_off = mido.Message(
                "control_change", control=123, value=0, channel=channel  # All Notes Off
            )
            self._send_message_direct(all_notes_off)

        # Clear state
        self._notes_held.clear()
        self.state.current_tick = 0

        logger.info("Sequencer playback stopped")

    async def start_recording(self):
        """Arm recording and start playback

        Process:
        1. Clear pattern
        2. Clear held notes
        3. Run one-bar pre-count when starting from stopped state
        4. Set is_recording flag
        5. Start playback

        When recording, all processed MIDI will be captured via record_message().
        """
        self.pattern.clear()
        self._notes_held.clear()

        was_playing = self.state.is_playing
        self.state.is_recording = False

        if not was_playing:
            await self._run_precount_bar()

        self.state.is_recording = True

        await self.start_playback()
        logger.info("Sequencer recording started")

    async def _run_precount_bar(self):
        """Run a one-bar pre-count before recording starts.

        Uses the current time signature and tempo. Clicks are emitted only when
        metronome is enabled, but timing delay is always applied.
        """
        beats_in_bar = max(1, int(self.state.time_signature_num))
        seconds_per_beat = self._seconds_per_beat()

        for beat_index in range(beats_in_bar):
            if self.state.metronome_enabled:
                if beat_index == 0:
                    self.clicker.play_downbeat()
                else:
                    self.clicker.play_beat()

            await asyncio.sleep(seconds_per_beat)

    def _seconds_per_beat(self) -> float:
        """Return seconds per beat from current tempo."""
        bpm = max(20.0, min(300.0, float(self.state.tempo)))
        return 60.0 / bpm

    async def stop_recording(self):
        """Disarm recording and stop playback

        Process:
        1. Clear is_recording flag
        2. Stop playback

        Pattern is preserved for playback.
        """
        self.state.is_recording = False
        await self.stop_playback()
        logger.info(
            f"Sequencer recording stopped ({self.pattern.get_event_count()} events)"
        )

    def clear_pattern(self):
        """Clear all events from current pattern

        Safe to call anytime (doesn't affect playback state)
        """
        self.pattern.clear()
        logger.info("Sequencer pattern cleared")

    # ── State Updates (from GUI) ──

    def set_tempo(self, bpm: float):
        """Update tempo with validation

        Args:
            bpm: Tempo in beats per minute (20-300)
        """
        self.state.on_tempo_changed(bpm)
        logger.debug(f"Sequencer tempo: {self.state.tempo} BPM")

    def set_time_signature(self, num: int, den: int):
        """Update time signature and recalculate loop length

        Args:
            num: Numerator (2-16)
            den: Denominator (2, 4, 8, 16)
        """
        self.state.on_time_signature_changed(num, den)
        logger.debug(f"Sequencer time signature: {num}/{den}")

    def set_pattern_bars(self, bars: int):
        """Update number of bars in pattern and recalculate loop length

        Args:
            bars: Number of bars (1-8)
        """
        self.state.on_pattern_bars_changed(bars)
        logger.debug(f"Sequencer pattern bars: {bars}")

    def set_quantization(self, quantization: str):
        """Update quantization grid for recording

        Args:
            quantization: Grid size ("1/4", "1/8", "1/16", "1/32")
        """
        self.state.on_quantization_changed(quantization)
        self._quantization_grid_ticks = self._calculate_quantization_grid()
        logger.debug(f"Sequencer quantization: {quantization}")

    def toggle_metronome(self):
        """Toggle metronome click on/off"""
        self.state.metronome_enabled = not self.state.metronome_enabled
        logger.debug(f"Sequencer metronome: {self.state.metronome_enabled}")

    # ── Persistence ──

    def to_dict(self) -> dict:
        """Serialize sequencer state and pattern for JSON preset storage

        Returns:
            Dictionary with "state" and "pattern" keys
        """
        return {
            "state": self.state.to_dict(),
            "pattern": self.pattern.to_dict(),
        }

    @classmethod
    def from_dict(
        cls, engine: "MidiEngine", context: "AppContext", data: dict
    ) -> "MidiSequencer":
        """Deserialize sequencer from preset data

        Args:
            engine: MidiEngine instance
            context: AppContext instance
            data: Dictionary with "state" and "pattern" keys

        Returns:
            New MidiSequencer with loaded state and pattern
        """
        sequencer = cls(engine, context)

        if "state" in data and isinstance(data["state"], dict):
            sequencer.state = SequencerState.from_dict(data["state"])

        if "pattern" in data and isinstance(data["pattern"], list):
            sequencer.pattern = Pattern.from_dict(data["pattern"])

        return sequencer

    def __repr__(self) -> str:
        return (
            f"MidiSequencer("
            f"playing={self.state.is_playing}, "
            f"recording={self.state.is_recording}, "
            f"tempo={self.state.tempo}, "
            f"events={self.pattern.get_event_count()}"
            f")"
        )
