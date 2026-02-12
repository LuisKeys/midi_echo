"""Button panel component for managing GUI button grid."""

import customtkinter as ctk
from typing import Callable, Dict, Optional, Any
from dataclasses import dataclass
from src.gui.components.theme import Theme


@dataclass
class ButtonSpec:
    """Specification for a button."""

    text: str
    row: int
    col: int
    color_name: str
    command: Callable
    long_press_handler: Optional[Callable] = None


class ButtonPanel:
    """Manages a grid of buttons with styling and interaction.

    Responsible for:
    - Creating and laying out buttons in a grid
    - Managing button state and styling
    - Handling button click/long-press events
    """

    def __init__(self, parent: ctk.CTk, theme: Theme):
        """Initialize button panel.

        Args:
            parent: Parent widget (the main window)
            theme: Theme instance for colors and fonts
        """
        self.parent = parent
        self.theme = theme
        self.buttons: Dict[str, ctk.CTkButton] = {}

        # Configure grid layout
        self.parent.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        self.parent.grid_rowconfigure((0, 1), weight=1, uniform="equal")

    def create_button(
        self,
        spec: ButtonSpec,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
    ) -> ctk.CTkButton:
        """Create and place a button.

        Args:
            spec: ButtonSpec defining button properties
            on_press: Callback for button press (for long-press detection)
            on_release: Callback for button release (for long-press detection)

        Returns:
            The created CTkButton
        """
        color = self.theme.get_color_tuple(spec.color_name)

        btn = ctk.CTkButton(
            self.parent,
            text=spec.text,
            font=("Arial", self.theme.get_font_size("main_button"), "bold"),
            fg_color=color,
            text_color="black",
            hover_color=color,
            corner_radius=10,
            command=spec.command,
        )

        # Place button in grid
        btn.grid(row=spec.row, column=spec.col, padx=10, pady=10, sticky="nsew")

        # Store reference
        self.buttons[spec.text] = btn

        # Add long-press detection if handler provided
        if spec.long_press_handler:
            if on_press and on_release:
                btn.bind("<Button-1>", lambda e: on_press())
                btn.bind("<ButtonRelease-1>", lambda e: on_release())

        return btn

    def get_button(self, text: str) -> Optional[ctk.CTkButton]:
        """Get a button by text label.

        Args:
            text: Button text/label

        Returns:
            Button widget or None if not found
        """
        return self.buttons.get(text)

    def update_button_text(self, text: str, new_text: str) -> None:
        """Update button text.

        Args:
            text: Current button text (identifier)
            new_text: New button text to display
        """
        btn = self.get_button(text)
        if btn:
            btn.configure(text=new_text)

    def update_button_color(self, text: str, color_name: str) -> None:
        """Update button color.

        Args:
            text: Button text (identifier)
            color_name: Color name from theme
        """
        btn = self.get_button(text)
        if btn:
            color = self.theme.get_color_tuple(color_name)
            btn.configure(fg_color=color)

    def update_font_sizes(self) -> None:
        """Update all button fonts after window resize."""
        new_font_size = self.theme.get_font_size("main_button")
        for btn in self.buttons.values():
            btn.configure(font=("Arial", new_font_size, "bold"))

    def force_redraw(self) -> None:
        """Force redraw of all buttons to fix rendering glitches."""
        self.parent.update_idletasks()
        for btn in self.buttons.values():
            current_color = btn.cget("fg_color")
            btn.configure(fg_color=current_color)
