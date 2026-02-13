"""Pattern editor tab modules."""

from .pattern_tab import _build_pattern_tab
from .timing_tab import _build_timing_tab
from .modes_tab import _build_modes_tab
from .velocity_tab import _build_velocity_tab
from .advanced_tab import _build_advanced_tab

__all__ = [
    "_build_pattern_tab",
    "_build_timing_tab",
    "_build_modes_tab",
    "_build_velocity_tab",
    "_build_advanced_tab",
]
