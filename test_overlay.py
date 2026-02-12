#!/usr/bin/env python3
"""Quick test script to verify the overlay changes.

This script demonstrates:
1. Dark violet theme-tinted overlay (#3D1A6D)
2. Increased opacity (0.65 instead of 0.5)
3. Click-to-close functionality on the overlay
"""

import customtkinter as ctk
from src.gui.components.popup_manager import PopupManager


def main():
    """Create a test window with popup to verify overlay changes."""
    app = ctk.CTk()
    app.title(
        "Overlay Test - Click buttons below, then click the darkened area to close"
    )
    app.geometry("800x600")

    # Create popup manager
    popup_mgr = PopupManager(app)

    # Add a test button to open a popup
    def open_popup():
        def content_builder(frame):
            label = ctk.CTkLabel(
                frame,
                text="Click outside this box\n(on the darkened area) to close it",
                font=("Arial", 16),
            )
            label.pack(pady=20)

            btn = ctk.CTkButton(
                frame,
                text="Or click here to close",
                command=popup.close,
                font=("Arial", 14),
            )
            btn.pack(pady=10)

        popup = popup_mgr.create_popup(
            title="Test Popup", content_builder=content_builder, width=400, height=200
        )
        popup.show()

    btn = ctk.CTkButton(
        app,
        text="Open Popup to Test Overlay",
        command=open_popup,
        font=("Arial", 16),
        height=60,
    )
    btn.pack(pady=20)

    info = ctk.CTkLabel(
        app,
        text=(
            "Changes made:\n"
            "✓ Overlay color: Dark violet (#3D1A6D) instead of black\n"
            "✓ Opacity: 0.65 (65%) instead of 0.5 (50%)\n"
            "✓ Click outside popup to close (click-to-close)\n\n"
            "Try it: Click the button above, then click the darkened area"
        ),
        font=("Arial", 12),
        justify="left",
    )
    info.pack(pady=20, padx=20)

    app.mainloop()


if __name__ == "__main__":
    main()
