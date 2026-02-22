"""Sequencer state model

Defines the complete state of the pattern sequencer including playback control,
timing configuration, quantization, and metronome settings.
"""

from dataclasses import dataclass, field


@dataclass
class SequencerState:
    """Complete state model for the MIDI pattern sequencer

    Playback Control:
        is_playing: True when pattern is looping
        is_recording: True when recording input to pattern
        metronome_enabled: True when metronome click audible

    Timing:
        tempo: BPM (20-300)
        time_signature_num: Numerator (2-16)
        time_signature_den: Denominator (2, 4, 8, 16)
        pattern_bars: Number of bars in pattern (1-8)
        loop_length_ticks: Calculated from bars + time signature

    Quantization:
        quantization: Grid size ("1/4", "1/8", "1/16", "1/32")

    Internal:
        current_tick: Current playhead position in ticks (0 to loop_length_ticks-1)
        metronome_channel: MIDI channel for metronome (usually 9)
        metronome_downbeat_note: Note number for bar start (37)
        metronome_beat_note: Note number for beat (39)
    """

    # Playback control
    is_playing: bool = False
    is_recording: bool = False
    metronome_enabled: bool = True

    # Timing
    tempo: float = 120.0  # BPM, 20–300
    time_signature_num: int = 4  # Numerator
    time_signature_den: int = 4  # Denominator
    pattern_bars: int = 1  # 1–8 typical

    # Quantization
    quantization: str = "1/16"  # "1/4", "1/8", "1/16", "1/32"

    # Internal state
    current_tick: int = 0
    loop_length_ticks: int = field(default=3840, init=False)  # Calculated

    # Metronome settings
    metronome_channel: int = 9  # Percussion channel
    metronome_downbeat_note: int = 37  # Side Stick
    metronome_beat_note: int = 39  # Hand Clap

    def __post_init__(self):
        """Calculate loop length after initialization"""
        self._validate_state()
        self._calculate_loop_length()

    def _validate_state(self):
        """Validate state values are in legal ranges"""
        self.tempo = max(20.0, min(300.0, self.tempo))
        self.time_signature_num = max(2, min(16, self.time_signature_num))
        self.pattern_bars = max(1, min(8, self.pattern_bars))

        if self.quantization not in ("1/4", "1/8", "1/16", "1/32"):
            self.quantization = "1/16"

    def _calculate_loop_length(self):
        """Calculate loop_length_ticks from bars + time signature

        Formula: bars * numerator * PPQN * (4 / denominator)
        Where PPQN = 960 (pulses per quarter note)
        """
        PPQN = 960
        self.loop_length_ticks = int(
            self.pattern_bars
            * self.time_signature_num
            * PPQN
            * (4 / self.time_signature_den)
        )

    def on_bars_changed(self):
        """Update loop length when bars or time signature changes"""
        self._calculate_loop_length()
        # Reset playhead if it's beyond new loop length
        self.current_tick = (
            self.current_tick % self.loop_length_ticks
            if self.loop_length_ticks > 0
            else 0
        )

    def on_tempo_changed(self, new_tempo: float):
        """Update tempo with validation"""
        self.tempo = max(20.0, min(300.0, new_tempo))

    def on_time_signature_changed(self, num: int, den: int):
        """Update time signature and recalculate loop length"""
        self.time_signature_num = max(2, min(16, num))
        self.time_signature_den = den  # Only allow 2, 4, 8, 16
        self.on_bars_changed()

    def on_pattern_bars_changed(self, bars: int):
        """Update pattern bars and recalculate loop length"""
        self.pattern_bars = max(1, min(8, bars))
        self.on_bars_changed()

    def on_quantization_changed(self, quantization: str):
        """Update quantization grid"""
        if quantization in ("1/4", "1/8", "1/16", "1/32"):
            self.quantization = quantization

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON persistence (in presets)"""
        return {
            "tempo": self.tempo,
            "time_signature": [self.time_signature_num, self.time_signature_den],
            "pattern_bars": self.pattern_bars,
            "quantization": self.quantization,
            "metronome_enabled": self.metronome_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SequencerState":
        """Deserialize from dictionary (loaded from presets)"""
        state = cls()

        if "tempo" in data:
            state.tempo = data["tempo"]

        if "time_signature" in data:
            sig = data["time_signature"]
            if isinstance(sig, list) and len(sig) == 2:
                state.time_signature_num = sig[0]
                state.time_signature_den = sig[1]

        if "pattern_bars" in data:
            state.pattern_bars = data["pattern_bars"]

        if "quantization" in data:
            state.quantization = data["quantization"]

        if "metronome_enabled" in data:
            state.metronome_enabled = data["metronome_enabled"]

        # Re-validate and calculate loop length
        state._validate_state()
        state._calculate_loop_length()

        return state
