"""Tempo editor popup builder."""

import customtkinter as ctk
from .layout_utils import LayoutSpacing


def build_tempo_editor(parent: ctk.CTkFrame, context) -> None:
    """Build a simple tempo editor with a slider and numeric display.

    Args:
        parent: Parent frame provided by PopupMenu
        context: AppContext with access to processor and gui
    """
    theme = context.gui.theme
    pm = context.gui.popup_manager
    state = getattr(context.processor, "arp_state", None)
    if state is None:
        lbl = ctk.CTkLabel(
            parent,
            text="No arpeggiator state found.",
            text_color=theme.get_color("text_black"),
        )
        lbl.pack()
        return

    frame = ctk.CTkFrame(parent, fg_color=theme.get_color("selector_bg"))
    frame.pack(
        expand=True,
        fill="both",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=LayoutSpacing.CONTAINER_PADY,
    )

    label = ctk.CTkLabel(
        frame,
        text=f"BPM: {state.timing.bpm}",
        font=("Arial", 20),
        text_color=theme.get_color("text_black"),
    )
    label.pack(pady=(8, 12))

    def on_change(val):
        try:
            bpm = int(float(val))
            state.timing.bpm = bpm
            label.configure(text=f"BPM: {bpm}")
        except Exception:
            pass

    slider = ctk.CTkSlider(
        frame, from_=20, to=300, number_of_steps=280, command=on_change
    )
    slider.set(state.timing.bpm)
    slider.pack(fill="x", padx=12, pady=8)

    def on_close():
        try:
            context.gui.popup_manager.active_popup.close()
        except Exception:
            pass

    btn = ctk.CTkButton(frame, text="Close", command=on_close, corner_radius=0)
    btn.pack(pady=12)

    def update_font_sizes():
        font_size = theme.get_font_size("label_medium")

        label.configure(
            font=("Arial", font_size), text_color=theme.get_color("text_black")
        )
        btn.configure(font=("Arial", theme.get_font_size("label_small")))

    frame.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", frame)
    update_font_sizes()
