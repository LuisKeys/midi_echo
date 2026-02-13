"""Tempo editor popup builder."""

import customtkinter as ctk


def build_tempo_editor(parent: ctk.CTkFrame, context) -> None:
    """Build a simple tempo editor with a slider and numeric display.

    Args:
        parent: Parent frame provided by PopupMenu
        context: AppContext with access to processor and gui
    """
    state = getattr(context.processor, "arp_state", None)
    if state is None:
        lbl = ctk.CTkLabel(parent, text="No arpeggiator state found.")
        lbl.pack()
        return

    frame = ctk.CTkFrame(parent, fg_color="#1F1F1F")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    label = ctk.CTkLabel(frame, text=f"BPM: {state.timing.bpm}", font=("Arial", 20))
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
