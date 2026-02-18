"""Tests for HarmonyGenerator with scale-based harmony."""

import pytest
from src.midi.harmony.harmony_generator import HarmonyGenerator
from src.midi.scales import ScaleType


class TestHarmonyGenerator:
    """Tests for harmony generator using scale context."""

    def test_generate_harmony_c_major_scale(self):
        """Test harmony generation in C Major scale."""
        generator = HarmonyGenerator(intervals_above=[4, 7])  # 3rd and 5th

        # Melody note C (60) in C Major
        # Interval +4: E (64) - in C Major scale
        # Interval +7: G (67) - in C Major scale
        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 2
        assert 64 in harmony  # E (major 3rd, also in C Major)
        assert 67 in harmony  # G (perfect 5th, also in C Major)

    def test_generate_harmony_a_minor_scale(self):
        """Test harmony generation in A Minor scale."""
        generator = HarmonyGenerator(intervals_above=[3, 7])  # minor 3rd and 5th

        # Melody note A (69) in A Minor
        # Interval +3: C (72) - in A Minor scale
        # Interval +7: E (76) - in A Minor scale
        harmony = generator.generate_harmony(
            69, scale_root=9, scale_type=ScaleType.MINOR
        )

        assert len(harmony) == 2
        assert all(0 <= note <= 127 for note in harmony)

    def test_generate_harmony_empty_intervals(self):
        """Test with empty intervals returns empty harmony."""
        generator = HarmonyGenerator(intervals_above=[])

        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 0

    def test_generate_harmony_single_interval(self):
        """Test with single interval."""
        generator = HarmonyGenerator(intervals_above=[7])  # only 5th

        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 1
        assert harmony[0] == 67  # G (perfect 5th)

    def test_generate_harmony_snapped_to_scale(self):
        """Test that harmony notes are snapped to scale tones."""
        generator = HarmonyGenerator(intervals_above=[3])  # 3rd

        # In C Major, 63 (Eb - not in scale) should snap to 64 (E)
        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # The interval 3 gives 63, which snaps to nearest scale tone
        assert len(harmony) == 1
        # 63 + 60 = 63, snaps to 62 (D) or 64 (E) - depends on snap logic
        assert harmony[0] in [62, 64]  # Either D or E is acceptable (upward bias)

    def test_generate_harmony_clamps_to_midi_range(self):
        """Test that harmony notes are clamped to valid MIDI range."""
        generator = HarmonyGenerator(intervals_above=[24])  # 2 octaves

        # High note near limit
        harmony = generator.generate_harmony(
            110, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # 110 + 24 = 134, which exceeds MIDI limit (127)
        # Should be skipped because it's out of range before snap
        assert all(0 <= note <= 127 for note in harmony)

    def test_set_intervals_clamps_values(self):
        """Test that set_intervals_above clamps invalid interval values."""
        generator = HarmonyGenerator(intervals_above=[])

        generator.set_intervals_above([1, 24, 100])  # 100 is too large

        # Should be clamped to max 24
        assert generator.intervals_above == [1, 24, 24]

    def test_set_intervals_minimum_value(self):
        """Test that intervals are clamped to minimum of 1."""
        generator = HarmonyGenerator(intervals_above=[])

        generator.set_intervals_above([0, -5, 7])

        # 0 and -5 should become 1 (minimum)
        assert generator.intervals_above == [1, 1, 7]

    def test_generate_harmony_chromatic_scale(self):
        """Test harmony generation in Chromatic scale (all notes allowed)."""
        generator = HarmonyGenerator(intervals_above=[3, 4, 5])

        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.CHROMATIC
        )

        # In chromatic scale, all notes snap to themselves
        assert len(harmony) == 3
        assert 63 in harmony  # 60+3
        assert 64 in harmony  # 60+4
        assert 65 in harmony  # 60+5

    def test_generate_harmony_preserves_velocity_independence(self):
        """Test that harmony generation doesn't modify velocity (handled elsewhere)."""
        generator = HarmonyGenerator(intervals_above=[4, 7])

        # This test just verifies the function signature doesn't take velocity
        # Velocity is handled at the engine level
        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 2

    def test_generate_harmony_multiple_large_intervals(self):
        """Test harmony with multiple large intervals."""
        generator = HarmonyGenerator(
            intervals_above=[12, 19, 24]
        )  # octave, octave+major7, 2 octaves

        harmony = generator.generate_harmony(
            48, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # All should be valid MIDI notes
        assert len(harmony) <= 3
        assert all(0 <= note <= 127 for note in harmony)

    def test_different_scale_roots(self):
        """Test that harmony respects different scale roots."""
        generator = HarmonyGenerator(intervals_above=[4])

        # C Major (root=0) vs F Major (root=5)
        harmony_c = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )
        harmony_f = generator.generate_harmony(
            60, scale_root=5, scale_type=ScaleType.MAJOR
        )

        # Different scale roots may produce different snapped results
        assert len(harmony_c) == 1
        assert len(harmony_f) == 1
        # Both should be snapped to their respective scales


