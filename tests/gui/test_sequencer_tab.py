"""Tests for sequencer tab transport button behavior."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.gui.components.tabs.sequencer_tab import (
    _on_play_clicked,
    _on_record_clicked,
    _update_button_states,
)


class _DummyButton:
    def __init__(self):
        self.state = {}

    def configure(self, **kwargs):
        self.state.update(kwargs)


def _make_context(is_playing=False, is_recording=False):
    sequencer = SimpleNamespace(
        state=SimpleNamespace(is_playing=is_playing, is_recording=is_recording),
        start_playback=Mock(return_value="start_playback_coro"),
        stop_playback=Mock(return_value="stop_playback_coro"),
        start_recording=Mock(return_value="start_recording_coro"),
        stop_recording=Mock(return_value="stop_recording_coro"),
    )

    gui = SimpleNamespace(
        _sequencer_play_button=_DummyButton(),
        _sequencer_record_button=_DummyButton(),
        root=SimpleNamespace(after=lambda _ms, callback: callback()),
    )

    return SimpleNamespace(
        sequencer=sequencer,
        gui=gui,
        event_loop=Mock(),
    )


def test_update_button_states_disables_play_while_recording():
    context = _make_context(is_playing=False, is_recording=True)

    _update_button_states(context)

    assert context.gui._sequencer_play_button.state["state"] == "disabled"
    assert context.gui._sequencer_record_button.state["state"] == "normal"


def test_update_button_states_disables_record_while_playing():
    context = _make_context(is_playing=True, is_recording=False)

    _update_button_states(context)

    assert context.gui._sequencer_play_button.state["state"] == "normal"
    assert context.gui._sequencer_record_button.state["state"] == "disabled"


def test_on_play_clicked_ignored_when_recording_active():
    context = _make_context(is_playing=False, is_recording=True)

    with patch(
        "src.gui.components.tabs.sequencer_tab.asyncio.run_coroutine_threadsafe"
    ) as submit:
        _on_play_clicked(context)

    submit.assert_not_called()


def test_on_record_clicked_ignored_when_playing_active():
    context = _make_context(is_playing=True, is_recording=False)

    with patch(
        "src.gui.components.tabs.sequencer_tab.asyncio.run_coroutine_threadsafe"
    ) as submit:
        _on_record_clicked(context)

    submit.assert_not_called()


def test_on_record_clicked_disables_play_immediately_when_arming():
    context = _make_context(is_playing=False, is_recording=False)

    class _Future:
        def add_done_callback(self, _callback):
            return None

    with patch(
        "src.gui.components.tabs.sequencer_tab.asyncio.run_coroutine_threadsafe",
        return_value=_Future(),
    ):
        _on_record_clicked(context)

    assert context.gui._sequencer_play_button.state["state"] == "disabled"
