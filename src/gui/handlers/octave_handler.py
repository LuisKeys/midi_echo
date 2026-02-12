"""Handler for octave feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class OctaveHandler(BaseHandler):
    """Handles octave shifting operations."""

    def on_button_press(self) -> None:
        """Cycle through octave values."""
        if not self.context.processor:
            return

        self.context.processor.octave = self.context.processor.octave + 1
        if self.context.processor.octave > 2:
            self.context.processor.octave = -2

        self.update_ui()
        logger.info(f"Octave: {self.context.processor.octave}")

    def on_button_long_press(self) -> None:
        """Reset octave to 0 on long press."""
        if not self.context.processor:
            return

        self.context.processor.octave = 0
        self.update_ui()
        logger.info("Octave reset to 0 (long press)")

    def update_ui(self) -> None:
        """Update button label with current octave."""
        if not self.context.gui or not self.context.processor:
            return

        oc_text = (
            f"OC\n{self.context.processor.octave}"
            if self.context.processor.octave != 0
            else "OC"
        )

        btn = self.context.gui.button_panel.get_button("OC")
        if btn:
            btn.configure(text=oc_text)
