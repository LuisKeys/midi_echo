"""Pattern tab for the ARP control interface."""

import customtkinter as ctk
import logging
from ..layout_utils import LayoutSpacing


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
    grid_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("selector_bg"))
    grid_frame.pack(
        expand=True,
        fill="both",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=LayoutSpacing.CONTAINER_PADY,
    )

    buttons = []
    accent_buttons = []

    def update_font_sizes():
        """Update font sizes of buttons (dimensions handled by grid weights)."""
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            for btn in buttons:
                btn.configure(font=("Arial", font_size))
            for btn in accent_buttons:
                btn.configure(font=("Arial", font_size))

            held_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
        except Exception:
            pass  # Widget might be destroyed

    parent.update_font_sizes = update_font_sizes
    if hasattr(context.gui, "popup_manager"):
        context.gui.popup_manager.register_element("content_elements", parent)

    def refresh_ui():
        """Refresh UI elements to match current state."""
        for i, btn in enumerate(buttons):
            btn.configure(
                fg_color=(
                    theme.get_color("preset_highlight")
                    if state.pattern.mask[i]
                    else (
                        theme.get_color("button_inactive"),
                        theme.get_color("button_inactive"),
                    )
                ),
                text_color=theme.get_color("text_black"),
            )
        for i, btn in enumerate(accent_buttons):
            btn.configure(
                fg_color=(
                    theme.get_color("preset_highlight")
                    if state.pattern.accents[i]
                    else (theme.get_color("popup_grey"), theme.get_color("popup_grey"))
                ),
                text_color=theme.get_color("text_black"),
            )
        # Update held notes
        held_text = (
            ", ".join(str(n) for n in sorted(state.held_notes))
            if state.held_notes
            else "None"
        )
        held_label.configure(
            text=f"Held Notes: {held_text}", width=theme.get_label_width(), anchor="e", text_color=theme.get_color("text_black")
        )

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
            fg = (
                theme.get_color("preset_highlight")
                if state.pattern.mask[idx]
                else (
                    theme.get_color("button_inactive"),
                    theme.get_color("button_inactive"),
                )
            )
            btn = ctk.CTkButton(
                grid_frame,
                text=text,
                fg_color=fg,
                text_color=theme.get_color("text_black"),
                corner_radius=0,
                command=make_toggle(idx),
            )
            btn.grid(
                row=r,
                column=c,
                padx=LayoutSpacing.GRID_CELL_PADX,
                pady=LayoutSpacing.GRID_CELL_PADY,
                sticky="nsew",
            )
            buttons.append(btn)

    # Accent buttons below
    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            fg = (
                theme.get_color("preset_highlight")
                if state.pattern.accents[idx]
                else (theme.get_color("popup_grey"), theme.get_color("popup_grey"))
            )
            btn = ctk.CTkButton(
                grid_frame,
                text="A",
                fg_color=fg,
                text_color=theme.get_color("text_black"),
                corner_radius=0,
                command=make_accent_toggle(idx),
            )
            btn.grid(
                row=3 + r,
                column=c,
                padx=LayoutSpacing.GRID_CELL_PADX,
                pady=LayoutSpacing.GRID_CELL_PADY,
                sticky="nsew",
            )
            accent_buttons.append(btn)

    # Held notes display
    held_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    held_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, LayoutSpacing.CONTAINER_PADY),
    )

    held_text = (
        ", ".join(str(n) for n in sorted(state.held_notes))
        if state.held_notes
        else "None"
    )
    held_label = ctk.CTkLabel(
        held_frame,
        text=f"Held Notes: {held_text}",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    held_label.configure(width=theme.get_label_width())
    held_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

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
