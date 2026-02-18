"""Event logging for MIDI monitoring."""

import logging
from datetime import datetime
from collections import deque
from threading import Lock
import mido

logger = logging.getLogger(__name__)

# MIDI note to note name mapping
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_note_to_name(note_number: int) -> str:
    """Convert MIDI note number (0-127) to note name.

    Args:
        note_number: MIDI note number (0-127)

    Returns:
        Note name in format like "C4", "D#5", etc.
    """
    if not 0 <= note_number <= 127:
        return f"N{note_number}"

    octave = (note_number // 12) - 1
    note = note_number % 12
    return f"{NOTE_NAMES[note]}{octave}"


class Event:
    """Represents a single MIDI event for logging."""

    def __init__(self, direction: str, msg: mido.Message, channel: int = 0):
        """Initialize an event.

        Args:
            direction: "in" for incoming, "out" for outgoing
            msg: The MIDI message
            channel: MIDI channel (0-15)
        """
        self.direction = direction
        self.msg = msg
        self.channel = channel
        self.timestamp = datetime.now()

    def format_time(self) -> str:
        """Format timestamp as HH:MM:SS.mmm"""
        return self.timestamp.strftime("%H:%M:%S.%f")[:-3]

    def format_event(self) -> str:
        """Format event for display.

        Returns formatted string like:
        "> 12:34:56.789 | note_on | CH 1 | C4 velocity 85"
        "< 12:34:56.790 | note_off | CH 1 | D4 velocity 64"
        "> 12:34:56.791 | control_change | CH 1 | CC 7 value 100"
        """
        direction_arrow = ">" if self.direction == "in" else "<"
        time_str = self.format_time()
        msg_type = self.msg.type
        channel_str = f"CH {self.channel + 1}"

        # Format message details based on type
        if msg_type in ("note_on", "note_off"):
            note_name = midi_note_to_name(self.msg.note)
            velocity = self.msg.velocity
            details = f"{note_name} velocity {velocity}"
        elif msg_type == "polytouch":
            note_name = midi_note_to_name(self.msg.note)
            value = self.msg.value
            details = f"{note_name} pressure {value}"
        elif msg_type == "control_change":
            cc = self.msg.control
            value = self.msg.value
            details = f"CC {cc} value {value}"
        elif msg_type == "program_change":
            program = self.msg.program
            details = f"Program {program}"
        elif msg_type == "pitchwheel":
            pitch = self.msg.pitch
            details = f"Pitch {pitch}"
        elif msg_type == "aftertouch":
            value = self.msg.value
            details = f"Pressure {value}"
        elif msg_type == "clock":
            details = "Clock tick"
        elif msg_type == "active_sensing":
            details = "Active sensing"
        else:
            details = str(self.msg)

        return f"{direction_arrow} {time_str} | {msg_type:18s} | {channel_str:6s} | {details}"


class EventLog:
    """Thread-safe event log for monitoring MIDI messages."""

    def __init__(self, max_events: int = 50):
        """Initialize event log.

        Args:
            max_events: Maximum number of events to keep in history
        """
        self.max_events = max_events
        self.events = deque(maxlen=max_events)
        self.lock = Lock()
        self.paused = False
        self.event_listeners = []

    def add_event(self, direction: str, msg: mido.Message, channel: int = 0) -> None:
        """Add an event to the log.

        Args:
            direction: "in" for incoming, "out" for outgoing
            msg: The MIDI message
            channel: MIDI channel (0-15)
        """
        if self.paused:
            return

        with self.lock:
            event = Event(direction, msg, channel)
            self.events.append(event)

        # Notify listeners
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying event listener: {e}")

    def get_events(self, limit: int = None) -> list[Event]:
        """Get recent events.

        Args:
            limit: Maximum number of recent events to return.
                  If None, returns all events.

        Returns:
            List of Event objects
        """
        with self.lock:
            events = list(self.events)

        if limit and len(events) > limit:
            events = events[-limit:]

        return events

    def clear(self) -> None:
        """Clear all events from history."""
        with self.lock:
            self.events.clear()

    def pause(self) -> None:
        """Pause event logging without clearing history."""
        self.paused = True

    def resume(self) -> None:
        """Resume event logging."""
        self.paused = False

    def is_paused(self) -> bool:
        """Check if logging is paused."""
        return self.paused

    def add_listener(self, callback) -> None:
        """Add a listener that gets called when events are added.

        Args:
            callback: Callable that takes (Event) as argument
        """
        self.event_listeners.append(callback)

    def remove_listener(self, callback) -> None:
        """Remove a listener."""
        try:
            self.event_listeners.remove(callback)
        except ValueError:
            pass
