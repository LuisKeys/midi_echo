"""Custom tabview with full control over tab button colors."""

import customtkinter as ctk
from typing import Dict, List, Callable, Optional


class CustomTabView(ctk.CTkFrame):
    """Custom tab view with customizable tab button styling.

    Provides a tabbed interface with full control over colors and appearance.
    Unlike CTkTabview, allows complete customization of tab button backgrounds.
    """

    def __init__(
        self, master, theme, fg_color="transparent", bg_color="transparent", **kwargs
    ):
        """Initialize custom tabview.

        Args:
            master: Parent widget
            theme: Theme object with color methods
            fg_color: Frame foreground color
            bg_color: Frame background color
        """
        super().__init__(master, fg_color=fg_color, bg_color=bg_color, **kwargs)

        self.theme = theme
        self._tabs: Dict[str, ctk.CTkFrame] = {}
        self._tab_buttons: Dict[str, ctk.CTkButton] = {}
        self._current_tab: Optional[str] = None
        self._tab_order: List[str] = []

        # Create tab button frame
        self.tab_button_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme.get_color("frame_bg"),
            bg_color=self.theme.get_color("frame_bg"),
        )
        self.tab_button_frame.pack(side="top", fill="x")

        # Create tab content frame
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme.get_color("frame_bg"),
            bg_color=self.theme.get_color("frame_bg"),
        )
        self.content_frame.pack(side="top", fill="both", expand=True)

    def add(self, tab_name: str) -> ctk.CTkFrame:
        """Add a new tab.

        Args:
            tab_name: Name of the tab

        Returns:
            Frame for the tab content
        """
        # Create tab content frame
        tab_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.theme.get_color("frame_bg"),
        )
        self._tabs[tab_name] = tab_frame
        self._tab_order.append(tab_name)

        # Create tab button
        tab_button = ctk.CTkButton(
            self.tab_button_frame,
            text=tab_name,
            corner_radius=0,
            fg_color=self.theme.get_color("control_bg"),
            hover_color=self.theme.get_color("control_hover"),
            text_color=self.theme.get_color("text_black"),
            font=("Courier New", self.theme.get_font_size("tab_text")),
            command=lambda: self._switch_tab(tab_name),
            height=50,
        )
        tab_button.pack(side="left", fill="both", expand=True)
        self._tab_buttons[tab_name] = tab_button

        # Auto-select first tab
        if len(self._tabs) == 1:
            self._switch_tab(tab_name)

        return tab_frame

    def _switch_tab(self, tab_name: str) -> None:
        """Switch to a different tab.

        Args:
            tab_name: Name of the tab to switch to
        """
        # Hide all tabs
        for frame in self._tabs.values():
            frame.pack_forget()

        # Update button colors
        for name, button in self._tab_buttons.items():
            if name == tab_name:
                # Active tab: use selected color
                button.configure(
                    fg_color=self.theme.get_color("state_active"),
                    text_color=self.theme.get_color("text_black"),
                    hover_color=self.theme.get_color("state_active"),
                )
            else:
                # Inactive tab: use control background
                button.configure(
                    fg_color=self.theme.get_color("control_bg"),
                    text_color=self.theme.get_color("text_black"),
                    hover_color=self.theme.get_color("control_hover"),
                )

        # Show selected tab
        if tab_name in self._tabs:
            self._tabs[tab_name].pack(fill="both", expand=True)
            self._current_tab = tab_name

    def tab(self, tab_name: str) -> ctk.CTkFrame:
        """Get a tab frame by name.

        Args:
            tab_name: Name of the tab

        Returns:
            Frame for the tab content
        """
        return self._tabs.get(tab_name, None)
