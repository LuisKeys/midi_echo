"""Comprehensive ARP control popup with tabbed interface."""

from typing import Callable
import customtkinter as ctk
from src.midi.arp.state_validator import ArpState
from .widgets import IncrementDecrementWidget
from .tabs import (
    _build_pattern_tab,
    _build_timing_tab,
    _build_modes_tab,
    _build_velocity_tab,
    _build_advanced_tab,
)


def build_pattern_editor(parent: ctk.CTkFrame, context) -> None:
    """Build a comprehensive ARP control interface inside the given parent frame.

    Uses tabs for organization: Pattern, Timing, Modes, Velocity, Advanced.
    """
    state = getattr(context.processor, "arp_state", None)
    if state is None:
        lbl = ctk.CTkLabel(parent, text="No arpeggiator state found.")
        lbl.pack()
        return

    # Main tabview
    tabview = ctk.CTkTabview(parent)
    tabview.pack(expand=True, fill="both", padx=10, pady=10)

    # Register tabview for font scaling
    if hasattr(parent.master, "popup_manager"):
        parent.master.popup_manager.register_element("content_elements", tabview)

    # Pattern Tab
    tabview.add("Pattern")
    _build_pattern_tab(tabview.tab("Pattern"), state, context)

    # Timing Tab
    tabview.add("Timing")
    _build_timing_tab(tabview.tab("Timing"), state, context)

    # Modes Tab
    tabview.add("Modes")
    _build_modes_tab(tabview.tab("Modes"), state, context)

    # Velocity Tab
    tabview.add("Velocity")
    _build_velocity_tab(tabview.tab("Velocity"), state, context)

    # Advanced Tab
    tabview.add("Advanced")
    _build_advanced_tab(tabview.tab("Advanced"), state, context)
