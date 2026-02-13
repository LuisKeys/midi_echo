"""Timing calculation module for arpeggiator engine.

Separates timing logic (BPM, divisions, swing) from the main engine loop
to enable independent testing and reuse.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class TimingMetadata:
    """Calculated timing metadata for a single step."""

    interval: float  # seconds between steps
    swing_delay: float  # additional delay for swing on odd steps
    total_sleep: float  # interval + swing_delay (always >= 0.001)


class TimingCalculator:
    """Calculates timing intervals based on BPM, division, and swing."""

    # Division factors: how much of a beat each division represents
    DIVISION_MAP: Dict[str, float] = {
        "1/4": 1.0,
        "1/8": 0.5,
        "1/16": 0.25,
        "1/32": 0.125,
        "TRIPLET": 1.0 / 3.0,
        "DOTTED": 1.5,
    }

    MIN_BPM = 20
    MAX_BPM = 300
    MAX_SWING_PCT = 75

    def __init__(self) -> None:
        """Initialize timing calculator."""
        pass

    def calculate_beat_interval(self, bpm: int) -> float:
        """Calculate seconds per beat from BPM.

        Args:
            bpm: Beats per minute (will be clamped to MIN_BPM..MAX_BPM)

        Returns:
            Seconds per beat.
        """
        bpm = max(self.MIN_BPM, min(self.MAX_BPM, int(bpm)))
        return 60.0 / bpm

    def calculate_step_interval(
        self, beat_interval: float, division: str, tempo_mul: float = 1.0
    ) -> float:
        """Calculate seconds per step based on division and tempo multiplier.

        Args:
            beat_interval: Seconds per beat (from calculate_beat_interval)
            division: Division string (1/4, 1/8, 1/16, 1/32, TRIPLET, DOTTED)
            tempo_mul: Tempo multiplier (default 1.0), useful for humanization

        Returns:
            Seconds per step.
        """
        div_upper = (division or "1/8").upper()
        factor = self.DIVISION_MAP.get(div_upper, 0.5)

        tempo_mul = max(0.0001, float(tempo_mul))
        return (beat_interval * factor) / tempo_mul

    def apply_swing(self, interval: float, swing_pct: int, is_odd_step: bool) -> float:
        """Calculate swing delay for a step.

        Args:
            interval: Step interval in seconds
            swing_pct: Swing percentage (0..75, will be clamped)
            is_odd_step: Whether this is an odd-numbered step (0-indexed)

        Returns:
            Swing delay in seconds (positive for delay, negative for anticipation).
        """
        if not swing_pct or interval <= 0:
            return 0.0

        swing_pct = max(0, min(self.MAX_SWING_PCT, int(swing_pct)))

        # Swing delay is a percentage of half the interval
        swing_force = (swing_pct / 100.0) * (interval / 2.0)

        # Odd steps are delayed, even steps are anticipated
        return swing_force if is_odd_step else -swing_force

    def calculate_timing(
        self,
        bpm: int,
        division: str,
        swing_pct: int = 0,
        step_number: int = 0,
        tempo_mul: float = 1.0,
    ) -> TimingMetadata:
        """Calculate complete timing metadata for a step.

        Args:
            bpm: Beats per minute
            division: Division string (1/4, 1/8, 1/16, 1/32, TRIPLET, DOTTED)
            swing_pct: Swing percentage (0..75)
            step_number: Current step number (0-indexed, used for odd/even)
            tempo_mul: Tempo multiplier (default 1.0)

        Returns:
            TimingMetadata with interval, swing_delay, and total_sleep.
        """
        beat_interval = self.calculate_beat_interval(bpm)
        interval = self.calculate_step_interval(beat_interval, division, tempo_mul)

        is_odd = (step_number % 2) == 1
        swing_delay = self.apply_swing(interval, swing_pct, is_odd)

        total_sleep = max(0.001, interval + swing_delay)

        return TimingMetadata(
            interval=interval,
            swing_delay=swing_delay,
            total_sleep=total_sleep,
        )

    def calculate_gate_duration(self, bpm: int, gate_pct: int) -> float:
        """Calculate note duration based on BPM and gate percentage.

        Args:
            bpm: Beats per minute
            gate_pct: Gate percentage (0..100, portion of beat to sustain note)

        Returns:
            Note duration in seconds.
        """
        beat_interval = self.calculate_beat_interval(bpm)
        gate_pct = max(0, min(100, int(gate_pct)))
        return max(0.01, (gate_pct / 100.0) * beat_interval)

    def get_supported_divisions(self) -> list[str]:
        """Get list of supported division strings."""
        return sorted(self.DIVISION_MAP.keys())
