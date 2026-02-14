"""Theme and styling management."""

from typing import Tuple
from src.config import AppConfig
from .layout_utils import LayoutSpacing


class Theme:
    """Manages colors and font sizing for the GUI.

    Responsible for:
    - Color palette definitions for light and dark modes
    - Dynamic font size calculation based on window dimensions
    - Theme-aware color tuples for customtkinter consistency
    """

    # Color definitions for light mode
    COLORS_LIGHT = {
        "cyan": "#B3E5FC",
        "violet": "#F8BBD9",
        "aqua": "#C8E6C9",
        "grey": "#F5F5F5",
        "red": "#FFCDD2",
        "bg": "#A3A3a3",
        "overlay": "#E8F5E8",
        "frame_bg": "#A3A3a3",
        "selector_bg": "#c9c8c8",
        "preset_highlight": "#A3A3a3",
        "button_inactive": "#B0BEC5",
        "button_inactive_light": "#CFD8DC",
        "text_white": "#CCCBCB",
        "text_black": "#454444",
        "button_text": "#000000",
        "popup_grey": "#A3A3a3",
    }

    # Color definitions for dark mode
    COLORS_DARK = {
        "cyan": "#B3E5FC",
        "violet": "#F8BBD9",
        "aqua": "#C8E6C9",
        "grey": "#F5F5F5",
        "red": "#FFCDD2",
        "bg": "#2D2D2D",
        "overlay": "#1E3A1E",
        "frame_bg": "#2D2D2D",
        "selector_bg": "#4D4D4D",
        "preset_highlight": "#2D2D2D",
        "button_inactive": "#555555",
        "button_inactive_light": "#666666",
        "text_white": "#FFFFFF",
        "text_black": "#D3D3D3",
        "button_text": "#000000",
        "popup_grey": "#2D2D2D",
    }

    # Base font sizes at reference window resolution (600x400)
    BASE_FONT_SIZES = {
        "popup_title": 20,
        "popup_value": 18,
        "popup_button": 20,
        "popup_close": 16,
        "main_button": 32,
        "tab_text": 18,
        "label_small": 14,
        "label_medium": 16,
        "increment_button": 14,
    }

    # Base padding values at reference window resolution
    BASE_PADDINGS = {
        "popup_control": 20,  # Vertical padding between controls in popups
        "popup_control_small": 10,  # Smaller padding for intermediate spacing
        "popup_frame": 20,  # Padding for popup frames and containers
        "tab_container": 20,  # Padding for tabview containers
    }

    def __init__(self, config: AppConfig):
        """Initialize theme with configuration.

        Args:
            config: AppConfig instance with window dimensions and theme mode
        """
        self.config = config
        self.mode = config.theme_mode
        self.current_width = config.window_width
        self.current_height = config.window_height

    def get_color(self, name: str) -> str:
        """Get a color by name.

        Args:
            name: Color name (e.g., 'cyan', 'violet')

        Returns:
            Hex color string
        """
        colors = self.COLORS_LIGHT if self.mode == "light" else self.COLORS_DARK
        return colors.get(name, "#000000")

    def get_color_tuple(self, name: str) -> Tuple[str, str]:
        """Get a color as a tuple for customtkinter light/dark modes.

        Args:
            name: Color name

        Returns:
            Tuple of (light_mode_color, dark_mode_color)
        """
        light_color = self.COLORS_LIGHT.get(name, "#000000")
        dark_color = self.COLORS_DARK.get(name, "#000000")
        return (light_color, dark_color)

    def get_font_size(self, element_type: str) -> int:
        """Calculate font size based on current window dimensions.

        Args:
            element_type: Type of element ('popup_title', 'popup_value', etc.)

        Returns:
            Calculated font size in points
        """
        base_size = self.BASE_FONT_SIZES.get(element_type, 12)
        return int(base_size * self.get_scale())

    def get_padding(self, element_type: str) -> int:
        """Calculate padding based on current window dimensions.

        Args:
            element_type: Type of element ('popup_control', 'popup_frame', etc.)

        Returns:
            Calculated padding in pixels
        """
        base_padding = self.BASE_PADDINGS.get(element_type, 10)
        return int(base_padding * self.get_scale())

    def get_scale(self) -> float:
        """Get the current scaling factor based on window dimensions.

        Returns:
            Scale factor where 1.0 is the base resolution
        """
        width_scale = self.current_width / self.config.base_window_width
        height_scale = self.current_height / self.config.base_window_height
        return (width_scale + height_scale) / 2

    def get_label_width(self) -> int:
        """Get uniform width for all control labels in pixels.

        Returns:
            Width in pixels (scales with font size)
        """
        # Calculate based on 18 characters at current font size
        # Using ~8 pixels per character as base estimate for 14pt font
        base_width = 144  # 18 chars × 8 pixels/char at base resolution
        return int(base_width * self.get_scale())

    def get_value_width(self) -> int:
        """Get uniform width for value display labels in pixels.

        Returns:
            Width in pixels (scales with font size) to fit 3 digits comfortably
        """
        # Width to fit 3 digits at 16pt font (e.g., "300")
        # Using ~10 pixels per character for 16pt font
        base_width = 50  # Approximately 3 digits at base resolution
        return int(base_width * self.get_scale())

    def update_window_size(self, width: int, height: int) -> None:
        """Update current window size for font scaling.

        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        self.current_width = width
        self.current_height = height
