"""Tests for MidiProcessor module."""

import pytest
import mido
from src.midi.processor import MidiProcessor
from src.midi.message_wrapper import MidiMessageWrapper


class TestMidiProcessor:
    """Tests for MIDI processor."""

    def test_process_note_on_arp_disabled(self):
        """Test note_on passes through when arp disabled."""
        processor = MidiProcessor()
        processor.arp_enabled = False
        msg = mido.Message("note_on", note=60, velocity=100)

        result = processor.process(msg)

        assert result is not None
        assert result.type == "note_on"
        assert result.note == 60
        assert result.velocity == 100

    def test_process_note_off_arp_disabled(self):
        """Test note_off passes through when arp disabled."""
        processor = MidiProcessor()
        processor.arp_enabled = False
        msg = mido.Message("note_off", note=60, velocity=0)

        result = processor.process(msg)

        assert result is not None
        assert result.type == "note_off"
        assert result.note == 60
        assert result.velocity == 0

    def test_process_note_on_arp_enabled_input_dropped(self):
        """Test input note_on is dropped when arp enabled."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("note_on", note=60, velocity=100)

        result = processor.process(msg)

        assert result is None

    def test_process_note_off_arp_enabled_input_dropped(self):
        """Test input note_off is dropped when arp enabled."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("note_off", note=60, velocity=0)

        result = processor.process(msg)

        assert result is None

    def test_process_note_on_arp_enabled_arp_note_passes(self):
        """Test arp-generated note_on passes through when arp enabled."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("note_on", note=60, velocity=100)
        wrapped_msg = MidiMessageWrapper(msg, is_arp=True)

        result = processor.process(wrapped_msg)

        assert result is not None
        assert result.type == "note_on"
        assert result.note == 60
        assert result.velocity == 100

    def test_process_note_off_arp_enabled_arp_note_passes(self):
        """Test arp-generated note_off passes through when arp enabled."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("note_off", note=60, velocity=0)
        wrapped_msg = MidiMessageWrapper(msg, is_arp=True)

        result = processor.process(wrapped_msg)

        assert result is not None
        assert result.type == "note_off"
        assert result.note == 60
        assert result.velocity == 0

    def test_process_non_note_message_passes(self):
        """Test non-note messages pass through regardless of arp state."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("control_change", control=7, value=100)

        result = processor.process(msg)

        assert result is not None
        assert result.type == "control_change"
        assert result.control == 7
        assert result.value == 100

    def test_process_meta_message_passes(self):
        """Test meta messages pass through unchanged."""
        processor = MidiProcessor()
        msg = mido.MetaMessage("end_of_track")

        result = processor.process(msg)

        assert result is msg  # Should return original for meta

    def test_arp_notes_update_held_notes_even_when_dropped(self):
        """Test that input notes update arp held notes even when dropped."""
        processor = MidiProcessor()
        processor.arp_enabled = True
        msg = mido.Message("note_on", note=60, velocity=100)

        result = processor.process(msg)

        assert result is None  # Dropped
        assert 60 in processor.arp_state.held_notes  # But held notes updated
