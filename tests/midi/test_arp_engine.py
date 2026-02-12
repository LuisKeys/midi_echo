"""Unit tests for ArpState and basic ArpEngine structure."""

from src.midi.arp_state import ArpState


def test_arp_state_defaults():
    """Test that ArpState initializes with sensible defaults."""
    state = ArpState()

    assert state.enabled is False
    assert state.mode == "UP"
    assert state.octave == 1
    assert state.bpm == 120
    assert state.division == "1/8"
    assert state.gate_pct == 50
    assert len(state.pattern_mask) == 12
    assert all(state.pattern_mask), "Pattern should start with all steps active"
    assert state.fixed_velocity == 100


def test_arp_state_to_dict():
    """Test serialization to dict."""
    state = ArpState(
        enabled=True,
        mode="DOWN",
        bpm=140,
        division="1/16",
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
    assert state.bpm == 100
    assert state.octave == 2


def test_arp_state_pattern_mask_mutation():
    """Test that pattern mask can be toggled."""
    state = ArpState()
    assert state.pattern_mask[0] is True

    state.pattern_mask[0] = False
    assert state.pattern_mask[0] is False

    state.pattern_mask[5] = False
    active = [i for i, v in enumerate(state.pattern_mask) if v]
    assert len(active) == 10  # 12 - 2 disabled
