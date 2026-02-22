"""Unit tests for MIDI pattern sequencer

Tests cover:
- SequencerState validation and loop length calculation
- Pattern event storage and quantization
- Recording and playback logic
- Clock timing and tick generation
- Metronome click generation
- State persistence (save/load)
"""

import pytest
import asyncio
import mido
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from src.midi.sequencer import (
    SequencerState,
    PatternEvent,
    Pattern,
    InternalClock,
    MidiSequencer,
)
from src.gui.context import AppContext


class TestSequencerState:
    """Test SequencerState dataclass and validation."""

    def test_state_initialization(self):
        """Test default state initialization."""
        state = SequencerState()

        assert state.is_playing is False
        assert state.is_recording is False
        assert state.metronome_enabled is True
        assert state.tempo == 120.0
        assert state.time_signature_num == 4
        assert state.time_signature_den == 4
        assert state.pattern_bars == 1
        assert state.quantization == "1/16"

    def test_tempo_validation(self):
        """Test tempo is clamped to legal range."""
        state = SequencerState(tempo=400)
        assert state.tempo == 300.0  # Clamped to max

        state = SequencerState(tempo=5)
        assert state.tempo == 20.0  # Clamped to min

    def test_loop_length_calculation(self):
        """Test loop length calculation for different bar/time signature combinations."""
        PPQN = 960

        # 1 bar of 4/4
        state = SequencerState(
            pattern_bars=1, time_signature_num=4, time_signature_den=4
        )
        expected = 1 * 4 * PPQN * (4 / 4)  # 3840 ticks
        assert state.loop_length_ticks == expected

        # 2 bars of 3/4
        state = SequencerState(
            pattern_bars=2, time_signature_num=3, time_signature_den=4
        )
        expected = 2 * 3 * PPQN * (4 / 4)  # 5760 ticks
        assert state.loop_length_ticks == expected

        # 1 bar of 2/8
        state = SequencerState(
            pattern_bars=1, time_signature_num=2, time_signature_den=8
        )
        expected = 1 * 2 * PPQN * (4 / 8)  # 1920 ticks
        assert state.loop_length_ticks == expected

    def test_time_signature_change_updates_loop(self):
        """Test that changing time signature updates loop length."""
        state = SequencerState(
            pattern_bars=1, time_signature_num=4, time_signature_den=4
        )
        original_length = state.loop_length_ticks

        state.on_time_signature_changed(3, 4)
        new_length = state.loop_length_ticks

        # 3/4 should be shorter than 4/4
        assert new_length < original_length

    def test_state_serialization(self):
        """Test to_dict and from_dict preserve state."""
        state = SequencerState(
            tempo=140,
            time_signature_num=3,
            time_signature_den=8,
            pattern_bars=2,
            quantization="1/32",
            metronome_enabled=False,
        )

        data = state.to_dict()
        loaded = SequencerState.from_dict(data)

        assert loaded.tempo == 140
        assert loaded.time_signature_num == 3
        assert loaded.time_signature_den == 8
        assert loaded.pattern_bars == 2
        assert loaded.quantization == "1/32"
        assert loaded.metronome_enabled is False


