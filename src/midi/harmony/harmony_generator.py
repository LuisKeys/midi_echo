"""Harmony generator for creating harmony notes based on melody and chord context."""

from typing import List, Optional, Tuple


class HarmonyGenerator:
    """Generates harmony notes for a given melody note using chord context."""

    def __init__(self, intervals: List[int]):
        self.intervals = intervals

    def set_intervals(self, intervals: List[int]) -> None:
        """Update the harmony intervals."""
        self.intervals = [max(1, min(24, i)) for i in intervals]

    def generate_harmony(
        self, melody_note: int, chord_root: Optional[int], chord_quality: str
    ) -> List[int]:
        """Generate harmony notes for the melody note.

        Args:
            melody_note: The input melody note (0-127)
            chord_root: Root note of the chord (0-127) or None
            chord_quality: "major", "minor", or "unknown"

        Returns:
            List of harmony note pitches (0-127), clamped to valid range.
        """
        if chord_root is None:
            return []

        harmony_notes = []
        for interval in self.intervals:
            # Adjust interval based on chord quality if needed
            adjusted_interval = interval
            if chord_quality == "minor" and interval == 4:  # major 3rd in minor chord
                adjusted_interval = 3  # minor 3rd

            harmony_note = melody_note + adjusted_interval
            if 0 <= harmony_note <= 127:
                harmony_notes.append(harmony_note)

        return harmony_notes
