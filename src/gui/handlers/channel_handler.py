"""Handler for channel selection feature."""

import logging
import time
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class ChannelHandler(BaseHandler):
    """Handles MIDI channel selection/rotation."""

    def __init__(self, context: AppContext):
        """Initialize channel handler.

        Args:
            context: AppContext for accessing app components
        """
        super().__init__(context)
        self.last_toggle_time = 0

    def on_button_press(self) -> None:
        """Rotate through MIDI channels with debounce."""
        if not self.context.processor or not self.context.app_config:
            return

        current_time = time.time() * 1000  # milliseconds
        if (
            current_time - self.last_toggle_time
            < self.context.app_config.short_press_threshold
        ):
            return  # Ignore rapid toggles

        self.last_toggle_time = current_time

        # Rotate through channels 0-15 (1-16), wrapping from 15 back to 0
        if self.context.processor.output_channel is None:
            self.context.processor.output_channel = 0
        elif self.context.processor.output_channel >= 15:
            self.context.processor.output_channel = 0
        else:
            self.context.processor.output_channel += 1

        self.update_ui()
        logger.info(f"Channel changed to: {self.context.processor.output_channel + 1}")

    def on_button_long_press(self) -> None:
        """Reset channel to 1 (index 0) on long press."""
        if not self.context.processor:
            return

        self.context.processor.output_channel = 0
        self.update_ui()
        logger.info("Channel reset to 1 (long press)")

    def update_ui(self) -> None:
        """Update button label with current channel."""
        if not self.context.gui or not self.context.processor:
            return

        # Ensure channel has a default value (should not be None)
        channel = self.context.processor.output_channel
        if channel is None:
            channel = 0
            self.context.processor.output_channel = 0

        # If channel is 1 (0-indexed as 0), show just "CH"
        # Otherwise show the channel number
        if channel == 0:
            button_text = "CH"
        else:
            ch_text = str(channel + 1)
            button_text = f"CH\n{ch_text}"

        btn = self.context.gui.button_panel.get_button("CH")
        if btn:
            btn.configure(text=button_text)
            # Update button colors: selected if channel is not 1 (0-indexed as 0)
            theme = self.context.gui.theme
            if channel != 0:
                btn.configure(
                    fg_color=(theme.BACKGROUND_SELECTED, theme.BACKGROUND_SELECTED),
                    hover_color=(theme.BACKGROUND_SELECTED, theme.BACKGROUND_SELECTED),
                )
            else:
                btn.configure(
                    fg_color=(theme.BACKGROUND_UNSELECTED, theme.BACKGROUND_UNSELECTED),
                    hover_color=(
                        theme.BACKGROUND_UNSELECTED,
                        theme.BACKGROUND_UNSELECTED,
                    ),
                )
