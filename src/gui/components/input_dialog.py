"""Simple text input dialog for user prompts."""

import customtkinter as ctk
import tkinter as tk
import re


class InputDialog(ctk.CTkToplevel):
    """Modal dialog for text input with validation."""

    def __init__(self, parent, title="Input", prompt="Enter value:", default_value=""):
        """Initialize input dialog.

        Args:
            parent: Parent window
            title: Dialog window title
            prompt: Prompt text to display
            default_value: Pre-filled value in entry field
        """
        super().__init__(parent)

        self.result = None
        self.title(title)
        self.geometry("400x150")

        # Set background color to make content visible
        self.configure(fg_color=("gray90", "gray15"))

        # Make modal (but don't grab yet)
        self.transient(parent)

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (150 // 2)
        self.geometry(f"+{x}+{y}")

        # Prompt label
        self.label = ctk.CTkLabel(self, text=prompt, font=("Arial", 14))
        self.label.pack(pady=(20, 10), padx=20)

        # Entry field
        self.entry = ctk.CTkEntry(self, width=350, font=("Arial", 12))
        self.entry.pack(pady=10, padx=20)
        self.entry.insert(0, default_value)
        self.entry.select_range(0, tk.END)

        # Bind Enter key to OK
        self.entry.bind("<Return>", lambda e: self._on_ok())
        self.entry.bind("<Escape>", lambda e: self._on_cancel())

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.ok_button = ctk.CTkButton(
            button_frame, text="OK", command=self._on_ok, width=100
        )
        self.ok_button.pack(side="left", padx=5)

        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=100,
            fg_color="gray30",
            hover_color="gray40",
        )
        self.cancel_button.pack(side="left", padx=5)

        # Force update to ensure widgets are rendered
        self.update_idletasks()

        # Now grab focus after window is fully viewable
        self.grab_set()
        self.entry.focus_set()

    def _on_ok(self):
        """Handle OK button click."""
        self.result = self.entry.get().strip()
        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.destroy()

    def get_input(self) -> str | None:
        """Show dialog and return user input (blocking).

        Returns:
            User input string or None if cancelled
        """
        self.wait_window()
        return self.result


def sanitize_filename(name: str) -> str:
    """Sanitize filename by removing invalid characters.

    Args:
        name: Proposed filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove leading/trailing dots and spaces
    name = name.strip(". ")
    return name


def prompt_for_filename(
    parent, title="Save Sequence", default_name="sequence"
) -> str | None:
    """Prompt user for a filename with validation.

    Args:
        parent: Parent window
        title: Dialog title
        default_name: Default filename (without extension)

    Returns:
        Sanitized filename with .mid extension, or None if cancelled
    """
    dialog = InputDialog(
        parent, title=title, prompt="Enter sequence name:", default_value=default_name
    )

    filename = dialog.get_input()

    if filename:
        # Sanitize and ensure .mid extension
        filename = sanitize_filename(filename)
        if not filename:
            return None
        if not filename.endswith(".mid"):
            filename += ".mid"
        return filename

    return None
