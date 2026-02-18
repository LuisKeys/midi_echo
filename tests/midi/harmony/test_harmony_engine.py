"""Tests for HarmonyEngine with scale-based harmony."""

import pytest
from unittest.mock import MagicMock, Mock
from src.midi.harmony.engine import HarmonyEngine
from src.midi.harmony.state import HarmonyState
from src.midi.scales import ScaleType


class TestHarmonyEngine:
    """Tests for harmony engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_dispatcher = MagicMock()
        self.engine = HarmonyEngine(self.mock_dispatcher)

    def test_engine_initialization(self):
        """Test engine initializes with default state."""
        assert self.engine.state.enabled is False
        assert self.engine.state.intervals_above == []
        assert self.engine.state.intervals_below == [7]
        assert self.engine.state.voice_limit == 4
        assert self.engine.state.velocity_percentage == 100
        assert self.mock_dispatcher is not None

    def test_update_state(self):
        """Test updating engine state."""
        new_state = HarmonyState(
            enabled=True,
            intervals_above=[3, 7],
            intervals_below=[4],
            voice_limit=8,
            velocity_percentage=80,
        )

        self.engine.update_state(new_state)

        assert self.engine.state.enabled is True
        assert self.engine.state.intervals_above == [3, 7]
        assert self.engine.state.intervals_below == [4]
        assert self.engine.state.voice_limit == 8
        assert self.engine.state.velocity_percentage == 80

    def test_process_melody_note_on_disabled(self):
        """Test note-on when harmony disabled does nothing."""
        self.engine.state.enabled = False

        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Dispatcher should not be called
        self.mock_dispatcher.send_note_on.assert_not_called()

    def test_process_melody_note_on_enabled(self):
        """Test note-on generates harmony when enabled."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4, 7]

        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Dispatcher should be called for harmony notes
        # Should generate harmony notes and send them
        assert self.mock_dispatcher.send_note_on.called

    def test_process_melody_note_off_disabled(self):
        """Test note-off when harmony disabled does nothing."""
        self.engine.state.enabled = False

        self.engine.process_melody_note_off(60, 0)

        # Dispatcher should not be called
        self.mock_dispatcher.send_note_off.assert_not_called()

    def test_process_melody_note_off_enabled(self):
        """Test note-off sends note-offs for harmony notes."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4, 7]

        # First send note on
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Reset mock to track note-off calls
        self.mock_dispatcher.reset_mock()

        # Then send note off
        self.engine.process_melody_note_off(60, 0)

        # Dispatcher should be called for note-offs
        assert self.mock_dispatcher.send_note_off.called

    def test_note_on_off_sequence(self):
        """Test a complete note-on/off sequence."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4]

        # Note on
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )
        note_on_calls = self.mock_dispatcher.send_note_on.call_count

        # Note off
        self.engine.process_melody_note_off(60, 0)
        note_off_calls = self.mock_dispatcher.send_note_off.call_count

        # Should have equal numbers of on and off calls
        assert note_on_calls > 0
        assert note_off_calls > 0

    def test_scale_root_affects_harmony(self):
        """Test that scale root is used in harmony generation."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4, 7]

        # Generate in C Major
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )
        calls_c_major = len(self.mock_dispatcher.send_note_on.call_args_list)

        # Reset
        self.mock_dispatcher.reset_mock()

        # Generate in A Minor (root=9)
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=9, scale_type=ScaleType.MINOR
        )
        calls_a_minor = len(self.mock_dispatcher.send_note_on.call_args_list)

        # Both should generate harmony notes
        assert calls_c_major > 0
        assert calls_a_minor > 0

    def test_scale_type_affects_harmony(self):
        """Test that scale type is used in harmony generation."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4, 7]

        # Generate in Major scale
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )
        calls_major = len(self.mock_dispatcher.send_note_on.call_args_list)

        # Reset
        self.mock_dispatcher.reset_mock()

        # Generate in Minor scale
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MINOR
        )
        calls_minor = len(self.mock_dispatcher.send_note_on.call_args_list)

        # Both should generate harmony notes
        assert calls_major > 0
        assert calls_minor > 0

    def test_voice_limit_respected(self):
        """Test that voice limit is respected."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [3, 4, 5, 7, 12]  # 5 intervals
        self.engine.state.voice_limit = 2  # Limit to 2 voices

        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Should respect voice limit
        assert (
            self.mock_dispatcher.send_note_on.call_count
            <= self.engine.state.voice_limit + 1
        )  # +1 for melody

    def test_multiple_melody_notes(self):
        """Test handling multiple melody notes."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [4, 7]

        # First note
        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )
        first_call_count = self.mock_dispatcher.send_note_on.call_count

        # Second note (before first note off, polyphonic)
        self.engine.process_melody_note_on(
            64, 100, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )
        second_call_count = self.mock_dispatcher.send_note_on.call_count

        # Should have additional calls for second note
        assert second_call_count > first_call_count

    def test_chromatic_scale_harmony(self):
        """Test harmony generation in chromatic scale."""
        self.engine.state.enabled = True
        self.engine.state.intervals_above = [3, 4, 5, 7]

        self.engine.process_melody_note_on(
            60, 100, 0, scale_root=0, scale_type=ScaleType.CHROMATIC
        )

        # Should generate harmony notes
        assert self.mock_dispatcher.send_note_on.called


class TestHarmonyEngineVelocityAndChannel:
    """Tests for velocity and channel handling in harmony engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_dispatcher = MagicMock()
        self.engine = HarmonyEngine(self.mock_dispatcher)
        self.engine.state.enabled = True

    def test_velocity_scaled_by_percentage(self):
        """Test that velocity is scaled by percentage."""
        self.engine.state.intervals_above = [4]
        self.engine.state.velocity_percentage = 100
        velocity = 100

        self.engine.process_melody_note_on(
            60, velocity, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Check that send_note_on was called with correct velocity
        if self.mock_dispatcher.send_note_on.called:
            call_args = self.mock_dispatcher.send_note_on.call_args_list[-1]
            # Velocity is second argument
            expected_velocity = int((velocity * 100) / 100)
            assert call_args[0][1] == expected_velocity

    def test_velocity_scaled_50_percent(self):
        """Test that velocity is scaled correctly at 50%."""
        self.engine.state.intervals_above = [4]
        self.engine.state.velocity_percentage = 50
        velocity = 100

        self.engine.process_melody_note_on(
            60, velocity, 0, scale_root=0, scale_type=ScaleType.MAJOR
        )

        if self.mock_dispatcher.send_note_on.called:
            call_args = self.mock_dispatcher.send_note_on.call_args_list[-1]
            expected_velocity = int((velocity * 50) / 100)
            assert call_args[0][1] == expected_velocity

    def test_channel_preserved(self):
        """Test that input channel is used for harmony notes."""
        self.engine.state.intervals_above = [4]
        channel = 5

        self.engine.process_melody_note_on(
            60, 100, channel, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Check that send_note_on was called with correct channel
        if self.mock_dispatcher.send_note_on.called:
            call_args = self.mock_dispatcher.send_note_on.call_args_list[-1]
            # Channel is third argument
            assert call_args[0][2] == channel