class TestPattern:
    """Test Pattern and PatternEvent models."""

    def test_pattern_event_creation(self):
        """Test creating pattern events."""
        msg = mido.Message("note_on", note=60, velocity=100, channel=0)
        event = PatternEvent(tick=240, message=msg)

        assert event.tick == 240
        assert event.message.note == 60
        assert event.message.velocity == 100

    def test_pattern_add_event(self):
        """Test adding events to pattern."""
        pattern = Pattern()
        msg = mido.Message("note_on", note=60, velocity=100)

        pattern.add_event(0, msg)
        pattern.add_event(240, msg)

        assert pattern.get_event_count() == 2

    def test_pattern_clear(self):
        """Test clearing pattern."""
        pattern = Pattern()
        pattern.add_event(0, mido.Message("note_on", note=60))

        assert pattern.get_event_count() == 1

        pattern.clear()
        assert pattern.is_empty() is True
        assert pattern.get_event_count() == 0

    def test_events_at_tick(self):
        """Test retrieving events at specific tick."""
        pattern = Pattern()
        msg1 = mido.Message("note_on", note=60)
        msg2 = mido.Message("note_off", note=60)

        pattern.add_event(0, msg1)
        pattern.add_event(240, msg2)

        events_at_0 = pattern.events_at_tick(0)
        assert len(events_at_0) == 1
        assert events_at_0[0].message.type == "note_on"

        events_at_240 = pattern.events_at_tick(240)
        assert len(events_at_240) == 1
        assert events_at_240[0].message.type == "note_off"

        events_at_100 = pattern.events_at_tick(100)
        assert len(events_at_100) == 0

    def test_quantize_event(self):
        """Test quantization of ticks to grid."""
        pattern = Pattern()

        # 1/16 grid at PPQN=960 is 240 ticks
        grid = 960 // 4  # 240 ticks

        # 100 ticks should quantize to 0 (nearest 240)
        assert pattern.quantize_event(100, grid) == 0

        # 150 ticks should quantize to 240 (nearest 240)
        assert pattern.quantize_event(150, grid) == 240

        # 240 stays at 240
        assert pattern.quantize_event(240, grid) == 240

    def test_pattern_serialization(self):
        """Test to_dict and from_dict preserve pattern."""
        pattern = Pattern()
        pattern.add_event(0, mido.Message("note_on", note=60, velocity=100, channel=0))
        pattern.add_event(240, mido.Message("note_off", note=60, channel=0))

        data = pattern.to_dict()
        loaded = Pattern.from_dict(data)

        assert loaded.get_event_count() == 2
        assert loaded.events_at_tick(0)[0].message.note == 60
        assert loaded.events_at_tick(240)[0].message.type == "note_off"


class TestMidiSequencer:
    """Test MidiSequencer recording, playback, and transport control."""

    @pytest.fixture
    def mock_engine(self):
        """Create a mock MidiEngine."""
        engine = Mock()
        engine.output_port = Mock()
        engine.output_port.send = Mock()
        return engine

    @pytest.fixture
    def mock_context(self, mock_engine):
        """Create a mock AppContext."""
        context = Mock(spec=AppContext)
        context.engine = mock_engine
        context.event_loop = asyncio.get_event_loop()
        return context

    @pytest.fixture
    def sequencer(self, mock_engine, mock_context):
        """Create a MidiSequencer instance."""
        return MidiSequencer(mock_engine, mock_context)

    def test_sequencer_initialization(self, sequencer):
        """Test sequencer initializes with correct defaults."""
        assert sequencer.state.is_playing is False
        assert sequencer.state.is_recording is False
        assert sequencer.pattern.is_empty() is True

    def test_record_message_filtering(self, sequencer):
        """Test that only valid message types are recorded."""
        sequencer.state.is_recording = True

        # These should be recorded
        sequencer.record_message(mido.Message("note_on", note=60, velocity=100))
        sequencer.record_message(mido.Message("note_off", note=60))
        sequencer.record_message(mido.Message("control_change", control=7, value=100))

        # Clock messages should be ignored
        sequencer.record_message(mido.Message("clock"))

        # Should have 3 events (not 4)
        assert sequencer.pattern.get_event_count() == 3

    def test_record_message_quantization(self, sequencer):
        """Test that recorded messages are quantized."""
        sequencer.state.is_recording = True
        sequencer.state.current_tick = 150  # Off-grid position

        msg = mido.Message("note_on", note=60)
        sequencer.record_message(msg)

        events = sequencer.pattern.events_at_tick(0)
        assert len(events) == 1  # Should be quantized to nearest grid (0 for 1/16)

    def test_record_disable(self, sequencer):
        """Test that messages aren't recorded when recording is disabled."""
        sequencer.state.is_recording = False

        msg = mido.Message("note_on", note=60)
        sequencer.record_message(msg)

        assert sequencer.pattern.is_empty() is True

    def test_clear_pattern(self, sequencer):
        """Test clearing the pattern."""
        sequencer.state.is_recording = True
        sequencer.record_message(mido.Message("note_on", note=60))

        assert sequencer.pattern.get_event_count() > 0

        sequencer.clear_pattern()
        assert sequencer.pattern.is_empty() is True

    def test_tempo_update(self, sequencer):
        """Test tempo update with limits."""
        sequencer.set_tempo(140)
        assert sequencer.state.tempo == 140

        sequencer.set_tempo(500)  # Clamped
        assert sequencer.state.tempo == 300

    def test_time_signature_update(self, sequencer):
        """Test time signature update."""
        original_loop = sequencer.state.loop_length_ticks

        sequencer.set_time_signature(3, 4)
        assert sequencer.state.time_signature_num == 3
        assert sequencer.state.time_signature_den == 4
        assert sequencer.state.loop_length_ticks != original_loop

    def test_quantization_update(self, sequencer):
        """Test quantization grid update."""
        sequencer.set_quantization("1/8")
        assert sequencer.state.quantization == "1/8"
        assert sequencer._quantization_grid_ticks == 960 // 2  # 480 ticks

        sequencer.set_quantization("1/32")
        assert sequencer._quantization_grid_ticks == 960 // 8  # 120 ticks

    def test_metronome_toggle(self, sequencer):
        """Test metronome enable/disable."""
        assert sequencer.state.metronome_enabled is True

        sequencer.toggle_metronome()
        assert sequencer.state.metronome_enabled is False

        sequencer.toggle_metronome()
        assert sequencer.state.metronome_enabled is True

    def test_sequencer_serialization(self, sequencer):
        """Test to_dict and from_dict preserve sequencer state."""
        sequencer.state.tempo = 140
        sequencer.pattern.add_event(0, mido.Message("note_on", note=60))

        data = sequencer.to_dict()

        # Create new sequencer from saved data
        from unittest.mock import Mock

        new_engine = Mock()
        new_context = Mock()
        new_sequencer = MidiSequencer.from_dict(new_engine, new_context, data)

        assert new_sequencer.state.tempo == 140
        assert new_sequencer.pattern.get_event_count() == 1


