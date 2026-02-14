"""Reusable GUI widgets for the MIDI Echo application."""

import customtkinter as ctk
from src.gui.components.layout_utils import LayoutSpacing


class IncrementDecrementWidget(ctk.CTkFrame):
    """A reusable widget for increment/decrement controls with hold-to-repeat functionality."""

    def __init__(
        self,
        parent,
        label_text,
        min_val,
        max_val,
        initial_val,
        step=1,
        callback=None,
        config=None,
        suffix=None,
        tap_callback=None,
        theme=None,
        label_width=None,
    ):
        super().__init__(
            parent, fg_color=theme.get_color("frame_bg") if theme else "#F5F5F5"
        )
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.callback = callback
        self.theme = theme
        self.label_width = label_width
        self.current_val = initial_val

        # Label
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=("Arial", 14),
            anchor="e",
            text_color=theme.get_color("text_black") if theme else None,
        )
        if self.label_width is not None:
            self.label.configure(width=self.label_width)
        self.label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

        # Minus button with hold logic
        self.minus_holding = False
        self.minus_timer = None

        self.minus_btn = ctk.CTkButton(
            self, text="-", width=80, height=50, corner_radius=0
        )
        self.minus_btn.bind("<ButtonPress-1>", lambda e: self.start_decr())
        self.minus_btn.bind("<ButtonRelease-1>", lambda e: self.stop_decr())
        self.minus_btn.pack(side="left", padx=LayoutSpacing.CONTROL_BUTTON_PADX)

        # Value display
        self.value_label = ctk.CTkLabel(
            self,
            text=str(self.current_val),
            font=("Arial", 16),
            anchor="center",
            text_color=theme.get_color("text_black") if theme else None,
        )
        if self.theme:
            self.value_label.configure(width=self.theme.get_value_width())
        self.value_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

        # Plus button with hold logic
        self.plus_holding = False
        self.plus_timer = None

        self.plus_btn = ctk.CTkButton(
            self, text="+", width=80, height=50, corner_radius=0
        )
        self.plus_btn.bind("<ButtonPress-1>", lambda e: self.start_incr())
        self.plus_btn.bind("<ButtonRelease-1>", lambda e: self.stop_incr())
        self.plus_btn.pack(side="left", padx=LayoutSpacing.CONTROL_BUTTON_PADX)

        # Suffix label
        if suffix:
            self.suffix_label = ctk.CTkLabel(
                self,
                text=suffix,
                font=("Arial", 14),
                text_color=theme.get_color("text_black") if theme else None,
            )
            self.suffix_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)

        # Tap button
        if tap_callback:
            self.tap_btn = ctk.CTkButton(
                self,
                text="Tap",
                width=80,
                height=50,
                command=tap_callback,
                corner_radius=0,
            )
            self.tap_btn.pack(side="right", padx=LayoutSpacing.ELEMENT_PADX)

        # Apply initial scaling
        if self.theme:
            self.update_font_sizes()

    def update_font_sizes(self) -> None:
        """Update font sizes based on theme (dimensions stay fixed)."""
        if not self.theme:
            return

        # Check if widget still exists
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        label_font_size = self.theme.get_font_size("label_small")
        value_font_size = self.theme.get_font_size("label_medium")
        btn_font_size = self.theme.get_font_size("increment_button")

        # Update label in single configure call
        label_config = {
            "font": ("Arial", label_font_size),
            "anchor": "e",
            "text_color": self.theme.get_color("text_black"),
        }
        if self.label_width is not None:
            label_config["width"] = self.label_width
        self.label.configure(**label_config)

        # Update value label in single configure call
        self.value_label.configure(
            font=("Arial", value_font_size),
            width=self.theme.get_value_width(),
            anchor="center",
            text_color=self.theme.get_color("text_black"),
        )

        for btn in [self.minus_btn, self.plus_btn]:
            btn.configure(font=("Arial", btn_font_size))

        if hasattr(self, "suffix_label"):
            self.suffix_label.configure(
                font=("Arial", label_font_size),
                text_color=self.theme.get_color("text_black"),
            )

        if hasattr(self, "tap_btn"):
            self.tap_btn.configure(font=("Arial", label_font_size))

    def start_decr(self):
        self.minus_holding = True
        self.decrement()
        self.minus_timer = self.after(500, self.start_decr_repeat)

    def start_decr_repeat(self):
        if self.minus_holding:
            self.minus_timer = self.after(
                self.config.hold_increment_rate, self.repeat_decr
            )

    def repeat_decr(self):
        if self.minus_holding:
            self.decrement()
            self.minus_timer = self.after(
                self.config.hold_increment_rate, self.repeat_decr
            )

    def stop_decr(self):
        self.minus_holding = False
        if self.minus_timer:
            self.after_cancel(self.minus_timer)
            self.minus_timer = None

    def start_incr(self):
        self.plus_holding = True
        self.increment()
        self.plus_timer = self.after(500, self.start_incr_repeat)

    def start_incr_repeat(self):
        if self.plus_holding:
            self.plus_timer = self.after(
                self.config.hold_increment_rate, self.repeat_incr
            )

    def repeat_incr(self):
        if self.plus_holding:
            self.increment()
            self.plus_timer = self.after(
                self.config.hold_increment_rate, self.repeat_incr
            )

    def stop_incr(self):
        self.plus_holding = False
        if self.plus_timer:
            self.after_cancel(self.plus_timer)
            self.plus_timer = None

    def decrement(self):
        new_val = max(self.min_val, self.current_val - self.step)
        if new_val != self.current_val:
            self.current_val = new_val
            self.value_label.configure(text=str(new_val))
            if self.callback:
                self.callback(new_val)

    def increment(self):
        new_val = min(self.max_val, self.current_val + self.step)
        if new_val != self.current_val:
            self.current_val = new_val
            self.value_label.configure(text=str(new_val))
            if self.callback:
                self.callback(new_val)

    def set_value(self, val):
        self.current_val = val
        self.value_label.configure(text=str(val))


