"""Main GUI window for MIDI Echo."""

import customtkinter as ctk
import logging
from src.config import AppConfig
from src.gui.context import AppContext
from src.gui.components import Theme, ButtonPanel, ButtonSpec, PopupManager
from src.gui.input import PressDetector
from src.gui.handlers import (
    TransposeHandler,
    OctaveHandler,
    ChannelHandler,
    FXHandler,
    ScaleHandler,
    ArpHandler,
    PresetHandler,
    PanicHandler,
)

logger = logging.getLogger(__name__)


class MidiGui(ctk.CTk):
    """Main GUI window for MIDI Echo."""

    def __init__(self, context: AppContext, config: AppConfig):
        """Initialize MIDI GUI.

        Args:
            context: AppContext for dependency injection
            config: AppConfig with configuration
        """
        ctk.set_appearance_mode("dark")
        super().__init__()

        self.context = context
        self.app_config = config
        self.context.app_config = config
        self.root = self
        # Alias to the underlying Tk root for components expecting `tk_root`
        self.tk_root = self

        # Setup theme
        self.theme = Theme(config)

        # Setup window
        self.title("MIDI Echo - Live Performance")
        self.geometry(f"{config.window_width}x{config.window_height}")
        self.configure(fg_color=self.theme.get_color("bg"))

        # Maximize window (platform-independent)
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.lift()
        self.attributes("-topmost", True)
        self.focus()

        # Setup components
        self.button_panel = ButtonPanel(self, self.theme)
        self.popup_manager = PopupManager(self, self.theme)
        self.press_detector = PressDetector(config, self)

        # Setup handlers
        self.handlers = {
            "TR": TransposeHandler(context),
            "OC": OctaveHandler(context),
            "CH": ChannelHandler(context),
            "FX": FXHandler(context),
            "SC": ScaleHandler(context),
            "AR": ArpHandler(context),
            "PS": PresetHandler(context),
            "ST": PanicHandler(context),
        }

        # Create buttons
        self._create_buttons()

        # Force redraw to fix rendering glitches
        self.after(100, self.button_panel.force_redraw)

        # Bind events
        self.bind("<Escape>", lambda e: self.quit())
        self.bind("<Configure>", lambda e: self._on_window_resize())

        # Update context
        context.update_gui(self)

        # Initialize button colors to match current state
        for key, handler in self.handlers.items():
            if hasattr(handler, "update_ui"):
                handler.update_ui()

    def _create_buttons(self) -> None:
        """Create all buttons for the interface."""
        button_specs = [
            # Row 0
            ButtonSpec("FX", 0, 0, "violet", self.handlers["FX"].on_button_press),
            ButtonSpec(
                "TR",
                0,
                1,
                "aqua",
                self.handlers["TR"].on_button_press,
                self.handlers["TR"].on_button_long_press,
            ),
            ButtonSpec(
                "OC",
                0,
                2,
                "aqua",
                self.handlers["OC"].on_button_press,
                self.handlers["OC"].on_button_long_press,
            ),
            ButtonSpec("SC", 0, 3, "aqua", self.handlers["SC"].on_button_press),
            # Row 1
            ButtonSpec(
                "AR",
                1,
                0,
                "aqua",
                self.handlers["AR"].on_button_press,
                self.handlers["AR"].on_button_long_press,
            ),
            ButtonSpec(
                "CH",
                1,
                1,
                "cyan",
                self.handlers["CH"].on_button_press,
                self.handlers["CH"].on_button_long_press,
            ),
            ButtonSpec("PS", 1, 2, "cyan", self.handlers["PS"].on_button_press),
            ButtonSpec("ST", 1, 3, "grey", self.handlers["ST"].on_button_press),
        ]

        for spec in button_specs:
            # Create button with long-press handlers if available
            if spec.long_press_handler:

                def make_press_handler(handler_key, spec_ref):
                    def on_press():
                        self.press_detector.on_button_press(
                            handler_key,
                            (
                                spec_ref.long_press_handler
                                if spec_ref.long_press_handler
                                else lambda: None
                            ),
                        )

                    return on_press

                def make_release_handler(handler_key, spec_ref):
                    def on_release():
                        self.press_detector.on_button_release(spec_ref.command)

                    return on_release

                self.button_panel.create_button(
                    spec,
                    on_press=make_press_handler(spec.text, spec),
                    on_release=make_release_handler(spec.text, spec),
                )
            else:
                self.button_panel.create_button(spec)

    def _on_window_resize(self) -> None:
        """Handle window resize event (debounced)."""
        if hasattr(self, "_resize_job") and self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._apply_resize)

    def _apply_resize(self) -> None:
        """Apply deferred resize updates."""
        self._resize_job = None
        self.theme.update_window_size(self.winfo_width(), self.winfo_height())
        self.button_panel.update_font_sizes()
        self.popup_manager.update_font_sizes()
