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

            theme = self.context.gui.theme

            # Root selection frame
            root_frame = ctk.CTkFrame(frame, fg_color=theme.get_color("frame_bg"))
            root_frame.pack(
                fill="x",
                padx=LayoutSpacing.CONTAINER_PADX,
                pady=(20, 10),
            )

            root_label = ctk.CTkLabel(
                root_frame,
                text="Root Note:",
                font=("Arial", 14),
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
                fg_color="#B0BEC5",
                button_color="#B0BEC5",
                button_hover_color="#B0BEC5",
                text_color=theme.get_color("button_text"),
                font=("Arial", 20),
                dropdown_font=("Arial", 30),
            )
            root_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            # Scale type selection frame
            type_frame = ctk.CTkFrame(frame, fg_color=theme.get_color("frame_bg"))
            type_frame.pack(
                fill="x",
                padx=LayoutSpacing.CONTAINER_PADX,
                pady=(10, 20),
            )

            type_label = ctk.CTkLabel(
                type_frame,
                text="Scale Type:",
                font=("Arial", 14),
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
                fg_color="#B0BEC5",
                button_color="#B0BEC5",
                button_hover_color="#B0BEC5",
                text_color=theme.get_color("button_text"),
                font=("Arial", 20),
                dropdown_font=("Arial", 30),
            )
            type_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

            def update_font_sizes():
                try:
                    if not frame.winfo_exists():
                        return
                    font_size = theme.get_font_size("label_small")

                    root_label.configure(
                        font=("Arial", font_size),
                        width=theme.get_label_width(),
                        anchor="e",
                        text_color=theme.get_color("text_black"),
                    )
                    root_menu.configure(font=("Arial", font_size))
                    type_label.configure(
                        font=("Arial", font_size),
                        width=theme.get_label_width(),
                        anchor="e",
                        text_color=theme.get_color("text_black"),
                    )
                    type_menu.configure(font=("Arial", font_size))
                except Exception:
                    pass  # Widget might be destroyed

            frame.update_font_sizes = update_font_sizes
            update_font_sizes()

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Scale Selection", build_scale_content
            )
            popup.show()
