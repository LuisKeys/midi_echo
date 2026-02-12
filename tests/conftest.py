"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from src.config import AppConfig
from src.gui.context import AppContext
from src.midi.processor import MidiProcessor


@pytest.fixture
def mock_config():
    """Fixture providing a mock AppConfig."""
    config = AppConfig(
        output="test_output",
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
    return config


@pytest.fixture
def mock_processor():
    """Fixture providing a mock MidiProcessor."""
    processor = Mock(spec=MidiProcessor)
    processor.transpose = 0
    processor.octave = 0
    processor.output_channel = None
    processor.fx_enabled = False
    processor.scale_enabled = False
    processor.arp_enabled = False
    return processor


@pytest.fixture
def mock_engine():
    """Fixture providing a mock MidiEngine."""
    engine = MagicMock()
    engine.queue = MagicMock()
    engine.queue.put_nowait = MagicMock()
    return engine


@pytest.fixture
def app_context(mock_processor, mock_engine):
    """Fixture providing an AppContext with mocked components."""
    context = AppContext(
        gui=None,
        engine=mock_engine,
        processor=mock_processor,
        event_loop=None,
    )
    return context
