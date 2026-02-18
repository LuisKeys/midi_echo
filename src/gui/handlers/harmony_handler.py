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
        """Create and show harmony type selection popup with 2-column layout."""

        def build_harmony_content(frame):
            import customtkinter as ctk

            def apply_selection():
                selected_intervals_above = []
                if major_3rd_above_var.get():
                    selected_intervals_above.append(4)
                if minor_3rd_above_var.get():
                    selected_intervals_above.append(3)
                if fifth_above_var.get():
                    selected_intervals_above.append(7)
                if octave_above_var.get():
                    selected_intervals_above.append(12)

                selected_intervals_below = []
                if major_3rd_below_var.get():
                    selected_intervals_below.append(4)
                if minor_3rd_below_var.get():
                    selected_intervals_below.append(3)
                if fifth_below_var.get():
                    selected_intervals_below.append(7)
                if octave_below_var.get():
                    selected_intervals_below.append(12)

                # Update state
                self.context.processor.harmony_state.intervals_above = (
                    selected_intervals_above
                )
                self.context.processor.harmony_state.intervals_below = (
                    selected_intervals_below
                )
                self.context.processor.harmony_state.velocity_percentage = int(
                    velocity_slider.get()
                )

                # Update harmony engine state
                if (
                    hasattr(self.context, "harmony_engine")
                    and self.context.harmony_engine
                ):
                    self.context.harmony_engine.update_state(
                        self.context.processor.harmony_state
                    )
                logger.info(
                    f"Harmony intervals above: {selected_intervals_above}, "
                    f"below: {selected_intervals_below}, "
                    f"velocity: {self.context.processor.harmony_state.velocity_percentage}%"
                )

            # Get current state
            current_intervals_above = (
                self.context.processor.harmony_state.intervals_above
            )
            current_intervals_below = (
                self.context.processor.harmony_state.intervals_below
            )
            current_velocity = self.context.processor.harmony_state.velocity_percentage

            # Get theme font sizes
            theme = self.context.gui.theme
            section_font_size = theme.get_font_size("label_small")
            checkbox_font_size = theme.get_font_size("label_small")

            # Create a columns frame for above/below side by side
            columns_frame = ctk.CTkFrame(frame, fg_color="transparent")
            columns_frame.pack(fill="both", expand=True, padx=10, pady=5)

            # --- LEFT COLUMN: ABOVE ROOT ---
            above_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
            above_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

            above_label = ctk.CTkLabel(
                above_frame,
                text="Above Root:",
                font=("Arial", section_font_size, "bold"),
                text_color=theme.get_color("text_black"),
            )
            above_label.pack(pady=(0, 5), anchor="w")

            major_3rd_above_var = ctk.BooleanVar(value=4 in current_intervals_above)
            minor_3rd_above_var = ctk.BooleanVar(value=3 in current_intervals_above)
            fifth_above_var = ctk.BooleanVar(value=7 in current_intervals_above)
            octave_above_var = ctk.BooleanVar(value=12 in current_intervals_above)

            major_3rd_above_cb = ctk.CTkCheckBox(
                above_frame,
                text="Major 3rd (+4)",
                variable=major_3rd_above_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            major_3rd_above_cb.pack(pady=2, anchor="w")

            minor_3rd_above_cb = ctk.CTkCheckBox(
                above_frame,
                text="Minor 3rd (+3)",
                variable=minor_3rd_above_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            minor_3rd_above_cb.pack(pady=2, anchor="w")

            fifth_above_cb = ctk.CTkCheckBox(
                above_frame,
                text="5th (+7)",
                variable=fifth_above_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            fifth_above_cb.pack(pady=2, anchor="w")

            octave_above_cb = ctk.CTkCheckBox(
                above_frame,
                text="Octave (+12)",
                variable=octave_above_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            octave_above_cb.pack(pady=2, anchor="w")

            # --- RIGHT COLUMN: BELOW ROOT ---
            below_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
            below_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

            below_label = ctk.CTkLabel(
                below_frame,
                text="Below Root:",
                font=("Arial", section_font_size, "bold"),
                text_color=theme.get_color("text_black"),
            )
            below_label.pack(pady=(0, 5), anchor="w")

            major_3rd_below_var = ctk.BooleanVar(value=4 in current_intervals_below)
            minor_3rd_below_var = ctk.BooleanVar(value=3 in current_intervals_below)
            fifth_below_var = ctk.BooleanVar(value=7 in current_intervals_below)
            octave_below_var = ctk.BooleanVar(value=12 in current_intervals_below)

            major_3rd_below_cb = ctk.CTkCheckBox(
                below_frame,
                text="Major 3rd (-4)",
                variable=major_3rd_below_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            major_3rd_below_cb.pack(pady=2, anchor="w")

            minor_3rd_below_cb = ctk.CTkCheckBox(
                below_frame,
                text="Minor 3rd (-3)",
                variable=minor_3rd_below_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            minor_3rd_below_cb.pack(pady=2, anchor="w")

            fifth_below_cb = ctk.CTkCheckBox(
                below_frame,
                text="5th (-7)",
                variable=fifth_below_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            fifth_below_cb.pack(pady=2, anchor="w")

            octave_below_cb = ctk.CTkCheckBox(
                below_frame,
                text="Octave (-12)",
                variable=octave_below_var,
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                command=apply_selection,
            )
            octave_below_cb.pack(pady=2, anchor="w")

            # --- VELOCITY SECTION AT BOTTOM ---
            separator = ctk.CTkFrame(frame, height=1, fg_color="gray50")
            separator.pack(fill="x", padx=10, pady=(5, 8))

            velocity_label = ctk.CTkLabel(
                frame,
                text="Velocity:",
                font=("Arial", section_font_size, "bold"),
                text_color=theme.get_color("text_black"),
            )
            velocity_label.pack(pady=(0, 5), anchor="w", padx=10)

            velocity_frame = ctk.CTkFrame(frame, fg_color="transparent")
            velocity_frame.pack(pady=(0, 10), padx=10, fill="x")

            velocity_slider = ctk.CTkSlider(
                velocity_frame,
                from_=0,
                to=200,
                number_of_steps=41,
                command=lambda v: (
                    apply_selection(),
                    velocity_value_label.configure(text=f"{int(float(v))}%"),
                ),
            )
            velocity_slider.set(current_velocity)
            velocity_slider.pack(side="left", fill="x", expand=True)

            velocity_value_label = ctk.CTkLabel(
                velocity_frame,
                text=f"{current_velocity}%",
                font=("Arial", checkbox_font_size),
                text_color=theme.get_color("text_black"),
                width=40,
            )
            velocity_value_label.pack(side="right", padx=(10, 0))

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Harmony Selection", build_harmony_content, width=380, height=300
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
