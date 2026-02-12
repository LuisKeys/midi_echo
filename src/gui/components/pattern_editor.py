"""12-step pattern editor popup content builder."""

from typing import Callable
import customtkinter as ctk


def build_pattern_editor(parent: ctk.CTkFrame, context) -> None:
    """Build a 4x3 pattern editor inside the given parent frame.

    Args:
        parent: Parent frame provided by PopupMenu
        context: AppContext with access to processor and gui
    """
    state = getattr(context.processor, "arp_state", None)
    if state is None:
        lbl = ctk.CTkLabel(parent, text="No arpeggiator state found.")
        lbl.pack()
        return

    grid_frame = ctk.CTkFrame(parent, fg_color="#1F1F1F")
    grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

    buttons = []

    def make_toggle(i: int):
        def _toggle():
            state.pattern_mask[i] = not state.pattern_mask[i]
            btn = buttons[i]
            btn.configure(
                fg_color="#00FF00" if state.pattern_mask[i] else ("#333333", "#333333")
            )

        return _toggle

    for r in range(3):
        for c in range(4):
            idx = r * 4 + c
            text = str(idx + 1)
            fg = "#00FF00" if state.pattern_mask[idx] else ("#333333", "#333333")
            btn = ctk.CTkButton(
                grid_frame,
                text=text,
                width=80,
                height=60,
                fg_color=fg,
                command=make_toggle(idx),
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            buttons.append(btn)
            grid_frame.grid_columnconfigure(c, weight=1)
        grid_frame.grid_rowconfigure(r, weight=1)

    # Bottom controls
    ctl_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A")
    ctl_frame.pack(fill="x", padx=10, pady=(0, 10))

    def on_close():
        # Popup close is handled by PopupMenu close button; but allow explicit close
        try:
            context.gui.popup_manager.active_popup.close()
        except Exception:
            pass

    save_btn = ctk.CTkButton(ctl_frame, text="Save", command=on_close)
    save_btn.pack(side="right", padx=8)
