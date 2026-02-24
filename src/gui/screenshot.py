"""Screenshot helper utilities.

Provides a fullscreen capture using `mss` and a small toast notification
helper that uses customtkinter to show a transient message.
"""

from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Optional

try:
    import mss
    from mss import tools
except Exception as exc:  # pragma: no cover - runtime dependency
    mss = None  # type: ignore

import customtkinter as ctk


def _project_root() -> Path:
    # src/gui/screenshot.py -> project root is two parents up
    return Path(__file__).resolve().parents[2]


def ensure_screenshots_dir() -> Path:
    root = _project_root()
    screenshots = root / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    return screenshots


def timestamp_filename() -> str:
    return time.strftime("%Y%m%d_%H%M%S") + ".png"


def capture_fullscreen(save_dir: Optional[Path] = None) -> Path:
    """Capture the full screen and save to a PNG file.

    Args:
        save_dir: Optional directory to save the screenshot. If not provided,
            saves into the project's `screenshots/` folder.

    Returns:
        Path to the saved PNG file.

    Raises:
        RuntimeError: if capturing fails or `mss` is not available.
    """
    if mss is None:
        raise RuntimeError("mss module not available; install the 'mss' package")

    if save_dir is None:
        save_dir = ensure_screenshots_dir()

    filename = timestamp_filename()
    out_path = Path(save_dir) / filename

    with mss.mss() as sct:
        # Grab the primary monitor (full virtual screen)
        monitor = sct.monitors[0]
        img = sct.grab(monitor)
        # Save to file
        tools.to_png(img.rgb, img.size, output=str(out_path))

    return out_path


def show_toast(parent: ctk.CTk, message: str, duration_ms: int = 2000) -> None:
    """Show a small transient toast-like window centered over `parent`.

    This is intentionally minimal so we don't introduce new framework code.
    """
    try:
        toast = ctk.CTkToplevel(parent)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        # Styling
        toast.configure(fg_color=("gray10", "gray80"))

        label = ctk.CTkLabel(toast, text=message, font=("Arial", 12))
        label.pack(padx=12, pady=8)

        # Center on parent
        parent.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        tw = toast.winfo_reqwidth()
        th = toast.winfo_reqheight()
        x = px + (pw // 2) - (tw // 2)
        y = py + (ph // 6)  # appear near top
        toast.geometry(f"+{x}+{y}")

        # Auto destroy after duration
        toast.after(duration_ms, toast.destroy)
    except Exception:
        # Fail silently if UI toast cannot be shown
        pass
