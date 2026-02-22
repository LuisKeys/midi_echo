"""Reusable TransportControls component: Play, Record, Clear, Metronome"""

import customtkinter as ctk
from typing import Optional


class TransportControls(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        theme,
        pm=None,
        play_cb: Optional[callable] = None,
        record_cb: Optional[callable] = None,
        clear_cb: Optional[callable] = None,
        met_cb: Optional[callable] = None,
        sequencer=None,
    ):
        super().__init__(parent, fg_color=theme.get_color("frame_bg"))
        self.theme = theme
        self.pm = pm
        self.sequencer = sequencer
        self._height = 60

        font_size = theme.get_font_size("popup_button")
        self._font = ("Arial", font_size)

        # Play
        self.play_button = ctk.CTkButton(
            self,
            text="Play",
            command=lambda: play_cb() if play_cb else None,
            height=self._height,
            corner_radius=0,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=self._font,
        )
        self.play_button.pack(side="left", expand=True, fill="x", padx=2)

        # Record
        self.record_button = ctk.CTkButton(
            self,
            text="Record",
            command=lambda: record_cb() if record_cb else None,
            height=self._height,
            corner_radius=0,
            fg_color="#FF9800",
            hover_color="#F57C00",
            font=self._font,
        )
        self.record_button.pack(side="left", expand=True, fill="x", padx=2)

        # Clear
        self.clear_button = ctk.CTkButton(
            self,
            text="Clear",
            command=lambda: clear_cb() if clear_cb else None,
            height=self._height,
            corner_radius=0,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            font=self._font,
        )
        self.clear_button.pack(side="left", expand=True, fill="x", padx=2)

        # Metronome
        met_color = (
            "#2196F3"
            if (sequencer and sequencer.state.metronome_enabled)
            else "#757575"
        )
        self.metronome_button = ctk.CTkButton(
            self,
            text="Met",
            command=lambda: met_cb() if met_cb else None,
            height=self._height,
            corner_radius=0,
            fg_color=met_color,
            hover_color="#1976D2",
            font=self._font,
        )
        self.metronome_button.pack(side="left", expand=True, fill="x", padx=2)

        # Register with popup manager for font/scale updates
        if self.pm:
            try:
                self.pm.register_element("content_elements", self.play_button)
                self.pm.register_element("content_elements", self.record_button)
                self.pm.register_element("content_elements", self.clear_button)
                self.pm.register_element("content_elements", self.metronome_button)
                self.pm.register_element("content_elements", self)
            except Exception:
                pass

    def register_callbacks(
        self, play_cb=None, record_cb=None, clear_cb=None, met_cb=None
    ):
        if play_cb:
            self.play_button.configure(command=play_cb)
        if record_cb:
            self.record_button.configure(command=record_cb)
        if clear_cb:
            self.clear_button.configure(command=clear_cb)
        if met_cb:
            self.metronome_button.configure(command=met_cb)

    def set_state(
        self,
        is_playing: bool,
        is_recording: bool,
        record_arming: bool = False,
        metronome_enabled: bool = False,
    ):
        # Update play button
        if is_playing:
            self.play_button.configure(fg_color="#1565C0", text="Stop", state="normal")
        elif is_recording or record_arming:
            self.play_button.configure(
                fg_color="#757575", text="Play", state="disabled"
            )
        else:
            self.play_button.configure(fg_color="#4CAF50", text="Play", state="normal")

        # Update record button
        if is_recording:
            self.record_button.configure(
                fg_color="#D32F2F", text="Stop Rec", state="normal"
            )
        elif is_playing:
            self.record_button.configure(
                fg_color="#757575", text="Record", state="disabled"
            )
        else:
            self.record_button.configure(
                fg_color="#FF9800", text="Record", state="normal"
            )

        # Metronome color
        if metronome_enabled:
            self.metronome_button.configure(fg_color="#2196F3")
        else:
            self.metronome_button.configure(fg_color="#757575")

    def update_font_sizes(self):
        try:
            font_size = self.theme.get_font_size("popup_button")
            self._font = ("Arial", font_size)
            self.play_button.configure(font=self._font)
            self.record_button.configure(font=self._font)
            self.clear_button.configure(font=self._font)
            self.metronome_button.configure(font=self._font)
        except Exception:
            pass
