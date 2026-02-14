"""Chord analyzer for detecting chord context from held notes."""

from typing import List, Optional, Tuple


class ChordAnalyzer:
    """Analyzes held notes to determine chord root and quality."""

    def __init__(self):
        self.held_notes: set[int] = set()

    def update_held_notes(self, held_notes: set[int]) -> None:
        """Update the set of currently held notes."""
        self.held_notes = held_notes.copy()

    def get_chord_context(self) -> Tuple[Optional[int], str]:
        """Return (root_note, quality) for the current chord.

        Returns (None, "") if no chord detected.
        """
        if not self.held_notes:
            return None, ""

        notes = sorted(list(self.held_notes))
        root = notes[0]

        # Simple chord detection
        intervals = [n - root for n in notes]

        has_major_3rd = 4 in intervals
        has_minor_3rd = 3 in intervals
        has_5th = 7 in intervals

        if has_major_3rd and has_5th:
            quality = "major"
        elif has_minor_3rd and has_5th:
            quality = "minor"
        else:
            quality = "unknown"

        return root, quality
