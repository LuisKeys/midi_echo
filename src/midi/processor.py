import mido
import logging
import time
from src.midi.arp.state_validator import ArpState
from src.midi.harmony.state import HarmonyState
from src.midi.message_wrapper import MidiMessageWrapper
from src.midi.scales import ScaleType, snap_note_to_scale

logger = logging.getLogger(__name__)


class MidiProcessor:
    """Handles MIDI message transformation and routing logic."""

    def __init__(self, verbose: bool = False, config: object = None):
        self.verbose = verbose
        self.config = config
        # State for live performance
        self.output_channel = None  # None means keep original
        self.transpose = 0
        self.octave = 0
        self.fx_enabled = False
        self.harmonizer_enabled = False
        self.scale_enabled = False
        self.scale_root = 0  # 0-11, default C
        self.scale_type = ScaleType.MAJOR
        # Backwards-compatible boolean flag
        self.arp_enabled = False
        # Full arpeggiator state container
        self.arp_state: ArpState = ArpState()
        # Harmonizer state
        self.harmony_state: HarmonyState = HarmonyState()
        self.harmony_engine = None  # Will be set from context
        self.error_state = False
        # Clock sync
        self.last_clock_time = None
        self.clock_intervals = []

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

        # Apply scale snapping for input notes before arp processing
        if (
            self.scale_enabled
            and new_msg.type in ["note_on", "note_off", "aftertouch", "polytouch"]
            and not is_arp
        ):
            new_msg.note = snap_note_to_scale(
                new_msg.note, self.scale_root, self.scale_type
            )

        # Handle harmonizer
        if self.harmonizer_enabled and self.harmony_engine and not is_arp:
            if port == getattr(self.config, "harmonizer_chord_port", ""):
                # Chord input
                self._update_chord_notes(new_msg)
            else:
                # Melody input
                self._process_melody_note(new_msg)

        # Handle arpeggiator input notes (only real input, not arp-generated)
        if self.arp_enabled and new_msg.type in ["note_on", "note_off"] and not is_arp:
            self._update_arp_notes(new_msg)

        # Drop input notes when arp is enabled (only allow arp-generated notes)
        if new_msg.type in ["note_on", "note_off"] and self.arp_enabled and not is_arp:
            return None

        # Apply transformations for note messages
        if new_msg.type in ["note_on", "note_off", "aftertouch", "polytouch"]:
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

        return new_msg

    def _update_arp_notes(self, msg: mido.Message) -> None:
        """Update held notes for arpeggiator based on input."""
        if msg.type == "note_on" and msg.velocity > 0:
            self.arp_state.held_notes.add(msg.note)
            self._update_arp_pattern()
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if self.arp_state.latch != "HOLD":
                self.arp_state.held_notes.discard(msg.note)
                self._update_arp_pattern()

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
                self.arp_state.timing.bpm = int(max(20, min(300, bpm)))
        self.last_clock_time = current_time

    def _update_chord_notes(self, msg: mido.Message) -> None:
        """Update held notes for chord analyzer."""
        if msg.type == "note_on" and msg.velocity > 0:
            self.harmony_engine.chord_analyzer.held_notes.add(msg.note)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            self.harmony_engine.chord_analyzer.held_notes.discard(msg.note)

    def _process_melody_note(self, msg: mido.Message) -> None:
        """Process melody note for harmonizer."""
        if msg.type == "note_on" and msg.velocity > 0:
            self.harmony_engine.process_melody_note_on(
                msg.note, msg.velocity, msg.channel
            )
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            self.harmony_engine.process_melody_note_off(msg.note, msg.channel)
