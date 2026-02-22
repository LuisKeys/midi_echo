"""Timing tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget
from ..layout_utils import LayoutSpacing
from ..tempo_control import create_tempo_control


def _build_timing_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Timing tab with BPM, division, swing, gate, sync."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # BPM control
    bpm_widget = create_tempo_control(
        parent,
        context,
        label_text="BPM:",
        theme=theme,
        label_width=theme.get_label_width(),
        show_tap=True,
    )
    bpm_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=theme.get_padding("popup_control"),
    )
    pm.register_element("content_elements", bpm_widget)

    # Store reference in handler for display updates
    if hasattr(context.gui, "handlers") and "AR" in context.gui.handlers:
        context.gui.handlers["AR"]._bpm_widget = bpm_widget

    # Division
    div_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    div_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    div_label = ctk.CTkLabel(
        div_frame,
        text="Division:",
        font=("Courier New", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    div_label.configure(width=theme.get_label_width())
    div_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    div_var = ctk.StringVar(value=state.timing.division)
    div_menu = ctk.CTkOptionMenu(
        div_frame,
        values=["1/4", "1/8", "1/16", "1/32", "TRIPLET", "DOTTED"],
        variable=div_var,
        command=lambda v: setattr(state.timing, "division", v),
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
    div_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    # Swing
    swing_widget = IncrementDecrementWidget(
        parent,
        "Swing:",
        0,
        75,
        state.timing.swing,
        callback=lambda v: setattr(state.timing, "swing", v),
        config=config,
        suffix="%",
        theme=theme,
        label_width=theme.get_label_width(),
    )
    swing_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", swing_widget)

    # Gate
    gate_widget = IncrementDecrementWidget(
        parent,
        "Gate:",
        0,
        100,
        state.gate_pct,
        callback=lambda v: setattr(state, "gate_pct", v),
        config=config,
        suffix="%",
        theme=theme,
        label_width=theme.get_label_width(),
    )
    gate_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", gate_widget)

    # External sync
    sync_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    sync_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    sync_var = ctk.BooleanVar(value=state.external_sync)
    sync_check = ctk.CTkCheckBox(
        sync_frame,
        text="External Clock Sync",
        variable=sync_var,
        command=lambda: setattr(state, "external_sync", sync_var.get()),
        font=("Courier New", 14),
        text_color=theme.get_color("text_black"),
    )
    sync_check.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    def update_font_sizes():
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            div_label.configure(
                font=("Courier New", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            div_menu.configure(font=("Courier New", font_size))
            sync_check.configure(
                font=("Courier New", font_size),
                text_color=theme.get_color("text_black"),
            )
        except Exception:
            pass  # Widget might be destroyed

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
