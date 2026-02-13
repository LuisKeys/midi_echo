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
        """Test with all pattern steps active."""
        pattern = [True] * 12
        indices = self.mode.build_active_indices(pattern)
        assert indices == list(range(12))

    def test_build_active_indices_sparse(self):
        """Test with sparse pattern."""
        pattern = [True, False, True, False] + [False] * 8
        indices = self.mode.build_active_indices(pattern)
        assert indices == [0, 2]

    def test_build_active_indices_empty(self):
        """Test with no active notes."""
        pattern = [False] * 12
        indices = self.mode.build_active_indices(pattern)
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
        """Test that active indices are reversed."""
        pattern = [True] * 12
        indices = self.mode.build_active_indices(pattern)
        assert indices == list(range(11, -1, -1))

    def test_build_active_indices_sparse(self):
        """Test with sparse pattern."""
        pattern = [True, False, True, False] + [False] * 8
        indices = self.mode.build_active_indices(pattern)
        assert indices == [2, 0]  # Reversed relative order

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
        pattern = [True, False, True, False, True, False] + [False] * 6
        indices = self.mode.build_active_indices(pattern)
        # Active: [0, 2, 4]
        # UP: [0, 2, 4]
        # DOWN (excluding endpoints): [2]
        # Result: [0, 2, 4, 2]
        assert indices == [0, 2, 4, 2]

    def test_build_active_indices_single_note(self):
        """Test with single active note."""
        pattern = [True] + [False] * 11
        indices = self.mode.build_active_indices(pattern)
        assert indices == [0]

    def test_build_active_indices_two_notes(self):
        """Test with two active notes."""
        pattern = [True, False, True] + [False] * 9
        indices = self.mode.build_active_indices(pattern)
        assert indices == [0, 2]

    def test_build_active_indices_three_notes(self):
        """Test with three active notes."""
        pattern = [True, False, True, False, True] + [False] * 7
        indices = self.mode.build_active_indices(pattern)
        # Active: [0, 2, 4]
        # UP: [0, 2, 4]
        # DOWN (reverse [0, 2, 4] is [4, 2, 0], minus endpoints): [2]
        # Result: [0, 2, 4, 2]
        assert indices == [0, 2, 4, 2]


class TestRandomMode:
    """Tests for RANDOM mode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mode = RandomMode()

    def test_build_active_indices_returns_all_active(self):
        """Test that all active indices are returned."""
        pattern = [True, False, True, False] + [False] * 8
        indices = self.mode.build_active_indices(pattern)
        assert set(indices) == {0, 2}

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
        """Test that all active indices are returned."""
        pattern = [True, False, True] + [False] * 9
        indices = self.mode.build_active_indices(pattern)
        assert indices == [0, 2]

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
