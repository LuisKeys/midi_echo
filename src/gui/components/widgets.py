"""Reusable GUI widgets for the MIDI Echo application."""

import customtkinter as ctk


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
    ):
        super().__init__(parent, fg_color="#2A2A2A")
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.callback = callback
        self.config = config
        self.current_val = initial_val

        # Label
        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 14))
        self.label.pack(side="left", padx=10)

        # Minus button with hold logic
        self.minus_holding = False
        self.minus_timer = None

        self.minus_btn = ctk.CTkButton(
            self, text="-", width=80, height=50, corner_radius=0
        )
        self.minus_btn.bind("<ButtonPress-1>", lambda e: self.start_decr())
        self.minus_btn.bind("<ButtonRelease-1>", lambda e: self.stop_decr())
        self.minus_btn.pack(side="left", padx=5)

        # Value display
        self.value_label = ctk.CTkLabel(
            self, text=str(self.current_val), font=("Arial", 16)
        )
        self.value_label.pack(side="left", padx=10)

        # Plus button with hold logic
        self.plus_holding = False
        self.plus_timer = None

        self.plus_btn = ctk.CTkButton(
            self, text="+", width=80, height=50, corner_radius=0
        )
        self.plus_btn.bind("<ButtonPress-1>", lambda e: self.start_incr())
        self.plus_btn.bind("<ButtonRelease-1>", lambda e: self.stop_incr())
        self.plus_btn.pack(side="left", padx=5)

        # Suffix label
        if suffix:
            self.suffix_label = ctk.CTkLabel(self, text=suffix, font=("Arial", 14))
            self.suffix_label.pack(side="left", padx=5)

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
            self.tap_btn.pack(side="right", padx=10)

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
