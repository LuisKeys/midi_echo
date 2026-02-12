"""Handler for scale feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class ScaleHandler(BaseHandler):
    """Handles scale enable/disable."""

    def on_button_press(self) -> None:
        """Toggle scale enabled state."""
        if not self.context.processor:
            return

        self.context.processor.scale_enabled = not self.context.processor.scale_enabled
        self.update_ui()
        logger.info(f"Scale enabled: {self.context.processor.scale_enabled}")

    def on_button_long_press(self) -> None:
        """No special action on long press."""
        pass

    def update_ui(self) -> None:
        """Update button color based on scale state."""
        if not self.context.gui or not self.context.processor:
            return

        new_color = "aqua" if self.context.processor.scale_enabled else None

        btn = self.context.gui.button_panel.get_button("SC")
        if btn:
            if new_color:
                btn.configure(
                    fg_color=self.context.gui.theme.get_color_tuple(new_color)
                )
            else:
                btn.configure(fg_color=("#4A4A4A", "#4A4A4A"))
