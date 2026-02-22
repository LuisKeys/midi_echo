"""Sequencer tab for pattern recording and playback control"""

import customtkinter as ctk
import asyncio
from ..widgets import IncrementDecrementWidget
from ..layout_utils import LayoutSpacing
from ..tempo_control import create_tempo_control
from ..transport_controls import TransportControls


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
    compact_row_pad = max(2, theme.get_padding("popup_control") // 2)
    compact_transport_height = 50
    compact_control_height = 42

    # ── Transport Controls (now a reusable component) ──
    transport_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    transport_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(compact_row_pad, compact_row_pad),
    )

    transport_controls = TransportControls(
        transport_frame,
        theme,
        pm=pm,
        play_cb=lambda: _on_play_clicked(context),
        record_cb=lambda: _on_record_clicked(context),
        clear_cb=lambda: _on_clear_clicked(context),
        met_cb=lambda: _on_metronome_clicked(context),
        sequencer=sequencer,
    )
    transport_controls.pack(fill="x")
    for button in (
        transport_controls.play_button,
        transport_controls.record_button,
        transport_controls.clear_button,
        transport_controls.metronome_button,
    ):
        button.configure(height=compact_transport_height)

    # Keep compatibility attributes for existing logic/tests
    context.gui._sequencer_play_button = transport_controls.play_button
    context.gui._sequencer_record_button = transport_controls.record_button
    context.gui._sequencer_metronome_button = transport_controls.metronome_button
    pm.register_element("content_elements", transport_controls)

    # ── Pattern Info ──
    info_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    info_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, compact_row_pad),
    )

    info_label = ctk.CTkLabel(
        info_frame,
        text=f"Pattern: {sequencer.pattern.get_event_count()} events",
        font=("Arial", 12),
        text_color=theme.get_color("text_black"),
        anchor="w",
    )
    info_label.pack(side="left", padx=LayoutSpacing.ELEMENT_PADX)
    pm.register_element("content_elements", info_label)
    context.gui._sequencer_info_label = info_label

    # ── Tempo Control ──
    tempo_widget = create_tempo_control(
        parent,
        context,
        label_text="Tempo:",
        theme=theme,
        label_width=theme.get_label_width(),
        show_tap=True,
    )
    tempo_widget.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, compact_row_pad),
    )
    tempo_widget.minus_btn.configure(height=compact_control_height)
    tempo_widget.plus_btn.configure(height=compact_control_height)
    if hasattr(tempo_widget, "tap_btn"):
        tempo_widget.tap_btn.configure(height=compact_control_height)
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
        pady=(0, compact_row_pad),
    )
    time_sig_widget.minus_btn.configure(height=compact_control_height)
    time_sig_widget.plus_btn.configure(height=compact_control_height)

    # Denominator dropdown (separate frame for den selection)
    den_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    den_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, compact_row_pad),
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
        height=compact_control_height,
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
        pady=(0, compact_row_pad),
    )
    bars_widget.minus_btn.configure(height=compact_control_height)
    bars_widget.plus_btn.configure(height=compact_control_height)
    pm.register_element("content_elements", bars_widget)

    # ── Quantization ──
    quant_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    quant_frame.pack(
        fill="x",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=(0, compact_row_pad),
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
        height=compact_control_height,
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

    # Font size update
    def update_font_sizes():
        try:
            if not parent.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")
            # transport controls font
            try:
                transport_controls.update_font_sizes()
            except Exception:
                pass
            quant_label.configure(
                font=("Arial", font_size),
                width=theme.get_label_width(),
                anchor="e",
                text_color=theme.get_color("text_black"),
            )
            info_label.configure(
                font=("Arial", font_size),
                text_color=theme.get_color("text_black"),
                anchor="w",
            )
            # Ensure Time Sig denominator label and menu use the same font/width
            try:
                den_label = getattr(time_sig_widget, "_den_label", None)
                if den_label:
                    den_label.configure(
                        font=("Arial", font_size),
                        width=theme.get_label_width(),
                        anchor="e",
                        text_color=theme.get_color("text_black"),
                    )
                den_menu = getattr(time_sig_widget, "_den_menu", None)
                if den_menu:
                    den_menu.configure(font=("Arial", font_size))
            except Exception:
                pass
        except Exception:
            pass

    parent.update_font_sizes = update_font_sizes
    pm.register_element("content_elements", parent)
    update_font_sizes()


def _on_play_clicked(context):
    """Toggle play/stop"""
    sequencer = context.sequencer
    loop = context.event_loop

    if sequencer.state.is_recording:
        return

    if sequencer.state.is_playing:
        future = asyncio.run_coroutine_threadsafe(sequencer.stop_playback(), loop)
    else:
        future = asyncio.run_coroutine_threadsafe(sequencer.start_playback(), loop)

    _schedule_button_state_refresh(context, future)
    _update_button_states(context)


def _on_record_clicked(context):
    """Toggle recording"""
    sequencer = context.sequencer
    loop = context.event_loop

    if sequencer.state.is_playing and not sequencer.state.is_recording:
        return

    if sequencer.state.is_recording:
        context.gui._sequencer_record_arming = False
        future = asyncio.run_coroutine_threadsafe(sequencer.stop_recording(), loop)
    else:
        context.gui._sequencer_record_arming = True
        future = asyncio.run_coroutine_threadsafe(sequencer.start_recording(), loop)

    _schedule_button_state_refresh(context, future)
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

    play_button = getattr(context.gui, "_sequencer_play_button", None)
    record_button = getattr(context.gui, "_sequencer_record_button", None)

    record_arming = bool(getattr(context.gui, "_sequencer_record_arming", False))
    play_disabled = sequencer.state.is_recording or record_arming
    record_disabled = sequencer.state.is_playing

    if play_button:
        if sequencer.state.is_playing:
            play_button.configure(fg_color="#1565C0", text="Stop", state="normal")
        elif play_disabled:
            play_button.configure(fg_color="#757575", text="Play", state="disabled")
        else:
            play_button.configure(fg_color="#4CAF50", text="Play", state="normal")

    if record_button:
        if sequencer.state.is_recording:
            record_button.configure(fg_color="#D32F2F", text="Stop Rec", state="normal")
        elif record_disabled:
            record_button.configure(fg_color="#757575", text="Record", state="disabled")
        else:
            record_button.configure(fg_color="#FF9800", text="Record", state="normal")


def _schedule_button_state_refresh(context, future):
    """Refresh transport UI when async transport task settles."""

    def refresh():
        _update_button_states(context)

    def on_done(_):
        context.gui._sequencer_record_arming = False
        gui = getattr(context, "gui", None)
        root = getattr(gui, "root", None) if gui else None
        tk_root = getattr(gui, "tk_root", None) if gui else None
        scheduler = root or tk_root

        if scheduler and hasattr(scheduler, "after"):
            scheduler.after(0, refresh)
        else:
            refresh()

    if future is not None and hasattr(future, "add_done_callback"):
        future.add_done_callback(on_done)


def _update_info_label(context):
    """Update pattern info label"""
    info_label = getattr(context.gui, "_sequencer_info_label", None)
    if info_label:
        count = context.sequencer.pattern.get_event_count()
        info_label.configure(text=f"Pattern: {count} events")
