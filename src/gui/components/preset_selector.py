"""Preset selector UI component for MIDI program selection."""

import customtkinter as ctk
import mido
import logging
from .layout_utils import LayoutSpacing
from src.gui.context import AppContext


logger = logging.getLogger(__name__)


def build_preset_selector(parent: ctk.CTkFrame, context: AppContext) -> None:
    """Build a preset selector grid with 0-127 MIDI programs.

    Args:
        parent: Parent frame to build the selector into
        context: AppContext for accessing handlers and components
    """
    if not context or not context.processor or not context.gui:
        logger.error("Missing context components for preset selector")
        return

    theme = context.gui.theme
    config = context.app_config
    preset_range_max = config.preset_range_max if config else 127
    current_program = getattr(
        context.gui.handlers["PS"] if context.gui else None, "current_program", 0
    )

    # Main container frame
    selector_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("selector_bg"))
    selector_frame.pack(
        expand=True,
        fill="both",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=LayoutSpacing.CONTAINER_PADY,
    )

    # Scrollable frame for the preset grid (handles overflow)
    scroll_frame = ctk.CTkScrollableFrame(
        selector_frame, fg_color=theme.get_color("selector_bg")
    )
    scroll_frame.pack(expand=True, fill="both")

    # Grid frame inside scrollable frame
    grid_frame = ctk.CTkFrame(scroll_frame, fg_color=theme.get_color("selector_bg"))
    grid_frame.pack(
        expand=True,
        fill="both",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=LayoutSpacing.CONTAINER_PADY,
    )

    buttons = []
    num_cols = 8  # 8 columns for preset buttons
    num_rows = (
        preset_range_max + 1 + num_cols - 1
    ) // num_cols  # Calculate needed rows

    # Configure grid weights for uniform sizing
    for c in range(num_cols):
        grid_frame.grid_columnconfigure(c, weight=1, uniform="col")
    for r in range(num_rows):
        grid_frame.grid_rowconfigure(r, weight=1, uniform="row")

    def update_font_sizes():
        """Update font sizes of preset buttons."""
        try:
            if not selector_frame.winfo_exists():
                return
            font_size = theme.get_font_size("label_small")

            for btn in buttons:
                btn.configure(font=("Arial", font_size))
        except Exception:
            pass

    selector_frame.update_font_sizes = update_font_sizes
    if hasattr(context.gui, "popup_manager"):
        context.gui.popup_manager.register_element("preset_selector", selector_frame)

    def make_preset_button(preset_num: int):
        """Create a handler for preset button click."""

        def _on_preset_click():
            # Send MIDI Program Change
            ch = context.processor.output_channel
            if ch is None:
                ch = 0  # Default to channel 0 if not set

            msg = mido.Message("program_change", channel=ch, program=preset_num)
            if context.event_loop:
                context.event_loop.call_soon_threadsafe(
                    context.engine.queue.put_nowait, msg
                )

            # Update handler state
            handler = context.gui.handlers.get("PS")
            if handler:
                handler.current_program = preset_num
                handler.update_ui()

            # Update button colors to highlight current preset
            for btn, num in zip(buttons, range(preset_range_max + 1)):
                if num == preset_num:
                    fg_color = theme.get_color_tuple("preset_highlight")
                else:
                    fg_color = theme.get_color_tuple("button_inactive")
                btn.configure(
                    fg_color=fg_color, text_color=theme.get_color("text_black")
                )

            logger.info(f"Preset {preset_num} selected (channel {ch})")

        return _on_preset_click

    # Create preset buttons
    for preset_num in range(preset_range_max + 1):
        row = preset_num // num_cols
        col = preset_num % num_cols

        # Highlight current preset
        is_current = preset_num == current_program
        if is_current:
            fg_color = theme.get_color_tuple("preset_highlight")
        else:
            fg_color = theme.get_color_tuple("button_inactive")

        btn = ctk.CTkButton(
            grid_frame,
            text=str(preset_num),
            fg_color=fg_color,
            text_color=theme.get_color("text_black"),
            corner_radius=0,
            height=50,
            command=make_preset_button(preset_num),
        )
        btn.grid(
            row=row,
            column=col,
            padx=LayoutSpacing.GRID_CELL_PADX,
            pady=LayoutSpacing.GRID_CELL_PADY,
            sticky="nsew",
        )
        buttons.append(btn)
