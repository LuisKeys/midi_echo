import mido
import platform
import logging

logger = logging.getLogger(__name__)


class PortManager:
    """Manages MIDI port discovery and filtering across platforms."""

    def __init__(self):
        self.system = platform.system()

    def get_input_names(self) -> list[str]:
        return mido.get_input_names()

    def get_output_names(self) -> list[str]:
        return mido.get_output_names()

    def filter_inputs(
        self, input_names: list[str], output_to_exclude: str = None
    ) -> list[str]:
        """Filters out system ports and specific output ports to prevent loops."""
        filtered = []
        for name in input_names:
            # Linux: Filter ALSA Through ports
            if self.system == "Linux" and "Midi Through" in name:
                logger.debug(f"Filtering system port: {name}")
                continue

            # Skip the specific output port to prevent immediate feedback loops,
            # UNLESS it's the only port available and we are in a dev environment.
            if output_to_exclude and name == output_to_exclude:
                if len(input_names) > 1:
                    logger.debug(f"Filtering output port from inputs: {name}")
                    continue
                else:
                    logger.warning(
                        f"Input and output are the same: {name}. Potential feedback loop!"
                    )

            filtered.append(name)
        return filtered

    def find_output_port(self, hint: str) -> str | None:
        """Finds the first output port matching the hint."""
        available = self.get_output_names()
        for name in available:
            if hint.lower() in name.lower():
                return name
        return None
