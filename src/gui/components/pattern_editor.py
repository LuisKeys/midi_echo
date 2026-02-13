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
    tabview = ctk.CTkTabview(parent, width=750, height=550)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)

    # Pattern Tab
    tabview.add("Pattern")
    _build_pattern_tab(tabview.tab("Pattern"), state, context)

    # Timing Tab
    tabview.add("Timing")
    _build_timing_tab(tabview.tab("Timing"), state, context)

    # Modes Tab
    tabview.add("Modes")
    _build_modes_tab(tabview.tab("Modes"), state, context)

    # Velocity Tab
    tabview.add("Velocity")
    _build_velocity_tab(tabview.tab("Velocity"), state, context)

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
                width=80,
                height=60,
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
            width=80,
            height=40,
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
    held_label = ctk.CTkLabel(
        held_frame, text=f"Held Notes: {held_text}", font=("Arial", 14)
    )
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

    recall_btn = ctk.CTkButton(
        held_frame, text="Recall Chord", width=120, height=50, command=recall_chord
    )
    recall_btn.pack(side="right", padx=10)


def _build_timing_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Timing tab with BPM, division, swing, gate, sync."""
    config = context.app_config
    # BPM control
    bpm_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    bpm_frame.pack(fill="x", padx=10, pady=10)

    bpm_label = ctk.CTkLabel(bpm_frame, text="BPM:", font=("Arial", 14))
    bpm_label.pack(side="left", padx=10)

    def bpm_decr():
        new_val = max(20, state.timing.bpm - 1)
        state.timing.bpm = new_val
        bpm_value.configure(text=str(new_val))

    def bpm_incr():
        new_val = min(300, state.timing.bpm + 1)
        state.timing.bpm = new_val
        bpm_value.configure(text=str(new_val))

    bpm_minus_holding = False
    bpm_minus_timer = None

    def start_bpm_minus():
        nonlocal bpm_minus_holding, bpm_minus_timer
        bpm_minus_holding = True
        bpm_decr()
        bpm_minus_timer = parent.after(500, start_bpm_minus_repeat)

    def start_bpm_minus_repeat():
        nonlocal bpm_minus_holding, bpm_minus_timer
        if bpm_minus_holding:
            bpm_minus_timer = parent.after(config.hold_increment_rate, repeat_bpm_minus)

    def repeat_bpm_minus():
        nonlocal bpm_minus_holding, bpm_minus_timer
        if bpm_minus_holding:
            bpm_decr()
            bpm_minus_timer = parent.after(config.hold_increment_rate, repeat_bpm_minus)

    def stop_bpm_minus():
        nonlocal bpm_minus_holding, bpm_minus_timer
        bpm_minus_holding = False
        if bpm_minus_timer:
            parent.after_cancel(bpm_minus_timer)
            bpm_minus_timer = None

    bpm_minus = ctk.CTkButton(bpm_frame, text="-", width=80, height=50)
    bpm_minus.bind("<ButtonPress-1>", lambda e: start_bpm_minus())
    bpm_minus.bind("<ButtonRelease-1>", lambda e: stop_bpm_minus())
    bpm_minus.pack(side="left", padx=5)

    bpm_value = ctk.CTkLabel(bpm_frame, text=str(state.timing.bpm), font=("Arial", 16))
    bpm_value.pack(side="left", padx=10)

    bpm_plus_holding = False
    bpm_plus_timer = None

    def start_bpm_plus():
        nonlocal bpm_plus_holding, bpm_plus_timer
        bpm_plus_holding = True
        bpm_incr()
        bpm_plus_timer = parent.after(500, start_bpm_plus_repeat)

    def start_bpm_plus_repeat():
        nonlocal bpm_plus_holding, bpm_plus_timer
        if bpm_plus_holding:
            bpm_plus_timer = parent.after(config.hold_increment_rate, repeat_bpm_plus)

    def repeat_bpm_plus():
        nonlocal bpm_plus_holding, bpm_plus_timer
        if bpm_plus_holding:
            bpm_incr()
            bpm_plus_timer = parent.after(config.hold_increment_rate, repeat_bpm_plus)

    def stop_bpm_plus():
        nonlocal bpm_plus_holding, bpm_plus_timer
        bpm_plus_holding = False
        if bpm_plus_timer:
            parent.after_cancel(bpm_plus_timer)
            bpm_plus_timer = None

    bpm_plus = ctk.CTkButton(bpm_frame, text="+", width=80, height=50)
    bpm_plus.bind("<ButtonPress-1>", lambda e: start_bpm_plus())
    bpm_plus.bind("<ButtonRelease-1>", lambda e: stop_bpm_plus())
    bpm_plus.pack(side="left", padx=5)

    # Tap button
    tap_btn = ctk.CTkButton(
        bpm_frame,
        text="Tap",
        width=80,
        height=50,
        command=lambda: context.gui.arp_handler.tap_tempo(),
    )
    tap_btn.pack(side="right", padx=10)

    # Division
    div_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    div_frame.pack(fill="x", padx=10, pady=(0, 10))

    div_label = ctk.CTkLabel(div_frame, text="Division:", font=("Arial", 14))
    div_label.pack(side="left", padx=10)

    div_var = ctk.StringVar(value=state.timing.division)
    div_menu = ctk.CTkOptionMenu(
        div_frame,
        values=["1/4", "1/8", "1/16", "1/32", "TRIPLET", "DOTTED"],
        variable=div_var,
        command=lambda v: setattr(state.timing, "division", v),
        width=150,
        height=50,
    )
    div_menu.pack(side="left", padx=10)

    # Swing
    swing_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    swing_frame.pack(fill="x", padx=10, pady=(0, 10))

    swing_label = ctk.CTkLabel(swing_frame, text="Swing:", font=("Arial", 14))
    swing_label.pack(side="left", padx=10)

    def swing_decr():
        new_val = max(0, state.timing.swing - 1)
        state.timing.swing = new_val
        swing_value.configure(text=str(new_val))

    def swing_incr():
        new_val = min(75, state.timing.swing + 1)
        state.timing.swing = new_val
        swing_value.configure(text=str(new_val))

    swing_minus_holding = False
    swing_minus_timer = None

    def start_swing_minus():
        nonlocal swing_minus_holding, swing_minus_timer
        swing_minus_holding = True
        swing_decr()
        swing_minus_timer = parent.after(500, start_swing_minus_repeat)

    def start_swing_minus_repeat():
        nonlocal swing_minus_holding, swing_minus_timer
        if swing_minus_holding:
            swing_minus_timer = parent.after(
                config.hold_increment_rate, repeat_swing_minus
            )

    def repeat_swing_minus():
        nonlocal swing_minus_holding, swing_minus_timer
        if swing_minus_holding:
            swing_decr()
            swing_minus_timer = parent.after(
                config.hold_increment_rate, repeat_swing_minus
            )

    def stop_swing_minus():
        nonlocal swing_minus_holding, swing_minus_timer
        swing_minus_holding = False
        if swing_minus_timer:
            parent.after_cancel(swing_minus_timer)
            swing_minus_timer = None

    swing_minus = ctk.CTkButton(swing_frame, text="-", width=80, height=50)
    swing_minus.bind("<ButtonPress-1>", lambda e: start_swing_minus())
    swing_minus.bind("<ButtonRelease-1>", lambda e: stop_swing_minus())
    swing_minus.pack(side="left", padx=5)

    swing_value = ctk.CTkLabel(
        swing_frame, text=str(state.timing.swing), font=("Arial", 16)
    )
    swing_value.pack(side="left", padx=10)

    swing_plus_holding = False
    swing_plus_timer = None

    def start_swing_plus():
        nonlocal swing_plus_holding, swing_plus_timer
        swing_plus_holding = True
        swing_incr()
        swing_plus_timer = parent.after(500, start_swing_plus_repeat)

    def start_swing_plus_repeat():
        nonlocal swing_plus_holding, swing_plus_timer
        if swing_plus_holding:
            swing_plus_timer = parent.after(
                config.hold_increment_rate, repeat_swing_plus
            )

    def repeat_swing_plus():
        nonlocal swing_plus_holding, swing_plus_timer
        if swing_plus_holding:
            swing_incr()
            swing_plus_timer = parent.after(
                config.hold_increment_rate, repeat_swing_plus
            )

    def stop_swing_plus():
        nonlocal swing_plus_holding, swing_plus_timer
        swing_plus_holding = False
        if swing_plus_timer:
            parent.after_cancel(swing_plus_timer)
            swing_plus_timer = None

    swing_plus = ctk.CTkButton(swing_frame, text="+", width=80, height=50)
    swing_plus.bind("<ButtonPress-1>", lambda e: start_swing_plus())
    swing_plus.bind("<ButtonRelease-1>", lambda e: stop_swing_plus())
    swing_plus.pack(side="left", padx=5)

    swing_pct = ctk.CTkLabel(swing_frame, text="%", font=("Arial", 14))
    swing_pct.pack(side="left", padx=5)

    # Gate
    gate_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    gate_frame.pack(fill="x", padx=10, pady=(0, 10))

    gate_label = ctk.CTkLabel(gate_frame, text="Gate:", font=("Arial", 14))
    gate_label.pack(side="left", padx=10)

    def gate_decr():
        new_val = max(0, state.gate_pct - 1)
        state.gate_pct = new_val
        gate_value.configure(text=str(new_val))

    def gate_incr():
        new_val = min(100, state.gate_pct + 1)
        state.gate_pct = new_val
        gate_value.configure(text=str(new_val))

    gate_minus_holding = False
    gate_minus_timer = None

    def start_gate_minus():
        nonlocal gate_minus_holding, gate_minus_timer
        gate_minus_holding = True
        gate_decr()
        gate_minus_timer = parent.after(500, start_gate_minus_repeat)

    def start_gate_minus_repeat():
        nonlocal gate_minus_holding, gate_minus_timer
        if gate_minus_holding:
            gate_minus_timer = parent.after(
                config.hold_increment_rate, repeat_gate_minus
            )

    def repeat_gate_minus():
        nonlocal gate_minus_holding, gate_minus_timer
        if gate_minus_holding:
            gate_decr()
            gate_minus_timer = parent.after(
                config.hold_increment_rate, repeat_gate_minus
            )

    def stop_gate_minus():
        nonlocal gate_minus_holding, gate_minus_timer
        gate_minus_holding = False
        if gate_minus_timer:
            parent.after_cancel(gate_minus_timer)
            gate_minus_timer = None

    gate_minus = ctk.CTkButton(gate_frame, text="-", width=80, height=50)
    gate_minus.bind("<ButtonPress-1>", lambda e: start_gate_minus())
    gate_minus.bind("<ButtonRelease-1>", lambda e: stop_gate_minus())
    gate_minus.pack(side="left", padx=5)

    gate_value = ctk.CTkLabel(gate_frame, text=str(state.gate_pct), font=("Arial", 16))
    gate_value.pack(side="left", padx=10)

    gate_plus_holding = False
    gate_plus_timer = None

    def start_gate_plus():
        nonlocal gate_plus_holding, gate_plus_timer
        gate_plus_holding = True
        gate_incr()
        gate_plus_timer = parent.after(500, start_gate_plus_repeat)

    def start_gate_plus_repeat():
        nonlocal gate_plus_holding, gate_plus_timer
        if gate_plus_holding:
            gate_plus_timer = parent.after(config.hold_increment_rate, repeat_gate_plus)

    def repeat_gate_plus():
        nonlocal gate_plus_holding, gate_plus_timer
        if gate_plus_holding:
            gate_incr()
            gate_plus_timer = parent.after(config.hold_increment_rate, repeat_gate_plus)

    def stop_gate_plus():
        nonlocal gate_plus_holding, gate_plus_timer
        gate_plus_holding = False
        if gate_plus_timer:
            parent.after_cancel(gate_plus_timer)
            gate_plus_timer = None

    gate_plus = ctk.CTkButton(gate_frame, text="+", width=80, height=50)
    gate_plus.bind("<ButtonPress-1>", lambda e: start_gate_plus())
    gate_plus.bind("<ButtonRelease-1>", lambda e: stop_gate_plus())
    gate_plus.pack(side="left", padx=5)

    gate_pct = ctk.CTkLabel(gate_frame, text="%", font=("Arial", 14))
    gate_pct.pack(side="left", padx=5)

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


def _build_modes_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Modes tab with mode, octave, direction, reset."""
    config = context.app_config
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
    oct_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    oct_frame.pack(fill="x", padx=10, pady=(0, 10))

    oct_label = ctk.CTkLabel(oct_frame, text="Octave Range:", font=("Arial", 14))
    oct_label.pack(side="left", padx=10)

    def oct_decr():
        new_val = max(1, state.octave - 1)
        state.octave = new_val
        oct_value.configure(text=str(new_val))

    def oct_incr():
        new_val = min(4, state.octave + 1)
        state.octave = new_val
        oct_value.configure(text=str(new_val))

    oct_minus_holding = False
    oct_minus_timer = None

    def start_oct_minus():
        nonlocal oct_minus_holding, oct_minus_timer
        oct_minus_holding = True
        oct_decr()
        oct_minus_timer = parent.after(500, start_oct_minus_repeat)

    def start_oct_minus_repeat():
        nonlocal oct_minus_holding, oct_minus_timer
        if oct_minus_holding:
            oct_minus_timer = parent.after(config.hold_increment_rate, repeat_oct_minus)

    def repeat_oct_minus():
        nonlocal oct_minus_holding, oct_minus_timer
        if oct_minus_holding:
            oct_decr()
            oct_minus_timer = parent.after(config.hold_increment_rate, repeat_oct_minus)

    def stop_oct_minus():
        nonlocal oct_minus_holding, oct_minus_timer
        oct_minus_holding = False
        if oct_minus_timer:
            parent.after_cancel(oct_minus_timer)
            oct_minus_timer = None

    oct_minus = ctk.CTkButton(oct_frame, text="-", width=80, height=50)
    oct_minus.bind("<ButtonPress-1>", lambda e: start_oct_minus())
    oct_minus.bind("<ButtonRelease-1>", lambda e: stop_oct_minus())
    oct_minus.pack(side="left", padx=5)

    oct_value = ctk.CTkLabel(oct_frame, text=str(state.octave), font=("Arial", 16))
    oct_value.pack(side="left", padx=10)

    oct_plus_holding = False
    oct_plus_timer = None

    def start_oct_plus():
        nonlocal oct_plus_holding, oct_plus_timer
        oct_plus_holding = True
        oct_incr()
        oct_plus_timer = parent.after(500, start_oct_plus_repeat)

    def start_oct_plus_repeat():
        nonlocal oct_plus_holding, oct_plus_timer
        if oct_plus_holding:
            oct_plus_timer = parent.after(config.hold_increment_rate, repeat_oct_plus)

    def repeat_oct_plus():
        nonlocal oct_plus_holding, oct_plus_timer
        if oct_plus_holding:
            oct_incr()
            oct_plus_timer = parent.after(config.hold_increment_rate, repeat_oct_plus)

    def stop_oct_plus():
        nonlocal oct_plus_holding, oct_plus_timer
        oct_plus_holding = False
        if oct_plus_timer:
            parent.after_cancel(oct_plus_timer)
            oct_plus_timer = None

    oct_plus = ctk.CTkButton(oct_frame, text="+", width=80, height=50)
    oct_plus.bind("<ButtonPress-1>", lambda e: start_oct_plus())
    oct_plus.bind("<ButtonRelease-1>", lambda e: stop_oct_plus())
    oct_plus.pack(side="left", padx=5)

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


