import mido
import logging
from src.midi.arp.state_validator import ArpState

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

    def process(self, msg: mido.Message) -> mido.Message | None:
        """
        Process an incoming MIDI message.
        Returns the message (possibly modified) to be sent, or None if it should be dropped.
        """
        # Ignore clock and sensing by default to reduce noise in logs
        if self.verbose and msg.type not in ["clock", "active_sensing"]:
            logger.info(f"Processing: {msg}")

        # Clone message to avoid side effects on the original
        if msg.is_meta:
            return msg

        new_msg = msg.copy()

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
