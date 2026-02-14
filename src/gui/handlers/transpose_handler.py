"""Handler for transpose feature."""

import logging
from src.gui.handlers.base_handler import BaseHandler
from src.gui.context import AppContext

logger = logging.getLogger(__name__)


class TransposeHandler(BaseHandler):
    """Handles transpose (pitch shift) operations."""

    def __init__(self, context: AppContext):
        """Initialize transpose handler.

        Args:
            context: AppContext for accessing app components
        """
        super().__init__(context)
        self.is_repeating = False
        self._value_label = None  # Reference to popup value label
        self._repeat_job = None

    def on_button_press(self) -> None:
        """Show transpose popup."""
        if self.context.gui:
            self._show_transpose_popup()

    def on_button_long_press(self) -> None:
        """Reset transpose to 0 on long press."""
        if self.context.processor:
            self.context.processor.transpose = 0
            self.update_ui()
            logger.info("Transpose reset to 0 (long press)")

    def adjust_transpose(self, delta: int = None, reset: bool = False) -> None:
        """Adjust transpose value.

        Args:
            delta: Amount to change transpose
            reset: If True, reset to 0
        """
        if not self.context.processor:
            return

        if reset:
            self.context.processor.transpose = 0
        elif delta is not None:
            self.context.processor.transpose += delta
            # Keep within bounds
            self.context.processor.transpose = max(
                -12, min(12, self.context.processor.transpose)
            )

        self.update_ui()
        logger.info(f"Transpose: {self.context.processor.transpose}")

    def update_ui(self) -> None:
        """Update button label and popup display."""
        if not self.context.gui or not self.context.processor:
            return

        tr_text = (
            f"TR\n{self.context.processor.transpose}"
            if self.context.processor.transpose != 0
            else "TR"
        )

        btn = self.context.gui.button_panel.get_button("TR")
        if btn:
            btn.configure(text=tr_text)

        # Update popup value label if it exists
        if self._value_label:
            self._value_label.configure(
                text=f"Value: {self.context.processor.transpose}"
            )

    def _show_transpose_popup(self) -> None:
        """Create and show transpose popup."""
        # Clear previous popup label reference
        self._value_label = None

        def build_transpose_content(frame):
            import customtkinter as ctk

            # Current value display
            value_label = ctk.CTkLabel(
                frame,
                text=f"Value: {self.context.processor.transpose}",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_value"),
                    "bold",
                ),
                text_color=self.context.gui.theme.get_color("text_black"),
            )
            value_label.pack(pady=8)
            self._value_label = value_label

            # Buttons row
            buttons_frame = ctk.CTkFrame(
                frame, fg_color=self.context.gui.theme.get_color("frame_bg")
            )
            buttons_frame.pack(
                fill="both",
                expand=True,
                padx=LayoutSpacing.CONTROL_BUTTON_PADX,
                pady=LayoutSpacing.CONTROL_BUTTON_PADY,
            )

            # Minus button
            btn_minus = ctk.CTkButton(
                buttons_frame,
                text="-",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                    "bold",
                ),
                fg_color=self.context.gui.theme.get_color_tuple("aqua"),
                text_color=self.context.gui.theme.get_color("text_black"),
                width=100,
                height=100,
                corner_radius=0,
                command=lambda: self.adjust_transpose(-1),
            )
            btn_minus.pack(
                side="left",
                padx=LayoutSpacing.CONTROL_BUTTON_PADX,
                pady=LayoutSpacing.CONTROL_BUTTON_PADY,
                fill="both",
                expand=True,
            )

            def on_minus_press():
                self.is_repeating = True
                # Start repeating only after long-press threshold
                if self.context.gui:
                    # schedule start of repeating; store job id so we can cancel
                    self._repeat_job = self.context.gui.tk_root.after(
                        self.context.app_config.long_press_threshold,
                        lambda: self._repeat_adjust(
                            -self.context.app_config.long_press_increment
                        ),
                    )

            def on_minus_release():
                # If the repeat job is still pending, cancel and perform a single step
                if self.context.gui and getattr(self, "_repeat_job", None):
                    try:
                        self.context.gui.tk_root.after_cancel(self._repeat_job)
                    except Exception:
                        pass
                    self._repeat_job = None
                    # single click already handled by button `command`; nothing to do
                else:
                    # repeating had started; stop it
                    self.is_repeating = False

            btn_minus.bind("<ButtonPress-1>", lambda e: on_minus_press())
            btn_minus.bind("<ButtonRelease-1>", lambda e: on_minus_release())

            # Zero button
            btn_zero = ctk.CTkButton(
                buttons_frame,
                text="0",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                    "bold",
                ),
                fg_color=self.context.gui.theme.get_color_tuple("cyan"),
                text_color=self.context.gui.theme.get_color("text_black"),
                width=100,
                height=100,
                corner_radius=0,
                command=lambda: self.adjust_transpose(reset=True),
            )
            btn_zero.pack(
                side="left",
                padx=LayoutSpacing.CONTROL_BUTTON_PADX,
                pady=LayoutSpacing.CONTROL_BUTTON_PADY,
                fill="both",
                expand=True,
            )

            # Plus button
            btn_plus = ctk.CTkButton(
                buttons_frame,
                text="+",
                font=(
                    "Arial",
                    self.context.gui.theme.get_font_size("popup_button"),
                    "bold",
                ),
                fg_color=self.context.gui.theme.get_color_tuple("aqua"),
                text_color=self.context.gui.theme.get_color("text_black"),
                width=100,
                height=100,
                corner_radius=0,
                command=lambda: self.adjust_transpose(1),
            )
            btn_plus.pack(
                side="left",
                padx=LayoutSpacing.CONTROL_BUTTON_PADX,
                pady=LayoutSpacing.CONTROL_BUTTON_PADY,
                fill="both",
                expand=True,
            )

            def on_plus_press():
                self.is_repeating = True
                if self.context.gui:
                    self._repeat_job = self.context.gui.tk_root.after(
                        self.context.app_config.long_press_threshold,
                        lambda: self._repeat_adjust(
                            self.context.app_config.long_press_increment
                        ),
                    )

            def on_plus_release():
                if self.context.gui and getattr(self, "_repeat_job", None):
                    try:
                        self.context.gui.tk_root.after_cancel(self._repeat_job)
                    except Exception:
                        pass
                    self._repeat_job = None
                    # single click already handled by button `command`;
                else:
                    self.is_repeating = False

            btn_plus.bind("<ButtonPress-1>", lambda e: on_plus_press())
            btn_plus.bind("<ButtonRelease-1>", lambda e: on_plus_release())

        if self.context.gui.popup_manager:
            popup = self.context.gui.popup_manager.create_popup(
                "Transpose", build_transpose_content
            )
            popup.show()

    def _repeat_adjust(self, increment: int) -> None:
        """Repeat adjustment during long press."""
        # Clear scheduled start job once repeating begins
        if getattr(self, "_repeat_job", None):
            self._repeat_job = None

        if self.is_repeating:
            self.adjust_transpose(increment)
            if self.context.gui:
                self.context.gui.tk_root.after(
                    50, lambda: self._repeat_adjust(increment)
                )
