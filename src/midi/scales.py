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
    Returns the snapped note number.
    """
    note_mod12 = note % 12
    scale_notes = get_scale_notes(root, scale_type)

    # Find the closest scale note, considering chromatic circle
    min_distance = 12
    candidates = []

    for scale_note in scale_notes:
        # Direct distance
        dist = abs(note_mod12 - scale_note)
        # Wrap-around distance
        wrap_dist = 12 - dist
        actual_dist = min(dist, wrap_dist)

        if actual_dist < min_distance:
            min_distance = actual_dist
            candidates = [scale_note]
        elif actual_dist == min_distance:
            candidates.append(scale_note)

    # If multiple candidates at same distance, choose the highest (upward bias)
    snapped_mod12 = max(candidates)

    # Calculate the snapped note, preserving octave
    octave = note // 12
    snapped_note = octave * 12 + snapped_mod12

    # Edge cases
    if snapped_note > 127:
        snapped_note -= 12
    elif snapped_note < 0:
        snapped_note += 12

    return snapped_note

def get_scale_display_name(root: int, scale_type: ScaleType) -> str:
    """Get the display name for the scale, e.g., 'C Major'."""
    root_name = NOTE_NAMES[root]
    scale_name = SCALE_NAMES[scale_type]
    return root_name + " " + scale_name