class SquareDropdown(ctk.CTkFrame):
    """A custom dropdown menu with squared corners and touch-friendly sizing."""

    def __init__(
        self,
        parent,
        values,
        variable=None,
        command=None,
        width=150,
        height=50,
        **kwargs,
    ):
        """Initialize dropdown with squared corners and large touch targets.

        Args:
            parent: Parent widget
            values: List of values for the dropdown
            variable: StringVar to track the selected value
            command: Callback when selection changes
            width: Width of the dropdown
            height: Height of the dropdown
            **kwargs: Additional arguments to pass to CTkFrame
        """
        super().__init__(parent, fg_color="#B0BEC5", corner_radius=0, **kwargs)

        self.values = values
        self.variable = variable
        self.command = command
        self.width = width
        self.height = height
        self._dropdown_open = False
        self._dropdown_window = None

        # Create the button to show current value
        self.button = ctk.CTkButton(
            self,
            text=variable.get() if variable else values[0],
            width=width,
            height=height,
            corner_radius=0,
            font=("Arial", 20),
            command=self._toggle_dropdown,
        )
        self.button.pack(fill="both", expand=True)

    def _toggle_dropdown(self):
        """Toggle the dropdown menu open/closed."""
        if self._dropdown_open:
            self._close_dropdown()
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        """Open the dropdown menu directly below the button."""
        self._dropdown_open = True

        # Force update to get accurate widget dimensions
        self.update_idletasks()

        # Get the absolute position of this dropdown button
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()

        # Get root window
        root = self
        while root.master:
            root = root.master

        # Create dropdown window positioned below the button
        self._dropdown_window = ctk.CTkToplevel(root)
        self._dropdown_window.geometry(f"{width}x300+{x}+{y}")
        self._dropdown_window.overrideredirect(True)
        self._dropdown_window.attributes("-topmost", True)

        # Create frame for items
        frame = ctk.CTkFrame(self._dropdown_window, fg_color="#F5F5F5", corner_radius=0)
        frame.pack(fill="both", expand=True)

        # Add buttons for each value
        for value in self.values:
            btn = ctk.CTkButton(
                frame,
                text=value,
                height=60,
                corner_radius=0,
                font=("Arial", 24),
                command=lambda v=value: self._select_value(v),
            )
            btn.pack(fill="x", padx=0, pady=1)

        # Close dropdown when clicking outside
        def close_on_focus_out(event=None):
            if self._dropdown_window and not self._dropdown_window.winfo_exists():
                self._dropdown_open = False
                return
            self._close_dropdown()

        self._dropdown_window.bind("<FocusOut>", close_on_focus_out)
        self._dropdown_window.focus()

    def _close_dropdown(self):
        """Close the dropdown menu."""
        self._dropdown_open = False
        if self._dropdown_window and self._dropdown_window.winfo_exists():
            self._dropdown_window.destroy()
        self._dropdown_window = None

    def _select_value(self, value):
        """Select a dropdown value."""
        if self.variable:
            self.variable.set(value)
        self.button.configure(text=value)
        if self.command:
            self.command(value)
        self._close_dropdown()

    def configure(self, **kwargs):
        """Configure widget - handle font specially."""
        font = kwargs.pop("font", None)
        if font:
            # Configure the button font
            self.button.configure(font=font)
        # Handle any other configuration
        if kwargs:
            super().configure(**kwargs)
