"""Handler for preset management feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class PresetHandler(BaseHandler):
    """Handles preset loading/saving (placeholder)."""

    def on_button_press(self) -> None:
        """Show preset selection popup (not yet implemented)."""
        logger.info("PS pressed - Presets not implemented yet")

    def on_button_long_press(self) -> None:
        """No special action on long press."""
        pass

    def update_ui(self) -> None:
        """No UI update needed."""
        pass
