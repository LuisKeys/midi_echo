"""MIDI dispatcher for thread-safe message queuing.

Handles enqueueing note_on and note_off messages to the MIDI engine queue
in a thread-safe manner.
"""

import logging
from typing import Optional

import mido

from src.midi.message_wrapper import MidiMessageWrapper

logger = logging.getLogger(__name__)


class MidiDispatcher:
    """Dispatches MIDI messages to engine queue with thread-safety."""

    def __init__(self, midi_engine) -> None:
        """Initialize dispatcher with MIDI engine reference.

        Args:
            midi_engine: MIDI engine with queue and optional event loop.
        """
        self.midi_engine = midi_engine

    def send_note_on(self, note: int, velocity: int, channel: int = 0) -> bool:
        """Send a note_on message.

        Args:
            note: MIDI note (0..127)
            velocity: MIDI velocity (0..127)
            channel: MIDI channel (0..15), default 0

        Returns:
            True if successfully enqueued, False on error.
        """
        try:
            message = mido.Message(
                "note_on", note=note, velocity=velocity, channel=channel
            )
            wrapped_message = MidiMessageWrapper(message, is_arp=True)
            result = self._enqueue_message(wrapped_message)
            logger.info(
                f"AR dispatcher sending note_on: note={note} velocity={velocity} enqueued={result}"
            )
            return result
        except Exception as e:
            logger.error(f"Error creating note_on message: {e}")
            return False

    def send_note_off(self, note: int, velocity: int = 0, channel: int = 0) -> bool:
        """Send a note_off message.

        Args:
            note: MIDI note (0..127)
            velocity: MIDI velocity (0..127), typically 0 for note_off
            channel: MIDI channel (0..15), default 0

        Returns:
            True if successfully enqueued, False on error.
        """
        try:
            message = mido.Message(
                "note_off", note=note, velocity=velocity, channel=channel
            )
            wrapped_message = MidiMessageWrapper(message, is_arp=True)
            return self._enqueue_message(wrapped_message)
        except Exception as e:
            logger.debug(f"Error creating note_off message: {e}")
            return False

    def _enqueue_message(self, message: mido.Message) -> bool:
        """Enqueue message to MIDI engine in thread-safe manner.

        Args:
            message: mido Message to enqueue.

        Returns:
            True if successfully enqueued, False on error.
        """
        try:
            # Check if queue exists first
            queue = getattr(self.midi_engine, "queue", None)
            if not queue:
                logger.error(f"MIDI engine queue not initialized yet")
                return False

            # Try to use event loop for thread-safe enqueueing
            event_loop = getattr(self.midi_engine, "_loop", None)
            if event_loop:
                try:
                    event_loop.call_soon_threadsafe(queue.put_nowait, message)
                    logger.debug(
                        f"AR message enqueued via event_loop.call_soon_threadsafe"
                    )
                except RuntimeError as e:
                    # Event loop may be closed or on wrong thread; fall back
                    logger.warning(
                        f"Event loop call_soon_threadsafe failed, falling back to direct enqueue: {e}"
                    )
                    queue.put_nowait(message)
            else:
                # No event loop; enqueue directly
                logger.debug(f"No event loop found on midi_engine, enqueueing directly")
                queue.put_nowait(message)
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue MIDI message: {e}")
            return False

    def has_queue(self) -> bool:
        """Check if MIDI engine has a valid queue.

        Returns:
            True if queue is available.
        """
        return hasattr(self.midi_engine, "queue") and self.midi_engine.queue is not None
