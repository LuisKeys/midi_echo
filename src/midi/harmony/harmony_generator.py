"""Harmony generator for creating harmony notes based on melody and scale context."""

from typing import List
from ..scales import ScaleType, snap_note_to_scale


class HarmonyGenerator:
    """Generates harmony notes for a given melody note using scale context."""

    def __init__(self, intervals: List[int]):
        self.intervals = intervals

    def set_intervals(self, intervals: List[int]) -> None:
        """Update the harmony intervals."""
        self.intervals = [max(1, min(24, i)) for i in intervals]

    def generate_harmony(
        self, melody_note: int, scale_root: int, scale_type: ScaleType
    ) -> List[int]:
        """Generate harmony notes for the melody note, snapped to scale.

        Args:
            melody_note: The input melody note (0-127)
            scale_root: Root of the scale (0-11)
            scale_type: ScaleType enum

        Returns:
            List of harmony note pitches (0-127), snapped to scale tones.
        """
        harmony_notes = []
        for interval in self.intervals:
            # Generate harmony note at the interval
            harmony_note = melody_note + interval

            # Snap to scale
            if 0 <= harmony_note <= 127:
                snapped_note = snap_note_to_scale(harmony_note, scale_root, scale_type)
                harmony_notes.append(snapped_note)

        return harmony_notes
