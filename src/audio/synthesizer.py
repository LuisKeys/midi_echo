"""Metronome click synthesis and playback.

Generates high-quality metronome clicks using sine wave synthesis and
plays them on the default audio output device.
"""

import asyncio
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class MetronomeClicker:
    """Synthesizes and plays metronome click sounds.

    Uses sine wave synthesis with amplitude envelope for natural-sounding clicks.
    Supports different click types (downbeat, beat) with customizable parameters.
    """

    def __init__(self, sample_rate: int = 44100):
        """Initialize metronome clicker.

        Args:
            sample_rate: Audio sample rate in Hz (default 44100)
        """
        self.sample_rate = sample_rate
        self._audio_output = None
        self._initialized = False

        # Configure default click parameters (can be customized)
        self.downbeat_freq = 1000  # Hz
        self.downbeat_velocity = 100  # 0-127
        self.beat_freq = 800  # Hz
        self.beat_velocity = 80  # 0-127
        self.click_duration = 0.05  # seconds
        self.attack_time = 0.005  # seconds
        self.release_time = 0.025  # seconds

        # Initialize audio output lazily on first use
        try:
            self._initialize_audio_output()
        except Exception as e:
            logger.warning(f"Audio initialization deferred: {e}")

    def _initialize_audio_output(self):
        """Initialize audio output device.

        Tries to use sounddevice library if available, falls back to
        alternative methods if needed.
        """
        if self._initialized:
            return

        try:
            import sounddevice as sd

            self._audio_output = sd
            self._initialized = True
            logger.info("Audio output initialized with sounddevice")
        except ImportError:
            logger.warning("sounddevice not available, trying simpleaudio...")
            try:
                import simpleaudio as sa

                self._audio_output = sa
                self._initialized = True
                logger.info("Audio output initialized with simpleaudio")
            except ImportError:
                logger.error(
                    "No audio library available. Install sounddevice or simpleaudio."
                )
                self._initialized = False

    async def play_downbeat(self):
        """Play a downbeat click (louder, lower frequency).

        This is called at the start of each bar. Runs asynchronously
        to avoid blocking the clock.
        """
        await self._play_click(
            frequency=self.downbeat_freq, velocity=self.downbeat_velocity
        )

    async def play_beat(self):
        """Play a regular beat click (softer, higher frequency).

        This is called on each beat. Runs asynchronously to avoid
        blocking the clock.
        """
        await self._play_click(frequency=self.beat_freq, velocity=self.beat_velocity)

    async def _play_click(self, frequency: float, velocity: int):
        """Internal method to synthesize and play a click.

        Args:
            frequency: Fundamental frequency in Hz
            velocity: MIDI velocity (0-127) controlling amplitude
        """
        if not self._initialized:
            try:
                self._initialize_audio_output()
            except Exception:
                logger.debug("Audio not available")
                return

        try:
            # Generate click sound
            audio_data = self._synthesize_click(frequency, velocity)

            # Play on default output (non-blocking in async context)
            if hasattr(self._audio_output, "play"):  # sounddevice
                await asyncio.to_thread(
                    self._audio_output.play, audio_data, self.sample_rate
                )
            elif hasattr(self._audio_output, "play_buffer"):  # simpleaudio
                # Convert to int16 for simpleaudio
                audio_int16 = (audio_data * 32767).astype(np.int16)
                play_obj = self._audio_output.play_buffer(
                    audio_int16,
                    num_channels=1,
                    bytes_per_sample=2,
                    sample_rate=self.sample_rate,
                )
                # Wait for playback in a thread to avoid blocking
                await asyncio.to_thread(play_obj.wait_done)
        except Exception as e:
            logger.debug(f"Error playing click: {e}")

    def _synthesize_click(self, frequency: float, velocity: int) -> np.ndarray:
        """Synthesize a sine wave click with amplitude envelope.

        The envelope has a sharp attack and smooth release for a natural click sound.

        Args:
            frequency: Fundamental frequency in Hz
            velocity: MIDI velocity (0-127) controlling amplitude

        Returns:
            Audio samples as numpy array (float32, normalized to [-1, 1])
        """
        # Calculate sample counts
        num_samples = int(self.click_duration * self.sample_rate)
        attack_samples = int(self.attack_time * self.sample_rate)
        release_samples = int(self.release_time * self.sample_rate)
        sustain_samples = num_samples - attack_samples - release_samples

        # Normalize velocity to amplitude (0-127) -> (0-1)
        amplitude = velocity / 127.0

        # Generate time array
        t = np.arange(num_samples) / self.sample_rate

        # Create sine wave
        click = amplitude * np.sin(2 * np.pi * frequency * t)

        # Apply envelope
        envelope = np.ones(num_samples)

        # Attack (linear ramp from 0 to 1)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Release (exponential decay)
        if release_samples > 0:
            release_start = num_samples - release_samples
            decay_rate = np.exp(-5 / release_samples)  # Controls decay rate
            release_env = np.power(decay_rate, np.arange(release_samples))
            envelope[release_start:] = release_env

        # Apply envelope to click
        click *= envelope

        # Ensure no clipping
        click = np.clip(click, -1.0, 1.0)

        return click.astype(np.float32)
