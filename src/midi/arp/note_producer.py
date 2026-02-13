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

    def calculate_velocity(
        self, step_idx: int, total_steps: int, state: ArpState
    ) -> int:
        """Calculate velocity for a note at a given position in the sequence.

        Args:
            step_idx: Current position in the expanded note sequence
            total_steps: Total number of notes in the expanded sequence
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
            ratio = step_idx / (total_steps - 1) if total_steps > 1 else 0
            vel = int(
                self.RAMP_MIN_VEL + ratio * (self.RAMP_MAX_VEL - self.RAMP_MIN_VEL)
            )
            return self._clamp_velocity(vel)

        elif vel_mode == "RAMP_DOWN":
            ratio = (
                (total_steps - 1 - step_idx) / (total_steps - 1)
                if total_steps > 1
                else 0
            )
            vel = int(
                self.RAMP_MIN_VEL + ratio * (self.RAMP_MAX_VEL - self.RAMP_MIN_VEL)
            )
            return self._clamp_velocity(vel)

        elif vel_mode == "ACCENT_FIRST":
            if step_idx == 0:
                return self.RAMP_MAX_VEL
            else:
                return self.RAMP_MIN_VEL

        else:  # ORIGINAL or unknown
            return self._clamp_velocity(state.velocity.fixed_velocity)

    def should_accent(self, note: int, state: ArpState) -> bool:
        """Check if a note should have an accent applied based on its semitone.

        Args:
            note: MIDI note number
            state: Current ArpState

        Returns:
            True if note should be accented.
        """
        semitone = note % 12
        return (
            state.pattern.accents
            and semitone < len(state.pattern.accents)
            and state.pattern.accents[semitone]
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
