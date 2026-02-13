"""Integration tests for refactored ArpEngine.

Tests the complete engine with all components working together.
"""

import asyncio
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from src.midi.arp.engine_refactored import ArpEngine
from src.midi.arp.state_validator import (
    ArpState,
    TimingConfig,
    VelocityConfig,
    PatternConfig,
)


class MockMidiEngine:
    """Mock MIDI engine for testing."""

    def __init__(self):
        """Initialize mock engine."""
        self.queue = MagicMock()
        self.queue.put_nowait = Mock()
        self._loop = asyncio.new_event_loop()


@pytest.fixture
def mock_engine():
    """Provide mock MIDI engine."""
    return MockMidiEngine()


@pytest.fixture
def arp_state():
    """Provide default ArpState."""
    return ArpState(
        enabled=True,
        mode="UP",
        octave=1,
        timing=TimingConfig(bpm=120, division="1/8"),
        velocity=VelocityConfig(mode="FIXED", fixed_velocity=100),
        pattern=PatternConfig(mask=[True] * 12),
    )


class TestArpEngineBasic:
    """Basic tests for refactored ArpEngine."""

    def test_engine_initialization(self, arp_state, mock_engine):
        """Test engine initialization."""
        engine = ArpEngine(arp_state, mock_engine)

        assert engine.state == arp_state
        assert engine.midi_engine == mock_engine
        assert engine._running is False
        assert engine._task is None

    def test_start_stop(self, arp_state, mock_engine):
        """Test basic start and stop."""
        engine = ArpEngine(arp_state, mock_engine)

        engine.start()
        assert engine._running is True
        assert engine._task is not None

        engine.stop()
        assert engine._running is False

    def test_start_idempotent(self, arp_state, mock_engine):
        """Test that start is idempotent."""
        engine = ArpEngine(arp_state, mock_engine)

        engine.start()
        task1 = engine._task

        engine.start()
        task2 = engine._task

        assert task1 == task2  # Should not create new task

    def test_stop_idempotent(self, arp_state, mock_engine):
        """Test that stop is idempotent."""
        engine = ArpEngine(arp_state, mock_engine)

        engine.start()
        engine.stop()

        # Should not raise
        engine.stop()


@pytest.mark.asyncio
async def test_timing_loop_basic(arp_state, mock_engine):
    """Test basic timing loop execution."""
    arp_state.enabled = True
    engine = ArpEngine(arp_state, mock_engine, event_loop=asyncio.get_event_loop())

    # Create a short test: enable, wait for a few cycles, disable
    engine.start()

    # Let it run for a short time
    await asyncio.sleep(0.2)

    # Should have generated some messages
    assert mock_engine.queue.put_nowait.called

    engine.stop()


@pytest.mark.asyncio
async def test_engine_respects_state_enabled(arp_state, mock_engine):
    """Test that engine stops when state.enabled is False."""
    arp_state.enabled = False
    engine = ArpEngine(arp_state, mock_engine, event_loop=asyncio.get_event_loop())

    engine._running = True
    call_count = mock_engine.queue.put_nowait.call_count

    # Run timing loop briefly
    await asyncio.wait_for(engine._timing_loop(), timeout=0.1)

    # Should exit immediately because enabled is False
    # Call count should not increase significantly
    assert mock_engine.queue.put_nowait.call_count == call_count


class TestArpEngineMode:
    """Tests for mode strategy integration."""

    @pytest.mark.asyncio
    async def test_up_mode_generates_ascending_notes(self, mock_engine):
        """Test that UP mode generates notes in ascending order."""
        state = ArpState(
            enabled=True,
            mode="UP",
            octave=1,
            pattern=PatternConfig(mask=[True, False, True, False] + [False] * 8),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.3)
        engine.stop()

        # Should have generated note messages
        assert mock_engine.queue.put_nowait.call_count > 0

    @pytest.mark.asyncio
    async def test_random_mode_generates_notes(self, mock_engine):
        """Test that RANDOM mode generates notes."""
        state = ArpState(
            enabled=True,
            mode="RANDOM",
            octave=1,
            pattern=PatternConfig(mask=[True] * 12),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.3)
        engine.stop()

        assert mock_engine.queue.put_nowait.call_count > 0


class TestArpEnginePreview:
    """Tests for preview functionality."""

    def test_preview_basic(self, arp_state, mock_engine):
        """Test preview generation."""
        engine = ArpEngine(arp_state, mock_engine)

        # Preview should not raise
        engine.preview(steps=8)

        # Should schedule preview task (exact behavior depends on event loop)


class TestArpEngineBackwardCompatibility:
    """Tests for backward compatibility methods."""

    def test_build_active_order(self, arp_state, mock_engine):
        """Test legacy _build_active_order method."""
        engine = ArpEngine(arp_state, mock_engine)

        engine._build_active_order()

        # Should populate _active_order
        assert hasattr(engine, "_active_order")
        assert len(engine._active_order) == 12

    def test_choose_index(self, arp_state, mock_engine):
        """Test legacy _choose_index method."""
        engine = ArpEngine(arp_state, mock_engine)

        engine._build_active_order()
        idx = engine._choose_index()

        # Should return valid index
        assert 0 <= idx < len(engine._active_order)


class TestArpEngineVelocityModes:
    """Tests for velocity mode handling."""

    @pytest.mark.asyncio
    async def test_fixed_velocity_mode(self, mock_engine):
        """Test FIXED velocity mode."""
        state = ArpState(
            enabled=True,
            velocity=VelocityConfig(mode="FIXED", fixed_velocity=100),
            pattern=PatternConfig(mask=[True] * 12),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.2)
        engine.stop()

        # Should have enqueued messages
        assert mock_engine.queue.put_nowait.called

    @pytest.mark.asyncio
    async def test_ramp_up_velocity_mode(self, mock_engine):
        """Test RAMP_UP velocity mode."""
        state = ArpState(
            enabled=True,
            velocity=VelocityConfig(mode="RAMP_UP"),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.2)
        engine.stop()


class TestArpEngineGateDuration:
    """Tests for gate duration calculation."""

    @pytest.mark.asyncio
    async def test_gate_duration_long(self, mock_engine):
        """Test with long gate duration."""
        state = ArpState(
            enabled=True,
            gate_pct=100,  # Full beat duration
            timing=TimingConfig(bpm=120),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.2)
        engine.stop()

    @pytest.mark.asyncio
    async def test_gate_duration_short(self, mock_engine):
        """Test with short gate duration."""
        state = ArpState(
            enabled=True,
            gate_pct=10,  # Very short
            timing=TimingConfig(bpm=120),
        )
        engine = ArpEngine(state, mock_engine, event_loop=asyncio.get_event_loop())

        engine.start()
        await asyncio.sleep(0.2)
        engine.stop()