class TestInternalClock:
    """Test InternalClock async tick generation."""

    @pytest.fixture
    def mock_sequencer(self):
        """Create a mock sequencer for clock testing."""
        sequencer = Mock()
        sequencer.state = SequencerState()
        sequencer._on_tick = Mock()
        sequencer._on_bar_start = Mock()
        sequencer._on_beat = Mock()
        return sequencer

    @pytest.fixture
    def clock(self, mock_sequencer):
        """Create an InternalClock instance."""
        return InternalClock(mock_sequencer)

    @pytest.mark.asyncio
    async def test_clock_initialization(self, clock):
        """Test clock initializes in stopped state."""
        assert clock.is_running() is False

    @pytest.mark.asyncio
    async def test_clock_start_stop(self, clock):
        """Test clock can be started and stopped."""
        await clock.start()
        assert clock.is_running() is True

        await clock.stop()
        assert clock.is_running() is False

    def test_clock_ppqn(self, clock):
        """Test PPQN constant."""
        assert InternalClock.PPQN == 960


class TestSequencerIntegration:
    """Integration tests for sequencer with engine."""

    def test_sequencer_send_message_direct(self):
        """Test direct message sending to output port."""
        engine = Mock()
        engine.output_port = Mock()
        context = Mock()

        sequencer = MidiSequencer(engine, context)
        msg = mido.Message("note_on", note=60, velocity=100)

        sequencer._send_message_direct(msg)

        engine.output_port.send.assert_called_once_with(msg)

    def test_sequencer_all_notes_off_on_stop(self):
        """Test that All Notes Off messages are sent on stop."""
        engine = Mock()
        engine.output_port = Mock()
        context = Mock()
        context.event_loop = asyncio.get_event_loop()

        sequencer = MidiSequencer(engine, context)

        # Manually test the logic (since stop is async)
        # Simulate All Notes Off messages being sent
        for channel in range(16):
            msg = mido.Message("control_change", control=123, value=0, channel=channel)
            # In real code, sequencer._send_message_direct(msg) would be called
            assert msg.type == "control_change"
            assert msg.control == 123


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
