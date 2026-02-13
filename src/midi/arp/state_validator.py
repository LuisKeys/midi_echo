"""ArpState validator with nested configuration objects and boundary checks."""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class TimingConfig:
    """Timing-related configuration for arpeggiator."""

    bpm: int = 120  # 20..300 BPM
    division: str = "1/8"  # 1/4, 1/8, 1/16, 1/32, TRIPLET, DOTTED
    swing: int = 0  # 0..75 percent
    tempo_mul: float = 1.0  # Tempo multiplier (not used by current engine)

    def __post_init__(self) -> None:
        self.bpm = self._validate_bpm(self.bpm)
        self.swing = self._validate_swing(self.swing)
        self.tempo_mul = max(0.1, min(4.0, self.tempo_mul))

    @staticmethod
    def _validate_bpm(bpm: int) -> int:
        """Ensure BPM is within acceptable range."""
        return max(20, min(300, int(bpm)))

    @staticmethod
    def _validate_swing(swing: int) -> int:
        """Ensure swing percentage is within 0..75%."""
        return max(0, min(75, int(swing)))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TimingConfig":
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in ("bpm", "division", "swing", "tempo_mul")
            }
        )


@dataclass
class VelocityConfig:
    """Velocity-related configuration for arpeggiator."""

    mode: str = "ORIGINAL"  # ORIGINAL, FIXED, RAMP_UP, RAMP_DOWN, RANDOM, ACCENT_FIRST
    fixed_velocity: int = 100  # 0..127

    def __post_init__(self) -> None:
        valid_modes = {
            "ORIGINAL",
            "FIXED",
            "RAMP_UP",
            "RAMP_DOWN",
            "RANDOM",
            "ACCENT_FIRST",
        }
        if self.mode not in valid_modes:
            self.mode = "ORIGINAL"
        self.fixed_velocity = self._validate_velocity(self.fixed_velocity)

    @staticmethod
    def _validate_velocity(vel: int) -> int:
        """Ensure velocity is within 0..127."""
        return max(0, min(127, int(vel)))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "VelocityConfig":
        return cls(**{k: v for k, v in d.items() if k in ("mode", "fixed_velocity")})


@dataclass
class PatternConfig:
    """Pattern and accent configuration for arpeggiator."""

    mask: List[bool] = field(default_factory=lambda: [True] * 12)
    accents: List[bool] = field(default_factory=lambda: [False] * 12)

    def __post_init__(self) -> None:
        self.mask = self._validate_pattern(self.mask)
        self.accents = self._validate_pattern(self.accents)

    @staticmethod
    def _validate_pattern(pattern: List[bool]) -> List[bool]:
        """Ensure pattern is 12 elements of booleans."""
        if not isinstance(pattern, list):
            return [True] * 12
        result = list(pattern)
        while len(result) < 12:
            result.append(False)
        return result[:12]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PatternConfig":
        return cls(**{k: v for k, v in d.items() if k in ("mask", "accents")})


@dataclass
class ArpState:
    """Refactored arpeggiator state with nested configuration objects.

    Maintains backward compatibility with legacy ArpState.to_dict() / from_dict()
    while providing nested config objects for cleaner organization and easier
    validation of related fields.
    """

    # Playback flags
    enabled: bool = False
    mode: str = "UP"  # UP, DOWN, UPDOWN, RANDOM, CHORD
    latch: str = "OFF"  # OFF, ON, HOLD

    # Octave control
    octave: int = 1  # 1..4
    octave_dir: str = "UP"  # UP, DOWN, BOTH
    reset_mode: str = "NEW_CHORD"  # NEW_CHORD, FIRST_NOTE, FREE_RUN

    # Gate control (0..100 percent of step duration)
    gate_pct: int = 50

    # Nested configuration objects
    timing: TimingConfig = field(default_factory=TimingConfig)
    velocity: VelocityConfig = field(default_factory=VelocityConfig)
    pattern: PatternConfig = field(default_factory=PatternConfig)

    def __post_init__(self) -> None:
        """Validate and normalize all state fields."""
        self.enabled = bool(self.enabled)
        self.octave = max(1, min(4, int(self.octave)))
        self.gate_pct = max(0, min(100, int(self.gate_pct)))

        valid_modes = {"UP", "DOWN", "UPDOWN", "RANDOM", "CHORD"}
        if self.mode not in valid_modes:
            self.mode = "UP"

        valid_latch = {"OFF", "ON", "HOLD"}
        if self.latch not in valid_latch:
            self.latch = "OFF"

        valid_octave_dir = {"UP", "DOWN", "BOTH"}
        if self.octave_dir not in valid_octave_dir:
            self.octave_dir = "UP"

        valid_reset = {"NEW_CHORD", "FIRST_NOTE", "FREE_RUN"}
        if self.reset_mode not in valid_reset:
            self.reset_mode = "NEW_CHORD"

        # Ensure nested configs are properly initialized
        if not isinstance(self.timing, TimingConfig):
            self.timing = TimingConfig()
        if not isinstance(self.velocity, VelocityConfig):
            self.velocity = VelocityConfig()
        if not isinstance(self.pattern, PatternConfig):
            self.pattern = PatternConfig()

    def to_dict(self) -> dict:
        """Export to dict format compatible with original ArpState.

        Maps nested configs back to flat structure for backward compatibility.
        """
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "octave": self.octave,
            "octave_dir": self.octave_dir,
            "latch": self.latch,
            "bpm": self.timing.bpm,
            "division": self.timing.division,
            "swing": self.timing.swing,
            "reset_mode": self.reset_mode,
            "gate_pct": self.gate_pct,
            "velocity_mode": self.velocity.mode,
            "fixed_velocity": self.velocity.fixed_velocity,
            "pattern_mask": self.pattern.mask,
            "accents": self.pattern.accents,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ArpState":
        """Import from dict, supporting both old flat and new nested formats.

        Automatically detects old format (bpm, division, etc.) and converts
        to nested structure.
        """
        # Handle new nested format
        if "timing" in d and isinstance(d["timing"], dict):
            timing_cfg = TimingConfig.from_dict(d["timing"])
        else:
            # Convert from old flat format
            timing_cfg = TimingConfig(
                bpm=d.get("bpm", 120),
                division=d.get("division", "1/8"),
                swing=d.get("swing", 0),
                tempo_mul=d.get("shift_tempo_mul", 1.0),
            )

        if "velocity" in d and isinstance(d["velocity"], dict):
            velocity_cfg = VelocityConfig.from_dict(d["velocity"])
        else:
            velocity_cfg = VelocityConfig(
                mode=d.get("velocity_mode", "ORIGINAL"),
                fixed_velocity=d.get("fixed_velocity", 100),
            )

        if "pattern" in d and isinstance(d["pattern"], dict):
            pattern_cfg = PatternConfig.from_dict(d["pattern"])
        else:
            pattern_cfg = PatternConfig(
                mask=d.get("pattern_mask", [True] * 12),
                accents=d.get("accents", [False] * 12),
            )

        return cls(
            enabled=d.get("enabled", False),
            mode=d.get("mode", "UP"),
            octave=d.get("octave", 1),
            octave_dir=d.get("octave_dir", "UP"),
            latch=d.get("latch", "OFF"),
            reset_mode=d.get("reset_mode", "NEW_CHORD"),
            gate_pct=d.get("gate_pct", 50),
            timing=timing_cfg,
            velocity=velocity_cfg,
            pattern=pattern_cfg,
        )

    def save(self, path: str) -> None:
        """Save state to JSON file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception:
            pass

    @classmethod
    def load(cls, path: str) -> "ArpState":
        """Load state from JSON file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls()
