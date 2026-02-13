"""Tests for NoteProducer module."""

import pytest
from src.midi.arp.note_producer import NoteProducer
from src.midi.arp.state_validator import ArpState, VelocityConfig, PatternConfig


class TestCalculateVelocity:
    """Tests for calculate_velocity method."""

    def setup_method(self):
        self.producer = NoteProducer()

    def test_velocity_original_mode(self):
        """ORIGINAL mode returns fixed_velocity."""
        state = ArpState(velocity=VelocityConfig(mode="ORIGINAL", fixed_velocity=100))
        vel = self.producer.calculate_velocity(0, 12, state)
        assert vel == 100

    def test_velocity_fixed_mode(self):
        """FIXED mode returns fixed_velocity for any step."""
        state = ArpState(velocity=VelocityConfig(mode="FIXED", fixed_velocity=80))
        assert self.producer.calculate_velocity(0, 12, state) == 80
        assert self.producer.calculate_velocity(5, 12, state) == 80
        assert self.producer.calculate_velocity(11, 12, state) == 80

    def test_velocity_random_mode(self):
        """RANDOM mode returns values in [RAMP_MIN_VEL, RAMP_MAX_VEL]."""
        state = ArpState(velocity=VelocityConfig(mode="RANDOM"))
        velocities = set()
        for step in range(20):
            vel = self.producer.calculate_velocity(step, 20, state)
            assert self.producer.RAMP_MIN_VEL <= vel <= self.producer.RAMP_MAX_VEL
            velocities.add(vel)
        assert len(velocities) > 1

    def test_velocity_ramp_up(self):
        """RAMP_UP mode increases velocity with step index."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_UP"))
        total = 12
        vel_start = self.producer.calculate_velocity(0, total, state)
        vel_mid = self.producer.calculate_velocity(6, total, state)
        vel_end = self.producer.calculate_velocity(11, total, state)
        assert vel_start < vel_mid < vel_end
        assert vel_start >= self.producer.RAMP_MIN_VEL
        assert vel_end <= self.producer.RAMP_MAX_VEL

    def test_velocity_ramp_up_single_step(self):
        """RAMP_UP with total_steps=1 returns RAMP_MIN_VEL."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_UP"))
        vel = self.producer.calculate_velocity(0, 1, state)
        assert vel == self.producer.RAMP_MIN_VEL

    def test_velocity_ramp_down(self):
        """RAMP_DOWN mode decreases velocity with step index."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_DOWN"))
        total = 12
        vel_start = self.producer.calculate_velocity(0, total, state)
        vel_mid = self.producer.calculate_velocity(6, total, state)
        vel_end = self.producer.calculate_velocity(11, total, state)
        assert vel_start > vel_mid > vel_end
        assert vel_start <= self.producer.RAMP_MAX_VEL
        assert vel_end >= self.producer.RAMP_MIN_VEL

    def test_velocity_ramp_down_single_step(self):
        """RAMP_DOWN with total_steps=1 returns RAMP_MIN_VEL."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_DOWN"))
        vel = self.producer.calculate_velocity(0, 1, state)
        assert vel == self.producer.RAMP_MIN_VEL

    def test_velocity_accent_first(self):
        """ACCENT_FIRST mode gives max velocity on step 0, min on others."""
        state = ArpState(velocity=VelocityConfig(mode="ACCENT_FIRST"))
        vel_first = self.producer.calculate_velocity(0, 12, state)
        vel_other = self.producer.calculate_velocity(6, 12, state)
        assert vel_first == 127
        assert vel_other == 40

    def test_velocity_unknown_mode_falls_back_to_original(self):
        """Unknown mode falls back to ORIGINAL (fixed_velocity)."""
        state = ArpState(velocity=VelocityConfig(mode="UNKNOWN", fixed_velocity=90))
        vel = self.producer.calculate_velocity(0, 12, state)
        assert vel == 90


class TestShouldAccent:
    """Tests for should_accent method."""

    def setup_method(self):
        self.producer = NoteProducer()

    def test_accent_when_enabled(self):
        """Accented semitone returns True."""
        accents = [True, False, True] + [False] * 9
        state = ArpState(pattern=PatternConfig(accents=accents, notes=[60, 61, 62]))
        assert self.producer.should_accent(60, state)
        assert not self.producer.should_accent(61, state)
        assert self.producer.should_accent(62, state)

    def test_accent_wraps_semitone(self):
        """Notes in different octaves share the same accent by semitone."""
        accents = [True] + [False] * 11
        state = ArpState(pattern=PatternConfig(accents=accents, notes=[48, 60, 72]))
        assert self.producer.should_accent(48, state)
        assert self.producer.should_accent(60, state)
        assert self.producer.should_accent(72, state)

    def test_accent_empty_list(self):
        """Empty accents list returns False."""
        state = ArpState(pattern=PatternConfig(accents=[], notes=[60]))
        assert not self.producer.should_accent(60, state)

    def test_accent_semitone_out_of_range(self):
        """If semitone >= len(accents) returns False."""
        state = ArpState(pattern=PatternConfig(accents=[True, True], notes=[60]))
        assert self.producer.should_accent(60, state)
        assert self.producer.should_accent(61, state)
        assert not self.producer.should_accent(62, state)


class TestApplyAccent:
    """Tests for _apply_accent method."""

    def setup_method(self):
        self.producer = NoteProducer()

    def test_apply_accent_boost(self):
        """Accent boosts velocity by 1.25x."""
        vel = 100
        accented = self.producer._apply_accent(vel)
        assert accented == int(vel * 1.25)

    def test_apply_accent_clamping(self):
        """Accent clamps to 127."""
        accented = self.producer._apply_accent(120)
        assert accented == 127

    def test_apply_accent_zero(self):
        """Accent on zero stays zero."""
        assert self.producer._apply_accent(0) == 0


class TestGetVelocityModes:
    """Tests for get_velocity_modes."""

    def test_all_modes_present(self):
        producer = NoteProducer()
        modes = producer.get_velocity_modes()
        assert "ORIGINAL" in modes
        assert "FIXED" in modes
        assert "RAMP_UP" in modes
        assert "RAMP_DOWN" in modes
        assert "RANDOM" in modes
        assert "ACCENT_FIRST" in modes
