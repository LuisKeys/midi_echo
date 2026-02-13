"""Velocity tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget, SquareDropdown


def _build_velocity_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Velocity tab with mode and fixed velocity."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    mode_frame.pack(fill="x", padx=10, pady=10)

    mode_label = ctk.CTkLabel(mode_frame, text="Velocity Mode:", font=("Arial", 14))
    mode_label.pack(side="left", padx=10)

    vel_mode_var = ctk.StringVar(value=state.velocity.mode)
    vel_mode_menu = SquareDropdown(
        mode_frame,
        values=["ORIGINAL", "FIXED", "RAMP_UP", "RAMP_DOWN", "RANDOM", "ACCENT_FIRST"],
        variable=vel_mode_var,
        command=lambda v: setattr(state.velocity, "mode", v),
        width=150,
        height=50,
    )
    vel_mode_menu.pack(side="left", padx=10)

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
    )
    fixed_widget.pack(fill="x", padx=10, pady=(0, 10))
    pm.register_element("content_elements", fixed_widget)

    def update_font_sizes():
        font_size = theme.get_font_size("label_small")

        mode_label.configure(font=("Arial", font_size))
        vel_mode_menu.configure(font=("Arial", font_size))

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
