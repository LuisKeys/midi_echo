"""Button press detection for long-press and short-press handling."""

from typing import Callable, Optional
from src.config import AppConfig


class PressDetector:
    """Detects and distinguishes between short and long button presses.

    Responsible for:
    - Tracking press start/end times
    - Triggering callbacks on long-press threshold
    - Managing debounce and repeat timers
    """

    def __init__(self, config: AppConfig, tk_root):
        """Initialize press detector.

        Args:
            config: AppConfig with threshold values
            tk_root: Tkinter root window for scheduling callbacks
        """
        self.config = config
        self.tk_root = tk_root

        # Current press state
        self.is_long_press = False
        self.press_timer = None
        self.repeat_timer = None

    def on_button_press(
        self,
        button_id: str,
        long_press_callback: Callable,
    ) -> None:
        """Handle button press - start long-press detection.

        Args:
            button_id: Unique identifier for the button
            long_press_callback: Callback to invoke on long press
        """
        self.is_long_press = False

        def trigger_long_press():
            self.is_long_press = True
            long_press_callback()

        self.press_timer = self.tk_root.after(
            self.config.long_press_threshold,
            trigger_long_press,
        )

    def on_button_release(self, short_press_callback: Callable) -> None:
        """Handle button release - trigger short press if not long press.

        Args:
            short_press_callback: Callback to invoke on short press
        """
        if self.press_timer:
            self.tk_root.after_cancel(self.press_timer)
            self.press_timer = None

        if not self.is_long_press:
            short_press_callback()

        self.is_long_press = False

    def start_repeat_timer(self, callback: Callable, delay_ms: int = 50) -> None:
        """Start a repeating timer for long-press increment operations.

        Args:
            callback: Callback to invoke repeatedly
            delay_ms: Delay between repeats in milliseconds
        """

        def repeat():
            callback()
            self.repeat_timer = self.tk_root.after(delay_ms, repeat)

        self.repeat_timer = self.tk_root.after(delay_ms, repeat)

    def stop_repeat_timer(self) -> None:
        """Stop the repeat timer."""
        if self.repeat_timer:
            self.tk_root.after_cancel(self.repeat_timer)
            self.repeat_timer = None

    def reset(self) -> None:
        """Reset all timers and state."""
        self.stop_repeat_timer()
        if self.press_timer:
            self.tk_root.after_cancel(self.press_timer)
            self.press_timer = None
        self.is_long_press = False
