"""Popup menu management for modal dialogs."""

import customtkinter as ctk
from typing import Callable, Dict, Optional, Any


class PopupManager:
    """Manages modal popup dialogs.

    Responsible for:
    - Creating and showing popup overlays
    - Managing popup lifecycle (show/hide/close)
    - Tracking popup elements for font updates
    """

    def __init__(self, parent: ctk.CTk):
        """Initialize popup manager.

        Args:
            parent: Parent widget (the main GUI window)
        """
        self.parent = parent
        self.active_popup: Optional[ctk.CTkFrame] = None
        self.overlay: Optional[ctk.CTkFrame] = None

        # Track popup elements for dynamic updates
        self.popup_elements: Dict[str, Any] = {
            "title_label": None,
            "close_btn": None,
            "content_elements": [],
        }

    def create_popup(
        self,
        title: str,
        content_builder: Callable,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "PopupMenu":
        """Create a new popup.

        Args:
            title: Popup title
            content_builder: Function to build popup content
            width: Popup width (defaults to 80% of parent)
            height: Popup height (defaults to 80% of parent)

        Returns:
            PopupMenu instance
        """
        # Close any existing popup
        if self.active_popup:
            self._close_current()

        # Calculate dimensions
        self.parent.update_idletasks()
        if width is None:
            width = int(self.parent.winfo_width() * 0.8)
        if height is None:
            height = int(self.parent.winfo_height() * 0.8)

        # Create popup
        popup = PopupMenu(
            parent=self.parent,
            title=title,
            content_builder=content_builder,
            popup_manager=self,
            width=width,
            height=height,
        )

        self.active_popup = popup
        return popup

    def _close_current(self) -> None:
        """Close the currently active popup."""
        if self.active_popup:
            try:
                if self.overlay:
                    self.overlay.place_forget()
                    self.overlay.destroy()
                self.overlay = None
                self.active_popup.place_forget()
                self.active_popup.destroy()
            except Exception:
                pass

            self.active_popup = None
            self.popup_elements = {
                "title_label": None,
                "close_btn": None,
                "content_elements": [],
            }

    def _create_overlay(self) -> ctk.CTkFrame:
        """Create a semi-transparent overlay with click-to-close functionality."""
        # Use a dark theme-tinted color (dark violet) instead of pure black
        overlay_color = "#3D1A6D"
        overlay = ctk.CTkFrame(self.parent, fg_color=overlay_color)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.configure(fg_color=(overlay_color, overlay_color))

        try:
            # Increased opacity from 0.5 to 0.65 for better visual separation
            overlay.attributes("-alpha", 0.65)
        except Exception:
            pass  # May not be supported on all platforms

        # Bind click event on overlay to close popup
        overlay.bind("<Button-1>", lambda e: self._close_current())

        overlay.lower()
        self.overlay = overlay
        return overlay

    def register_element(self, key: str, element: Any) -> None:
        """Register a popup element for tracking.

        Args:
            key: Element identifier
            element: The widget element
        """
        self.popup_elements[key] = element

    def is_popup_open(self) -> bool:
        """Check if a popup is currently open."""
        return self.active_popup is not None


class PopupMenu(ctk.CTkFrame):
    """A modal popup menu overlay."""

    def __init__(
        self,
        parent: ctk.CTk,
        title: str,
        content_builder: Callable,
        popup_manager: PopupManager,
        width: int,
        height: int,
    ):
        """Initialize popup.

        Args:
            parent: Parent widget
            title: Popup title
            content_builder: Function to build content
            popup_manager: PopupManager instance for lifecycle management
            width: Popup width
            height: Popup height
        """
        super().__init__(
            parent, fg_color="#2A2A2A", corner_radius=10, width=width, height=height
        )

        self.parent = parent
        self.popup_manager = popup_manager
        self.title_text = title
        self.content_builder = content_builder
        self.popup_width = width
        self.popup_height = height

        # Create overlay
        self.popup_manager._create_overlay()

        # Prevent shrinking
        self.pack_propagate(False)

        # Build layout
        self._create_layout()

        # Bind click event to prevent propagation to overlay
        self.bind("<Button-1>", lambda e: None)

    def _create_layout(self) -> None:
        """Create popup layout."""
        # Top bar with title and close button
        top_frame = ctk.CTkFrame(self, fg_color="#2A2A2A")
        top_frame.pack(fill="x", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            top_frame,
            text=self.title_text,
            font=("Arial", 32, "bold"),
            text_color="#FFFFFF",
        )
        title_label.pack(side="left", fill="x", expand=True)
        self.popup_manager.register_element("title_label", title_label)

        close_btn = ctk.CTkButton(
            top_frame,
            text="✕",
            font=("Arial", 24, "bold"),
            fg_color="#555555",
            text_color="white",
            hover_color="#FF0000",
            width=60,
            height=60,
            command=self.close,
        )
        close_btn.pack(side="right")
        self.popup_manager.register_element("close_btn", close_btn)

        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="#2A2A2A")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Build content
        self.content_builder(content_frame)

    def show(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Show the popup.

        Args:
            x: X position (centers on parent if None)
            y: Y position (centers on parent if None)
        """
        self.parent.update_idletasks()

        if x is None or y is None:
            x = (self.parent.winfo_width() - self.popup_width) // 2
            y = (self.parent.winfo_height() - self.popup_height) // 2

        self.place(x=x, y=y)
        self.lift()
        self.focus()

    def close(self) -> None:
        """Close the popup."""
        self.popup_manager._close_current()
