"""Pattern tab for the ARP control interface."""

import customtkinter as ctk
import logging


def _build_pattern_tab(parent: ctk.CTkFrame, state, context) -> None:
    """Build the Pattern tab with step buttons, accents, and held notes."""
    theme = context.gui.theme
    # Validation
    if not state or not hasattr(state, "pattern") or not state.pattern:
        logging.warning("Invalid state for pattern tab, using defaults")
        # Could set defaults, but for now, just proceed assuming it's ok
    if not isinstance(state.pattern.mask, list) or len(state.pattern.mask) != 12:
        logging.warning("Invalid pattern mask, resetting to all True")
        state.pattern.mask = [True] * 12
    if not isinstance(state.pattern.accents, list) or len(state.pattern.accents) != 12:
        logging.warning("Invalid pattern accents, resetting to all False")
        state.pattern.accents = [False] * 12

    # Pattern grid
    grid_frame = ctk.CTkFrame(parent, fg_color="#1F1F1F")
    grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

    buttons = []
    accent_buttons = []

    def update_font_sizes():
        """Update font sizes of buttons (dimensions handled by grid weights)."""
        font_size = theme.get_font_size("label_small")

        for btn in buttons:
            btn.configure(font=("Arial", font_size))
        for btn in accent_buttons:
            btn.configure(font=("Arial", font_size))

        held_label.configure(font=("Arial", font_size))

    parent.update_font_sizes = update_font_sizes
    if hasattr(context.gui, "popup_manager"):
        context.gui.popup_manager.register_element("content_elements", parent)

    def refresh_ui():
        """Refresh UI elements to match current state."""
        for i, btn in enumerate(buttons):
            btn.configure(
                fg_color="#00FF00" if state.pattern.mask[i] else ("#333333", "#333333")
            )
        for i, btn in enumerate(accent_buttons):
            btn.configure(
                fg_color=(
                    "#FFFF00" if state.pattern.accents[i] else ("#555555", "#555555")
                )
            )
        # Update held notes
        held_text = (
            ", ".join(str(n) for n in sorted(state.held_notes))
            if state.held_notes
            else "None"
        )
        held_label.configure(text=f"Held Notes: {held_text}")

    def make_toggle(i: int):
        def _toggle():
            state.pattern.mask[i] = not state.pattern.mask[i]
            # Update pattern notes when mask changes
            if context.processor:
                context.processor._update_arp_pattern()
            refresh_ui()

        return _toggle

    def make_accent_toggle(i: int):
        def _toggle():
            state.pattern.accents[i] = not state.pattern.accents[i]
            refresh_ui()

        return _toggle

    # Configure grid weights so buttons fill available space
    for c in range(4):
        grid_frame.grid_columnconfigure(c, weight=1, uniform="col")
    for r in range(6):
        grid_frame.grid_rowconfigure(r, weight=1, uniform="row")

    # Step buttons
    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            text = str(idx + 1)
            fg = "#00FF00" if state.pattern.mask[idx] else ("#333333", "#333333")
            btn = ctk.CTkButton(
                grid_frame,
                text=text,
                fg_color=fg,
                corner_radius=0,
                command=make_toggle(idx),
            )
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            buttons.append(btn)

    # Accent buttons below
    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            fg = "#FFFF00" if state.pattern.accents[idx] else ("#555555", "#555555")
            btn = ctk.CTkButton(
                grid_frame,
                text="A",
                fg_color=fg,
                corner_radius=0,
                command=make_accent_toggle(idx),
            )
            btn.grid(row=3 + r, column=c, padx=2, pady=2, sticky="nsew")
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
            state.pattern.accents = [False] * 12  # Reset accents
            for note in state.chord_memory:
                semitone = note % 12
                state.pattern.mask[semitone] = True
            refresh_ui()

    # Initial refresh
    refresh_ui()
    update_font_sizes()

    # Set up periodic refresh for external state changes
    def schedule_refresh():
        try:
            if parent.winfo_exists():
                refresh_ui()
                parent.after(250, schedule_refresh)  # Refresh 4x/second
        except Exception:
            pass  # Widget destroyed, stop refreshing

    schedule_refresh()
