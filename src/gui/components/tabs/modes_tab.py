"""Modes tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget


def _build_modes_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Modes tab with mode, octave, direction, reset."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    mode_frame.pack(fill="x", padx=10, pady=10)

    mode_label = ctk.CTkLabel(mode_frame, text="Mode:", font=("Arial", 14))
    mode_label.pack(side="left", padx=10)

    mode_var = ctk.StringVar(value=state.mode)
    mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["UP", "DOWN", "UPDOWN", "RANDOM", "CHORD"],
        variable=mode_var,
        command=lambda v: setattr(state, "mode", v),
        width=150,
        height=50,
    )
    mode_menu.pack(side="left", padx=10)

    # Octave
    oct_widget = IncrementDecrementWidget(
        parent,
        "Octave Range:",
        1,
        4,
        state.octave,
        callback=lambda v: setattr(state, "octave", v),
        config=config,
        theme=theme,
    )
    oct_widget.pack(fill="x", padx=10, pady=(0, 10))
    pm.register_element("content_elements", oct_widget)

    # Octave direction
    dir_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    dir_frame.pack(fill="x", padx=10, pady=(0, 10))

    dir_label = ctk.CTkLabel(dir_frame, text="Octave Direction:", font=("Arial", 14))
    dir_label.pack(side="left", padx=10)

    dir_var = ctk.StringVar(value=state.octave_dir)
    dir_menu = ctk.CTkOptionMenu(
        dir_frame,
        values=["UP", "DOWN", "BOTH"],
        variable=dir_var,
        command=lambda v: setattr(state, "octave_dir", v),
        width=150,
        height=50,
    )
    dir_menu.pack(side="left", padx=10)

    # Reset mode
    reset_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    reset_frame.pack(fill="x", padx=10, pady=(0, 10))

    reset_label = ctk.CTkLabel(reset_frame, text="Reset Mode:", font=("Arial", 14))
    reset_label.pack(side="left", padx=10)

    reset_var = ctk.StringVar(value=state.reset_mode)
    reset_menu = ctk.CTkOptionMenu(
        reset_frame,
        values=["NEW_CHORD", "FIRST_NOTE", "FREE_RUN"],
        variable=reset_var,
        command=lambda v: setattr(state, "reset_mode", v),
        width=150,
        height=50,
    )
    reset_menu.pack(side="left", padx=10)

    def update_font_sizes():
        font_size = theme.get_font_size("label_small")

        mode_label.configure(font=("Arial", font_size))
        mode_menu.configure(font=("Arial", font_size))
        dir_label.configure(font=("Arial", font_size))
        dir_menu.configure(font=("Arial", font_size))
        reset_label.configure(font=("Arial", font_size))
        reset_menu.configure(font=("Arial", font_size))

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
