"""Tests for PresetHandler."""

import pytest
from unittest.mock import Mock, MagicMock
from src.gui.handlers.preset_handler import PresetHandler
from src.gui.context import AppContext


def create_test_context(default_preset=0, with_gui=False):
    """Helper to create a test context with proper mocking."""
    mock_config = Mock()
    mock_config.default_preset = default_preset

    mock_processor = Mock()
    mock_processor.output_channel = 0

    mock_engine = Mock()
    mock_engine.queue = Mock()

    gui = None
    event_loop = None

    if with_gui:
        gui = Mock()
        gui.button_panel = Mock()
        gui.theme = Mock()
        gui.theme.get_color_tuple = Mock(return_value=("cyan", "cyan"))
        gui.popup_manager = Mock()
        gui.handlers = {}
        event_loop = Mock()

    context = AppContext(
        gui=gui,
        engine=mock_engine,
        processor=mock_processor,
        event_loop=event_loop,
    )
    context.app_config = mock_config
    return context


def test_preset_handler_init():
    """Test preset handler initialization."""
    context = create_test_context(default_preset=5)
    handler = PresetHandler(context)

    assert handler.current_program == 5


def test_preset_handler_init_default():
    """Test preset handler initialization with default."""
    context = create_test_context(default_preset=0)
    handler = PresetHandler(context)

    assert handler.current_program == 0


def test_preset_handler_update_ui():
    """Test preset handler updates PS button color."""
    context = create_test_context(with_gui=True)

    mock_button = Mock()
    context.gui.button_panel.get_button = Mock(return_value=mock_button)

    handler = PresetHandler(context)
    handler.update_ui()

    # Verify button was retrieved
    context.gui.button_panel.get_button.assert_called_with("PS")

    # Verify button color was configured to cyan
    mock_button.configure.assert_called_once()


def test_preset_handler_on_button_press_opens_modal():
    """Test that pressing PS button opens preset selector modal."""
    context = create_test_context(with_gui=True)

    mock_popup = Mock()
    context.gui.popup_manager.create_popup = Mock(return_value=mock_popup)

    handler = PresetHandler(context)
    handler.on_button_press()

    # Verify popup was created and shown
    context.gui.popup_manager.create_popup.assert_called_once()
    mock_popup.show.assert_called_once()


def test_preset_handler_long_press_does_nothing():
    """Test that long press does nothing (no-op)."""
    context = create_test_context()
    handler = PresetHandler(context)

    # This should not raise any exceptions
    handler.on_button_long_press()

    # Verify nothing changed
    assert handler.current_program == 0


def test_preset_handler_wrap_around():
    """Test that preset handler properly wraps preset numbers."""
    context = create_test_context()
    handler = PresetHandler(context)

    # Set initial program
    handler.current_program = 50
    assert handler.current_program == 50

    # Update to another program
    handler.current_program = 127
    assert handler.current_program == 127

    # Wrap to 0
    handler.current_program = 0
    assert handler.current_program == 0
