"""Sequencer tab for pattern recording and playback control"""

import customtkinter as ctk
import asyncio
from ..widgets import IncrementDecrementWidget
from ..layout_utils import LayoutSpacing


def _build_sequencer_tab(parent: ctk.CTkFrame, context) -> None:
    """Build the Sequencer tab with pattern control and configuration.

    Layout:
    - Transport buttons: Play, Record, Clear, Metronome
    - Controls: Tempo, Time Signature, Pattern Bars, Quantization
    """
    sequencer = context.sequencer
    if not sequencer:
        error_label = ctk.CTkLabel(
            parent,
            text="Sequencer not initialized",
            text_color="red",
        )
        error_label.pack(padx=20, pady=20)
        return

    config = context.app_config
    theme = context.gui.theme
    pm = context.gui.popup_manager

    # ── Transport Controls Frame ──
    transport_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    transport_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(theme.get_padding("popup_control"), theme.get_padding("popup_control")),
    )

    transport_label = ctk.CTkLabel(
        transport_frame,
        text="Transport:",
        font=("Arial", 14),
        text_color=theme.get_color("text_black"),
    )
    transport_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", transport_label)

    # Play button
    play_button = ctk.CTkButton(
        transport_frame,
        text="Play",
        command=lambda: _on_play_clicked(context),
        width=80,
        height=50,
        corner_radius=0,
        fg_color="#4CAF50",
        hover_color="#45a049",
        font=("Arial", 14),
    )
    play_button.pack(side="left", padx=2)
    pm.register_element("content_elements", play_button)
    context.gui._sequencer_play_button = play_button  # Store for state updates

    # Record button
    record_button = ctk.CTkButton(
        transport_frame,
        text="Record",
        command=lambda: _on_record_clicked(context),
        width=80,
        height=50,
        corner_radius=0,
        fg_color="#FF9800",
        hover_color="#F57C00",
        font=("Arial", 14),
    )
    record_button.pack(side="left", padx=2)
    pm.register_element("content_elements", record_button)
    context.gui._sequencer_record_button = record_button

    # Clear button
    clear_button = ctk.CTkButton(
        transport_frame,
        text="Clear",
        command=lambda: _on_clear_clicked(context),
        width=80,
        height=50,
        corner_radius=0,
        fg_color="#9C27B0",
        hover_color="#7B1FA2",
        font=("Arial", 14),
    )
    clear_button.pack(side="left", padx=2)
    pm.register_element("content_elements", clear_button)

    # Metronome toggle button
    metronome_button = ctk.CTkButton(
        transport_frame,
        text="Met",
        command=lambda: _on_metronome_clicked(context),
        width=80,
        height=50,
        corner_radius=0,
        fg_color="#2196F3" if sequencer.state.metronome_enabled else "#757575",
        hover_color="#1976D2",
        font=("Arial", 14),
    )
    metronome_button.pack(side="left", padx=2)
    pm.register_element("content_elements", metronome_button)
    context.gui._sequencer_metronome_button = metronome_button

    # ── Tempo Control ──
    tempo_widget = IncrementDecrementWidget(
        parent,
        "Tempo:",
        20,
        300,
        sequencer.state.tempo,
        callback=lambda v: sequencer.set_tempo(v),
        config=config,
        suffix=" BPM",
        theme=theme,
        label_width=theme.get_label_width(),
    )
    tempo_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", tempo_widget)

    # ── Time Signature ──
    def on_time_sig_changed(new_num):
        """Update time signature numerator"""
        sequencer.set_time_signature(new_num, sequencer.state.time_signature_den)

    time_sig_widget = IncrementDecrementWidget(
        parent,
        "Time Sig:",
        2,
        16,
        sequencer.state.time_signature_num,
        callback=on_time_sig_changed,
        config=config,
        suffix=f"/{sequencer.state.time_signature_den}",
        theme=theme,
        label_width=theme.get_label_width(),
    )
    time_sig_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", time_sig_widget)

    # Denominator dropdown (separate frame for den selection)
    den_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    den_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    den_label = ctk.CTkLabel(
        den_frame,
        text="Time Sig Den:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    den_label.configure(width=theme.get_label_width())
    den_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", den_label)

    den_var = ctk.StringVar(value=str(sequencer.state.time_signature_den))

    def on_den_changed(value):
        try:
            den = int(value)
            sequencer.set_time_signature(sequencer.state.time_signature_num, den)
        except:
            pass

    den_menu = ctk.CTkOptionMenu(
        den_frame,
        values=["2", "4", "8", "16"],
        variable=den_var,
        command=on_den_changed,
        width=80,
        height=40,
        corner_radius=0,
        fg_color="#B0BEC5",
        button_color="#B0BEC5",
        button_hover_color="#B0BEC5",
        text_color=theme.get_color("button_text"),
        font=("Arial", 14),
        dropdown_font=("Arial", 20),
    )
    den_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", den_menu)

    # Store reference for font updates
    time_sig_widget._den_label = den_label
    time_sig_widget._den_menu = den_menu

    # ── Pattern Bars ──
    bars_widget = IncrementDecrementWidget(
        parent,
        "Pattern Bars:",
        1,
        8,
        sequencer.state.pattern_bars,
        callback=lambda v: sequencer.set_pattern_bars(v),
        config=config,
        theme=theme,
        label_width=theme.get_label_width(),
    )
    bars_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )
    pm.register_element("content_elements", bars_widget)

    # ── Quantization ──
    quant_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    quant_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, theme.get_padding("popup_control")),
    )

    quant_label = ctk.CTkLabel(
        quant_frame,
        text="Quantize:",
        font=("Arial", 14),
        anchor="e",
        text_color=theme.get_color("text_black"),
    )
    quant_label.configure(width=theme.get_label_width())
    quant_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", quant_label)

    quant_var = ctk.StringVar(value=sequencer.state.quantization)
    quant_menu = ctk.CTkOptionMenu(
        quant_frame,
        values=["1/4", "1/8", "1/16", "1/32"],
        variable=quant_var,
        command=lambda v: sequencer.set_quantization(v),
        width=80,
        height=40,
        corner_radius=0,
        fg_color="#B0BEC5",
        button_color="#B0BEC5",
        button_hover_color="#B0BEC5",
        text_color=theme.get_color("button_text"),
        font=("Arial", 14),
        dropdown_font=("Arial", 20),
    )
    quant_menu.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", quant_menu)

    # ── Pattern Info ──
    info_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    info_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(theme.get_padding("popup_control"), 0),
    )

    info_label = ctk.CTkLabel(
        info_frame,
        text=f"Pattern: {sequencer.pattern.get_event_count()} events",
        font=("Arial", 12),
        text_color=theme.get_color("text_black"),
    )
    info_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", info_label)
    context.gui._sequencer_info_label = info_label

    # Font size update
    def update_font_sizes():
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            transport_label.configure(
                font=("Arial", font_size),
                text_color=theme.get_color("text_black"),
            )
            quant_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            info_label.configure(
                font=("Arial", font_size), text_color=theme.get_color("text_black")
            )
        except Exception:
            pass

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()


