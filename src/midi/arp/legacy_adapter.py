"""Legacy compatibility adapter for ArpEngine and ArpState.

This module provides backward compatibility for code that imports from the old
src.midi.arp_engine and src.midi.arp_state modules. All imports are forwarded
to the refactored modules in src.midi.arp/.

This adapter allows gradual migration of existing code without breaking
compatibility.

Usage (both work identically):
    # Old import (works via this adapter)
    from src.midi.arp_engine import ArpEngine
    from src.midi.arp_state import ArpState

    # New import (preferred going forward)
    from src.midi.arp.engine_refactored import ArpEngine
    from src.midi.arp.state_validator import ArpState
"""

# Re-export all public names from the refactored modules
from src.midi.arp.engine_refactored import ArpEngine  # noqa: F401
from src.midi.arp.state_validator import (  # noqa: F401
    ArpState,
    TimingConfig,
    VelocityConfig,
    PatternConfig,
)

__all__ = [
    "ArpEngine",
    "ArpState",
    "TimingConfig",
    "VelocityConfig",
    "PatternConfig",
]
