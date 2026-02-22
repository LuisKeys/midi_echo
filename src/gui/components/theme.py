"""Theme and styling management."""

from typing import Tuple
from src.config import AppConfig
from .layout_utils import LayoutSpacing


class Theme:
    """Manages colors and font sizing for the GUI.

    Uses a simplified 4-color theme system for easier maintenance and reasoning:
    - Background_Unselected: Inactive buttons, frames, overlays
    - Background_Selected: Active/selected buttons and controls
    - Background_Hover: Hover states
    - Font_and_Border: All text, labels, and borders

    Responsible for:
    - 4-color palette definitions (mapped through legacy semantic color names for backwards compatibility)
    - Dynamic font size calculation based on window dimensions
    - Theme-aware color tuples for customtkinter consistency
    """

    # Physical colors used in the application
    GREEN = "#00FF66"
    DARK_GREEN = "#006633"
    BLACK = "#000000"

    # 4 Canonical Color Theme
    # Simplified theme system using only 4 colors for easier maintenance and reasoning
    BACKGROUND_UNSELECTED = BLACK  # Inactive buttons, frames, overlays, defaults
    BACKGROUND_SELECTED = DARK_GREEN  # Active/selected buttons and controls
    BACKGROUND_HOVER = DARK_GREEN  # Hover states for buttons and controls
    FONT_AND_BORDER = GREEN  # All text, labels, and borders

    # Legacy Color Mapping: Maps old color names to the 4 canonical colors
    # This provides backwards compatibility with existing code that uses semantic color names.
    # Maintainers: When changing colors, only edit the 4 canonical colors above.
    LEGACY_COLOR_MAP = {
        # Active/selected states -> BACKGROUND_SELECTED
        "state_active": BACKGROUND_SELECTED,
        "state_playing": BACKGROUND_SELECTED,
        "state_recording": BACKGROUND_SELECTED,
        "state_metronome_on": BACKGROUND_SELECTED,
        # Inactive/default states -> BACKGROUND_UNSELECTED
        "state_default": BACKGROUND_UNSELECTED,
        "button_inactive": BACKGROUND_UNSELECTED,
        "button_inactive_light": BACKGROUND_UNSELECTED,
        "state_disabled": BACKGROUND_UNSELECTED,
        "state_stop": BACKGROUND_UNSELECTED,
        "state_metronome_off": BACKGROUND_UNSELECTED,
        "bg": BACKGROUND_UNSELECTED,
        "overlay": BACKGROUND_UNSELECTED,
        "frame_bg": BACKGROUND_UNSELECTED,
        "selector_bg": BACKGROUND_UNSELECTED,
        "preset_highlight": BACKGROUND_UNSELECTED,
        "control_bg": BACKGROUND_UNSELECTED,
        "control_pressed": BACKGROUND_UNSELECTED,
        "popup_grey": BACKGROUND_UNSELECTED,
        "main_menu_button": BACKGROUND_UNSELECTED,
        # Hover states -> BACKGROUND_HOVER
        "control_hover": BACKGROUND_HOVER,
        "state_warning": BACKGROUND_HOVER,
        # Text and borders -> FONT_AND_BORDER
        "text_white": FONT_AND_BORDER,
        "text_black": FONT_AND_BORDER,
        "button_text": FONT_AND_BORDER,
        "border": FONT_AND_BORDER,
        "red": FONT_AND_BORDER,
        "cyan": FONT_AND_BORDER,
        "violet": FONT_AND_BORDER,
        "aqua": FONT_AND_BORDER,
        "matrix_green": FONT_AND_BORDER,
        "matrix_green_bright": FONT_AND_BORDER,
        "matrix_green_dim": FONT_AND_BORDER,
        "matrix_green_muted": FONT_AND_BORDER,
        "grey": FONT_AND_BORDER,
    }

    # Keep compatibility fields for any callers/tests expecting these names
    COLORS_LIGHT = LEGACY_COLOR_MAP
    COLORS_DARK = LEGACY_COLOR_MAP

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
        # Theme mode removed: theme is now a single, fixed 4-color palette.
        self.current_width = config.window_width
        self.current_height = config.window_height

    def get_color(self, name: str) -> str:
        """Get a color by name.

        Args:
            name: Color name (e.g., 'state_active', 'button_text')

        Returns:
            Hex color string mapped to one of the 4 canonical theme colors
        """
        # Look up the color in the legacy mapping; fall back to BACKGROUND_UNSELECTED
        return self.LEGACY_COLOR_MAP.get(name, self.BACKGROUND_UNSELECTED)

    def get_color_tuple(self, name: str) -> Tuple[str, str]:
        """Get a color as a tuple for customtkinter light/dark modes.

        Args:
            name: Color name

        Returns:
            Tuple of (light_mode_color, dark_mode_color) both mapped to the same canonical color
        """
        # Look up the color in the legacy mapping; fall back to BACKGROUND_UNSELECTED
        color = self.LEGACY_COLOR_MAP.get(name, self.BACKGROUND_UNSELECTED)
        # Return identical light/dark tuple for compatibility with customtkinter
        return (color, color)

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