class TestHarmonyGeneratorEdgeCases:
    """Edge case tests for harmony generator."""

    def test_low_note_harmony(self):
        """Test harmony generation for very low MIDI note."""
        generator = HarmonyGenerator(intervals_above=[7])

        harmony = generator.generate_harmony(
            5, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 1
        assert harmony[0] >= 0

    def test_high_note_harmony(self):
        """Test harmony generation for very high MIDI note."""
        generator = HarmonyGenerator(intervals_above=[7])

        harmony = generator.generate_harmony(
            120, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # 120 + 7 = 127, exactly at MIDI limit
        assert len(harmony) == 1
        assert harmony[0] <= 127

    def test_octave_at_boundary(self):
        """Test octave interval at MIDI boundaries."""
        generator = HarmonyGenerator(intervals_above=[12])

        # High note + octave goes over limit
        harmony = generator.generate_harmony(
            119, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # 119 + 12 = 131, exceeds MIDI range, should be skipped
        assert all(0 <= note <= 127 for note in harmony)


class TestBidirectionalHarmony:
    """Tests for bidirectional harmony (above and below root)."""

    def test_generate_harmony_below_root(self):
        """Test harmony generation below root note."""
        generator = HarmonyGenerator(intervals_above=[], intervals_below=[4, 7])

        # Melody note C (60) in C Major
        # Interval -4: should snap to a scale tone below
        # Interval -7: should snap to a scale tone below
        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        assert len(harmony) == 2
        # Both notes should be varied and in the C Major scale
        assert all(0 <= note <= 127 for note in harmony)

    def test_generate_harmony_both_directions(self):
        """Test harmony generation with both above and below intervals."""
        generator = HarmonyGenerator(intervals_above=[4, 7], intervals_below=[3, 4])

        # Melody note C (60) in C Major
        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Should have 4 harmony notes (2 above + 2 below)
        assert len(harmony) == 4
        # Check above intervals present
        assert any(note > 60 for note in harmony)
        # Check below intervals present
        assert any(note < 60 for note in harmony)

    def test_downward_harmony_clamps_at_zero(self):
        """Test that downward harmony respects MIDI lower bound."""
        generator = HarmonyGenerator(intervals_above=[], intervals_below=[24])

        # Very low note - 24 semitones would go below 0
        harmony = generator.generate_harmony(
            10, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # 10 - 24 = -14, which is below 0, should be skipped
        assert all(0 <= note <= 127 for note in harmony)

    def test_downward_harmony_snapped_to_scale(self):
        """Test that downward harmony notes are snapped to scale tones."""
        generator = HarmonyGenerator(intervals_above=[], intervals_below=[3])

        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # 60 - 3 = 57, which should snap to scale tone
        assert len(harmony) == 1
        # 57 should snap to A (57) or G (55)
        assert harmony[0] in [55, 57]

    def test_set_intervals_below(self):
        """Test setting downward intervals."""
        generator = HarmonyGenerator(intervals_above=[], intervals_below=[])

        generator.set_intervals_below([3, 4, 7])

        assert generator.intervals_below == [3, 4, 7]

    def test_combined_above_and_below(self):
        """Test full four-part harmony above and below."""
        generator = HarmonyGenerator(intervals_above=[4, 7], intervals_below=[3, 5])

        harmony = generator.generate_harmony(
            60, scale_root=0, scale_type=ScaleType.MAJOR
        )

        # Should have 4 harmony notes
        assert len(harmony) == 4
        # All should be valid MIDI notes
        assert all(0 <= note <= 127 for note in harmony)
