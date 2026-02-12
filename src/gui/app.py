import customtkinter as ctk
import logging
import mido
import asyncio

logger = logging.getLogger(__name__)


class MidiGui(ctk.CTk):
    def __init__(self, engine, processor, loop):
        super().__init__()

        self.engine = engine
        self.processor = processor
        self.loop = loop

        self.title("MIDI Echo - Live Performance")
        self.geometry("600x400")

        # Color palette
        self.colors = {
            "cyan": "#00FFFF",
            "violet": "#8A2BE2",
            "aqua": "#7FFFD4",
            "grey": "#808080",
            "red": "#FF0000",
            "bg": "#1A1A1A",
        }

        self.configure(fg_color=self.colors["bg"])

        # Configure grid 4x2
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        self.grid_rowconfigure((0, 1), weight=1, uniform="equal")

        # Buttons definition
        self.buttons = {}

        # Row 0
        self._create_button("CH", 0, 0, self.colors["cyan"], self.toggle_channel)
        self._create_button("FX", 0, 1, self.colors["violet"], self.toggle_fx)
        self._create_button("PS", 0, 2, self.colors["cyan"], self.show_presets)
        self._create_button("ST", 0, 3, self.colors["grey"], self.midi_panic)

        # Row 1
        self._create_button("TR", 1, 0, self.colors["aqua"], self.change_transpose)
        self._create_button("OC", 1, 1, self.colors["aqua"], self.change_octave)
        self._create_button("SC", 1, 2, self.colors["aqua"], self.toggle_scale)
        self._create_button("AR", 1, 3, self.colors["aqua"], self.toggle_arp)

    def _create_button(self, text, row, col, color, command):
        btn = ctk.CTkButton(
            self,
            text=text,
            font=("Arial", 32, "bold"),
            fg_color=color,
            text_color="black",
            hover_color=color,  # Keep it bright
            corner_radius=10,
            command=command,
        )
        btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        self.buttons[text] = btn

    # Handlers
    def toggle_channel(self):
        # Dummy rotation for now: None -> 0 -> 1 ...
        if self.processor.output_channel is None:
            self.processor.output_channel = 0
        elif self.processor.output_channel >= 15:
            self.processor.output_channel = None
        else:
            self.processor.output_channel += 1

        ch_text = (
            "BY"
            if self.processor.output_channel is None
            else str(self.processor.output_channel + 1)
        )
        self.buttons["CH"].configure(text=f"CH\n{ch_text}")
        logger.info(f"Channel changed to: {self.processor.output_channel}")

    def toggle_fx(self):
        self.processor.fx_enabled = not self.processor.fx_enabled
        new_color = self.colors["violet"] if self.processor.fx_enabled else "#4A4A4A"
        self.buttons["FX"].configure(fg_color=new_color)
        logger.info(f"FX enabled: {self.processor.fx_enabled}")

    def show_presets(self):
        logger.info("PS pressed - Presets not implemented yet")

    def midi_panic(self):
        logger.info("ST pressed - MIDI PANIC")
        self.buttons["ST"].configure(fg_color=self.colors["red"])
        # Send All Notes Off to all 16 channels
        for ch in range(16):
            msg = mido.Message("control_change", channel=ch, control=123, value=0)
            self.loop.call_soon_threadsafe(self.engine.queue.put_nowait, msg)

        self.after(
            500, lambda: self.buttons["ST"].configure(fg_color=self.colors["grey"])
        )

    def change_transpose(self):
        self.processor.transpose = (self.processor.transpose + 1) % 13  # 0 to 12
        self.buttons["TR"].configure(text=f"TR\n{self.processor.transpose}")
        logger.info(f"Transpose: {self.processor.transpose}")

    def change_octave(self):
        self.processor.octave = self.processor.octave + 1
        if self.processor.octave > 2:
            self.processor.octave = -2
        self.buttons["OC"].configure(text=f"OC\n{self.processor.octave}")
        logger.info(f"Octave: {self.processor.octave}")

    def toggle_scale(self):
        self.processor.scale_enabled = not self.processor.scale_enabled
        new_color = self.colors["aqua"] if self.processor.scale_enabled else "#4A4A4A"
        self.buttons["SC"].configure(fg_color=new_color)
        logger.info(f"Scale enabled: {self.processor.scale_enabled}")

    def toggle_arp(self):
        self.processor.arp_enabled = not self.processor.arp_enabled
        new_color = self.colors["aqua"] if self.processor.arp_enabled else "#4A4A4A"
        self.buttons["AR"].configure(fg_color=new_color)
        logger.info(f"Arp enabled: {self.processor.arp_enabled}")
