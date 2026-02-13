"""Timing tab for the ARP control interface."""

import customtkinter as ctk
from ..widgets import IncrementDecrementWidget, SquareDropdown


def _build_timing_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Timing tab with BPM, division, swing, gate, sync."""
    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # BPM control
    bpm_widget = IncrementDecrementWidget(
        parent,
        "BPM:",
        20,
        300,
        state.timing.bpm,
        callback=lambda v: setattr(state.timing, "bpm", v),
        config=config,
        tap_callback=lambda: context.gui.handlers["AR"].tap_tempo(),
        theme=theme,
    )
    bpm_widget.pack(fill="x", padx=10, pady=10)
    pm.register_element("content_elements", bpm_widget)

    # Store reference in handler for display updates
    if hasattr(context.gui, "handlers") and "AR" in context.gui.handlers:
        context.gui.handlers["AR"]._bpm_widget = bpm_widget

    # Division
    div_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    div_frame.pack(fill="x", padx=10, pady=(0, 10))

    div_label = ctk.CTkLabel(div_frame, text="Division:", font=("Arial", 14))
    div_label.pack(side="left", padx=10)

    div_var = ctk.StringVar(value=state.timing.division)
    div_menu = SquareDropdown(
        div_frame,
        values=["1/4", "1/8", "1/16", "1/32", "TRIPLET", "DOTTED"],
        variable=div_var,
        command=lambda v: setattr(state.timing, "division", v),
        width=150,
        height=50,
    )
    div_menu.pack(side="left", padx=10)

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
    )
    swing_widget.pack(fill="x", padx=10, pady=(0, 10))
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
    )
    gate_widget.pack(fill="x", padx=10, pady=(0, 10))
    pm.register_element("content_elements", gate_widget)

    # External sync
    sync_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    sync_frame.pack(fill="x", padx=10, pady=(0, 10))

    sync_var = ctk.BooleanVar(value=state.external_sync)
    sync_check = ctk.CTkCheckBox(
        sync_frame,
        text="External Clock Sync",
        variable=sync_var,
        command=lambda: setattr(state, "external_sync", sync_var.get()),
        font=("Arial", 14),
    )
    sync_check.pack(side="left", padx=10)

    def update_font_sizes():
        font_size = theme.get_font_size("label_small")

        div_label.configure(font=("Arial", font_size))
        div_menu.configure(font=("Arial", font_size))
        sync_check.configure(font=("Arial", font_size))

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()
