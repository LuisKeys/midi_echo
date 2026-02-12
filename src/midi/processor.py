import mido
import logging

logger = logging.getLogger(__name__)


class MidiProcessor:
    """Handles MIDI message transformation and routing logic."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def process(self, msg: mido.Message) -> mido.Message | None:
        """
        Process an incoming MIDI message.
        Returns the message (possibly modified) to be sent, or None if it should be dropped.
        """
        # Ignore clock and sensing by default to reduce noise in logs
        if self.verbose and msg.type not in ["clock", "active_sensing"]:
            logger.info(f"Processing: {msg}")

        # Basic echo: returns the message as is
        return msg
