"""Tests for arpeggiator mode strategies."""

import pytest
from src.midi.arp.modes import (
    ArpMode,
    UpMode,
    DownMode,
    UpDownMode,
    RandomMode,
    ChordMode,
    create_mode,
)


class TestUpMode:
    """Tests for UP mode (ascending notes)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = UpMode()

    def test_build_active_indices_all_active(self):
        """Test with all notes."""
        notes = list(range(12))
        indices = self.mode.build_active_indices(notes)
        assert indices == list(range(12))

    def test_build_active_indices_sparse(self):
        """Test with sparse notes."""
        notes = [60, 62]
        indices = self.mode.build_active_indices(notes)
        assert indices == [0, 1]

    def test_build_active_indices_empty(self):
        """Test with no notes."""
        notes = []
        indices = self.mode.build_active_indices(notes)
        assert indices == []

    def test_choose_next_advances_linearly(self):
        """Test that position advances sequentially."""
        active = [0, 2, 4, 6]

        idx, new_pos = self.mode.choose_next(active, 0)
        assert idx == 0
        assert new_pos == 1

        idx, new_pos = self.mode.choose_next(active, 1)
        assert idx == 1
        assert new_pos == 2

    def test_choose_next_wraps(self):
        """Test position wraps at end."""
        active = [0, 2, 4]
        idx, new_pos = self.mode.choose_next(active, 2)
        assert idx == 2
        assert new_pos == 0  # Wraps back to start


class TestDownMode:
    """Tests for DOWN mode (descending notes)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = DownMode()

    def test_build_active_indices_reversed(self):
        """Test that indices are reversed."""
        notes = list(range(12))
        indices = self.mode.build_active_indices(notes)
        assert indices == list(range(11, -1, -1))

    def test_build_active_indices_sparse(self):
        """Test with sparse notes."""
        notes = [60, 62]
        indices = self.mode.build_active_indices(notes)
        assert indices == [1, 0]  # Reversed

    def test_choose_next_advances_linearly(self):
        """Test that position advances sequentially."""
        active = [6, 4, 2, 0]  # Reversed order

        idx, new_pos = self.mode.choose_next(active, 0)
        assert idx == 0
        assert new_pos == 1


class TestUpDownMode:
    """Tests for UPDOWN mode (bouncing pattern)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = UpDownMode()

    def test_build_active_indices_simple(self):
        """Test UP + DOWN path construction."""
        notes = [60, 62, 64]  # 0, 2, 4 semitones
        indices = self.mode.build_active_indices(notes)
        # UP: [0, 1, 2]
        # DOWN (excluding endpoints): [1]
        # Result: [0, 1, 2, 1]
        assert indices == [0, 1, 2, 1]

    def test_build_active_indices_single_note(self):
        """Test with single note."""
        notes = [60]
        indices = self.mode.build_active_indices(notes)
        assert indices == [0]

    def test_build_active_indices_two_notes(self):
        """Test with two notes."""
        notes = [60, 62]
        indices = self.mode.build_active_indices(notes)
        assert indices == [0, 1]

    def test_build_active_indices_three_notes(self):
        """Test with three notes."""
        notes = [60, 62, 64]
        indices = self.mode.build_active_indices(notes)
        # UP: [0, 1, 2]
        # DOWN (reverse [0, 1, 2] is [2, 1, 0], minus endpoints): [1]
        # Result: [0, 1, 2, 1]
        assert indices == [0, 1, 2, 1]


class TestRandomMode:
    """Tests for RANDOM mode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = RandomMode()

    def test_build_active_indices_returns_all_active(self):
        """Test that all indices are returned."""
        notes = [60, 62]
        indices = self.mode.build_active_indices(notes)
        assert set(indices) == {0, 1}

    def test_choose_next_returns_random_index(self):
        """Test that choose_next returns valid random index."""
        active = [1, 3, 5, 7]

        # Run multiple times to check randomness
        indices_chosen = set()
        for pos in range(20):
            idx, new_pos = self.mode.choose_next(active, pos)
            assert 0 <= idx < len(active)
            indices_chosen.add(idx)

        # Should have seen multiple different indices due to randomness
        assert len(indices_chosen) > 1


class TestChordMode:
    """Tests for CHORD mode (placeholder for future multi-note feature)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = ChordMode()

    def test_build_active_indices_returns_all(self):
        """Test that all indices are returned."""
        notes = [60, 62]
        indices = self.mode.build_active_indices(notes)
        assert indices == [0, 1]

    def test_choose_next_currently_sequential(self):
        """Test that CHORD currently behaves like UP (placeholder)."""
        active = [0, 2, 4]
        idx, new_pos = self.mode.choose_next(active, 0)
        assert idx == 0
        assert new_pos == 1


class TestModeFactory:
    """Tests for create_mode factory function."""

    def test_create_mode_up(self):
        """Test creating UP mode."""
        mode = create_mode("UP")
        assert isinstance(mode, UpMode)

    def test_create_mode_down(self):
        """Test creating DOWN mode."""
        mode = create_mode("DOWN")
        assert isinstance(mode, DownMode)

    def test_create_mode_updown(self):
        """Test creating UPDOWN mode."""
        mode = create_mode("UPDOWN")
        assert isinstance(mode, UpDownMode)

    def test_create_mode_random(self):
        """Test creating RANDOM mode."""
        mode = create_mode("RANDOM")
        assert isinstance(mode, RandomMode)

    def test_create_mode_chord(self):
        """Test creating CHORD mode."""
        mode = create_mode("CHORD")
        assert isinstance(mode, ChordMode)

    def test_create_mode_default(self):
        """Test that unknown mode defaults to UP."""
        mode = create_mode("UNKNOWN")
        assert isinstance(mode, UpMode)

    def test_create_mode_case_insensitive(self):
        """Test that mode names are case-insensitive."""
        mode_up = create_mode("up")
        mode_up_upper = create_mode("UP")
        assert isinstance(mode_up, UpMode)
        assert isinstance(mode_up_upper, UpMode)
