"""Application configuration management."""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Configuration container for MIDI Echo application.

    All configuration values are loaded from environment variables with sensible defaults.
    """

    # MIDI Configuration
    output: str
    verbose: bool
    list_ports: bool

    # UI Configuration - Press Detection
    short_press_threshold: int  # milliseconds
    long_press_threshold: int  # milliseconds
    long_press_increment: int  # semitones per repeat

    # UI Configuration - Window
    window_width: int
    window_height: int

    # UI Configuration - Fonts
    base_window_width: int  # Reference width for font scaling
    base_window_height: int  # Reference height for font scaling

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        return cls(
            output=os.getenv("OUTPUT", ""),
            verbose=os.getenv("VERBOSE", "false").lower() == "true",
            list_ports=os.getenv("LIST_PORTS", "false").lower() == "true",
            short_press_threshold=int(os.getenv("SHORT_PRESS_THRESHOLD", "200")),
            long_press_threshold=int(os.getenv("LONG_PRESS_THRESHOLD", "500")),
            long_press_increment=int(os.getenv("LONG_PRESS_INCREMENT", "5")),
            window_width=int(os.getenv("WINDOW_WIDTH", "600")),
            window_height=int(os.getenv("WINDOW_HEIGHT", "400")),
            base_window_width=600,
            base_window_height=400,
        )
