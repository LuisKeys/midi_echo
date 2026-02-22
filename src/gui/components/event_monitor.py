"""Event monitor widget for displaying MIDI events."""

import customtkinter as ctk
from src.midi.event_log import EventLog


class EventMonitor(ctk.CTkFrame):
    """Widget for monitoring MIDI events in real-time."""

    def __init__(self, parent, event_log: EventLog, theme):
        """Initialize event monitor.

        Args:
            parent: Parent widget
            event_log: EventLog instance to monitor
            theme: Theme instance for colors
        """
        super().__init__(parent, fg_color=theme.get_color("bg"))

        self.event_log = event_log
        self.theme = theme
        self.grid_rowconfigure(1, weight=1)  # Row 1 (display) gets extra space
        self.grid_columnconfigure(0, weight=1)

        # Store widget references for font updates
        self.title_label = None
        self.status_label = None
        self.text_display = None
        self.pause_button = None
        self.clear_button = None
        self.count_label = None

        # Create header
        header_frame = ctk.CTkFrame(self, fg_color=theme.get_color("bg"))
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=theme.get_padding("popup_frame"),
            pady=theme.get_padding("popup_frame"),
        )
        header_frame.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="MIDI Event Monitor",
            font=("Courier New", theme.get_font_size("popup_title"), "bold"),
            text_color=theme.get_color("text_white"),
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=5)

        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Active",
            font=("Courier New", theme.get_font_size("popup_value")),
            text_color=theme.get_color("text_white"),
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=5)

        # Create event display area
        display_frame = ctk.CTkFrame(self, fg_color=theme.get_color("bg"))
        display_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=theme.get_padding("popup_frame"),
            pady=theme.get_padding("popup_control_small"),
        )
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

        # Text widget for displaying events
        self.text_display = ctk.CTkTextbox(
            display_frame,
            font=("Courier New", theme.get_font_size("label_small")),
            fg_color=theme.get_color("frame_bg"),
            text_color=theme.get_color("text_white"),
            border_color=theme.get_color("button_inactive"),
            border_width=1,
        )
        self.text_display.grid(row=0, column=0, sticky="nsew")
        self.text_display.configure(state="disabled")

        # Create control panel
        control_frame = ctk.CTkFrame(self, fg_color=theme.get_color("bg"))
        control_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=theme.get_padding("popup_frame"),
            pady=theme.get_padding("popup_frame"),
        )
        control_frame.grid_columnconfigure(1, weight=1)

        # Pause/Resume button
        self.pause_button = ctk.CTkButton(
            control_frame,
            text="Pause",
            fg_color=theme.get_color_tuple("aqua"),
            hover_color=theme.get_color_tuple("cyan"),
            text_color=theme.get_color("button_text"),
            font=("Courier New", theme.get_font_size("popup_button")),
            command=self._on_pause_click,
        )
        self.pause_button.grid(row=0, column=0, padx=5, pady=5)

        # Clear button
        self.clear_button = ctk.CTkButton(
            control_frame,
            text="Clear",
            fg_color=theme.get_color_tuple("red"),
            hover_color=theme.get_color_tuple("grey"),
            text_color=theme.get_color("button_text"),
            font=("Courier New", theme.get_font_size("popup_button")),
            command=self._on_clear_click,
        )
        self.clear_button.grid(row=0, column=2, padx=5, pady=5)

        # Event count label
        self.count_label = ctk.CTkLabel(
            control_frame,
            text="0 events",
            font=("Courier New", theme.get_font_size("popup_value")),
            text_color=theme.get_color("text_white"),
        )
        self.count_label.grid(row=0, column=1, padx=5)

        # Subscribe to event log
        self.event_log.add_listener(self._on_event_added)

        # Initial update
        self._update_display()

    def update_font_sizes(self) -> None:
        """Update font sizes for all UI elements.

        Called by popup_manager when window is resized to keep fonts
        scaled relative to window size.
        """
        try:
            if self.title_label and self.title_label.winfo_exists():
                self.title_label.configure(
                    font=(
                        "Courier New",
                        self.theme.get_font_size("popup_title"),
                        "bold",
                    )
                )

            if self.status_label and self.status_label.winfo_exists():
                self.status_label.configure(
                    font=("Courier New", self.theme.get_font_size("popup_value"))
                )

            if self.text_display and self.text_display.winfo_exists():
                self.text_display.configure(
                    font=("Courier New", self.theme.get_font_size("label_small"))
                )

            if self.pause_button and self.pause_button.winfo_exists():
                self.pause_button.configure(
                    font=("Courier New", self.theme.get_font_size("popup_button"))
                )

            if self.clear_button and self.clear_button.winfo_exists():
                self.clear_button.configure(
                    font=("Courier New", self.theme.get_font_size("popup_button"))
                )

            if self.count_label and self.count_label.winfo_exists():
                self.count_label.configure(
                    font=("Courier New", self.theme.get_font_size("popup_value"))
                )
        except Exception:
            pass  # Widget might have been destroyed

    def _on_event_added(self, event) -> None:
        """Called when a new event is added to the log."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the text display with current events."""
        events = self.event_log.get_events()

        # Update text widget
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")

        if events:
            event_lines = [event.format_event() for event in events]
            content = "\n".join(event_lines)
            self.text_display.insert("end", content)

            # Auto-scroll to bottom
            self.text_display.see("end")
        else:
            self.text_display.insert("end", "No events yet...")

        self.text_display.configure(state="disabled")

        # Update count
        self.count_label.configure(text=f"{len(events)} events")

        # Update status
        if self.event_log.is_paused():
            self.status_label.configure(
                text="⏸ Paused", text_color=self.theme.get_color("red")
            )
        else:
            self.status_label.configure(
                text="●  Active", text_color=self.theme.get_color("aqua")
            )

    def _on_pause_click(self) -> None:
        """Handle pause button click."""
        if self.event_log.is_paused():
            self.event_log.resume()
            self.pause_button.configure(text="Pause")
        else:
            self.event_log.pause()
            self.pause_button.configure(text="Resume")

        self._update_display()

    def _on_clear_click(self) -> None:
        """Handle clear button click."""
        self.event_log.clear()
        self._update_display()

    def cleanup(self) -> None:
        """Clean up when monitor is closed."""
        self.event_log.remove_listener(self._on_event_added)
