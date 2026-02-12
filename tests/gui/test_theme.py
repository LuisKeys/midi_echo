"""Tests for Theme component."""

import pytest
from src.gui.components.theme import Theme
from src.config import AppConfig


def test_theme_color_retrieval():
    """Test that theme colors are retrieved correctly."""
    config = AppConfig(
        output="test",
        verbose=False,
        list_ports=False,
        short_press_threshold=200,
        long_press_threshold=500,
        long_press_increment=5,
        window_width=600,
        window_height=400,
        base_window_width=600,
        base_window_height=400,
    )
    theme = Theme(config)

    assert theme.get_color("cyan") == "#00FFFF"
    assert theme.get_color("violet") == "#8A2BE2"
    assert theme.get_color("red") == "#FF0000"


def test_theme_color_tuple():
    """Test that color tuples are created correctly."""
    config = AppConfig(
        output="test",
        verbose=False,
        list_ports=False,
        short_press_threshold=200,
        long_press_threshold=500,
        long_press_increment=5,
        window_width=600,
        window_height=400,
        base_window_width=600,
        base_window_height=400,
    )
    theme = Theme(config)

    color_tuple = theme.get_color_tuple("cyan")
    assert color_tuple == ("#00FFFF", "#00FFFF")


def test_theme_font_size_calculation():
    """Test font size calculation at base resolution."""
    config = AppConfig(
        output="test",
        verbose=False,
        list_ports=False,
        short_press_threshold=200,
        long_press_threshold=500,
        long_press_increment=5,
        window_width=600,
        window_height=400,
        base_window_width=600,
        base_window_height=400,
    )
    theme = Theme(config)

    # At base resolution, font sizes should match base values
    assert theme.get_font_size("main_button") == 32
    assert theme.get_font_size("popup_title") == 36


def test_theme_font_size_scaling():
    """Test font size scaling at different resolutions."""
    config = AppConfig(
        output="test",
        verbose=False,
        list_ports=False,
        short_press_threshold=200,
        long_press_threshold=500,
        long_press_increment=5,
        window_width=600,
        window_height=400,
        base_window_width=600,
        base_window_height=400,
    )
    theme = Theme(config)

    # Update to 2x size
    theme.update_window_size(1200, 800)

    # Font sizes should double
    assert theme.get_font_size("main_button") == 64
    assert theme.get_font_size("popup_title") == 72
