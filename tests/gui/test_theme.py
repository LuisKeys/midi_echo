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


def test_theme_color_retrieval():
    """Test that theme colors are retrieved correctly."""
    config = _make_config()
    theme = Theme(config)

    assert theme.get_color("cyan") == "#00FFFF"
    assert theme.get_color("violet") == "#8A2BE2"
    assert theme.get_color("red") == "#FF0000"


def test_theme_color_tuple():
    """Test that color tuples are created correctly."""
    config = _make_config()
    theme = Theme(config)

    color_tuple = theme.get_color_tuple("cyan")
    assert color_tuple == ("#00FFFF", "#00FFFF")


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


def test_all_colors_defined():
    """Test that all expected colors are defined in the theme."""
    config = _make_config()
    theme = Theme(config)

    expected_colors = [
        "cyan",
        "violet",
        "aqua",
        "grey",
        "red",
        "bg",
        "overlay",
        "frame_bg",
        "selector_bg",
        "preset_highlight",
        "button_inactive",
        "button_inactive_light",
        "text_white",
        "text_black",
        "popup_grey",
    ]

    for color in expected_colors:
        assert color in theme.COLORS
