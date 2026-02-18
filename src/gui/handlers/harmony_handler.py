"""Handler for harmonizer feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class HarmonyHandler(BaseHandler):
    """Handles harmonizer enable/disable."""

    def on_button_press(self) -> None:
        """Toggle harmonizer enabled state."""
        if not self.context.processor:
            return

        self.context.processor.harmonizer_enabled = (
            not self.context.processor.harmonizer_enabled
        )
        # Also sync the harmony_state.enabled
        self.context.processor.harmony_state.enabled = (
            self.context.processor.harmonizer_enabled
        )

        # Update the harmony engine's state as well
        if hasattr(self.context, "harmony_engine") and self.context.harmony_engine:
            self.context.harmony_engine.update_state(
                self.context.processor.harmony_state
            )

        # When enabling harmonizer, auto-enable scale to constrain harmony to scale tones
        if self.context.processor.harmonizer_enabled:
            self.context.processor.scale_enabled = True
            # Mutual exclusion: disable arp when enabling harmonizer
            self.context.processor.arp_enabled = False
            if hasattr(self.context.processor, "arp_state"):
                self.context.processor.arp_state.enabled = False

        self.update_ui()
        # Update arp UI as well
        if hasattr(self.context.gui, "handlers") and "AR" in self.context.gui.handlers:
            self.context.gui.handlers["AR"].update_ui()
        # Update scale UI as well to reflect auto-enable
        if hasattr(self.context.gui, "handlers") and "SC" in self.context.gui.handlers:
            self.context.gui.handlers["SC"].update_ui()
        logger.info(f"Harmonizer enabled: {self.context.processor.harmonizer_enabled}")
        if self.context.processor.harmonizer_enabled:
            logger.info("Scale auto-enabled with harmonizer")

    def _show_harmony_popup(self) -> None:
        """Create and show harmony type selection popup."""

        def build_harmony_content(frame):
            import customtkinter as ctk

            def apply_selection():
                selected_intervals = []
                if major_3rd_var.get():
                    selected_intervals.append(4)
                if minor_3rd_var.get():
                    selected_intervals.append(3)
                if fifth_var.get():
                    selected_intervals.append(7)
                if octave_var.get():
                    selected_intervals.append(12)

                if selected_intervals:
                    self.context.processor.harmony_state.intervals = selected_intervals
                    # Update harmony engine state
                    if (
                        hasattr(self.context, "harmony_engine")
                        and self.context.harmony_engine
                    ):
                        self.context.harmony_engine.update_state(
                            self.context.processor.harmony_state
                        )
                    logger.info(f"Harmony intervals set to: {selected_intervals}")
                else:
                    logger.warning("No harmony intervals selected")

            # Title
            title_label = ctk.CTkLabel(
                frame,
                text="Select Harmony Intervals:",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_label"),
                    "bold",
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
            )
            title_label.pack(
                pady=(
                    self.context.gui.theme.get_padding("popup_control"),
                    self.context.gui.theme.get_padding("popup_control_small"),
                )
            )

            # Checkboxes for intervals
            current_intervals = self.context.processor.harmony_state.intervals

            major_3rd_var = ctk.BooleanVar(value=4 in current_intervals)
            minor_3rd_var = ctk.BooleanVar(value=3 in current_intervals)
            fifth_var = ctk.BooleanVar(value=7 in current_intervals)
            octave_var = ctk.BooleanVar(value=12 in current_intervals)

            major_3rd_cb = ctk.CTkCheckBox(
                frame,
                text="Major 3rd (+4 semitones)",
                variable=major_3rd_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
                command=apply_selection,
            )
            major_3rd_cb.pack(
                pady=self.context.gui.theme.get_padding("popup_control_small"),
                anchor="w",
            )

            minor_3rd_cb = ctk.CTkCheckBox(
                frame,
                text="Minor 3rd (+3 semitones)",
                variable=minor_3rd_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
                command=apply_selection,
            )
            minor_3rd_cb.pack(
                pady=self.context.gui.theme.get_padding("popup_control_small"),
                anchor="w",
            )

            fifth_cb = ctk.CTkCheckBox(
                frame,
                text="5th (+7 semitones)",
                variable=fifth_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
                command=apply_selection,
            )
            fifth_cb.pack(
                pady=self.context.gui.theme.get_padding("popup_control_small"),
                anchor="w",
            )

            octave_cb = ctk.CTkCheckBox(
                frame,
                text="Octave (+12 semitones)",
                variable=octave_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
                command=apply_selection,
            )
            octave_cb.pack(
                pady=self.context.gui.theme.get_padding("popup_control_small"),
                anchor="w",
            )

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Harmony Selection", build_harmony_content, width=300, height=250
            )
            popup.show()

    def on_button_long_press(self) -> None:
        """Open harmony type selector on long press."""
        if not self.context.gui or not self.context.processor:
            return

        self._show_harmony_popup()

    def update_ui(self) -> None:
        """Update button color based on harmonizer state."""
        if not self.context.gui or not self.context.processor:
            return

        # If arp is enabled, harmonizer cannot be enabled
        if self.context.processor.arp_enabled:
            self.context.processor.harmonizer_enabled = False
            self.context.processor.harmony_state.enabled = False

        # Sync harmony_state.enabled with processor.harmonizer_enabled
        self.context.processor.harmony_state.enabled = (
            self.context.processor.harmonizer_enabled
        )

        # Update the harmony engine's state to stay in sync
        if hasattr(self.context, "harmony_engine") and self.context.harmony_engine:
            self.context.harmony_engine.update_state(
                self.context.processor.harmony_state
            )

        if self.context.processor.harmonizer_enabled:
            color_name = "violet"
        else:
            color_name = "button_inactive_light"

        btn = self.context.gui.button_panel.get_button("HZ")
        if btn:
            btn.configure(fg_color=self.context.gui.theme.get_color_tuple(color_name))
