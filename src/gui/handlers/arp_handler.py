"""Handler for arpeggiator feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class ArpHandler(BaseHandler):
    """Handles arpeggiator enable/disable."""

    def on_button_press(self) -> None:
        """Toggle arpeggiator enabled state."""
        if not self.context.processor:
            return

        self.context.processor.arp_enabled = not self.context.processor.arp_enabled
        self.update_ui()
        logger.info(f"Arp enabled: {self.context.processor.arp_enabled}")

    def on_button_long_press(self) -> None:
        """No special action on long press."""
        pass

    def update_ui(self) -> None:
        """Update button color based on arp state."""
        if not self.context.gui or not self.context.processor:
            return

        new_color = "aqua" if self.context.processor.arp_enabled else None

        btn = self.context.gui.button_panel.get_button("AR")
        if btn:
            if new_color:
                btn.configure(
                    fg_color=self.context.gui.theme.get_color_tuple(new_color)
                )
            else:
                btn.configure(fg_color=("#4A4A4A", "#4A4A4A"))
