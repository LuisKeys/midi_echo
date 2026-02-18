"""Lightbox component for dimming the background."""

import customtkinter as ctk
from src.gui.components.theme import Theme


class Lightbox(ctk.CTkFrame):
    """Semi-transparent-look overlay to dim the background.

    Responsible for:
    - Covering the parent widget with a themed color
    - Handling click-to-dismiss events
    - Lifecycle management (show/hide/destroy)
    """

    def __init__(self, parent: ctk.CTk, theme: Theme, command=None):
        """Initialize lightbox.

        Args:
            parent: Parent widget to cover
            theme: Theme instance for colors
            command: Optional callback when clicked
        """
        color = theme.get_color("overlay")
        super().__init__(parent, fg_color=color, corner_radius=0)
        self.command = command

        # Bind click event with propagation stop
        if self.command:
            self.bind("<Button-1>", self._on_click)

    def show(self):
        """Display the lightbox covering the parent."""
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lower()

    def hide(self):
        """Remove the lightbox from view."""
        self.place_forget()

    def _on_click(self, event):
        """Handle click events and stop propagation."""
        if self.command:
            self.command()
        return "break"  # Stop event propagation
