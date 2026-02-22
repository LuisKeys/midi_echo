"""Application context for dependency injection."""

from typing import TYPE_CHECKING
import asyncio
import time
from src.state import AppState

if TYPE_CHECKING:
    from src.gui.app import MidiGui
    from src.midi.engine import MidiEngine
    from src.midi.processor import MidiProcessor
    from src.midi.event_log import EventLog
    from src.midi.sequencer import MidiSequencer
    from src.config import AppConfig


class AppContext:
    """Central context holding references to all application components.

    This enables dependency injection throughout the application, making
    components decoupled and testable.
    """

    def __init__(
        self,
        gui: "MidiGui" = None,
        engine: "MidiEngine" = None,
        processor: "MidiProcessor" = None,
        event_loop: asyncio.AbstractEventLoop = None,
        app_config: "AppConfig" = None,
        arp_engine: object = None,
        harmony_engine: object = None,
        event_log: "EventLog" = None,
        sequencer: "MidiSequencer" = None,
        app_state: AppState = None,
    ):
        """Initialize application context.

        Args:
            gui: The MidiGui window instance
            engine: The MIDI engine for message routing
            processor: The MIDI message processor
            event_loop: The asyncio event loop for async operations
            app_config: The application configuration
            event_log: The event log for monitoring MIDI messages
            sequencer: The MIDI pattern sequencer
        """
        self.gui = gui
        self.engine = engine
        self.processor = processor
        self.event_loop = event_loop
        self.arp_engine = arp_engine
        self.harmony_engine = harmony_engine
        self.app_config = app_config
        self.event_log = event_log
        self.sequencer = sequencer
        if app_state:
            self.app_state = app_state
        elif processor and hasattr(processor, "app_state"):
            self.app_state = processor.app_state
        else:
            self.app_state = AppState()
        self._tempo_widgets = self.app_state.ui_runtime.tempo_widgets
        self._tap_times = self.app_state.ui_runtime.tap_times

    def update_engine(self, engine: "MidiEngine") -> None:
        """Update the engine reference after initialization."""
        self.engine = engine

    def update_gui(self, gui: "MidiGui") -> None:
        """Update the GUI reference after initialization."""
        self.gui = gui

    def get_global_tempo(self) -> int:
        """Get the current global tempo (BPM)."""
        if self.app_state and self.app_state.arp:
            return int(self.app_state.arp.timing.bpm)
        if self.sequencer:
            return int(self.sequencer.state.tempo)
        return 120

    def register_tempo_widget(self, widget) -> None:
        """Register a tempo widget for synchronized UI updates."""
        if widget not in self._tempo_widgets:
            self._tempo_widgets.append(widget)

    def _notify_tempo_widgets(self, bpm: int, source_widget=None) -> None:
        """Update all registered tempo widgets to the latest BPM."""
        stale_widgets = []
        for widget in self._tempo_widgets:
            if widget is source_widget:
                continue
            try:
                if widget.winfo_exists():
                    widget.set_value(int(bpm))
                else:
                    stale_widgets.append(widget)
            except Exception:
                stale_widgets.append(widget)

        if stale_widgets:
            self._tempo_widgets = [
                widget for widget in self._tempo_widgets if widget not in stale_widgets
            ]

    def set_global_tempo(self, bpm: int, source_widget=None) -> int:
        """Set tempo globally for both arpeggiator and sequencer states."""
        clamped = max(20, min(300, int(bpm)))

        if self.app_state and self.app_state.arp:
            self.app_state.arp.timing.bpm = clamped
        elif self.processor and hasattr(self.processor, "arp_state"):
            self.processor.arp_state.timing.bpm = clamped

        if self.app_state and self.app_state.sequencer:
            self.app_state.sequencer.on_tempo_changed(clamped)
        elif self.sequencer:
            self.sequencer.state.on_tempo_changed(clamped)

        self._notify_tempo_widgets(clamped, source_widget=source_widget)
        return clamped

    def tap_tempo(self, source_widget=None) -> int | None:
        """Compute and apply tempo from tap intervals."""
        now = time.time()
        self._tap_times.append(now)

        if len(self._tap_times) > 6:
            self._tap_times.pop(0)

        if len(self._tap_times) < 2:
            return None

        intervals = [
            t2 - t1 for t1, t2 in zip(self._tap_times[:-1], self._tap_times[1:])
        ]
        avg = sum(intervals) / len(intervals)
        if avg <= 0:
            return None

        bpm = int(round(60.0 / avg))
        return self.set_global_tempo(bpm, source_widget=source_widget)
