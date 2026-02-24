"""Matrix-style background animation layer."""

import tkinter as tk
import random
import time
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Column:
    """Represents a column of falling text."""

    x: int
    y: float
    speed: float
    base_speed: float
    trail_length: int
    boost_timer: int
    text_ids: List[int]


class MatrixLayer:
    """Matrix-style background animation using Canvas.

    Runs a low-CPU animation loop in the UI thread.
    """

    FRAME_MS = 33  # ~30 FPS
    FONT_SIZE = 14
    FONT_NAME = "Consolas"
    TRAIL_DEPTH = 20
    CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"

    def __init__(self, root: tk.Tk):
        """Initialize Matrix layer.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.canvas = tk.Canvas(
            root, bg="#050505", highlightthickness=0, takefocus=False
        )
        self.canvas.pack(fill="both", expand=True)

        self.columns: List[Column] = []
        self.running = False
        self.last_frame_time = 0
        self.column_count = 0
        self._resize_scheduled = False

        # Bind resize
        self.canvas.bind("<Configure>", self._on_resize)

        # Defer initial setup until canvas is mapped
        self.canvas.after(100, self._setup_columns)

    def _setup_columns(self):
        """Pre-create columns and text items."""
        # Clean up old items
        for col in self.columns:
            for text_id in col.text_ids:
                self.canvas.delete(text_id)

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1:
            width = 800
        if height <= 1:
            height = 600

        self.column_count = width // self.FONT_SIZE
        self.columns = []

        for i in range(self.column_count):
            x = i * self.FONT_SIZE
            y = random.uniform(-self.TRAIL_DEPTH * self.FONT_SIZE, 0)
            speed = random.uniform(1, 3)
            trail_length = random.randint(5, 15)

            text_ids = []
            for j in range(self.TRAIL_DEPTH):
                text_id = self.canvas.create_text(
                    x,
                    y - j * self.FONT_SIZE,
                    text=random.choice(self.CHAR_SET),
                    fill="#00FF00",
                    font=(self.FONT_NAME, self.FONT_SIZE),
                    anchor="nw",
                )
                text_ids.append(text_id)

            column = Column(
                x=x,
                y=y,
                speed=speed,
                base_speed=speed,
                trail_length=trail_length,
                boost_timer=0,
                text_ids=text_ids,
            )
            self.columns.append(column)

    def _on_resize(self, event):
        """Handle window resize."""
        new_count = event.width // self.FONT_SIZE
        if abs(new_count - self.column_count) > 5 and not self._resize_scheduled:
            self._resize_scheduled = True
            self.canvas.after(200, self._do_resize)

    def _do_resize(self):
        """Deferred resize handler."""
        self._resize_scheduled = False
        self._setup_columns()

    def start(self):
        """Start the animation."""
        if not self.running:
            self.running = True
            self.last_frame_time = time.time()
            self._tick()

    def stop(self):
        """Stop the animation."""
        self.running = False

    def _tick(self):
        """Animation tick."""
        if not self.running:
            return

        start_time = time.time()
        self._update()
        self._render()

        # Schedule next frame
        elapsed = (time.time() - start_time) * 1000
        delay = max(1, self.FRAME_MS - int(elapsed))
        self.root.after(delay, self._tick)

    def _update(self):
        """Update column positions."""
        height = self.canvas.winfo_height()
        for col in self.columns:
            col.y += col.speed
            if col.y > height + self.TRAIL_DEPTH * self.FONT_SIZE:
                col.y = random.uniform(-self.TRAIL_DEPTH * self.FONT_SIZE, 0)
                col.speed = col.base_speed
                col.trail_length = random.randint(5, 15)

            if col.boost_timer > 0:
                col.boost_timer -= self.FRAME_MS
                if col.boost_timer <= 0:
                    col.speed = col.base_speed

    def _render(self):
        """Render the animation."""
        height = self.canvas.winfo_height()
        for col in self.columns:
            for i, text_id in enumerate(col.text_ids):
                offset_y = col.y - i * self.FONT_SIZE
                if 0 <= offset_y <= height:
                    # Randomize character occasionally
                    if random.random() < 0.1:  # 10% chance
                        char = random.choice(self.CHAR_SET)
                        self.canvas.itemconfig(text_id, text=char)

                    # Calculate color gradient
                    intensity = max(0, 1 - (i / col.trail_length))
                    green = int(255 * intensity)
                    color = f"#{0:02x}{green:02x}{0:02x}"

                    self.canvas.coords(text_id, col.x, offset_y)
                    self.canvas.itemconfig(text_id, fill=color)
                else:
                    # Hide off-screen
                    self.canvas.coords(text_id, -100, -100)

    def react(self, note: int, velocity: int):
        """React to MIDI note for visual effect.

        Args:
            note: MIDI note number
            velocity: Note velocity
        """
        if self.columns:
            col_index = note % len(self.columns)
            col = self.columns[col_index]
            col.speed = col.base_speed * 2
            col.trail_length = min(self.TRAIL_DEPTH, velocity // 5)
            col.boost_timer = 200  # ms
