"""Tests for TransposeHandler."""

import pytest
from unittest.mock import Mock
from src.gui.handlers.transpose_handler import TransposeHandler


def test_transpose_handler_adjust(app_context):
    """Test transpose adjustment."""
    handler = TransposeHandler(app_context)

    # Adjust up
    handler.adjust_transpose(1)
    assert app_context.processor.transpose == 1

    # Adjust down
    handler.adjust_transpose(-1)
    assert app_context.processor.transpose == 0

    # Reset
    handler.adjust_transpose(delta=5)
    assert app_context.processor.transpose == 5
    handler.adjust_transpose(reset=True)
    assert app_context.processor.transpose == 0


def test_transpose_handler_bounds(app_context):
    """Test transpose stays within bounds."""
    handler = TransposeHandler(app_context)

    # Set to max
    app_context.processor.transpose = 12
    handler.adjust_transpose(1)
    assert app_context.processor.transpose == 12  # Clamped to max

    # Set to min
    app_context.processor.transpose = -12
    handler.adjust_transpose(-1)
    assert app_context.processor.transpose == -12  # Clamped to min


def test_transpose_handler_long_press(app_context):
    """Test long press resets transpose."""
    app_context.processor.transpose = 5
    handler = TransposeHandler(app_context)

    handler.on_button_long_press()
    assert app_context.processor.transpose == 0
