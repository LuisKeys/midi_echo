"""Handler for scale feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext
from src.midi.scales import ScaleType, get_scale_display_name, NOTE_NAMES, SCALE_NAMES
from src.gui.components.layout_utils import LayoutSpacing
import customtkinter as ctk

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

        scale_name = ""
        if self.context.processor.scale_enabled:
            scale_name = get_scale_display_name(
                self.context.processor.scale_root, self.context.processor.scale_type
            )

        btn_text = f"SC\n{scale_name}" if scale_name else "SC"

        btn = self.context.gui.button_panel.get_button("SC")
        if btn:
            btn.configure(text=btn_text)
            theme = self.context.gui.theme
            if self.context.processor.scale_enabled:
                active_color = theme.get_color("state_active")
                hover_color = theme.get_color("control_hover")
                btn.configure(
                    fg_color=(active_color, active_color),
                    hover_color=(hover_color, hover_color),
                )
            else:
                disabled_base = theme.get_color("button_inactive")
                pressed_color = theme.get_color("control_pressed")
                btn.configure(
                    fg_color=(disabled_base, disabled_base),
                    hover_color=(pressed_color, pressed_color),
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

            theme = self.context.gui.theme

            # Root selection frame
            root_frame = ctk.CTkFrame(frame, fg_color=theme.get_color("frame_bg"))
            root_frame.pack(
                fill="x",
                padx=LayoutSpacing.CONTAINER_PADX,
                pady=(
                    theme.get_padding("popup_control"),
                    theme.get_padding("popup_control_small"),
                ),
            )

            root_label = ctk.CTkLabel(
                root_frame,
                text="Root Note:",
                font=("Courier New", 14),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            root_label.configure(width=theme.get_label_width())
            root_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            root_var = ctk.StringVar(
                value=NOTE_NAMES[self.context.processor.scale_root]
            )
            root_menu = ctk.CTkOptionMenu(
                root_frame,
                values=NOTE_NAMES,
                variable=root_var,
                command=lambda v: apply_selection(root_var, type_var),
                width=150,
                height=50,
                corner_radius=0,
                fg_color=theme.get_color("control_bg"),
                button_color=theme.get_color("control_bg"),
                button_hover_color=theme.get_color("control_hover"),
                text_color=theme.get_color("button_text"),
                dropdown_fg_color=theme.get_color("control_bg"),
                dropdown_hover_color=theme.get_color("control_hover"),
                dropdown_text_color=theme.get_color("button_text"),
                font=("Courier New", 20),
                dropdown_font=("Courier New", 30),
            )
            root_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            # Scale type selection frame
            type_frame = ctk.CTkFrame(frame, fg_color=theme.get_color("frame_bg"))
            type_frame.pack(
                fill="x",
                padx=LayoutSpacing.CONTAINER_PADX,
                pady=(
                    theme.get_padding("popup_control_small"),
                    theme.get_padding("popup_control"),
                ),
            )

            type_label = ctk.CTkLabel(
                type_frame,
                text="Scale Type:",
                font=("Courier New", 14),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            type_label.configure(width=theme.get_label_width())
            type_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            scale_type_names = [SCALE_NAMES[st] for st in ScaleType]
            current_type_name = SCALE_NAMES[self.context.processor.scale_type]
            type_var = ctk.StringVar(value=current_type_name)
            type_menu = ctk.CTkOptionMenu(
                type_frame,
                values=scale_type_names,
                variable=type_var,
                command=lambda v: apply_selection(root_var, type_var),
                width=150,
                height=50,
                corner_radius=0,
                fg_color=theme.get_color("control_bg"),
                button_color=theme.get_color("control_bg"),
                button_hover_color=theme.get_color("control_hover"),
                text_color=theme.get_color("button_text"),
                dropdown_fg_color=theme.get_color("control_bg"),
                dropdown_hover_color=theme.get_color("control_hover"),
                dropdown_text_color=theme.get_color("button_text"),
                font=("Courier New", 20),
                dropdown_font=("Courier New", 30),
            )
            type_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            def update_font_sizes():
                try:
                    if not frame.winfo_exists():
                        return
                    font_size = theme.get_font_size("label_small")

                    root_label.configure(
                        font=("Courier New", font_size),
                        width=theme.get_label_width(),
                        anchor="e",
                        text_color=theme.get_color("text_black"),
                    )
                    root_menu.configure(font=("Courier New", font_size))
                    type_label.configure(
                        font=("Courier New", font_size),
                        width=theme.get_label_width(),
                        anchor="e",
                        text_color=theme.get_color("text_black"),
                    )
                    type_menu.configure(font=("Courier New", font_size))
                except Exception:
                    pass  # Widget might be destroyed

            frame.update_font_sizes = update_font_sizes
            update_font_sizes()

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Scale Selection", build_scale_content
            )
            popup.show()
