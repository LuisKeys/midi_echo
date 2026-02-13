"""Advanced tab for the ARP control interface."""

import customtkinter as ctk
from src.midi.arp.state_validator import ArpState


def _build_advanced_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Advanced tab with latch, enable, save/load."""
    # Latch
    latch_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    latch_frame.pack(fill="x", padx=10, pady=10)

    latch_label = ctk.CTkLabel(latch_frame, text="Latch:", font=("Arial", 14))
    latch_label.pack(side="left", padx=10)

    latch_var = ctk.StringVar(value=state.latch)
    latch_menu = ctk.CTkOptionMenu(
        latch_frame,
        values=["OFF", "ON", "HOLD"],
        variable=latch_var,
        command=lambda v: setattr(state, "latch", v),
        width=150,
        height=50,
    )
    latch_menu.pack(side="left", padx=10)

    # Enable toggle
    enable_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    enable_frame.pack(fill="x", padx=10, pady=(0, 10))

    enable_var = ctk.BooleanVar(value=state.enabled)
    enable_check = ctk.CTkCheckBox(
        enable_frame,
        text="Enabled",
        variable=enable_var,
        command=lambda: setattr(state, "enabled", enable_var.get()),
        font=("Arial", 14),
    )
    enable_check.pack(side="left", padx=10)

    # Save/Load
    preset_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    preset_frame.pack(fill="x", padx=10, pady=(0, 10))

    save_btn = ctk.CTkButton(
        preset_frame,
        text="Save Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _save_preset(state),
    )
    save_btn.pack(side="left", padx=10)

    load_btn = ctk.CTkButton(
        preset_frame,
        text="Load Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _load_preset(state),
    )
    load_btn.pack(side="left", padx=10)


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
