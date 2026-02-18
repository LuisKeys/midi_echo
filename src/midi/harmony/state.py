"""HarmonyState for harmonizer configuration."""

from dataclasses import dataclass, field
from typing import List
import json


@dataclass
class HarmonyState:
    """State configuration for harmonizer."""

    enabled: bool = False
    intervals_above: List[int] = field(default_factory=list)
    intervals_below: List[int] = field(default_factory=lambda: [7])
    voice_limit: int = 4
    velocity_percentage: int = 100

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "intervals_above": self.intervals_above,
            "intervals_below": self.intervals_below,
            "voice_limit": self.voice_limit,
            "velocity_percentage": self.velocity_percentage,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            enabled=d.get("enabled", False),
            intervals_above=d.get("intervals_above", d.get("intervals", [])),
            intervals_below=d.get("intervals_below", [7]),
            voice_limit=d.get("voice_limit", 4),
            velocity_percentage=d.get("velocity_percentage", 100),
        )

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except:
            return cls()
