"""Tests for ArpState validator and nested configuration objects."""

import pytest
import json
import tempfile
from src.midi.arp.state_validator import (
    ArpState,
    TimingConfig,
    VelocityConfig,
    PatternConfig,
)


class TestTimingConfig:
    """Tests for TimingConfig validation."""

    def test_default_values(self):
        """Test default values."""
        config = TimingConfig()
        assert config.bpm == 120
        assert config.division == "1/8"
        assert config.swing == 0
        assert config.tempo_mul == 1.0

    def test_bpm_validation(self):
        """Test BPM clamping."""
        # Too low
        config = TimingConfig(bpm=5)
        assert config.bpm >= TimingConfig._validate_bpm(5)

        # Too high
        config = TimingConfig(bpm=500)
        assert config.bpm <= 300

        # Valid
        config = TimingConfig(bpm=120)
        assert config.bpm == 120

    def test_swing_validation(self):
        """Test swing percentage clamping."""
        config = TimingConfig(swing=100)
        assert config.swing == 75

        config = TimingConfig(swing=-10)
        assert config.swing == 0

        config = TimingConfig(swing=50)
        assert config.swing == 50

    def test_tempo_mul_validation(self):
        """Test tempo multiplier clamping."""
        config = TimingConfig(tempo_mul=0.05)
        assert config.tempo_mul == 0.1

        config = TimingConfig(tempo_mul=10.0)
        assert config.tempo_mul == 4.0

    def test_to_dict(self):
        """Test serialization to dict."""
        config = TimingConfig(bpm=100, division="1/16", swing=25)
        d = config.to_dict()
        assert d["bpm"] == 100
        assert d["division"] == "1/16"
        assert d["swing"] == 25

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {"bpm": 140, "division": "1/32", "swing": 30}
        config = TimingConfig.from_dict(d)
        assert config.bpm == 140
        assert config.division == "1/32"
        assert config.swing == 30


class TestVelocityConfig:
    """Tests for VelocityConfig validation."""

    def test_default_values(self):
        """Test default values."""
        config = VelocityConfig()
        assert config.mode == "ORIGINAL"
        assert config.fixed_velocity == 100

    def test_mode_validation(self):
        """Test velocity mode validation."""
        valid_modes = {
            "ORIGINAL",
            "FIXED",
            "RAMP_UP",
            "RAMP_DOWN",
            "RANDOM",
            "ACCENT_FIRST",
        }

        # Valid mode
        for mode in valid_modes:
            config = VelocityConfig(mode=mode)
            assert config.mode == mode

        # Invalid mode defaults to ORIGINAL
        config = VelocityConfig(mode="INVALID")
        assert config.mode == "ORIGINAL"

    def test_velocity_clamping(self):
        """Test fixed velocity clamping."""
        config = VelocityConfig(fixed_velocity=200)
        assert config.fixed_velocity == 127

        config = VelocityConfig(fixed_velocity=-10)
        assert config.fixed_velocity == 0

    def test_to_dict(self):
        """Test serialization."""
        config = VelocityConfig(mode="FIXED", fixed_velocity=80)
        d = config.to_dict()
        assert d["mode"] == "FIXED"
        assert d["fixed_velocity"] == 80

    def test_from_dict(self):
        """Test deserialization."""
        d = {"mode": "RAMP_UP", "fixed_velocity": 90}
        config = VelocityConfig.from_dict(d)
        assert config.mode == "RAMP_UP"
        assert config.fixed_velocity == 90


class TestPatternConfig:
    """Tests for PatternConfig validation."""

    def test_default_values(self):
        """Test default values."""
        config = PatternConfig()
        assert len(config.mask) == 12
        assert all(config.mask)  # All True by default
        assert len(config.accents) == 12
        assert not any(config.accents)  # All False by default

    def test_pattern_padding(self):
        """Test pattern padding to 12 elements."""
        config = PatternConfig(mask=[True, False, True])
        assert len(config.mask) == 12
        assert config.mask[:3] == [True, False, True]
        assert config.mask[3:] == [False] * 9

    def test_pattern_truncation(self):
        """Test pattern truncation to 12 elements."""
        config = PatternConfig(mask=[True] * 20)
        assert len(config.mask) == 12

    def test_invalid_pattern_types(self):
        """Test handling of invalid pattern types."""
        config = PatternConfig(mask="not a list")
        assert len(config.mask) == 12
        assert all(config.mask)  # Defaults to all True

    def test_to_dict(self):
        """Test serialization."""
        mask = [True, False] * 6
        config = PatternConfig(mask=mask)
        d = config.to_dict()
        assert d["mask"] == mask

    def test_from_dict(self):
        """Test deserialization."""
        mask = [True, False, True] + [False] * 9
        d = {"mask": mask, "accents": [False] * 12}
        config = PatternConfig.from_dict(d)
        assert config.mask == mask


