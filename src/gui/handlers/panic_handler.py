"""Handler for MIDI panic feature."""

import logging
import mido
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class PanicHandler(BaseHandler):
    """Handles MIDI panic (all notes off) operation."""

    def on_button_press(self) -> None:
        """Send all notes off to all MIDI channels."""
        logger.info("ST pressed - MIDI PANIC")

        if not self.context.gui or not self.context.engine:
            return

        # Change button color to red
        btn = self.context.gui.button_panel.get_button("ST")
        if btn:
            btn.configure(fg_color=self.context.gui.theme.get_color_tuple("red"))

        # Send All Notes Off (CC 123) to all 16 channels
        for ch in range(16):
            msg = mido.Message("control_change", channel=ch, control=123, value=0)
            if self.context.event_loop:
                self.context.event_loop.call_soon_threadsafe(
                    self.context.engine.queue.put_nowait, msg
                )

        # Reset button color after 500ms
        if self.context.gui:
            self.context.gui.root.after(
                500,
                lambda: (
                    btn.configure(
                        fg_color=self.context.gui.theme.get_color_tuple("grey")
                    )
                    if btn
                    else None
                ),
            )

    def on_button_long_press(self) -> None:
        """Open the event monitor on long press."""
        if not self.context.gui or not self.context.event_log:
            return

        logger.info("ST long pressed - opening event monitor")
        self.context.gui.popup_manager.show_event_monitor(self.context.event_log)

    def update_ui(self) -> None:
        """No persistent UI update needed."""
        pass
