"""Audio synthesis and playback module for internal sound generation.

This module provides click synthesis and audio output for features like the
metronome, replacing MIDI-based audio.
"""

from .synthesizer import MetronomeClicker

__all__ = ["MetronomeClicker"]
