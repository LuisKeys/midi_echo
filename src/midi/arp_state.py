"""Backward compatibility shim for arp_state.py

This module has been refactored into src.midi.arp/state_validator.py.
All imports are forwarded to the refactored module for compatibility.

NEW CODE SHOULD USE:
    from src.midi.arp.state_validator import ArpState

LEGACY CODE CAN STILL USE:
    from src.midi.arp_state import ArpState
"""

# Re-export from refactored module
from src.midi.arp.state_validator import (
    ArpState,
    TimingConfig,
    VelocityConfig,
    PatternConfig,
)

__all__ = ["ArpState", "TimingConfig", "VelocityConfig", "PatternConfig"]
