"""Comprehensive ARP control popup with tabbed interface."""

from typing import Callable
import customtkinter as ctk
from src.midi.arp.state_validator import ArpState


def build_pattern_editor(parent: ctk.CTkFrame, context) -> None:
    """Build a comprehensive ARP control interface inside the given parent frame.

    Uses tabs for organization: Pattern, Timing, Modes, Velocity, Advanced.
    """
    state = getattr(context.processor, "arp_state", None)
    if state is None:
        lbl = ctk.CTkLabel(parent, text="No arpeggiator state found.")
        lbl.pack()
        return

    # Main tabview
    tabview = ctk.CTkTabview(parent, width=650, height=500)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)

    # Pattern Tab
    tabview.add("Pattern")
    _build_pattern_tab(tabview.tab("Pattern"), state, context)

    # Timing Tab
    tabview.add("Timing")
    _build_timing_tab(tabview.tab("Timing"), state, context)

    # Modes Tab
    tabview.add("Modes")
    _build_modes_tab(tabview.tab("Modes"), state)

    # Velocity Tab
    tabview.add("Velocity")
    _build_velocity_tab(tabview.tab("Velocity"), state)

    # Advanced Tab
    tabview.add("Advanced")
    _build_advanced_tab(tabview.tab("Advanced"), state, context)


