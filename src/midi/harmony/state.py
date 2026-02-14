"""HarmonyState for harmonizer configuration."""

from dataclasses import dataclass, field
from typing import List
import json


@dataclass
class HarmonyState:
    """State configuration for harmonizer."""

    enabled: bool = False
    intervals: List[int] = field(default_factory=lambda: [4, 7])
    voice_limit: int = 4

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "intervals": self.intervals,
            "voice_limit": self.voice_limit,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            enabled=d.get("enabled", False),
            intervals=d.get("intervals", [4, 7]),
            voice_limit=d.get("voice_limit", 4),
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
