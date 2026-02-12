"""Handler for arpeggiator feature."""

import logging
import time
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext
from src.gui.components.pattern_editor import build_pattern_editor
from src.gui.components.tempo_editor import build_tempo_editor

logger = logging.getLogger(__name__)


class ArpHandler(BaseHandler):
    """Handles arpeggiator enable/disable."""

    def __init__(self, context: AppContext):
        super().__init__(context)
        # store recent tap timestamps for tap-tempo
        self._tap_times: list[float] = []

    def on_button_press(self) -> None:
        """Toggle arpeggiator enabled state."""
        if not self.context.processor:
            return

        # Toggle both the simple flag and the richer state container
        self.context.processor.arp_enabled = not self.context.processor.arp_enabled
        if hasattr(self.context.processor, "arp_state"):
            self.context.processor.arp_state.enabled = (
                self.context.processor.arp_enabled
            )

        # Start/stop the ArpEngine on the engine event loop
        try:
            arp_engine = getattr(self.context, "arp_engine", None)
            if arp_engine and self.context.event_loop:
                if self.context.processor.arp_enabled:
                    self.context.event_loop.call_soon_threadsafe(arp_engine.start)
                else:
                    self.context.event_loop.call_soon_threadsafe(arp_engine.stop)
        except Exception:
            logger.exception("Failed to start/stop arp engine")

        self.update_ui()
        logger.info(f"Arp enabled: {self.context.processor.arp_enabled}")
        # Toggle both the simple flag and the richer state container
        self.context.processor.arp_enabled = not self.context.processor.arp_enabled
        if hasattr(self.context.processor, "arp_state"):
            self.context.processor.arp_state.enabled = (
                self.context.processor.arp_enabled
            )
        self.update_ui()
        logger.info(f"Arp enabled: {self.context.processor.arp_enabled}")

    def on_button_long_press(self) -> None:
        """Open the pattern editor popup on long press."""
        if not self.context or not self.context.gui:
            return

        popup = self.context.gui.popup_manager.create_popup(
            "Pattern Editor",
            lambda parent: build_pattern_editor(parent, self.context),
        )
        popup.show()

    def tap_tempo(self) -> None:
        """Record a tap for tempo detection and update BPM."""
        if not self.context or not self.context.processor:
            return

        now = time.time()
        self._tap_times.append(now)
        # Keep last 6 taps
        if len(self._tap_times) > 6:
            self._tap_times.pop(0)

        if len(self._tap_times) >= 2:
            intervals = [
                t2 - t1 for t1, t2 in zip(self._tap_times[:-1], self._tap_times[1:])
            ]
            avg = sum(intervals) / len(intervals)
            if avg > 0:
                bpm = int(round(60.0 / avg))
                self.context.processor.arp_state.bpm = max(20, min(300, bpm))
                logger.info(
                    f"Tap tempo BPM set to {self.context.processor.arp_state.bpm}"
                )
                self.update_ui()

    def open_tempo_editor(self) -> None:
        """Open a popup to edit BPM precisely (hold-edit mode)."""
        if not self.context or not self.context.gui:
            return

        popup = self.context.gui.popup_manager.create_popup(
            "Tempo",
            lambda parent: build_tempo_editor(parent, self.context),
            width=400,
            height=240,
        )
        popup.show()

    def update_ui(self) -> None:
        """Update button color based on arp state."""
        if not self.context.gui or not self.context.processor:
            return

        enabled = self.context.processor.arp_enabled
        if hasattr(self.context.processor, "arp_state"):
            enabled = self.context.processor.arp_state.enabled

        new_color = "aqua" if enabled else None

        btn = self.context.gui.button_panel.get_button("AR")
        if btn:
            if new_color:
                btn.configure(
                    fg_color=self.context.gui.theme.get_color_tuple(new_color)
                )
            else:
                btn.configure(fg_color=("#4A4A4A", "#4A4A4A"))
