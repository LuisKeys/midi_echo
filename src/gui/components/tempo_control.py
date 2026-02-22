"""Shared tempo control widget for ARP and Sequencer tabs."""

import customtkinter as ctk
from .widgets import IncrementDecrementWidget


def create_tempo_control(
    parent: ctk.CTkFrame,
    context,
    label_text: str,
    theme,
    label_width: int,
    show_tap: bool = True,
):
    """Create a synchronized tempo control with fast hold and optional tap tempo."""

    def on_tempo_changed(value: int) -> None:
        context.set_global_tempo(value, source_widget=tempo_widget)

    def on_tap() -> None:
        context.tap_tempo()

    tempo_widget = IncrementDecrementWidget(
        parent,
        label_text,
        20,
        300,
        context.get_global_tempo(),
        callback=on_tempo_changed,
        config=context.app_config,
        suffix=" BPM",
        tap_callback=on_tap if show_tap else None,
        theme=theme,
        label_width=label_width,
        hold_step=context.app_config.long_press_increment,
    )

    context.register_tempo_widget(tempo_widget)
    return tempo_widget
