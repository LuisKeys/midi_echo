"""Handler for scale feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext
from src.midi.scales import ScaleType, get_scale_display_name, NOTE_NAMES, SCALE_NAMES
from src.gui.components.layout_utils import LayoutSpacing

logger = logging.getLogger(__name__)


class ScaleHandler(BaseHandler):
    """Handles scale enable/disable and selection."""

    def on_button_press(self) -> None:
        """Toggle scale enabled state."""
        if not self.context.processor:
            return

        self.context.processor.scale_enabled = not self.context.processor.scale_enabled
        self.update_ui()
        logger.info(f"Scale enabled: {self.context.processor.scale_enabled}")

    def on_button_long_press(self) -> None:
        """Show scale selection popup."""
        if self.context.gui:
            self._show_scale_popup()

    def update_ui(self) -> None:
        """Update button color and text based on scale state."""
        if not self.context.gui or not self.context.processor:
            return

        new_color = "aqua" if self.context.processor.scale_enabled else None

        scale_name = ""
        if self.context.processor.scale_enabled:
            scale_name = get_scale_display_name(
                self.context.processor.scale_root, self.context.processor.scale_type
            )

        btn_text = f"SC\n{scale_name}" if scale_name else "SC"

        btn = self.context.gui.button_panel.get_button("SC")
        if btn:
            btn.configure(text=btn_text)
            if new_color:
                btn.configure(
                    fg_color=self.context.gui.theme.get_color_tuple(new_color)
                )
            else:
                btn.configure(
                    fg_color=self.context.gui.theme.get_color_tuple(
                        "button_inactive_light"
                    )
                )

    def _show_scale_popup(self) -> None:
        """Create and show scale selection popup."""

        def apply_selection(root_var, type_var):
            new_root = NOTE_NAMES.index(root_var.get())
            new_type_name = type_var.get()
            new_type = next(st for st in ScaleType if SCALE_NAMES[st] == new_type_name)
            self.context.processor.scale_root = new_root
            self.context.processor.scale_type = new_type
            self.update_ui()
            logger.info(f"Scale set to: {get_scale_display_name(new_root, new_type)}")

        def build_scale_content(frame):
            import customtkinter as ctk

            # Root selection
            root_label = ctk.CTkLabel(
                frame,
                text="Root Note:",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_label"),
                    "bold",
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
            )
            root_label.pack(pady=(8, 4))

            root_var = ctk.StringVar(
                value=NOTE_NAMES[self.context.processor.scale_root]
            )
            root_menu = ctk.CTkOptionMenu(
                frame,
                values=NOTE_NAMES,
                variable=root_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                fg_color=self.context.gui.theme.get_color_tuple("aqua"),
                button_color=self.context.gui.theme.get_color_tuple("aqua"),
                button_hover_color=self.context.gui.theme.get_color_tuple("aqua_hover"),
                text_color=self.context.gui.theme.get_color("button_text"),
                command=lambda value: apply_selection(root_var, type_var),
            )
            root_menu.pack(pady=(0, 8))

            # Scale type selection
            type_label = ctk.CTkLabel(
                frame,
                text="Scale Type:",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_label"),
                    "bold",
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
            )
            type_label.pack(pady=(8, 4))

            scale_type_names = [SCALE_NAMES[st] for st in ScaleType]
            current_type_name = SCALE_NAMES[self.context.processor.scale_type]
            type_var = ctk.StringVar(value=current_type_name)
            type_menu = ctk.CTkOptionMenu(
                frame,
                values=scale_type_names,
                variable=type_var,
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                ),
                fg_color=self.context.gui.theme.get_color_tuple("aqua"),
                button_color=self.context.gui.theme.get_color_tuple("aqua"),
                button_hover_color=self.context.gui.theme.get_color_tuple("aqua_hover"),
                text_color=self.context.gui.theme.get_color("button_text"),
                command=lambda value: apply_selection(root_var, type_var),
            )
            type_menu.pack(pady=(0, 8))

            # Apply button removed - selection applies immediately

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Scale Selection", build_scale_content
            )
            popup.show()
