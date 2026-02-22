"""Pattern model for recording and storing MIDI events

Patterns store absolute tick positions relative to the loop start.
Uses PPQN=960 for high precision.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import mido


@dataclass
class PatternEvent:
    """Single MIDI event in a pattern

    Attributes:
        tick: Absolute tick position within loop (0 to loop_length_ticks)
        message: The mido.Message to replay at this tick
    """

    tick: int
    message: mido.Message

    def to_dict(self) -> dict:
        """Serialize event to dictionary for JSON storage"""
        msg = self.message
        event_dict = {
            "tick": self.tick,
            "message": {
                "type": msg.type,
            },
        }

        # Add optional fields based on message type
        if hasattr(msg, "note"):
            event_dict["message"]["note"] = msg.note

        if hasattr(msg, "velocity"):
            event_dict["message"]["velocity"] = msg.velocity

        if hasattr(msg, "channel"):
            event_dict["message"]["channel"] = msg.channel

        if hasattr(msg, "control"):
            event_dict["message"]["control"] = msg.control

        if hasattr(msg, "value"):
            event_dict["message"]["value"] = msg.value

        return event_dict

    @classmethod
    def from_dict(cls, data: dict) -> "PatternEvent":
        """Deserialize event from dictionary"""
        tick = data["tick"]
        msg_dict = data["message"]

        # Reconstruct mido.Message
        msg_type = msg_dict["type"]
        msg_kwargs = {
            k: v for k, v in msg_dict.items() if k != "type" and v is not None
        }

        message = mido.Message(msg_type, **msg_kwargs)
        return cls(tick=tick, message=message)


@dataclass
class Pattern:
    """Single-track MIDI pattern with recording and playback

    Stores events as a list of PatternEvents with absolute tick positions.
    Supports quantization, loop wrapping, and JSON serialization.
    """

    events: List[PatternEvent] = field(default_factory=list)

    def add_event(self, tick: int, message: mido.Message):
        """Add a MIDI message to the pattern at the specified tick"""
        self.events.append(PatternEvent(tick, message))

    def clear(self):
        """Remove all events from the pattern"""
        self.events.clear()

    def events_at_tick(self, tick: int) -> List[PatternEvent]:
        """Return all events due to play at a specific tick"""
        return [e for e in self.events if e.tick == tick]

    def is_empty(self) -> bool:
        """Check if pattern has any events"""
        return len(self.events) == 0

    def get_event_count(self) -> int:
        """Return total number of events in pattern"""
        return len(self.events)

    def get_first_tick(self) -> Optional[int]:
        """Return the tick of the first event, or None if empty"""
        if not self.events:
            return None
        return min(e.tick for e in self.events)

    def get_last_tick(self) -> Optional[int]:
        """Return the tick of the last event, or None if empty"""
        if not self.events:
            return None
        return max(e.tick for e in self.events)

    def quantize_event(self, tick: int, grid_ticks: int) -> int:
        """Quantize a tick to the nearest grid position

        Args:
            tick: The tick to quantize
            grid_ticks: The grid size in ticks

        Returns:
            The quantized tick position (rounded to nearest grid)
        """
        if grid_ticks <= 0:
            return tick
        return round(tick / grid_ticks) * grid_ticks

    def to_dict(self) -> list:
        """Serialize all events to list of dicts for JSON storage"""
        return [e.to_dict() for e in self.events]

    @classmethod
    def from_dict(cls, data: list) -> "Pattern":
        """Deserialize pattern from list of event dicts"""
        pattern = cls()
        for event_data in data:
            pattern.events.append(PatternEvent.from_dict(event_data))
        return pattern

    def __repr__(self) -> str:
        return f"Pattern(events={len(self.events)})"
