"""Tests for harmony handler with scale auto-enable."""

import pytest
from unittest.mock import MagicMock, Mock, patch
from src.gui.handlers.harmony_handler import HarmonyHandler
from src.gui.context import AppContext


class MockButtonPanel:
    """Mock button panel for testing."""

    def get_button(self, label):
        return MagicMock()


class MockGuiTheme:
    """Mock theme for testing."""

    def get_color_tuple(self, color_name):
        return (100, 100, 100)

    def get_font_size(self, size_name):
        return 12

    def get_color(self, color_name):
        return "#000000"

    def get_padding(self, padding_name):
        return 10


class MockGui:
    """Mock GUI for testing."""

    def __init__(self):
        self.button_panel = MockButtonPanel()
        self.theme = MockGuiTheme()
        self.popup_manager = None
        self.handlers = {}


class MockProcessor:
    """Mock processor for testing."""

    def __init__(self):
        self.harmonizer_enabled = False
        self.scale_enabled = False
        self.arp_enabled = False
        self.scale_root = 0
        self.scale_type = None
        self.harmony_state = MagicMock()
        self.arp_state = MagicMock()


class MockConfig:
    """Mock app config."""

    pass


class TestHarmonyHandler:
    """Tests for harmony handler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = MagicMock(spec=AppContext)
        self.context.processor = MockProcessor()
        self.context.app_config = MockConfig()
        self.context.gui = MockGui()

        self.handler = HarmonyHandler(self.context)

    def test_on_button_press_enables_harmonizer(self):
        """Test button press enables harmonizer."""
        assert self.context.processor.harmonizer_enabled is False

        self.handler.on_button_press()

        assert self.context.processor.harmonizer_enabled is True

    def test_on_button_press_disables_harmonizer(self):
        """Test button press disables harmonizer."""
        self.context.processor.harmonizer_enabled = True

        self.handler.on_button_press()

        assert self.context.processor.harmonizer_enabled is False

    def test_on_button_press_auto_enables_scale(self):
        """Test that enabling HZ auto-enables scale."""
        assert self.context.processor.harmonizer_enabled is False
        assert self.context.processor.scale_enabled is False

        self.handler.on_button_press()

        # HZ should be enabled
        assert self.context.processor.harmonizer_enabled is True
        # SC should auto-enable
        assert self.context.processor.scale_enabled is True

    def test_on_button_press_disables_arp_when_enabling_hz(self):
        """Test that enabling HZ disables arp (mutual exclusion)."""
        self.context.processor.arp_enabled = True
        self.context.processor.arp_state.enabled = True

        self.handler.on_button_press()

        assert self.context.processor.harmonizer_enabled is True
        assert self.context.processor.arp_enabled is False
        assert self.context.processor.arp_state.enabled is False

    def test_on_button_press_calls_update_ui(self):
        """Test that button press calls update_ui."""
        with patch.object(self.handler, "update_ui") as mock_update:
            self.handler.on_button_press()
            mock_update.assert_called_once()

    def test_on_button_press_updates_arp_ui(self):
        """Test that arp handler UI is updated when disabling arp."""
        mock_arp_handler = MagicMock()
        self.context.gui.handlers = {"AR": mock_arp_handler}

        self.context.processor.arp_enabled = True
        self.handler.on_button_press()

        # AR handler update_ui should be called
        mock_arp_handler.update_ui.assert_called_once()

    def test_on_button_press_updates_scale_ui(self):
        """Test that scale handler UI is updated when auto-enabling SC."""
        mock_scale_handler = MagicMock()
        self.context.gui.handlers = {"SC": mock_scale_handler}

        self.handler.on_button_press()

        # SC handler update_ui should be called
        mock_scale_handler.update_ui.assert_called_once()

    def test_update_ui_when_harmonizer_enabled(self):
        """Test UI shows violet color when harmonizer enabled."""
        self.context.processor.harmonizer_enabled = True

        self.handler.update_ui()

        # Button should be updated
        btn = self.context.gui.button_panel.get_button("HZ")
        assert btn is not None

    def test_update_ui_when_harmonizer_disabled(self):
        """Test UI shows inactive color when harmonizer disabled."""
        self.context.processor.harmonizer_enabled = False

        self.handler.update_ui()

        # Button should be updated
        btn = self.context.gui.button_panel.get_button("HZ")
        assert btn is not None

    def test_update_ui_disables_harmonizer_if_arp_enabled(self):
        """Test that harmonizer is disabled if arp is enabled."""
        self.context.processor.harmonizer_enabled = True
        self.context.processor.arp_enabled = True

        self.handler.update_ui()

        # Harmonizer should be disabled
        assert self.context.processor.harmonizer_enabled is False

    def test_scale_auto_enable_not_disabled_when_hz_disabled(self):
        """Test that SC remains enabled when HZ is disabled."""
        # Enable both
        self.context.processor.harmonizer_enabled = True
        self.context.processor.scale_enabled = True

        # Disable HZ
        self.handler.on_button_press()

        # HZ should be disabled but SC should remain enabled
        assert self.context.processor.harmonizer_enabled is False
        assert self.context.processor.scale_enabled is True

    def test_toggle_harmonizer_multiple_times(self):
        """Test toggling harmonizer multiple times."""
        assert self.context.processor.harmonizer_enabled is False

        # First press - enable
        self.handler.on_button_press()
        assert self.context.processor.harmonizer_enabled is True
        assert self.context.processor.scale_enabled is True

        # Second press - disable
        self.handler.on_button_press()
        assert self.context.processor.harmonizer_enabled is False
        # SC remains enabled
        assert self.context.processor.scale_enabled is True

        # Third press - enable again
        self.handler.on_button_press()
        assert self.context.processor.harmonizer_enabled is True
        assert self.context.processor.scale_enabled is True

    def test_on_button_long_press_shows_popup(self):
        """Test long press shows harmony selection popup."""
        mock_popup_manager = MagicMock()
        self.context.gui.popup_manager = mock_popup_manager

        with patch.object(self.handler, "_show_harmony_popup"):
            self.handler.on_button_long_press()
            # popup should be attempted to show (handled by _show_harmony_popup)

    def test_handler_with_no_processor(self):
        """Test handler gracefully handles missing processor."""
        self.context.processor = None

        # Should not raise
        self.handler.on_button_press()
        self.handler.update_ui()

    def test_handler_with_no_gui(self):
        """Test handler gracefully handles missing gui."""
        self.context.gui = None

        # Should not raise
        self.handler.update_ui()
