"""Centralized state model for the MIDI Echo application."""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from src.midi.arp.state_validator import ArpState
from src.midi.harmony.state import HarmonyState
from src.midi.scales import ScaleType

if TYPE_CHECKING:
    from src.midi.sequencer.sequencer_state import SequencerState


def _default_sequencer_state() -> "SequencerState":
    from src.midi.sequencer.sequencer_state import SequencerState

    return SequencerState()


@dataclass
class PerformanceState:
    """Musical/performance transformation state."""

    output_channel: Optional[int] = None
    transpose: int = 0
    octave: int = 0
    fx_enabled: bool = False
    harmonizer_enabled: bool = False
    scale_enabled: bool = False
    scale_root: int = 0
    scale_type: ScaleType = ScaleType.MAJOR
    arp_enabled: bool = False


@dataclass
class TransportIOState:
    """Transport/clock/IO runtime state."""

    error_state: bool = False
    last_clock_time: Optional[float] = None
    clock_intervals: list[float] = field(default_factory=list)


@dataclass
class UIRuntimeState:
    """UI runtime/ephemeral state."""

    tempo_widgets: list[object] = field(default_factory=list)
    tap_times: list[float] = field(default_factory=list)


@dataclass
class AppState:
    """Single root state container for the entire app."""

    schema_version: int = 1
    performance: PerformanceState = field(default_factory=PerformanceState)
    transport_io: TransportIOState = field(default_factory=TransportIOState)
    ui_runtime: UIRuntimeState = field(default_factory=UIRuntimeState)
    arp: ArpState = field(default_factory=ArpState)
    harmony: HarmonyState = field(default_factory=HarmonyState)
    sequencer: "SequencerState" = field(default_factory=_default_sequencer_state)
