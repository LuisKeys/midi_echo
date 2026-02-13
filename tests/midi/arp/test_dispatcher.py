"""Tests for MidiDispatcher module."""

import pytest
from unittest.mock import Mock, MagicMock, call
from src.midi.arp.dispatcher import MidiDispatcher
import mido


class MockMidiEngine:
    """Mock MIDI engine for testing."""

    def __init__(self, has_queue=True, has_loop=False):
        """Initialize mock engine."""
        self.queue = Mock() if has_queue else None
        self._loop = Mock() if has_loop else None


class TestMidiDispatcher:
    """Tests for MIDI dispatcher."""

    def test_send_note_on_basic(self):
        """Test sending a note_on message."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is True
        engine.queue.put_nowait.assert_called_once()
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True
        message = wrapped.msg
        assert message.type == "note_on"
        assert message.note == 60
        assert message.velocity == 100

    def test_send_note_on_with_channel(self):
        """Test sending note_on with channel."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100, channel=5)

        assert result is True
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True
        message = wrapped.msg
        assert message.channel == 5

    def test_send_note_on_marks_as_arp(self):
        """Test that note_on messages are marked as arpeggiator-generated."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is True
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True

    def test_send_note_off_basic(self):
        """Test sending a note_off message."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_off(60, 0)

        assert result is True
        engine.queue.put_nowait.assert_called_once()
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True
        message = wrapped.msg
        assert message.type == "note_off"
        assert message.note == 60
        assert message.velocity == 0

    def test_send_note_off_default_velocity(self):
        """Test note_off with default velocity."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_off(60)

        assert result is True
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True
        message = wrapped.msg
        assert message.velocity == 0

    def test_enqueue_without_event_loop(self):
        """Test enqueueing without event loop."""
        engine = MockMidiEngine(has_queue=True, has_loop=False)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is True
        # Should enqueue directly without call_soon_threadsafe
        engine.queue.put_nowait.assert_called_once()

    def test_enqueue_with_event_loop(self):
        """Test enqueueing with event loop."""
        engine = MockMidiEngine(has_queue=True, has_loop=True)
        engine._loop.call_soon_threadsafe = Mock()
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is True
        # Should use call_soon_threadsafe
        engine._loop.call_soon_threadsafe.assert_called_once()

    def test_send_note_on_queue_error(self):
        """Test handling of queue errors."""
        engine = MockMidiEngine(has_queue=True)
        engine.queue.put_nowait.side_effect = Exception("Queue error")
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is False

    def test_send_note_on_no_queue(self):
        """Test sending when queue is not available."""
        engine = MockMidiEngine(has_queue=False)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_on(60, 100)

        assert result is False

    def test_has_queue_true(self):
        """Test queue availability detection."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        assert dispatcher.has_queue() is True

    def test_has_queue_false(self):
        """Test queue availability when queue is None."""
        engine = MockMidiEngine(has_queue=False)
        dispatcher = MidiDispatcher(engine)

        assert dispatcher.has_queue() is False

    def test_has_queue_no_attribute(self):
        """Test queue availability when engine has no queue attribute."""
        engine = Mock(spec=[])  # No queue attribute
        dispatcher = MidiDispatcher(engine)

        assert dispatcher.has_queue() is False

    def test_multiple_messages(self):
        """Test sending multiple messages."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result1 = dispatcher.send_note_on(60, 100)
        result2 = dispatcher.send_note_on(62, 90)
        result3 = dispatcher.send_note_off(60)

        assert result1 is True
        assert result2 is True
        assert result3 is True
        assert engine.queue.put_nowait.call_count == 3

    def test_send_note_off_marks_as_arp(self):
        """Test that note_off messages are marked as arpeggiator-generated."""
        engine = MockMidiEngine(has_queue=True)
        dispatcher = MidiDispatcher(engine)

        result = dispatcher.send_note_off(60, 0)

        assert result is True
        args = engine.queue.put_nowait.call_args[0]
        wrapped = args[0]
        assert wrapped.is_arp is True
