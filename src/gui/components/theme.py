"""Theme and styling management."""

from typing import Tuple
from src.config import AppConfig


class Theme:
    """Manages colors and font sizing for the GUI.

    Responsible for:
    - Color palette definitions
    - Dynamic font size calculation based on window dimensions
    - Theme-aware color tuples for customtkinter consistency
    """

    # Color definitions
    COLORS = {
        "cyan": "#00FFFF",
        "violet": "#8A2BE2",
        "aqua": "#7FFFD4",
        "grey": "#E8E8E8",
        "red": "#FF0000",
        "bg": "#1A1A1A",
    }

    # Base font sizes at reference window resolution
    BASE_FONT_SIZES = {
        "popup_title": 36,
        "popup_value": 33,
        "popup_button": 42,
        "popup_close": 42,
        "main_button": 32,
    }

    def __init__(self, config: AppConfig):
        """Initialize theme with configuration.

        Args:
            config: AppConfig instance with window dimensions
        """
        self.config = config
        self.current_width = config.window_width
        self.current_height = config.window_height

    def get_color(self, name: str) -> str:
        """Get a color by name.

        Args:
            name: Color name (e.g., 'cyan', 'violet')

        Returns:
            Hex color string
        """
        return self.COLORS.get(name, "#000000")

    def get_color_tuple(self, name: str) -> Tuple[str, str]:
        """Get a color as a tuple for customtkinter light/dark modes.

        Args:
            name: Color name

        Returns:
            Tuple of (light_mode_color, dark_mode_color)
        """
        color = self.get_color(name)
        return (color, color)

    def get_font_size(self, element_type: str) -> int:
        """Calculate font size based on current window dimensions.

        Args:
            element_type: Type of element ('popup_title', 'popup_value', etc.)

        Returns:
            Calculated font size in points
        """
        # Calculate scale factor based on window size
        width_scale = self.current_width / self.config.base_window_width
        height_scale = self.current_height / self.config.base_window_height
        scale = (width_scale + height_scale) / 2

        base_size = self.BASE_FONT_SIZES.get(element_type, 12)
        return int(base_size * scale)

    def update_window_size(self, width: int, height: int) -> None:
        """Update current window size for font scaling.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.current_width = width
        self.current_height = height
