import mido
import logging
import time
from src.midi.arp.state_validator import ArpState
from src.midi.message_wrapper import MidiMessageWrapper

logger = logging.getLogger(__name__)


class MidiProcessor:
    """Handles MIDI message transformation and routing logic."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # State for live performance
        self.output_channel = None  # None means keep original
        self.transpose = 0
        self.octave = 0
        self.fx_enabled = False
        self.scale_enabled = False
        # Backwards-compatible boolean flag
        self.arp_enabled = False
        # Full arpeggiator state container
        self.arp_state: ArpState = ArpState()
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
        else:
            original_msg = msg
            is_arp = False

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

        # Handle arpeggiator input notes
        if self.arp_enabled and new_msg.type in ["note_on", "note_off"]:
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
            self._update_arp_mask()
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if self.arp_state.latch != "HOLD":
                self.arp_state.held_notes.discard(msg.note)
                self._update_arp_mask()

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

    def _update_arp_mask(self) -> None:
        """Update pattern mask based on held notes."""
        self.arp_state.pattern.mask = [False] * 12
        for note in self.arp_state.held_notes:
            semitone = note % 12
            self.arp_state.pattern.mask[semitone] = True
        # Update chord memory
        self.arp_state.chord_memory = sorted(list(self.arp_state.held_notes))