def _build_pattern_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Pattern tab with step buttons, accents, and held notes."""
    # Pattern grid
    grid_frame = ctk.CTkFrame(parent, fg_color="#1F1F1F")
    grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

    buttons = []
    accent_buttons = []

    def make_toggle(i: int):
        def _toggle():
            state.pattern.mask[i] = not state.pattern.mask[i]
            btn = buttons[i]
            btn.configure(
                fg_color="#00FF00" if state.pattern.mask[i] else ("#333333", "#333333")
            )

        return _toggle

    def make_accent_toggle(i: int):
        def _toggle():
            state.pattern.accents[i] = not state.pattern.accents[i]
            btn = accent_buttons[i]
            btn.configure(
                fg_color=(
                    "#FFFF00" if state.pattern.accents[i] else ("#555555", "#555555")
                )
            )

        return _toggle

    # Step buttons
    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            text = str(idx + 1)
            fg = "#00FF00" if state.pattern.mask[idx] else ("#333333", "#333333")
            btn = ctk.CTkButton(
                grid_frame,
                text=text,
                width=60,
                height=50,
                fg_color=fg,
                command=make_toggle(idx),
            )
            btn.grid(row=r, column=c, padx=4, pady=4)
            buttons.append(btn)

    # Accent buttons below
    for c in range(4):
        idx = c
        fg = "#FFFF00" if state.pattern.accents[idx] else ("#555555", "#555555")
        btn = ctk.CTkButton(
            grid_frame,
            text="A",
            width=60,
            height=30,
            fg_color=fg,
            command=make_accent_toggle(idx),
        )
        btn.grid(row=3, column=c, padx=4, pady=2)
        accent_buttons.append(btn)

    # Held notes display
    held_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    held_frame.pack(fill="x", padx=10, pady=(0, 10))

    held_text = (
        ", ".join(str(n) for n in sorted(state.held_notes))
        if state.held_notes
        else "None"
    )
    held_label = ctk.CTkLabel(held_frame, text=f"Held Notes: {held_text}")
    held_label.pack(side="left", padx=10)

    # Chord memory recall
    def recall_chord():
        if state.chord_memory:
            state.pattern.mask = [False] * 12
            for note in state.chord_memory:
                semitone = note % 12
                state.pattern.mask[semitone] = True
            # Update buttons
            for i, btn in enumerate(buttons):
                btn.configure(
                    fg_color=(
                        "#00FF00" if state.pattern.mask[i] else ("#333333", "#333333")
                    )
                )

    recall_btn = ctk.CTkButton(held_frame, text="Recall Chord", command=recall_chord)
    recall_btn.pack(side="right", padx=10)


def _build_timing_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Timing tab with BPM, division, swing, gate, sync."""
    # BPM control
    bpm_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    bpm_frame.pack(fill="x", padx=10, pady=10)

    bpm_label = ctk.CTkLabel(bpm_frame, text="BPM:")
    bpm_label.pack(side="left", padx=10)

    bpm_slider = ctk.CTkSlider(
        bpm_frame,
        from_=20,
        to=300,
        number_of_steps=280,
        command=lambda v: setattr(state.timing, "bpm", int(v)),
    )
    bpm_slider.set(state.timing.bpm)
    bpm_slider.pack(side="left", fill="x", expand=True, padx=10)

    bpm_value = ctk.CTkLabel(bpm_frame, text=str(state.timing.bpm))
    bpm_value.pack(side="left", padx=10)

    # Update value label
    def update_bpm_label(v):
        bpm_value.configure(text=str(int(v)))
        setattr(state.timing, "bpm", int(v))

    bpm_slider.configure(command=update_bpm_label)

    # Tap button
    tap_btn = ctk.CTkButton(
        bpm_frame, text="Tap", command=lambda: context.gui.arp_handler.tap_tempo()
    )
    tap_btn.pack(side="right", padx=10)

    # Division
    div_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    div_frame.pack(fill="x", padx=10, pady=(0, 10))

    div_label = ctk.CTkLabel(div_frame, text="Division:")
    div_label.pack(side="left", padx=10)

    div_var = ctk.StringVar(value=state.timing.division)
    div_menu = ctk.CTkOptionMenu(
        div_frame,
        values=["1/4", "1/8", "1/16", "1/32", "TRIPLET", "DOTTED"],
        variable=div_var,
        command=lambda v: setattr(state.timing, "division", v),
    )
    div_menu.pack(side="left", padx=10)

    # Swing
    swing_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    swing_frame.pack(fill="x", padx=10, pady=(0, 10))

    swing_label = ctk.CTkLabel(swing_frame, text="Swing:")
    swing_label.pack(side="left", padx=10)

    swing_slider = ctk.CTkSlider(
        swing_frame,
        from_=0,
        to=75,
        number_of_steps=75,
        command=lambda v: setattr(state.timing, "swing", int(v)),
    )
    swing_slider.set(state.timing.swing)
    swing_slider.pack(side="left", fill="x", expand=True, padx=10)

    swing_value = ctk.CTkLabel(swing_frame, text=str(state.timing.swing))
    swing_value.pack(side="left", padx=10)

    def update_swing_label(v):
        swing_value.configure(text=str(int(v)))
        setattr(state.timing, "swing", int(v))

    swing_slider.configure(command=update_swing_label)

    # Gate
    gate_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    gate_frame.pack(fill="x", padx=10, pady=(0, 10))

    gate_label = ctk.CTkLabel(gate_frame, text="Gate %:")
    gate_label.pack(side="left", padx=10)

    gate_slider = ctk.CTkSlider(
        gate_frame,
        from_=0,
        to=100,
        number_of_steps=100,
        command=lambda v: setattr(state, "gate_pct", int(v)),
    )
    gate_slider.set(state.gate_pct)
    gate_slider.pack(side="left", fill="x", expand=True, padx=10)

    gate_value = ctk.CTkLabel(gate_frame, text=str(state.gate_pct))
    gate_value.pack(side="left", padx=10)

    def update_gate_label(v):
        gate_value.configure(text=str(int(v)))
        setattr(state, "gate_pct", int(v))

    gate_slider.configure(command=update_gate_label)

    # External sync
    sync_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    sync_frame.pack(fill="x", padx=10, pady=(0, 10))

    sync_var = ctk.BooleanVar(value=state.external_sync)
    sync_check = ctk.CTkCheckBox(
        sync_frame,
        text="External Clock Sync",
        variable=sync_var,
        command=lambda: setattr(state, "external_sync", sync_var.get()),
    )
    sync_check.pack(side="left", padx=10)


