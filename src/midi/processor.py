import mido
import logging
import time
from src.midi.arp.state_validator import ArpState
from src.midi.harmony.state import HarmonyState
from src.midi.message_wrapper import MidiMessageWrapper
from src.midi.scales import ScaleType, snap_note_to_scale
from src.state import AppState

logger = logging.getLogger(__name__)


class MidiProcessor:
    """Handles MIDI message transformation and routing logic."""

    def __init__(
        self,
        verbose: bool = False,
        config: object = None,
        event_log=None,
        app_state: AppState = None,
    ):
        self.verbose = verbose
        self.config = config
        self.event_log = event_log
        self.app_state = app_state or AppState()
        self.harmony_engine = None  # Will be set from context
        self.context = None

    @property
    def output_channel(self):
        return self.app_state.performance.output_channel

    @output_channel.setter
    def output_channel(self, value):
        self.app_state.performance.output_channel = value

    @property
    def transpose(self):
        return self.app_state.performance.transpose

    @transpose.setter
    def transpose(self, value):
        self.app_state.performance.transpose = int(value)

    @property
    def octave(self):
        return self.app_state.performance.octave

    @octave.setter
    def octave(self, value):
        self.app_state.performance.octave = int(value)

    @property
    def fx_enabled(self):
        return self.app_state.performance.fx_enabled

    @fx_enabled.setter
    def fx_enabled(self, value):
        self.app_state.performance.fx_enabled = bool(value)

    @property
    def harmonizer_enabled(self):
        return self.app_state.performance.harmonizer_enabled

    @harmonizer_enabled.setter
    def harmonizer_enabled(self, value):
        self.app_state.performance.harmonizer_enabled = bool(value)

    @property
    def scale_enabled(self):
        return self.app_state.performance.scale_enabled

    @scale_enabled.setter
    def scale_enabled(self, value):
        self.app_state.performance.scale_enabled = bool(value)

    @property
    def scale_root(self):
        return self.app_state.performance.scale_root

    @scale_root.setter
    def scale_root(self, value):
        self.app_state.performance.scale_root = max(0, min(11, int(value)))

    @property
    def scale_type(self):
        return self.app_state.performance.scale_type

    @scale_type.setter
    def scale_type(self, value):
        if isinstance(value, ScaleType):
            self.app_state.performance.scale_type = value
        else:
            try:
                self.app_state.performance.scale_type = ScaleType(value)
            except Exception:
                self.app_state.performance.scale_type = ScaleType.MAJOR

    @property
    def arp_enabled(self):
        return self.app_state.performance.arp_enabled

    @arp_enabled.setter
    def arp_enabled(self, value):
        enabled = bool(value)
        self.app_state.performance.arp_enabled = enabled
        self.app_state.arp.enabled = enabled

    @property
    def arp_state(self) -> ArpState:
        return self.app_state.arp

    @arp_state.setter
    def arp_state(self, value: ArpState):
        self.app_state.arp = value
        self.app_state.performance.arp_enabled = bool(getattr(value, "enabled", False))

    @property
    def harmony_state(self) -> HarmonyState:
        return self.app_state.harmony

    @harmony_state.setter
    def harmony_state(self, value: HarmonyState):
        self.app_state.harmony = value

    @property
    def error_state(self):
        return self.app_state.transport_io.error_state

    @error_state.setter
    def error_state(self, value):
        self.app_state.transport_io.error_state = bool(value)

    @property
    def last_clock_time(self):
        return self.app_state.transport_io.last_clock_time

    @last_clock_time.setter
    def last_clock_time(self, value):
        self.app_state.transport_io.last_clock_time = value

    @property
    def clock_intervals(self):
        return self.app_state.transport_io.clock_intervals

    @clock_intervals.setter
    def clock_intervals(self, value):
        self.app_state.transport_io.clock_intervals = list(value)

    def process(self, msg) -> mido.Message | None:
        """
        Process an incoming MIDI message.
        Returns the message (possibly modified) to be sent, or None if it should be dropped.
        """
        # Unwrap if it's a wrapper
        if isinstance(msg, MidiMessageWrapper):
            original_msg = msg.msg
            is_arp = msg.is_arp
            port = msg.port
        else:
            original_msg = msg
            is_arp = False
            port = ""

        # Ignore clock and sensing by default to reduce noise in logs
        if self.verbose and original_msg.type not in ["clock", "active_sensing"]:
            logger.info(f"Processing: {original_msg}")

        # Handle clock for external sync
        if original_msg.type == "clock" and self.arp_state.external_sync:
            self._handle_clock()

        # Clone message to avoid side effects on the original
        if original_msg.is_meta:
            return original_msg

        new_msg = original_msg.copy()

        # Apply scale snapping FIRST for input notes (before arp/harmony processing)
        if (
            self.scale_enabled
            and new_msg.type in ["note_on", "note_off", "polytouch"]
            and not is_arp
        ):
            new_msg.note = snap_note_to_scale(
                new_msg.note, self.scale_root, self.scale_type
            )

        # Handle harmonizer
        if self.harmonizer_enabled and self.harmony_engine and not is_arp:
            if new_msg.type in ["note_on", "note_off"]:
                self._process_melody_note(new_msg)

        # Handle arpeggiator input notes (only real input, not arp-generated)
        if self.arp_enabled and new_msg.type in ["note_on", "note_off"] and not is_arp:
            self._update_arp_notes(new_msg)

        # Drop input notes when arp is enabled (only allow arp-generated notes)
        if new_msg.type in ["note_on", "note_off"] and self.arp_enabled and not is_arp:
            return None

        # Apply transformations for note messages
        if new_msg.type in ["note_on", "note_off", "polytouch"]:
            # Transposition and Octave
            shift = self.transpose + (self.octave * 12)
            if shift != 0:
                new_note = new_msg.note + shift
                if 0 <= new_note <= 127:
                    new_msg.note = new_note
                else:
                    return None  # Drop if out of MIDI range

        # Apply channel mapping
        if self.output_channel is not None and hasattr(new_msg, "channel"):
            new_msg.channel = self.output_channel

        # Log outgoing event
        if new_msg and self.event_log:
            channel = getattr(new_msg, "channel", 0)
            self.event_log.add_event("out", new_msg, channel)

        return new_msg

    def _update_arp_notes(self, msg: mido.Message) -> None:
        """Update held notes for arpeggiator based on input."""
        if msg.type == "note_on" and msg.velocity > 0:
            self.arp_state.held_notes.add(msg.note)
            logger.debug(
                f"AR note added: {msg.note}, held_notes now: {sorted(self.arp_state.held_notes)}"
            )
            self._update_arp_pattern()
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if self.arp_state.latch != "HOLD":
                self.arp_state.held_notes.discard(msg.note)
                logger.debug(
                    f"AR note removed: {msg.note}, held_notes now: {sorted(self.arp_state.held_notes)}"
                )
                self._update_arp_pattern()

    def _update_arp_pattern(self) -> None:
        """Update arpeggiator pattern from held notes."""
        # Sync held_notes to pattern.notes so the arp engine can generate from them
        self.arp_state.pattern.notes = sorted(list(self.arp_state.held_notes))
        logger.debug(f"AR pattern.notes updated: {self.arp_state.pattern.notes}")

    def _handle_clock(self) -> None:
        """Handle MIDI clock message for external sync."""
        current_time = time.time()
        if self.last_clock_time is not None:
            interval = current_time - self.last_clock_time
            self.clock_intervals.append(interval)
            if len(self.clock_intervals) > 24:  # Keep last 24 intervals
                self.clock_intervals.pop(0)
            if len(self.clock_intervals) >= 6:  # Need some samples
                avg_interval = sum(self.clock_intervals) / len(self.clock_intervals)
                quarter_time = avg_interval * 24  # 24 clocks per quarter
                bpm = 60.0 / quarter_time
                clamped_bpm = int(max(20, min(300, bpm)))
                if self.context and hasattr(self.context, "set_global_tempo"):
                    self.context.set_global_tempo(clamped_bpm)
                else:
                    self.arp_state.timing.bpm = clamped_bpm
        self.last_clock_time = current_time

    def _process_melody_note(self, msg: mido.Message) -> None:
        """Process melody note for harmonizer."""
        if msg.type == "note_on" and msg.velocity > 0:
            self.harmony_engine.process_melody_note_on(
                msg.note, msg.velocity, msg.channel, self.scale_root, self.scale_type
            )
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            self.harmony_engine.process_melody_note_off(msg.note, msg.channel)

    def clear_arp_cache(self) -> None:
        """Clear all arpeggiator state to prevent stale notes."""
        self.arp_state.held_notes.clear()
        self.arp_state.pattern.notes.clear()
        logger.info("AR cache cleared: held_notes and pattern.notes reset to empty")
