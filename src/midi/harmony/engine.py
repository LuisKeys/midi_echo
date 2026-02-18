"""Harmony engine coordinating harmony generation and voice management."""

from .harmony_generator import HarmonyGenerator
from .voice_manager import VoiceManager
from .state import HarmonyState
from ..arp.dispatcher import MidiDispatcher
from ..scales import ScaleType


class HarmonyEngine:
    """Main harmony engine coordinating harmony generation and voice management."""

    def __init__(self, dispatcher: MidiDispatcher):
        self.state = HarmonyState()
        self.harmony_generator = HarmonyGenerator(
            self.state.intervals_above, self.state.intervals_below
        )
        self.voice_manager = VoiceManager(self.state.voice_limit)
        self.dispatcher = dispatcher

    def update_state(self, state: HarmonyState) -> None:
        """Update the harmony state and propagate to components."""
        self.state = state
        self.harmony_generator.set_intervals_above(state.intervals_above)
        self.harmony_generator.set_intervals_below(state.intervals_below)
        self.voice_manager.set_max_voices(state.voice_limit)

    def process_melody_note_on(
        self,
        note: int,
        velocity: int,
        channel: int,
        scale_root: int,
        scale_type: ScaleType,
    ) -> None:
        """Process a melody note-on, generate and send harmony notes.

        Args:
            note: The melody note (0-127)
            velocity: MIDI velocity
            channel: MIDI channel
            scale_root: Root of the scale (0-11)
            scale_type: ScaleType enum
        """
        if not self.state.enabled:
            return

        harmony_notes = self.harmony_generator.generate_harmony(
            note, scale_root, scale_type
        )
        allocated_harmonies = self.voice_manager.allocate_voices(note, harmony_notes)

        # Scale harmony velocity based on percentage
        harmony_velocity = int((velocity * self.state.velocity_percentage) / 100)
        harmony_velocity = max(
            0, min(127, harmony_velocity)
        )  # Clamp to valid MIDI range

        # Send harmony note-ons
        for h_note in allocated_harmonies:
            self.dispatcher.send_note_on(h_note, harmony_velocity, channel)

    def process_melody_note_off(self, note: int, channel: int) -> None:
        """Process a melody note-off, send harmony note-offs."""
        if not self.state.enabled:
            return

        harmony_notes = self.voice_manager.deallocate_voices(note)

        # Send harmony note-offs
        for h_note in harmony_notes:
            self.dispatcher.send_note_off(h_note, 0, channel)