def _build_modes_tab(parent: ctk.CTkFrame, state) -> None:
    """Build the Modes tab with mode, octave, direction, reset."""
    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    mode_frame.pack(fill="x", padx=10, pady=10)

    mode_label = ctk.CTkLabel(mode_frame, text="Mode:")
    mode_label.pack(side="left", padx=10)

    mode_var = ctk.StringVar(value=state.mode)
    mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["UP", "DOWN", "UPDOWN", "RANDOM", "CHORD"],
        variable=mode_var,
        command=lambda v: setattr(state, "mode", v),
    )
    mode_menu.pack(side="left", padx=10)

    # Octave
    oct_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    oct_frame.pack(fill="x", padx=10, pady=(0, 10))

    oct_label = ctk.CTkLabel(oct_frame, text="Octave Range:")
    oct_label.pack(side="left", padx=10)

    oct_var = ctk.IntVar(value=state.octave)
    oct_slider = ctk.CTkSlider(
        oct_frame,
        from_=1,
        to=4,
        number_of_steps=3,
        variable=oct_var,
        command=lambda v: setattr(state, "octave", int(v)),
    )
    oct_slider.pack(side="left", fill="x", expand=True, padx=10)

    oct_value = ctk.CTkLabel(oct_frame, text=str(state.octave))
    oct_value.pack(side="left", padx=10)

    def update_oct_label(v):
        oct_value.configure(text=str(int(v)))
        setattr(state, "octave", int(v))

    oct_slider.configure(command=update_oct_label)

    # Octave direction
    dir_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    dir_frame.pack(fill="x", padx=10, pady=(0, 10))

    dir_label = ctk.CTkLabel(dir_frame, text="Octave Direction:")
    dir_label.pack(side="left", padx=10)

    dir_var = ctk.StringVar(value=state.octave_dir)
    dir_menu = ctk.CTkOptionMenu(
        dir_frame,
        values=["UP", "DOWN", "BOTH"],
        variable=dir_var,
        command=lambda v: setattr(state, "octave_dir", v),
    )
    dir_menu.pack(side="left", padx=10)

    # Reset mode
    reset_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    reset_frame.pack(fill="x", padx=10, pady=(0, 10))

    reset_label = ctk.CTkLabel(reset_frame, text="Reset Mode:")
    reset_label.pack(side="left", padx=10)

    reset_var = ctk.StringVar(value=state.reset_mode)
    reset_menu = ctk.CTkOptionMenu(
        reset_frame,
        values=["NEW_CHORD", "FIRST_NOTE", "FREE_RUN"],
        variable=reset_var,
        command=lambda v: setattr(state, "reset_mode", v),
    )
    reset_menu.pack(side="left", padx=10)


def _build_velocity_tab(parent: ctk.CTkFrame, state) -> None:
    """Build the Velocity tab with mode and fixed velocity."""
    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    mode_frame.pack(fill="x", padx=10, pady=10)

    mode_label = ctk.CTkLabel(mode_frame, text="Velocity Mode:")
    mode_label.pack(side="left", padx=10)

    vel_mode_var = ctk.StringVar(value=state.velocity.mode)
    vel_mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["ORIGINAL", "FIXED", "RAMP_UP", "RAMP_DOWN", "RANDOM", "ACCENT_FIRST"],
        variable=vel_mode_var,
        command=lambda v: setattr(state.velocity, "mode", v),
    )
    vel_mode_menu.pack(side="left", padx=10)

    # Fixed velocity
    fixed_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    fixed_frame.pack(fill="x", padx=10, pady=(0, 10))

    fixed_label = ctk.CTkLabel(fixed_frame, text="Fixed Velocity:")
    fixed_label.pack(side="left", padx=10)

    fixed_slider = ctk.CTkSlider(
        fixed_frame,
        from_=0,
        to=127,
        number_of_steps=127,
        command=lambda v: setattr(state.velocity, "fixed_velocity", int(v)),
    )
    fixed_slider.set(state.velocity.fixed_velocity)
    fixed_slider.pack(side="left", fill="x", expand=True, padx=10)

    fixed_value = ctk.CTkLabel(fixed_frame, text=str(state.velocity.fixed_velocity))
    fixed_value.pack(side="left", padx=10)

    def update_fixed_label(v):
        fixed_value.configure(text=str(int(v)))
        setattr(state.velocity, "fixed_velocity", int(v))

    fixed_slider.configure(command=update_fixed_label)


def _build_advanced_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Advanced tab with latch, enable, save/load."""
    # Latch
    latch_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    latch_frame.pack(fill="x", padx=10, pady=10)

    latch_label = ctk.CTkLabel(latch_frame, text="Latch:")
    latch_label.pack(side="left", padx=10)

    latch_var = ctk.StringVar(value=state.latch)
    latch_menu = ctk.CTkOptionMenu(
        latch_frame,
        values=["OFF", "ON", "HOLD"],
        variable=latch_var,
        command=lambda v: setattr(state, "latch", v),
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
    )
    enable_check.pack(side="left", padx=10)

    # Save/Load
    preset_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    preset_frame.pack(fill="x", padx=10, pady=(0, 10))

    save_btn = ctk.CTkButton(
        preset_frame, text="Save Preset", command=lambda: _save_preset(state)
    )
    save_btn.pack(side="left", padx=10)

    load_btn = ctk.CTkButton(
        preset_frame, text="Load Preset", command=lambda: _load_preset(state)
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
