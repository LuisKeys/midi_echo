"""Handler for MIDI pattern sequencer control"""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext
from src.gui.components.sequencer_popup import build_sequencer_popup

logger = logging.getLogger(__name__)


class SequencerHandler(BaseHandler):
    """Handles MIDI pattern sequencer control and recording/playback."""

    def __init__(self, context: AppContext):
        """Initialize sequencer handler.

        Args:
            context: AppContext for accessing app components
        """
        super().__init__(context)
        logger.info("Sequencer handler initialized")

    def on_button_press(self) -> None:
        """Open sequencer control popup."""
        if not self.context or not self.context.gui:
            logger.warning("Cannot open sequencer: missing GUI context")
            return

        if not self.context.sequencer:
            logger.warning("Cannot open sequencer: sequencer not initialized")
            return

        popup = self.context.gui.popup_manager.create_popup(
            "Pattern Sequencer",
            lambda parent: build_sequencer_popup(parent, self.context),
            width=600,
            height=500,
        )
        popup.show()
        logger.info("Sequencer popup opened")

    def on_button_long_press(self) -> None:
        """No special action on long press."""
        pass

    def update_ui(self) -> None:
        """Update SQ (sequencer) button color based on playback state."""
        if not self.context.gui or not self.context.sequencer:
            return

        btn = self.context.gui.button_panel.get_button("SQ")
        if btn:
            sequencer = self.context.sequencer
            theme = self.context.gui.theme

            # Red when recording, green when playing, cyan otherwise
            if sequencer.state.is_recording:
                color = theme.get_color_tuple("red")
            elif sequencer.state.is_playing:
                color = theme.get_color_tuple("green")
            else:
                color = theme.get_color_tuple("cyan")

            btn.configure(fg_color=color, hover_color=color)
