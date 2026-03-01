"""Application configuration management."""

import os
import platform
from dataclasses import dataclass
from typing import List


def get_system() -> str:
    """Return the operating system name."""
    return platform.system()


# OS-aware MIDI output patterns for dynamic port discovery
# These patterns are used to filter available MIDI ports by OS
OUTPUT_PATTERNS = {
    "Darwin": ["Virtual Bus", "IAC Driver", "IAC"],  # macOS virtual ports
    "Linux": [
        "VirMIDI",
        "TiMidity",
        "ALSA",
        "Midi Through",
    ],  # Linux virtual/synth ports
    "Windows": ["loopMIDI", "Virtual", "MIDI Yoke"],  # Windows virtual ports
}


@dataclass
class AppConfig:
    """Configuration container for MIDI Echo application.

    All configuration values are loaded from environment variables with sensible defaults.
    """

    # MIDI Configuration
    output: str  # Deprecated: kept for backward compatibility
    preferred_outputs: List[str]  # OS-aware list of preferred MIDI outputs
    verbose: bool
    list_ports: bool

    # Audio Configuration
    audio_device_id: int | None  # Specific audio device ID, or None for default

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

    # UI Configuration - Button Hold
    hold_increment_rate: int  # milliseconds between increments when holding button

    # Preset Configuration
    preset_range_max: int  # Maximum MIDI program number (0-127)
    default_preset: int  # Default preset on startup (0-127)

    # Theme Configuration
    # Theme Configuration removed: theme mode is fixed to simplified palette

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        audio_device_str = os.getenv("AUDIO_DEVICE", "").strip()
        audio_device_id = None
        if audio_device_str:
            try:
                audio_device_id = int(audio_device_str)
            except ValueError:
                audio_device_id = None

        system = get_system()

        # Try to get explicit output override (for backward compatibility)
        explicit_output = None
        if system == "Darwin":
            explicit_output = os.getenv("MAC_OUTPUT", "").strip()
        elif system == "Linux":
            explicit_output = os.getenv("LINUX_OUTPUT", "").strip()
        else:
            explicit_output = os.getenv("OUTPUT", "").strip()

        # Build preferred outputs list: explicit override takes priority, then OS defaults
        preferred_outputs = []
        if explicit_output:
            # If explicit output is set, use it as the only preference
            preferred_outputs = [explicit_output]
        else:
            # Use OS-aware defaults
            preferred_outputs = OUTPUT_PATTERNS.get(system, [])

        # Also check for PREFER_OUTPUTS_OVERRIDE (comma-separated list)
        prefer_override = os.getenv("PREFER_OUTPUTS_OVERRIDE", "").strip()
        if prefer_override:
            preferred_outputs = [
                p.strip().strip('"').strip("'")
                for p in prefer_override.split(",")
                if p.strip()
            ]

        return cls(
            output=explicit_output or "",  # Keep for backward compatibility
            preferred_outputs=preferred_outputs,
            verbose=os.getenv("VERBOSE", "false").lower() == "true",
            list_ports=os.getenv("LIST_PORTS", "false").lower() == "true",
            audio_device_id=audio_device_id,
            short_press_threshold=int(os.getenv("SHORT_PRESS_THRESHOLD", "200")),
            long_press_threshold=int(os.getenv("LONG_PRESS_THRESHOLD", "500")),
            long_press_increment=int(os.getenv("LONG_PRESS_INCREMENT", "5")),
            window_width=int(os.getenv("WINDOW_WIDTH", "600")),
            window_height=int(os.getenv("WINDOW_HEIGHT", "400")),
            base_window_width=600,
            base_window_height=400,
            hold_increment_rate=int(os.getenv("HOLD_INCREMENT_RATE", "50")),
            preset_range_max=int(os.getenv("PRESET_RANGE_MAX", "127")),
            default_preset=int(os.getenv("DEFAULT_PRESET", "0")),
            # THEME_MODE deprecated/ignored; theme is simplified to three colors
        )
