"""Advanced tab for the ARP control interface."""

import customtkinter as ctk
import json
from src.midi.arp.state_validator import ArpState
from ..layout_utils import LayoutSpacing


def _build_advanced_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Advanced tab with latch, enable, save/load."""
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # Latch
    latch_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    latch_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=theme.get_padding("popup_control"),
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
        pady=(0, theme.get_padding("popup_control")),
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
        pady=(0, theme.get_padding("popup_control")),
    )

    save_btn = ctk.CTkButton(
        preset_frame,
        text="Save Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _save_preset(state, context),
    )
    save_btn.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

    load_btn = ctk.CTkButton(
        preset_frame,
        text="Load Preset",
        width=120,
        height=50,
        corner_radius=0,
        command=lambda: _load_preset(state, context),
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


def _save_preset(state, context):
    """Save current state to a preset file (arp_state + sequencer)."""
    try:
        preset_data = {
            "arp_state": state.to_dict(),
        }

        # Also save sequencer state if available
        if hasattr(context, "sequencer") and context.sequencer:
            preset_data["sequencer"] = context.sequencer.to_dict()

        with open("arp_preset.json", "w", encoding="utf-8") as f:
            json.dump(preset_data, f, indent=2)
        print("Preset saved successfully")
    except Exception as e:
        print(f"Save failed: {e}")


def _load_preset(state, context):
    """Load state from a preset file (arp_state + sequencer)."""
    try:
        with open("arp_preset.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load arp_state
        if "arp_state" in data:
            loaded = ArpState.from_dict(data["arp_state"])
            # Copy attributes
            for attr in vars(loaded):
                if hasattr(state, attr):
                    setattr(state, attr, getattr(loaded, attr))

        # Load sequencer state if available
        if "sequencer" in data and hasattr(context, "sequencer") and context.sequencer:
            from src.midi.sequencer import MidiSequencer

            context.sequencer = MidiSequencer.from_dict(
                context.engine, context, data["sequencer"]
            )

        # Keep arp and sequencer tempos in sync after load
        if hasattr(context, "set_global_tempo"):
            context.set_global_tempo(state.timing.bpm)

        print("Preset loaded successfully")
    except Exception as e:
        print(f"Load failed: {e}")
