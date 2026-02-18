# scales.py - Scale definitions and note snapping logic for MIDI processing

from typing import List, Dict
from enum import Enum


class ScaleType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    LOCRIAN = "locrian"
    CHROMATIC = "chromatic"


# Scale intervals from root (semitones)
SCALE_INTERVALS: Dict[ScaleType, List[int]] = {
    ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11],
    ScaleType.MINOR: [0, 2, 3, 5, 7, 8, 10],
    ScaleType.DORIAN: [0, 2, 3, 5, 7, 9, 10],
    ScaleType.PHRYGIAN: [0, 1, 3, 5, 7, 8, 10],
    ScaleType.LYDIAN: [0, 2, 4, 6, 7, 9, 11],
    ScaleType.MIXOLYDIAN: [0, 2, 4, 5, 7, 9, 10],
    ScaleType.LOCRIAN: [0, 1, 3, 5, 6, 8, 10],
    ScaleType.CHROMATIC: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}

# Scale names for display
SCALE_NAMES: Dict[ScaleType, str] = {
    ScaleType.MAJOR: "Major",
    ScaleType.MINOR: "Minor",
    ScaleType.DORIAN: "Dorian",
    ScaleType.PHRYGIAN: "Phrygian",
    ScaleType.LYDIAN: "Lydian",
    ScaleType.MIXOLYDIAN: "Mixolydian",
    ScaleType.LOCRIAN: "Locrian",
    ScaleType.CHROMATIC: "Chromatic",
}

# Note names for root selection
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def get_scale_notes(root: int, scale_type: ScaleType) -> List[int]:
    """Get the list of note numbers (0-11) for the given root and scale type."""
    intervals = SCALE_INTERVALS[scale_type]
    return [(note + root) % 12 for note in intervals]


def snap_note_to_scale(note: int, root: int, scale_type: ScaleType) -> int:
    """
    Snap a MIDI note (0-127) to the nearest note in the scale.
    Considers adjacent octaves to prevent large jumps.
    Returns the snapped note number.
    """
    note_mod12 = note % 12
    octave = note // 12
    scale_notes = get_scale_notes(root, scale_type)

    # Candidate notes in current octave and adjacent octaves
    candidates_with_octaves = []

    for scale_note in scale_notes:
        # Check current octave
        snapped = octave * 12 + scale_note
        if 0 <= snapped <= 127:
            distance = abs(note - snapped)
            candidates_with_octaves.append((distance, snapped))

        # Check octave above
        snapped_up = (octave + 1) * 12 + scale_note
        if snapped_up <= 127:
            distance = abs(note - snapped_up)
            candidates_with_octaves.append((distance, snapped_up))

        # Check octave below
        snapped_down = (octave - 1) * 12 + scale_note
        if snapped_down >= 0:
            distance = abs(note - snapped_down)
            candidates_with_octaves.append((distance, snapped_down))

    if not candidates_with_octaves:
        return note  # Fallback: return original if no valid snaps

    # Find minimum distance; if tied, prefer upward (higher note)
    min_distance = min(c[0] for c in candidates_with_octaves)
    candidates_at_min = [c[1] for c in candidates_with_octaves if c[0] == min_distance]

    return max(candidates_at_min)  # Upward bias: choose highest candidate


def get_scale_display_name(root: int, scale_type: ScaleType) -> str:
    """Get the display name for the scale, e.g., 'C Major'."""
    root_name = NOTE_NAMES[root]
    scale_name = SCALE_NAMES[scale_type]
    return root_name + " " + scale_name
