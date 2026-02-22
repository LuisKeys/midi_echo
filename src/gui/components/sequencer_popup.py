"""Sequencer control popup with tabbed interface"""

import customtkinter as ctk
from .layout_utils import LayoutSpacing
from .tabs import _build_sequencer_tab


def build_sequencer_popup(parent: ctk.CTkFrame, context) -> None:
    """Build the sequencer control popup inside the given parent frame.

    Args:
        parent: Parent frame for the popup
        context: AppContext for accessing app components
    """
    sequencer = context.sequencer
    if sequencer is None:
        lbl = ctk.CTkLabel(
            parent,
            text="Sequencer not initialized.",
            text_color="red",
        )
        lbl.pack()
        return

    theme = context.gui.theme

    # Single frame for sequencer controls (no tabs needed for single tab)
    # But we still use a frame for consistent styling
    content_frame = ctk.CTkFrame(parent, fg_color=theme.get_color("frame_bg"))
    content_frame.pack(
        expand=True,
        fill="both",
        padx=LayoutSpacing.CONTAINER_PADX,
        pady=theme.get_padding("tab_container"),
    )

    # Build the sequencer tab content
    _build_sequencer_tab(content_frame, context)
