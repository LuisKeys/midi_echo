"""MIDI Pattern Sequencer

Single-track loop-based MIDI sequencer that records fully processed output
and replays it with an internal PPQN-based clock.

Responsibilities:
- Recording: Tap processed MIDI messages, quantize to grid, store in pattern
- Playback: Loop pattern, emit MIDI directly to output port
- Timing: Async clock with PPQN=960 resolution for high-precision playback
- State: Manage tempo, time signature, pattern bars, quantization, metronome
"""

from .sequencer_state import SequencerState
from .pattern import Pattern, PatternEvent
from .clock import InternalClock
from .sequencer import MidiSequencer

__all__ = [
    "SequencerState",
    "Pattern",
    "PatternEvent",
    "InternalClock",
    "MidiSequencer",
]
