"""Reusable TransportControls component: Play, Record, Clear, Metronome"""

import customtkinter as ctk
from typing import Optional
from .theme import Theme


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
        super().__init__(parent, fg_color=theme.BACKGROUND_UNSELECTED)
        self.theme = theme
        self.pm = pm
        self.sequencer = sequencer
        self._height = 60

        font_size = theme.get_font_size("popup_button")
        self._font = ("Courier New", font_size)

        def button_style(state_color_key: str):
            canonical_color = Theme._get_canonical_color(state_color_key)
            return {
                "corner_radius": 0,
                "fg_color": canonical_color,
                "hover_color": theme.BACKGROUND_HOVER,
                "text_color": theme.FONT_AND_BORDER,
                "border_width": 1,
                "border_color": theme.FONT_AND_BORDER,
                "font": self._font,
            }

        # Play
        self.play_button = ctk.CTkButton(
            self,
            text="Play",
            command=lambda: play_cb() if play_cb else None,
            height=self._height,
            **button_style("button_inactive"),
        )
        self.play_button.pack(side="left", expand=True, fill="x", padx=2)

        # Record
        self.record_button = ctk.CTkButton(
            self,
            text="Record",
            command=lambda: record_cb() if record_cb else None,
            height=self._height,
            **button_style("button_inactive"),
        )
        self.record_button.pack(side="left", expand=True, fill="x", padx=2)

        # Clear
        self.clear_button = ctk.CTkButton(
            self,
            text="Clear",
            command=lambda: clear_cb() if clear_cb else None,
            height=self._height,
            **button_style("button_inactive"),
        )
        self.clear_button.pack(side="left", expand=True, fill="x", padx=2)

        # Metronome
        met_color = (
            self.theme.BACKGROUND_SELECTED
            if (sequencer and sequencer.state.metronome_enabled)
            else self.theme.BACKGROUND_UNSELECTED
        )
        self.metronome_button = ctk.CTkButton(
            self,
            text="Met",
            command=lambda: met_cb() if met_cb else None,
            height=self._height,
            corner_radius=0,
            fg_color=met_color,
            hover_color=self.theme.BACKGROUND_HOVER,
            text_color=self.theme.FONT_AND_BORDER,
            border_width=1,
            border_color=self.theme.FONT_AND_BORDER,
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
            self.play_button.configure(
                fg_color=self.theme.BACKGROUND_SELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
                text="Stop",
                state="normal",
            )
        elif is_recording or record_arming:
            self.play_button.configure(
                fg_color=self.theme.BACKGROUND_UNSELECTED,
                hover_color=self.theme.BACKGROUND_UNSELECTED,
                text="Play",
                state="disabled",
            )
        else:
            self.play_button.configure(
                fg_color=self.theme.BACKGROUND_SELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
                text="Play",
                state="normal",
            )

        # Update record button
        if is_recording:
            self.record_button.configure(
                fg_color=self.theme.BACKGROUND_SELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
                text="Stop Rec",
                state="normal",
            )
        elif is_playing:
            self.record_button.configure(
                fg_color=self.theme.BACKGROUND_UNSELECTED,
                hover_color=self.theme.BACKGROUND_UNSELECTED,
                text="Record",
                state="disabled",
            )
        else:
            self.record_button.configure(
                fg_color=self.theme.BACKGROUND_SELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
                text="Record",
                state="normal",
            )

        # Metronome color
        if metronome_enabled:
            self.metronome_button.configure(
                fg_color=self.theme.BACKGROUND_SELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
            )
        else:
            self.metronome_button.configure(
                fg_color=self.theme.BACKGROUND_UNSELECTED,
                hover_color=self.theme.BACKGROUND_HOVER,
            )

    def update_font_sizes(self):
        try:
            font_size = self.theme.get_font_size("popup_button")
            self._font = ("Courier New", font_size)
            self.play_button.configure(font=self._font)
            self.record_button.configure(font=self._font)
            self.clear_button.configure(font=self._font)
            self.metronome_button.configure(font=self._font)
        except Exception:
            pass
