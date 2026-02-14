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
        """Update PS button color to cyan (active state)."""
        if not self.context.gui or not self.context.processor:
            logger.warning("Cannot update UI: missing GUI or processor")
            return

        btn = self.context.gui.button_panel.get_button("PS")
        if btn:
            # Always use cyan color for PS button (matching other state buttons)
            color_tuple = self.context.gui.theme.get_color_tuple("cyan")
            btn.configure(fg_color=color_tuple, hover_color=color_tuple)
            logger.debug(f"PS button color updated to cyan")
