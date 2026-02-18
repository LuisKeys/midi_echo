"""Arpeggiator engine package with refactored components for MIDI echo.

This package contains a fully refactored arpeggiator engine with separated concerns:

Modules:
- timing.py: TimingCalculator for BPM/division/swing calculations
- modes.py: ArpMode strategy pattern for different playback patterns
- note_producer.py: NoteProducer for velocity and accent logic
- dispatcher.py: MidiDispatcher for thread-safe MIDI message queuing
- state_validator.py: Refactored ArpState with nested configuration objects
- engine_refactored.py: Main ArpEngine orchestrating all components
- legacy_adapter.py: Backward compatibility shim

Import Examples:
    # New (recommended)
    from src.midi.arp.engine_refactored import ArpEngine
    from src.midi.arp.state_validator import ArpState

    # Legacy (still works, via compatibility shim)
    from src.midi.arp_engine import ArpEngine
    from src.midi.arp_state import ArpState
"""

from .arp_engin import ArpEngine
from .state_validator import ArpState, TimingConfig, VelocityConfig, PatternConfig

__all__ = ["ArpEngine", "ArpState", "TimingConfig", "VelocityConfig", "PatternConfig"]
