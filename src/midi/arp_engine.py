"""Backward compatibility shim for arp_engine.py

This module has been refactored into src.midi.arp/engine_refactored.py
with separated concerns for timing, modes, note production, and MIDI dispatching.

All imports are forwarded to the refactored module for compatibility.

Architecture:
- src.midi.arp.timing: BPM/division/swing calculations
- src.midi.arp.modes: Strategy pattern for UP/DOWN/UPDOWN/RANDOM/CHORD
- src.midi.arp.note_producer: Velocity and accent logic
- src.midi.arp.dispatcher: Thread-safe MIDI message queuing
- src.midi.arp.engine_refactored: Orchestrates all components

NEW CODE SHOULD USE:
    from src.midi.arp.engine_refactored import ArpEngine

LEGACY CODE CAN STILL USE:
    from src.midi.arp_engine import ArpEngine
"""

# Re-export from refactored module
from src.midi.arp.arp_engin import ArpEngine

__all__ = ["ArpEngine"]