class TestArpState:
    """Tests for refactored ArpState."""

    def test_default_values(self):
        """Test default values."""
        state = ArpState()
        assert state.enabled is False
        assert state.mode == "UP"
        assert state.octave == 1
        assert state.gate_pct == 50
        assert isinstance(state.timing, TimingConfig)
        assert isinstance(state.velocity, VelocityConfig)
        assert isinstance(state.pattern, PatternConfig)

    def test_octave_clamping(self):
        """Test octave clamping."""
        state = ArpState(octave=10)
        assert state.octave == 4

        state = ArpState(octave=0)
        assert state.octave == 1

    def test_gate_pct_clamping(self):
        """Test gate percentage clamping."""
        state = ArpState(gate_pct=150)
        assert state.gate_pct == 100

        state = ArpState(gate_pct=-10)
        assert state.gate_pct == 0

    def test_mode_validation(self):
        """Test mode validation."""
        valid_modes = {"UP", "DOWN", "UPDOWN", "RANDOM", "CHORD"}

        for mode in valid_modes:
            state = ArpState(mode=mode)
            assert state.mode == mode

        state = ArpState(mode="INVALID")
        assert state.mode == "UP"

    def test_to_dict_flat_format(self):
        """Test serialization to flat format (backward compatibility)."""
        state = ArpState(
            enabled=True,
            mode="DOWN",
            octave=2,
            timing=TimingConfig(bpm=140),
            velocity=VelocityConfig(mode="FIXED", fixed_velocity=90),
        )

        d = state.to_dict()

        # Check flat structure
        assert d["enabled"] is True
        assert d["mode"] == "DOWN"
        assert d["octave"] == 2
        assert d["bpm"] == 140  # From timing
        assert d["velocity_mode"] == "FIXED"
        assert d["fixed_velocity"] == 90

    def test_from_dict_flat_format(self):
        """Test deserialization from flat format (legacy)."""
        d = {
            "enabled": True,
            "mode": "UPDOWN",
            "octave": 3,
            "bpm": 160,
            "division": "1/16",
            "swing": 25,
            "velocity_mode": "RAMP_UP",
            "fixed_velocity": 80,
            "pattern_mask": [True, False] * 6,
        }

        state = ArpState.from_dict(d)

        assert state.enabled is True
        assert state.mode == "UPDOWN"
        assert state.octave == 3
        assert state.timing.bpm == 160
        assert state.timing.division == "1/16"
        assert state.timing.swing == 25
        assert state.velocity.mode == "RAMP_UP"
        assert state.velocity.fixed_velocity == 80

    def test_from_dict_nested_format(self):
        """Test deserialization from nested format."""
        d = {
            "enabled": True,
            "mode": "DOWN",
            "timing": {
                "bpm": 150,
                "division": "1/32",
                "swing": 40,
                "tempo_mul": 1.5,
            },
            "velocity": {
                "mode": "ACCENT_FIRST",
                "fixed_velocity": 100,
            },
            "pattern": {
                "mask": [True, False] * 6,
                "accents": [True] + [False] * 11,
            },
        }

        state = ArpState.from_dict(d)

        assert state.timing.bpm == 150
        assert state.velocity.mode == "ACCENT_FIRST"
        assert state.pattern.mask == [True, False] * 6

    def test_save_and_load(self):
        """Test save and load from file."""
        original = ArpState(
            enabled=True,
            mode="UPDOWN",
            octave=3,
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            original.save(filepath)
            loaded = ArpState.load(filepath)

            assert loaded.enabled == original.enabled
            assert loaded.mode == original.mode
            assert loaded.octave == original.octave
        finally:
            import os

            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file returns default."""
        state = ArpState.load("/nonexistent/path/file.json")

        # Should return default ArpState
        assert state.enabled is False
        assert state.mode == "UP"

    def test_backward_compatibility_shift_fields(self):
        """Test that old shift_ fields are handled in from_dict."""
        d = {
            "shift_probability": 80,
            "shift_humanize_ms": 10,
            "shift_tempo_mul": 1.5,
        }

        state = ArpState.from_dict(d)
        # shift_tempo_mul should be applied to timing config
        assert state.timing.tempo_mul == 1.5

    def test_nested_config_auto_init(self):
        """Test that nested configs are auto-initialized if missing."""
        state = ArpState()
        # Manually corrupt the configs
        state.timing = None
        state.velocity = None
        state.pattern = None

        # Call __post_init__ again
        state.__post_init__()

        # Should be re-initialized
        assert isinstance(state.timing, TimingConfig)
        assert isinstance(state.velocity, VelocityConfig)
        assert isinstance(state.pattern, PatternConfig)
