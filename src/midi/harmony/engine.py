"""Harmony engine coordinating chord analysis, harmony generation, and voice management."""

from .chord_analyzer import ChordAnalyzer
from .harmony_generator import HarmonyGenerator
from .voice_manager import VoiceManager
from .state import HarmonyState
from ..arp.dispatcher import MidiDispatcher
from typing import Optional


class HarmonyEngine:
    """Main harmony engine coordinating all components."""

    def __init__(self, dispatcher: MidiDispatcher):
        self.state = HarmonyState()
        self.chord_analyzer = ChordAnalyzer()
        self.harmony_generator = HarmonyGenerator(self.state.intervals)
        self.voice_manager = VoiceManager(self.state.voice_limit)
        self.dispatcher = dispatcher

    def update_state(self, state: HarmonyState) -> None:
        """Update the harmony state and propagate to components."""
        self.state = state
        self.harmony_generator.set_intervals(state.intervals)
        self.voice_manager.set_max_voices(state.voice_limit)

    def update_chord_context(self, held_notes: set[int]) -> None:
        """Update the chord analyzer with current held notes."""
        self.chord_analyzer.update_held_notes(held_notes)

    def process_melody_note_on(self, note: int, velocity: int, channel: int) -> None:
        """Process a melody note-on, generate and send harmony notes."""
        if not self.state.enabled:
            return

        chord_root, chord_quality = self.chord_analyzer.get_chord_context()
        harmony_notes = self.harmony_generator.generate_harmony(
            note, chord_root, chord_quality
        )
        allocated_harmonies = self.voice_manager.allocate_voices(note, harmony_notes)

        # Send harmony note-ons
        for h_note in allocated_harmonies:
            self.dispatcher.send_note_on(h_note, velocity, channel)

    def process_melody_note_off(self, note: int, channel: int) -> None:
        """Process a melody note-off, send harmony note-offs."""
        if not self.state.enabled:
            return

        harmony_notes = self.voice_manager.deallocate_voices(note)

        # Send harmony note-offs
        for h_note in harmony_notes:
            self.dispatcher.send_note_off(h_note, channel)
