"""Tests for Theme component."""

import pytest
from src.gui.components.theme import Theme
from src.config import AppConfig


def _make_config():
    return AppConfig(
        output="test",
        verbose=False,
        list_ports=False,
        short_press_threshold=200,
        long_press_threshold=500,
        long_press_increment=5,
        hold_increment_rate=50,
        window_width=600,
        window_height=400,
        base_window_width=600,
        base_window_height=400,
        preset_range_max=127,
        default_preset=0,
    )


def test_theme_font_size_calculation():
    """Test font size calculation at base resolution."""
    config = _make_config()
    theme = Theme(config)

    # At base resolution, font sizes should match base values
    assert theme.get_font_size("main_button") == 32
    assert theme.get_font_size("popup_title") == 20


def test_theme_font_size_scaling():
    """Test font size scaling at different resolutions."""
    config = _make_config()
    theme = Theme(config)

    # Update to 2x size
    theme.update_window_size(1200, 800)

    # Font sizes should double
    assert theme.get_font_size("main_button") == 64
    assert theme.get_font_size("popup_title") == 40


def test_canonical_theme_colors_exist():
    """Test that the 4 canonical theme colors and accent color are defined."""
    config = _make_config()
    theme = Theme(config)

    # Verify the 4 canonical color constants exist and are hex colors
    assert theme.BACKGROUND_UNSELECTED == "#000000"
    assert theme.BACKGROUND_SELECTED == "#006633"
    assert theme.BACKGROUND_HOVER == "#006633"
    assert theme.FONT_AND_BORDER == "#00FF66"
    assert theme.ACCENT_RED == "#FF3333"

    # Verify they are properly assigned
    assert isinstance(theme.BACKGROUND_UNSELECTED, str)
    assert isinstance(theme.BACKGROUND_SELECTED, str)
    assert isinstance(theme.BACKGROUND_HOVER, str)
    assert isinstance(theme.FONT_AND_BORDER, str)
    assert isinstance(theme.ACCENT_RED, str)
