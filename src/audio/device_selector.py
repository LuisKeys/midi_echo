"""Audio device enumeration and selection utilities.

Provides functionality to list available audio devices and select a specific
device for metronome playback on multi-audio-output systems.
"""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


def list_audio_devices() -> List[dict]:
    """List all available audio output devices.

    Returns:
        List of dicts with 'id', 'name', and 'is_default' keys.
        Empty list if sounddevice is not available.
    """
    try:
        import sounddevice as sd

        devices = []
        for idx, device_info in enumerate(sd.query_devices()):
            # Only include devices that have output channels
            if device_info["max_output_channels"] > 0:
                devices.append(
                    {
                        "id": idx,
                        "name": device_info["name"],
                        "is_default": idx
                        == sd.default.device[1],  # default output device
                        "channels": device_info["max_output_channels"],
                        "sample_rate": device_info["default_samplerate"],
                    }
                )
        return devices
    except (ImportError, OSError):
        logger.warning("sounddevice not available for device enumeration")
        return []


def find_device_by_name(name_substring: str) -> Optional[int]:
    """Find a device ID by partial name match.

    Case-insensitive search. Returns the first device whose name contains
    the given substring.

    Args:
        name_substring: Partial name to search for (e.g., "Focusrite", "Scarlett")

    Returns:
        Device ID if found, None otherwise.
    """
    devices = list_audio_devices()
    search_lower = name_substring.lower()

    for device in devices:
        if search_lower in device["name"].lower():
            return device["id"]

    logger.warning(f"No device found matching '{name_substring}'")
    return None


def get_device_info(device_id: Optional[int]) -> Optional[dict]:
    """Get detailed information about a specific device.

    Args:
        device_id: Device ID index, or None for default device

    Returns:
        Device info dict, or None if device not found or sounddevice unavailable.
    """
    devices = list_audio_devices()

    if device_id is None:
        # Return default device
        for device in devices:
            if device["is_default"]:
                return device
        # If no default marked, return first available
        return devices[0] if devices else None

    for device in devices:
        if device["id"] == device_id:
            return device

    return None


def validate_device_id(device_id: Optional[int]) -> bool:
    """Check if a device ID is valid and has output capability.

    Args:
        device_id: Device ID to validate (None is valid - means use default)

    Returns:
        True if device is valid or device_id is None, False otherwise.
    """
    if device_id is None:
        return True

    devices = list_audio_devices()
    return any(d["id"] == device_id for d in devices)
