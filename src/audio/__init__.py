"""Audio synthesis and playback module for internal sound generation.

This module provides click synthesis and audio output for features like the
metronome, replacing MIDI-based audio.
"""

from .synthesizer import MetronomeClicker
from .device_selector import (
    list_audio_devices,
    find_device_by_name,
    get_device_info,
    validate_device_id,
)

__all__ = [
    "MetronomeClicker",
    "list_audio_devices",
    "find_device_by_name",
    "get_device_info",
    "validate_device_id",
]
