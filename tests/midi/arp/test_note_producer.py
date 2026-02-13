"""Tests for NoteProducer module."""

import pytest
from src.midi.arp.note_producer import NoteProducer
from src.midi.arp.state_validator import ArpState, VelocityConfig, PatternConfig


class TestNoteProducerCalculateNote:
    """Tests for note calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = NoteProducer()
        self.state = ArpState()

    def test_calculate_note_octave_1(self):
        """Test note calculation with octave 1."""
        # Step 0 (C), octave 1
        note = self.producer._calculate_note(0, octave=1)
        assert note == 60  # Middle C

        # Step 1 (C#), octave 1
        note = self.producer._calculate_note(1, octave=1)
        assert note == 61

    def test_calculate_note_different_octaves(self):
        """Test note calculation with different octaves."""
        # Step 0 at different octaves
        note_oct1 = self.producer._calculate_note(0, octave=1)
        note_oct2 = self.producer._calculate_note(0, octave=2)
        note_oct3 = self.producer._calculate_note(0, octave=3)

        assert note_oct2 == note_oct1 + 12
        assert note_oct3 == note_oct1 + 24

    def test_calculate_note_wraps_semitones(self):
        """Test that step indices wrap within 12 semitones."""
        note_step0 = self.producer._calculate_note(0, octave=1)
        note_step12 = self.producer._calculate_note(12, octave=1)
        # Step 12 should wrap to step 0 of next octave
        assert note_step12 == note_step0 + 12

    def test_calculate_note_clamping(self):
        """Test that notes are clamped to MIDI range."""
        # Very high octave should clamp to max
        note = self.producer._calculate_note(11, octave=100)
        assert note <= 127

        # Octave 1 step 0 should not be clamped
        note = self.producer._calculate_note(0, octave=1)
        assert note == 60


class TestNoteProducerVelocity:
    """Tests for velocity calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = NoteProducer()

    def test_velocity_original_mode(self):
        """Test ORIGINAL velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="ORIGINAL", fixed_velocity=100))
        vel = self.producer._calculate_velocity(0, state)
        assert vel == 100

    def test_velocity_fixed_mode(self):
        """Test FIXED velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="FIXED", fixed_velocity=80))
        vel = self.producer._calculate_velocity(0, state)
        assert vel == 80

        vel = self.producer._calculate_velocity(5, state)
        assert vel == 80  # Should be same for all steps

    def test_velocity_random_mode(self):
        """Test RANDOM velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="RANDOM"))

        # Run multiple times to get randomness
        velocities = set()
        for step in range(10):
            vel = self.producer._calculate_velocity(step, state)
            assert self.producer.RAMP_MIN_VEL <= vel <= self.producer.RAMP_MAX_VEL
            velocities.add(vel)

        # Should have multiple different values
        assert len(velocities) > 1

    def test_velocity_ramp_up(self):
        """Test RAMP_UP velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_UP"))

        vel_start = self.producer._calculate_velocity(0, state)
        vel_middle = self.producer._calculate_velocity(6, state)
        vel_end = self.producer._calculate_velocity(11, state)

        assert vel_start < vel_middle < vel_end
        assert vel_start >= self.producer.RAMP_MIN_VEL
        assert vel_end <= self.producer.RAMP_MAX_VEL

    def test_velocity_ramp_down(self):
        """Test RAMP_DOWN velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="RAMP_DOWN"))

        vel_start = self.producer._calculate_velocity(0, state)
        vel_middle = self.producer._calculate_velocity(6, state)
        vel_end = self.producer._calculate_velocity(11, state)

        assert vel_start > vel_middle > vel_end
        assert vel_start <= self.producer.RAMP_MAX_VEL
        assert vel_end >= self.producer.RAMP_MIN_VEL

    def test_velocity_accent_first(self):
        """Test ACCENT_FIRST velocity mode."""
        state = ArpState(velocity=VelocityConfig(mode="ACCENT_FIRST"))

        vel_first = self.producer._calculate_velocity(0, state)
        vel_other = self.producer._calculate_velocity(6, state)

        assert vel_first > vel_other
        assert vel_first == 127  # Max velocity
        assert vel_other == 40  # Min ramp velocity


class TestNoteProducerAccent:
    """Tests for accent logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = NoteProducer()

    def test_should_accent_when_enabled(self):
        """Test accent detection."""
        accents = [True, False, True] + [False] * 9
        state = ArpState(pattern=PatternConfig(accents=accents))

        assert self.producer._should_accent(0, state)
        assert not self.producer._should_accent(1, state)
        assert self.producer._should_accent(2, state)
        assert not self.producer._should_accent(3, state)

    def test_should_accent_no_accents_list(self):
        """Test when accents list is empty."""
        state = ArpState(pattern=PatternConfig(accents=[]))
        assert not self.producer._should_accent(0, state)

    def test_apply_accent_boost(self):
        """Test accent velocity boost."""
        vel = 100
        accented = self.producer._apply_accent(vel)
        assert accented > vel
        assert accented == int(vel * 1.25)

    def test_apply_accent_clamping(self):
        """Test accent clamping to max velocity."""
        vel = 120  # 120 * 1.25 = 150, which exceeds max
        accented = self.producer._apply_accent(vel)
        assert accented <= 127


class TestNoteProducerIntegration:
    """Integration tests for full note production."""

    def setup_method(self):
        """Set up test fixtures."""
        self.producer = NoteProducer()

    def test_produce_note_complete(self):
        """Test complete note production."""
        state = ArpState(
            octave=2,
            velocity=VelocityConfig(mode="FIXED", fixed_velocity=100),
        )

        note, velocity = self.producer.produce_note(0, state)

        assert 0 <= note <= 127
        assert 0 <= velocity <= 127
        assert note == 60 + 12  # Octave 2

    def test_produce_note_with_accent(self):
        """Test note production with accent."""
        state = ArpState(
            octave=1,
            velocity=VelocityConfig(mode="FIXED", fixed_velocity=100),
            pattern=PatternConfig(
                mask=[True] * 12,
                accents=[True, False] + [False] * 10,
            ),
        )

        # Note 0 with accent
        _, vel_accented = self.producer.produce_note(0, state)
        # Note 1 without accent
        _, vel_normal = self.producer.produce_note(1, state)

        assert vel_accented > vel_normal

    def test_get_velocity_modes(self):
        """Test list of supported velocity modes."""
        modes = self.producer.get_velocity_modes()
        assert "ORIGINAL" in modes
        assert "FIXED" in modes
        assert "RAMP_UP" in modes
        assert "RAMP_DOWN" in modes
        assert "RANDOM" in modes
        assert "ACCENT_FIRST" in modes