def _on_play_clicked(context):
    """Toggle play/stop"""
    sequencer = context.sequencer
    loop = context.event_loop

    if sequencer.state.is_playing:
        asyncio.run_coroutine_threadsafe(sequencer.stop_playback(), loop)
    else:
        asyncio.run_coroutine_threadsafe(sequencer.start_playback(), loop)

    _update_button_states(context)


def _on_record_clicked(context):
    """Toggle recording"""
    sequencer = context.sequencer
    loop = context.event_loop

    if sequencer.state.is_recording:
        asyncio.run_coroutine_threadsafe(sequencer.stop_recording(), loop)
    else:
        asyncio.run_coroutine_threadsafe(sequencer.start_recording(), loop)

    _update_button_states(context)


def _on_clear_clicked(context):
    """Clear pattern"""
    context.sequencer.clear_pattern()
    _update_info_label(context)


def _on_metronome_clicked(context):
    """Toggle metronome"""
    context.sequencer.toggle_metronome()

    # Update button color
    button = getattr(context.gui, "_sequencer_metronome_button", None)
    if button:
        theme = context.gui.theme
        if context.sequencer.state.metronome_enabled:
            button.configure(fg_color="#2196F3")
        else:
            button.configure(fg_color="#757575")


def _update_button_states(context):
    """Update transport button appearance based on state"""
    sequencer = context.sequencer
    theme = context.gui.theme

    play_button = getattr(context.gui, "_sequencer_play_button", None)
    record_button = getattr(context.gui, "_sequencer_record_button", None)

    if play_button:
        if sequencer.state.is_playing:
            play_button.configure(fg_color="#1565C0", text="Stop")
        else:
            play_button.configure(fg_color="#4CAF50", text="Play")

    if record_button:
        if sequencer.state.is_recording:
            record_button.configure(fg_color="#D32F2F", text="Stop Rec")
        else:
            record_button.configure(fg_color="#FF9800", text="Record")


def _update_info_label(context):
    """Update pattern info label"""
    info_label = getattr(context.gui, "_sequencer_info_label", None)
    if info_label:
        count = context.sequencer.pattern.get_event_count()
        info_label.configure(text=f"Pattern: {count} events")
