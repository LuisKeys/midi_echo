"""Handler for MultiChannel feature."""

import logging
import time
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class MultiChannelHandler(BaseHandler):
    """Toggles MultiChannel mode which maps pitch classes to MIDI channels."""

    def __init__(self, context: AppContext):
        """Initialize the handler.

        Args:
            context: AppContext for accessing app components
        """
        super().__init__(context)
        self.last_toggle_time = 0

    def on_button_press(self) -> None:
        """Toggle MultiChannel mode with debounce."""
        if (
            not self.context
            or not self.context.processor
            or not self.context.app_config
        ):
            return

        current_time = time.time() * 1000  # milliseconds
        if current_time - self.last_toggle_time < getattr(
            self.context.app_config, "short_press_threshold", 200
        ):
            return

        self.last_toggle_time = current_time
        current = getattr(self.context.processor, "multi_channel_enabled", False)
        self.context.processor.multi_channel_enabled = not current

        self.update_ui()
        logger.info(
            "MultiChannel %s",
            "enabled" if self.context.processor.multi_channel_enabled else "disabled",
        )

    def on_button_long_press(self) -> None:
        """Disable MultiChannel on long press (explicit reset)."""
        if not self.context or not self.context.processor:
            return

        self.context.processor.multi_channel_enabled = False
        self.update_ui()
        logger.info("MultiChannel disabled (long press)")

    def update_ui(self) -> None:
        """Update MC button to reflect current MultiChannel state."""
        if not self.context or not self.context.gui or not self.context.processor:
            return

        enabled = getattr(self.context.processor, "multi_channel_enabled", False)
        btn = self.context.gui.button_panel.get_button("MC")
        if not btn:
            return

        theme = self.context.gui.theme
        if enabled:
            btn.configure(
                fg_color=(theme.BACKGROUND_SELECTED, theme.BACKGROUND_SELECTED),
                hover_color=(theme.BACKGROUND_SELECTED, theme.BACKGROUND_SELECTED),
            )
        else:
            btn.configure(
                fg_color=(theme.BACKGROUND_UNSELECTED, theme.BACKGROUND_UNSELECTED),
                hover_color=(theme.BACKGROUND_UNSELECTED, theme.BACKGROUND_UNSELECTED),
            )

        try:
            btn.update_idletasks()
        except Exception:
            pass