def _build_velocity_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Velocity tab with mode and fixed velocity."""
    config = context.app_config
    # Mode
    mode_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    mode_frame.pack(fill="x", padx=10, pady=10)

    mode_label = ctk.CTkLabel(mode_frame, text="Velocity Mode:", font=("Arial", 14))
    mode_label.pack(side="left", padx=10)

    vel_mode_var = ctk.StringVar(value=state.velocity.mode)
    vel_mode_menu = ctk.CTkOptionMenu(
        mode_frame,
        values=["ORIGINAL", "FIXED", "RAMP_UP", "RAMP_DOWN", "RANDOM", "ACCENT_FIRST"],
        variable=vel_mode_var,
        command=lambda v: setattr(state.velocity, "mode", v),
        width=150,
        height=50,
    )
    vel_mode_menu.pack(side="left", padx=10)

    # Fixed velocity
    fixed_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    fixed_frame.pack(fill="x", padx=10, pady=(0, 10))

    fixed_label = ctk.CTkLabel(fixed_frame, text="Fixed Velocity:", font=("Arial", 14))
    fixed_label.pack(side="left", padx=10)

    def fixed_decr():
        new_val = max(0, state.velocity.fixed_velocity - 1)
        state.velocity.fixed_velocity = new_val
        fixed_value.configure(text=str(new_val))

    def fixed_incr():
        new_val = min(127, state.velocity.fixed_velocity + 1)
        state.velocity.fixed_velocity = new_val
        fixed_value.configure(text=str(new_val))

    fixed_minus_holding = False
    fixed_minus_timer = None

    def start_fixed_minus():
        nonlocal fixed_minus_holding, fixed_minus_timer
        fixed_minus_holding = True
        fixed_decr()
        fixed_minus_timer = parent.after(500, start_fixed_minus_repeat)

    def start_fixed_minus_repeat():
        nonlocal fixed_minus_holding, fixed_minus_timer
        if fixed_minus_holding:
            fixed_minus_timer = parent.after(
                config.hold_increment_rate, repeat_fixed_minus
            )

    def repeat_fixed_minus():
        nonlocal fixed_minus_holding, fixed_minus_timer
        if fixed_minus_holding:
            fixed_decr()
            fixed_minus_timer = parent.after(
                config.hold_increment_rate, repeat_fixed_minus
            )

    def stop_fixed_minus():
        nonlocal fixed_minus_holding, fixed_minus_timer
        fixed_minus_holding = False
        if fixed_minus_timer:
            parent.after_cancel(fixed_minus_timer)
            fixed_minus_timer = None

    fixed_minus = ctk.CTkButton(fixed_frame, text="-", width=80, height=50)
    fixed_minus.bind("<ButtonPress-1>", lambda e: start_fixed_minus())
    fixed_minus.bind("<ButtonRelease-1>", lambda e: stop_fixed_minus())
    fixed_minus.pack(side="left", padx=5)

    fixed_value = ctk.CTkLabel(
        fixed_frame, text=str(state.velocity.fixed_velocity), font=("Arial", 16)
    )
    fixed_value.pack(side="left", padx=10)

    fixed_plus_holding = False
    fixed_plus_timer = None

    def start_fixed_plus():
        nonlocal fixed_plus_holding, fixed_plus_timer
        fixed_plus_holding = True
        fixed_incr()
        fixed_plus_timer = parent.after(500, start_fixed_plus_repeat)

    def start_fixed_plus_repeat():
        nonlocal fixed_plus_holding, fixed_plus_timer
        if fixed_plus_holding:
            fixed_plus_timer = parent.after(
                config.hold_increment_rate, repeat_fixed_plus
            )

    def repeat_fixed_plus():
        nonlocal fixed_plus_holding, fixed_plus_timer
        if fixed_plus_holding:
            fixed_incr()
            fixed_plus_timer = parent.after(
                config.hold_increment_rate, repeat_fixed_plus
            )

    def stop_fixed_plus():
        nonlocal fixed_plus_holding, fixed_plus_timer
        fixed_plus_holding = False
        if fixed_plus_timer:
            parent.after_cancel(fixed_plus_timer)
            fixed_plus_timer = None

    fixed_plus = ctk.CTkButton(fixed_frame, text="+", width=80, height=50)
    fixed_plus.bind("<ButtonPress-1>", lambda e: start_fixed_plus())
    fixed_plus.bind("<ButtonRelease-1>", lambda e: stop_fixed_plus())
    fixed_plus.pack(side="left", padx=5)


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
        command=lambda: _save_preset(state),
    )
    save_btn.pack(side="left", padx=10)

    load_btn = ctk.CTkButton(
        preset_frame,
        text="Load Preset",
        width=120,
        height=50,
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
