"""Voice manager for tracking harmony voices and preventing overload."""

from typing import Dict, List, Set


class VoiceManager:
    """Manages active harmony voices to prevent MIDI overload."""

    def __init__(self, max_voices: int = 4):
        self.max_voices = max_voices
        self.active_voices: Dict[int, List[int]] = (
            {}
        )  # melody_note -> list of harmony_notes
        self.voice_count = 0

    def set_max_voices(self, max_voices: int) -> None:
        """Update the maximum number of harmony voices."""
        self.max_voices = max(1, min(16, max_voices))

    def allocate_voices(self, melody_note: int, harmony_notes: List[int]) -> List[int]:
        """Allocate voices for harmony notes, respecting the limit.

        Returns the list of harmony notes that can be allocated.
        """
        available_slots = self.max_voices - self.voice_count
        if available_slots <= 0:
            return []

        allocated = harmony_notes[:available_slots]
        self.active_voices[melody_note] = allocated
        self.voice_count += len(allocated)
        return allocated

    def deallocate_voices(self, melody_note: int) -> List[int]:
        """Deallocate voices for a melody note.

        Returns the list of harmony notes that were active.
        """
        if melody_note not in self.active_voices:
            return []

        harmony_notes = self.active_voices.pop(melody_note)
        self.voice_count -= len(harmony_notes)
        return harmony_notes

    def get_active_harmonies(self, melody_note: int) -> List[int]:
        """Get currently active harmony notes for a melody note."""
        return self.active_voices.get(melody_note, [])
