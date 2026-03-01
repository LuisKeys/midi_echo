import mido
import platform
import logging
from typing import List

logger = logging.getLogger(__name__)


class PortManager:
    """Manages MIDI port discovery and filtering across platforms."""

    def __init__(self):
        self.system = platform.system()
        self._available_outputs = None  # Cache for available outputs

    def get_input_names(self) -> list[str]:
        return mido.get_input_names()

    def get_output_names(self) -> list[str]:
        """Get available output ports (cached)."""
        if self._available_outputs is None:
            self._available_outputs = mido.get_output_names()
        return self._available_outputs

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
        """Finds the first output port matching the hint (backward compatibility)."""
        available = self.get_output_names()
        for name in available:
            if hint.lower() in name.lower():
                return name
        return None

    def filter_by_patterns(self, patterns: List[str]) -> List[str]:
        """Filter available output ports by a list of name patterns.

        Args:
            patterns: List of substring patterns to match (case-insensitive)

        Returns:
            List of output port names that match any pattern, in order of pattern priority.
        """
        available = self.get_output_names()
        matched_ports = []

        for pattern in patterns:
            for name in available:
                if pattern.lower() in name.lower() and name not in matched_ports:
                    matched_ports.append(name)
                    logger.debug(f"Port matched pattern '{pattern}': {name}")

        return matched_ports

    def find_output_port_from_patterns(
        self, patterns: List[str]
    ) -> tuple[str | None, List[str]]:
        """Find the best output port from a list of patterns.

        Args:
            patterns: List of preferred output patterns (in priority order)

        Returns:
            Tuple of (selected_port, list_of_all_available_ports)
            selected_port is None if no patterns match any available port.
        """
        available = self.get_output_names()
        matched = self.filter_by_patterns(patterns)

        # Return first match if found, otherwise None
        if matched:
            logger.info(
                f"Selected output port: {matched[0]} (from {len(matched)} matches)"
            )
            return matched[0], available
        else:
            logger.warning(f"No output ports matched patterns: {patterns}")
            return None, available
