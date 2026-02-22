"""Handler for preset management feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext
from src.gui.components.preset_selector import build_preset_selector

logger = logging.getLogger(__name__)


class PresetHandler(BaseHandler):
    """Handles MIDI preset (program change) selection."""

    def __init__(self, context: AppContext):
        """Initialize preset handler.

        Args:
            context: AppContext for accessing app components
        """
        super().__init__(context)
        # Load current preset from config or use default
        config = context.app_config
        self.current_program = config.default_preset if config else 0
        logger.info(f"Preset handler initialized with program {self.current_program}")

    def on_button_press(self) -> None:
        """Open preset selection modal."""
        if not self.context or not self.context.gui:
            logger.warning("Cannot open preset selector: missing GUI context")
            return

        popup = self.context.gui.popup_manager.create_popup(
            "Select Preset",
            lambda parent: build_preset_selector(parent, self.context),
            width=600,
            height=500,
        )
        popup.show()
        logger.info("Preset selector opened")

    def on_button_long_press(self) -> None:
        """No special action on long press."""
        pass

    def update_ui(self) -> None:
        """Update PS button color to black (default state)."""
        if not self.context.gui or not self.context.processor:
            logger.warning("Cannot update UI: missing GUI or processor")
            return

        btn = self.context.gui.button_panel.get_button("PS")
        if btn:
            # Use BACKGROUND_UNSELECTED for PS button (main menu button style)
            theme = self.context.gui.theme
            btn.configure(
                fg_color=(theme.BACKGROUND_UNSELECTED, theme.BACKGROUND_UNSELECTED),
                hover_color=(theme.BACKGROUND_UNSELECTED, theme.BACKGROUND_UNSELECTED),
            )
            logger.debug(f"PS button color updated")
