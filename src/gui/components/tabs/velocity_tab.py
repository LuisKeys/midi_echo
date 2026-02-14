"""Velocity tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget
from ..layout_utils import LayoutSpacing


def _build_velocity_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Velocity tab with mode and fixed velocity."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    mode_frame.pack(fill="x", padx=LayoutSpacing.CONTAINER_PADX, pady=20)

    mode_label = ctk.CTkLabel(
        mode_frame,
        text="Velocity Mode:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    mode_label.configure(width=theme.get_label_width())
    mode_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    vel_mode_var = ctk.StringVar(value=state.velocity.mode)
    vel_mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["ORIGINAL", "FIXED", "RAMP_UP", "RAMP_DOWN", "RANDOM", "ACCENT_FIRST"],
        variable=vel_mode_var,
        command=lambda v: setattr(state.velocity, "mode", v),
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
    vel_mode_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    # Fixed velocity
    fixed_widget = IncrementDecrementWidget(
        parent,
        "Fixed Velocity:",
        0,
        127,
        state.velocity.fixed_velocity,
        callback=lambda v: setattr(state.velocity, "fixed_velocity", v),
        config=config,
        theme=theme,
        label_width=theme.get_label_width(),
    )
    fixed_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, 20),
    )
    pm.register_element("content_elements", fixed_widget)

    def update_font_sizes():
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            mode_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            vel_mode_menu.configure(font=("Arial", font_size))
        except Exception:
            pass  # Widget might be destroyed

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
