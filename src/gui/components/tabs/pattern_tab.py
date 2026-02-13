"""Pattern tab for the ARP control interface."""

import customtkinter as ctk


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
