"""Arpeggiator persistent state container."""

from dataclasses import dataclass, field
from typing import List
import json


@dataclass
class ArpState:
    enabled: bool = False
    mode: str = "UP"  # UP, DOWN, UPDOWN, RANDOM, CHORD
    octave: int = 1  # 1..4
    octave_dir: str = "UP"  # UP, DOWN, BOTH
    latch: str = "OFF"  # OFF, ON, HOLD

    bpm: int = 120
    division: str = "1/8"  # 1/4, 1/8, 1/16, 1/32, TRIPLET, DOTTED
    swing: int = 0  # 0..75 percent
    reset_mode: str = "NEW_CHORD"  # NEW_CHORD, FIRST_NOTE, FREE_RUN

    gate_pct: int = 50  # 0..100
    velocity_mode: str = (
        "ORIGINAL"  # ORIGINAL, FIXED, RAMP_UP, RAMP_DOWN, RANDOM, ACCENT_FIRST
    )
    fixed_velocity: int = 100

    # Pattern: 12-step mask, True=play, False=rest
    pattern_mask: List[bool] = field(default_factory=lambda: [True] * 12)
    accents: List[bool] = field(default_factory=lambda: [False] * 12)

    # Shift-related transient modifiers (not persisted by default)
    shift_probability: int = 100  # percent
    shift_humanize_ms: int = 0
    shift_tempo_mul: float = 1.0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "octave": self.octave,
            "octave_dir": self.octave_dir,
            "latch": self.latch,
            "bpm": self.bpm,
            "division": self.division,
            "swing": self.swing,
            "reset_mode": self.reset_mode,
            "gate_pct": self.gate_pct,
            "velocity_mode": self.velocity_mode,
            "fixed_velocity": self.fixed_velocity,
            "pattern_mask": self.pattern_mask,
            "accents": self.accents,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ArpState":
        inst = cls()
        for k, v in d.items():
            if hasattr(inst, k):
                setattr(inst, k, v)
        return inst

    def save(self, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception:
            pass

    @classmethod
    def load(cls, path: str) -> "ArpState":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls()
