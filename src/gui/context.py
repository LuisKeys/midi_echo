"""Application context for dependency injection."""

from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from src.gui.app import MidiGui
    from src.midi.engine import MidiEngine
    from src.midi.processor import MidiProcessor
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
    ):
        """Initialize application context.

        Args:
            gui: The MidiGui window instance
            engine: The MIDI engine for message routing
            processor: The MIDI message processor
            event_loop: The asyncio event loop for async operations
            app_config: The application configuration
        """
        self.gui = gui
        self.engine = engine
        self.processor = processor
        self.event_loop = event_loop
        self.arp_engine = arp_engine
        self.harmony_engine = harmony_engine
        self.app_config = app_config

    def update_engine(self, engine: "MidiEngine") -> None:
        """Update the engine reference after initialization."""
        self.engine = engine

    def update_gui(self, gui: "MidiGui") -> None:
        """Update the GUI reference after initialization."""
        self.gui = gui
