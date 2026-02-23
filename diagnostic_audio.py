#!/usr/bin/env python3
"""Diagnostic tool for audio device enumeration and testing.

Use this script to:
1. List all available audio devices
2. Identify your desired audio output device (e.g., Focusrite Scarlett)
3. Test audio playback on a specific device
4. Get the device ID to set in your .env file

Usage:
    python -m diagnostic_audio          # List all devices
    python -m diagnostic_audio test 2   # Test audio playback on device 2
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def print_devices():
    """List all available audio output devices."""
    try:
        from src.audio import list_audio_devices
    except ImportError:
        print(
            "Error: Cannot import audio utilities. Make sure you're in the project root."
        )
        return

    devices = list_audio_devices()

    if not devices:
        print("No audio output devices found!")
        return

    print("\n" + "=" * 70)
    print("AVAILABLE AUDIO OUTPUT DEVICES")
    print("=" * 70 + "\n")

    for device in devices:
        marker = " <-- DEFAULT" if device["is_default"] else ""
        print(f"ID: {device['id']}")
        print(f"  Name: {device['name']}{marker}")
        print(f"  Channels: {device['channels']}")
        print(f"  Sample Rate: {device['sample_rate']} Hz")
        print()

    print("=" * 70)
    print("\nTo use a specific device for the metronome, add this to your .env file:")
    print("  AUDIO_DEVICE=<device_id>")
    print("\nExample:")
    for device in devices:
        if "focusrite" in device["name"].lower():
            print(f"  AUDIO_DEVICE={device['id']}  # {device['name']}")
            break
    print()


def test_audio(device_id: int):
    """Test audio playback on a specific device.

    Args:
        device_id: Device ID to test
    """
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        print("Error: sounddevice not installed. Install with: pip install sounddevice")
        return

    try:
        from src.audio import get_device_info
    except ImportError:
        print("Error: Cannot import audio utilities.")
        return

    device_info = get_device_info(device_id)

    if not device_info:
        print(f"Error: Device {device_id} not found!")
        return

    print("\n" + "=" * 70)
    print(f"TESTING AUDIO OUTPUT ON DEVICE {device_id}")
    print("=" * 70)
    print(f"Device: {device_info['name']}")
    print(f"Channels: {device_info['channels']}")
    print(f"Sample Rate: {device_info['sample_rate']} Hz")
    print()

    # Generate a short beep
    sample_rate = 44100
    duration = 0.5  # seconds
    frequency = 440  # Hz (A4 note)

    # Create sine wave
    samples = np.arange(sample_rate * duration)
    waveform = np.sin(2 * np.pi * frequency * samples / sample_rate)

    # Reduce amplitude to avoid clipping
    waveform = waveform * 0.3

    print("Playing 440 Hz tone for 0.5 seconds...")
    print("You should hear a beep on the selected device.")
    print()

    try:
        sd.play(waveform, sample_rate, device=device_id, blocking=True)
        print("✓ Playback successful!")
    except Exception as e:
        print(f"✗ Playback failed: {e}")
    finally:
        print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_devices()
    elif sys.argv[1] == "test":
        if len(sys.argv) < 3:
            print("Usage: python -m diagnostic_audio test <device_id>")
            sys.exit(1)
        try:
            device_id = int(sys.argv[2])
            test_audio(device_id)
        except ValueError:
            print(f"Error: '{sys.argv[2]}' is not a valid device ID (must be integer)")
            sys.exit(1)
    elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print(__doc__)
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print("Use --help for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
