"""Note producer for arpeggiator engine.

Generates MIDI note values and velocities based on pattern step,
velocity mode, and accent configuration.
"""

import random
from typing import Tuple

from .state_validator import ArpState


class NoteProducer:
    """Produces note information (pitch and velocity) for a pattern step."""

    BASE_NOTE = 60  # Middle C (C4)
    MIN_NOTE = 0
    MAX_NOTE = 127
    MIN_VELOCITY = 0
    MAX_VELOCITY = 127

    RAMP_MIN_VEL = 40
    RAMP_MAX_VEL = 127

    def __init__(self) -> None:
        """Initialize note producer."""
        pass

    def produce_note(self, step_idx: int, state: ArpState) -> Tuple[int, int]:
        """Generate MIDI note and velocity for a pattern step.

        Args:
            step_idx: Index in the 12-step pattern (0..11)
            state: Current ArpState

        Returns:
            Tuple of (note, velocity) where both are in MIDI range [0..127].
        """
        # Calculate note pitch
        note = self._calculate_note(step_idx, state.octave)

        # Calculate velocity based on mode
        velocity = self._calculate_velocity(step_idx, state)

        # Apply accent boost if enabled
        if self._should_accent(step_idx, state):
            velocity = self._apply_accent(velocity)

        return note, velocity

    def _calculate_note(self, step_idx: int, octave: int) -> int:
        """Calculate MIDI note value from pattern step and octave.

        Args:
            step_idx: Index in 12-step pattern (0..11, representing C..B)
            octave: Octave offset (1..4, where 1 is base octave)

        Returns:
            MIDI note (0..127).
        """
        # Pattern represents 12 semitones in an octave
        base_note = self.BASE_NOTE + step_idx

        # Octave offset: octave 1 = no offset, octave 2 = +12, etc.
        octave = max(1, min(4, int(octave)))
        octave_offset = (octave - 1) * 12

        note = base_note + octave_offset
        return max(self.MIN_NOTE, min(self.MAX_NOTE, note))

    def _calculate_velocity(self, step_idx: int, state: ArpState) -> int:
        """Calculate velocity based on velocity mode in state.

        Args:
            step_idx: Index in 12-step pattern
            state: Current ArpState

        Returns:
            Velocity (0..127).
        """
        vel_mode = (state.velocity.mode or "ORIGINAL").upper()

        if vel_mode == "FIXED":
            return self._clamp_velocity(state.velocity.fixed_velocity)

        elif vel_mode == "RANDOM":
            return random.randint(self.RAMP_MIN_VEL, self.RAMP_MAX_VEL)

        elif vel_mode == "RAMP_UP":
            # Velocity increases from step 0 to 11
            ratio = step_idx / 11.0 if step_idx > 0 else 0
            vel = int(
                self.RAMP_MIN_VEL + ratio * (self.RAMP_MAX_VEL - self.RAMP_MIN_VEL)
            )
            return self._clamp_velocity(vel)

        elif vel_mode == "RAMP_DOWN":
            # Velocity decreases from step 0 to 11
            ratio = (11 - step_idx) / 11.0
            vel = int(
                self.RAMP_MIN_VEL + ratio * (self.RAMP_MAX_VEL - self.RAMP_MIN_VEL)
            )
            return self._clamp_velocity(vel)

        elif vel_mode == "ACCENT_FIRST":
            # First step is accented, others are lower
            if step_idx == 0:
                return self.RAMP_MAX_VEL
            else:
                return self.RAMP_MIN_VEL

        else:  # ORIGINAL or unknown
            return self._clamp_velocity(state.velocity.fixed_velocity)

    def _should_accent(self, step_idx: int, state: ArpState) -> bool:
        """Check if this step should have an accent applied.

        Args:
            step_idx: Index in 12-step pattern
            state: Current ArpState

        Returns:
            True if step should be accented.
        """
        return (
            state.pattern.accents
            and step_idx < len(state.pattern.accents)
            and state.pattern.accents[step_idx]
        )

    def _apply_accent(self, velocity: int) -> int:
        """Apply accent boost to velocity.

        Accent multiplies velocity by 1.25 and clamps to max velocity.

        Args:
            velocity: Base velocity (0..127)

        Returns:
            Accented velocity (0..127).
        """
        accented = int(velocity * 1.25)
        return self._clamp_velocity(accented)

    @staticmethod
    def _clamp_velocity(vel: int) -> int:
        """Clamp velocity to valid MIDI range.

        Args:
            vel: Raw velocity value

        Returns:
            Velocity clamped to [0..127].
        """
        return max(0, min(127, int(vel)))

    def get_velocity_modes(self) -> list[str]:
        """Get list of supported velocity modes.

        Returns:
            List of velocity mode strings.
        """
        return [
            "ORIGINAL",
            "FIXED",
            "RAMP_UP",
            "RAMP_DOWN",
            "RANDOM",
            "ACCENT_FIRST",
        ]
