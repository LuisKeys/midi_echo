"""Base handler for feature operations."""

from abc import ABC, abstractmethod
from src.gui.context import AppContext


class BaseHandler(ABC):
    """Abstract base class for feature handlers.

    Handlers encapsulate the logic for specific features like transpose,
    octave shifting, channel selection, etc.
    """

    def __init__(self, context: AppContext):
        """Initialize handler.

        Args:
            context: AppContext for accessing app components
        """
        self.context = context

    @abstractmethod
    def on_button_press(self) -> None:
        """Handle button press event."""
        pass

    @abstractmethod
    def on_button_long_press(self) -> None:
        """Handle button long press event."""
        pass

    @abstractmethod
    def update_ui(self) -> None:
        """Update the UI with current state."""
        pass
