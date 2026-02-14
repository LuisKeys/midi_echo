"""Advanced tab for the ARP control interface."""

import customtkinter as ctk
from src.midi.arp.state_validator import ArpState
from ..layout_utils import LayoutSpacing


def _build_advanced_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Advanced tab with latch, enable, save/load."""
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Latch
    latch_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    latch_frame.pack(
        fill="x", padx=LayoutSpacing.CONTAINER_PADX, pady=LayoutSpacing.CONTAINER_PADY
    )

    latch_label = ctk.CTkLabel(
        latch_frame,
        text="Latch:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    latch_label.configure(width=theme.get_label_width())
    latch_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    latch_var = ctk.StringVar(value=state.latch)
    latch_menu = ctk.CTkOptionMenu(
        latch_frame,
        values=["OFF", "ON", "HOLD"],
        variable=latch_var,
        command=lambda v: setattr(state, "latch", v),
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
    latch_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    # Enable toggle
    enable_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    enable_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, LayoutSpacing.CONTAINER_PADY),
    )

    enable_var = ctk.BooleanVar(value=state.enabled)
    enable_check = ctk.CTkCheckBox(
        enable_frame,
        text="Enabled",
        variable=enable_var,
        command=lambda: setattr(state, "enabled", enable_var.get()),
        font=("Arial", 14),
        text_color=theme.get_color("text_black"),
    )
    enable_check.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    # Save/Load
    preset_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    preset_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, LayoutSpacing.CONTAINER_PADY),
    )

    save_btn = ctk.CTkButton(
        preset_frame,
        text="Save Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _save_preset(state),
    )
    save_btn.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    load_btn = ctk.CTkButton(
        preset_frame,
        text="Load Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _load_preset(state),
    )
    load_btn.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    def update_font_sizes():
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            latch_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            latch_menu.configure(font=("Arial", font_size))
            enable_check.configure(
                font=("Arial", font_size), text_color=theme.get_color("text_black")
            )
            save_btn.configure(font=("Arial", font_size))
            load_btn.configure(font=("Arial", font_size))
        except Exception:
            pass  # Widget might be destroyed

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()


def _save_preset(state):
    """Save current state to a preset file."""
    try:
        state.save("arp_preset.json")
    except Exception as e:
        print(f"Save failed: {e}")


def _load_preset(state):
    """Load state from a preset file."""
    try:
        loaded = ArpState.load("arp_preset.json")
        # Copy attributes
        for attr in vars(loaded):
            if hasattr(state, attr):
                setattr(state, attr, getattr(loaded, attr))
    except Exception as e:
        print(f"Load failed: {e}")
