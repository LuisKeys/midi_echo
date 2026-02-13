"""Arpeggiator mode strategies for different playback patterns.

Each mode encapsulates how notes are selected and how position advances
through the active note set.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import random


class ArpMode(ABC):
    """Abstract base class for arpeggiator playback modes."""

    @abstractmethod
    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Build list of active note indices from pattern mask.

        Args:
            pattern_mask: List of 12 booleans indicating which notes are active.

        Returns:
            List of indices (0..11) that are currently active, in playing order.
        """
        pass

    @abstractmethod
    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Choose the next note and advance position.

        Args:
            active_indices: List of active indices from build_active_indices.
            current_position: Current position in the active_indices list.

        Returns:
            Tuple of (index into active_indices, new_position).
        """
        pass

    def reset_position(self) -> int:
        """Get initial position for mode."""
        return 0


class UpMode(ArpMode):
    """Play notes in ascending order."""

    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Return active indices in ascending order."""
        return [i for i, active in enumerate(pattern_mask) if active]

    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Return current index and advance position linearly."""
        if not active_indices:
            return 0, 0

        pos = current_position % len(active_indices)
        new_pos = (current_position + 1) % len(active_indices)
        return pos, new_pos


class DownMode(ArpMode):
    """Play notes in descending order."""

    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Return active indices in descending order."""
        active = [i for i, v in enumerate(pattern_mask) if v]
        return list(reversed(active))

    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Return current index and advance position linearly."""
        if not active_indices:
            return 0, 0

        pos = current_position % len(active_indices)
        new_pos = (current_position + 1) % len(active_indices)
        return pos, new_pos


class UpDownMode(ArpMode):
    """Play notes ascending then descending, bouncing at endpoints."""

    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Return path: up + down (excluding endpoints to avoid repetition)."""
        active = [i for i, v in enumerate(pattern_mask) if v]
        if not active:
            return []
        if len(active) == 1:
            return active

        # Up path: all notes
        up = active
        # Down path: all notes except first and last (to avoid repeating endpoints)
        down = list(reversed(active))[1:-1] if len(active) > 2 else []

        return up + down

    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Return current index and advance position linearly."""
        if not active_indices:
            return 0, 0

        pos = current_position % len(active_indices)
        new_pos = (current_position + 1) % len(active_indices)
        return pos, new_pos


class RandomMode(ArpMode):
    """Play notes in random order."""

    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Return all active indices (randomness applied per-note)."""
        return [i for i, active in enumerate(pattern_mask) if active]

    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Return random index (position stays at 0)."""
        if not active_indices:
            return 0, 0

        idx = random.randrange(len(active_indices))
        # Position doesn't advance in random mode; new_pos = 0 indicates we start fresh
        return idx, 0

    def reset_position(self) -> int:
        """Random mode doesn't use position tracking."""
        return 0


class ChordMode(ArpMode):
    """Play all active notes simultaneously (future feature).

    Currently behaves like UpMode as a placeholder.
    When implemented, will play all notes at once rather than sequentially.
    """

    def build_active_indices(self, pattern_mask: List[bool]) -> List[int]:
        """Return all active indices."""
        return [i for i, active in enumerate(pattern_mask) if active]

    def choose_next(
        self, active_indices: List[int], current_position: int
    ) -> Tuple[int, int]:
        """Return current index and advance position (placeholder).

        TODO: Future implementation will return all indices at once,
        represented as a special position value.
        """
        if not active_indices:
            return 0, 0

        pos = current_position % len(active_indices)
        new_pos = (current_position + 1) % len(active_indices)
        return pos, new_pos


def create_mode(mode_name: str) -> ArpMode:
    """Factory function to create mode instance by name.

    Args:
        mode_name: Name of mode (UP, DOWN, UPDOWN, RANDOM, CHORD)

    Returns:
        ArpMode instance, defaults to UpMode if name not recognized.
    """
    mode_map = {
        "UP": UpMode,
        "DOWN": DownMode,
        "UPDOWN": UpDownMode,
        "RANDOM": RandomMode,
        "CHORD": ChordMode,
    }
    mode_class = mode_map.get((mode_name or "UP").upper(), UpMode)
    return mode_class()
