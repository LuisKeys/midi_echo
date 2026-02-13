"""Tests for TimingCalculator module."""

import pytest
from src.midi.arp.timing import TimingCalculator, TimingMetadata


class TestTimingCalculator:
    """Tests for timing calculations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calc = TimingCalculator()

    def test_calculate_beat_interval(self):
        """Test beat interval calculation from BPM."""
        # 120 BPM = 0.5 seconds per beat
        interval = self.calc.calculate_beat_interval(120)
        assert abs(interval - 0.5) < 0.001

        # 60 BPM = 1.0 second per beat
        interval = self.calc.calculate_beat_interval(60)
        assert abs(interval - 1.0) < 0.001

        # 240 BPM = 0.25 seconds per beat
        interval = self.calc.calculate_beat_interval(240)
        assert abs(interval - 0.25) < 0.001

    def test_calculate_beat_interval_clamping(self):
        """Test that BPM is clamped to valid range."""
        # Very low BPM should be clamped to MIN_BPM
        interval = self.calc.calculate_beat_interval(5)
        assert interval == self.calc.calculate_beat_interval(self.calc.MIN_BPM)

        # Very high BPM should be clamped to MAX_BPM
        interval = self.calc.calculate_beat_interval(1000)
        assert interval == self.calc.calculate_beat_interval(self.calc.MAX_BPM)

    def test_calculate_step_interval(self):
        """Test step interval calculation based on division."""
        beat_interval = 0.5  # 120 BPM

        # 1/4 note = 1.0 * beat_interval
        interval = self.calc.calculate_step_interval(beat_interval, "1/4")
        assert abs(interval - 0.5) < 0.001

        # 1/8 note = 0.5 * beat_interval
        interval = self.calc.calculate_step_interval(beat_interval, "1/8")
        assert abs(interval - 0.25) < 0.001

        # 1/16 note = 0.25 * beat_interval
        interval = self.calc.calculate_step_interval(beat_interval, "1/16")
        assert abs(interval - 0.125) < 0.001

    def test_calculate_step_interval_triplet_dotted(self):
        """Test special divisions."""
        beat_interval = 1.0  # 60 BPM

        # Triplet = 1/3
        interval = self.calc.calculate_step_interval(beat_interval, "TRIPLET")
        assert abs(interval - (1.0 / 3.0)) < 0.001

        # Dotted = 1.5
        interval = self.calc.calculate_step_interval(beat_interval, "DOTTED")
        assert abs(interval - 1.5) < 0.001

    def test_calculate_step_interval_tempo_mul(self):
        """Test tempo multiplier effect."""
        beat_interval = 1.0

        # Normal tempo
        interval = self.calc.calculate_step_interval(
            beat_interval, "1/8", tempo_mul=1.0
        )

        # Double tempo (tempo_mul=2.0 speeds up by 2x)
        interval_fast = self.calc.calculate_step_interval(
            beat_interval, "1/8", tempo_mul=2.0
        )
        assert interval_fast < interval
        assert abs(interval_fast - interval / 2) < 0.001

    def test_apply_swing(self):
        """Test swing delay calculation."""
        interval = 1.0

        # No swing
        delay = self.calc.apply_swing(interval, 0, is_odd_step=True)
        assert delay == 0.0

        # Positive swing on odd step (delay)
        delay = self.calc.apply_swing(interval, 50, is_odd_step=True)
        assert delay > 0  # Odd steps are delayed

        # Negative swing on even step (anticipation)
        delay = self.calc.apply_swing(interval, 50, is_odd_step=False)
        assert delay < 0  # Even steps are anticipated

        # Swing magnitude should be symmetric
        delay_odd = self.calc.apply_swing(interval, 50, is_odd_step=True)
        delay_even = self.calc.apply_swing(interval, 50, is_odd_step=False)
        assert abs(delay_odd + delay_even) < 0.001

    def test_apply_swing_clamping(self):
        """Test swing percentage clamping."""
        interval = 1.0

        # Swing > 75% should be clamped
        delay_unclamped = self.calc.apply_swing(interval, 50, is_odd_step=True)
        delay_clamped = self.calc.apply_swing(interval, 100, is_odd_step=True)
        assert delay_clamped == self.calc.apply_swing(interval, 75, is_odd_step=True)

    def test_calculate_timing_complete(self):
        """Test complete timing metadata calculation."""
        metadata = self.calc.calculate_timing(
            bpm=120,
            division="1/8",
            swing_pct=0,
            step_number=0,
        )

        assert isinstance(metadata, TimingMetadata)
        assert metadata.interval > 0
        assert metadata.total_sleep >= 0.001

        # Even step with no swing should have no swing_delay
        assert metadata.swing_delay == 0

    def test_calculate_timing_with_swing(self):
        """Test timing with swing applied."""
        metadata_even = self.calc.calculate_timing(
            bpm=120,
            division="1/8",
            swing_pct=50,
            step_number=0,  # even
        )

        metadata_odd = self.calc.calculate_timing(
            bpm=120,
            division="1/8",
            swing_pct=50,
            step_number=1,  # odd
        )

        # Odd step should be delayed, even should be anticipated
        assert metadata_odd.swing_delay > 0
        assert metadata_even.swing_delay < 0

    def test_calculate_gate_duration(self):
        """Test note gate duration calculation."""
        # 120 BPM, 100% gate = full beat duration
        duration = self.calc.calculate_gate_duration(bpm=120, gate_pct=100)
        assert abs(duration - 0.5) < 0.001

        # 120 BPM, 50% gate = half beat
        duration = self.calc.calculate_gate_duration(bpm=120, gate_pct=50)
        assert abs(duration - 0.25) < 0.001

        # 0% gate should clamp to minimum
        duration = self.calc.calculate_gate_duration(bpm=120, gate_pct=0)
        assert duration >= 0.01

    def test_get_supported_divisions(self):
        """Test list of supported divisions."""
        divisions = self.calc.get_supported_divisions()
        assert "1/4" in divisions
        assert "1/8" in divisions
        assert "1/16" in divisions
        assert "1/32" in divisions
        assert "TRIPLET" in divisions
        assert "DOTTED" in divisions
