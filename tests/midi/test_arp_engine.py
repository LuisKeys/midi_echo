"""Unit tests for ArpState and basic ArpEngine structure."""

from src.midi.arp.state_validator import ArpState, TimingConfig


def test_arp_state_defaults():
    """Test that ArpState initializes with sensible defaults."""
    state = ArpState()

    assert state.enabled is False
    assert state.mode == "UP"
    assert state.octave == 1
    assert state.timing.bpm == 120
    assert state.timing.division == "1/8"
    assert state.gate_pct == 50
    assert len(state.pattern.mask) == 12
    assert all(state.pattern.mask), "Pattern should start with all steps active"
    assert state.velocity.fixed_velocity == 100


def test_arp_state_to_dict():
    """Test serialization to dict."""
    state = ArpState(
        enabled=True,
        mode="DOWN",
        timing=TimingConfig(bpm=140, division="1/16"),
    )
    d = state.to_dict()

    assert d["enabled"] is True
    assert d["mode"] == "DOWN"
    assert d["bpm"] == 140
    assert d["division"] == "1/16"


def test_arp_state_from_dict():
    """Test deserialization from dict."""
    data = {
        "enabled": True,
        "mode": "RANDOM",
        "bpm": 100,
        "octave": 2,
    }
    state = ArpState.from_dict(data)

    assert state.enabled is True
    assert state.mode == "RANDOM"
    assert state.timing.bpm == 100
    assert state.octave == 2


def test_arp_state_pattern_mask_mutation():
    """Test that pattern mask can be toggled."""
    state = ArpState()
    assert state.pattern.mask[0] is True

    state.pattern.mask[0] = False
    assert state.pattern.mask[0] is False

    state.pattern.mask[5] = False
    active = [i for i, v in enumerate(state.pattern.mask) if v]
    assert len(active) == 10  # 12 - 2 disabled
