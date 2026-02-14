"""Modes tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget
from ..layout_utils import LayoutSpacing


def _build_modes_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Modes tab with mode, octave, direction, reset."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    mode_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=theme.get_padding("popup_control"),
    )

    mode_label = ctk.CTkLabel(
        mode_frame,
        text="Mode:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    mode_label.configure(width=theme.get_label_width())
    mode_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    mode_var = ctk.StringVar(value=state.mode)
    mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["UP", "DOWN", "UPDOWN", "RANDOM", "CHORD"],
        variable=mode_var,
        command=lambda v: setattr(state, "mode", v),
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
    mode_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

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
        label_width=theme.get_label_width(),
    )
    oct_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", oct_widget)

    # Octave direction
    dir_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    dir_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    dir_label = ctk.CTkLabel(
        dir_frame,
        text="Octave Direction:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    dir_label.configure(width=theme.get_label_width())
    dir_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    dir_var = ctk.StringVar(value=state.octave_dir)
    dir_menu = ctk.CTkOptionMenu(
        dir_frame,
        values=["UP", "DOWN", "BOTH"],
        variable=dir_var,
        command=lambda v: setattr(state, "octave_dir", v),
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
    dir_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    # Reset mode
    reset_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    reset_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    reset_label = ctk.CTkLabel(
        reset_frame,
        text="Reset Mode:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    reset_label.configure(width=theme.get_label_width())
    reset_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    reset_var = ctk.StringVar(value=state.reset_mode)
    reset_menu = ctk.CTkOptionMenu(
        reset_frame,
        values=["NEW_CHORD", "FIRST_NOTE", "FREE_RUN"],
        variable=reset_var,
        command=lambda v: setattr(state, "reset_mode", v),
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
    reset_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

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
            mode_menu.configure(font=("Arial", font_size))
            dir_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            dir_menu.configure(font=("Arial", font_size))
            reset_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            reset_menu.configure(font=("Arial", font_size))
        except Exception:
            pass  # Widget might be destroyed

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
