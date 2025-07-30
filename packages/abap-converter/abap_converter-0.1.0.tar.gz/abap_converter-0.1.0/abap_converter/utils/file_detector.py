"""Smart ABAP file detection (IDE-agnostic)."""
from __future__ import annotations

import ctypes
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional

RECENT_THRESHOLD_SECONDS = 10

# ─── Active window helpers ────────────────────────────────────────────────


def _title_windows() -> Optional[str]:
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value.strip() or None
    except Exception:  # noqa: BLE001
        return None


def _title_macos() -> Optional[str]:
    try:
        from AppKit import NSWorkspace  # type: ignore
        active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return active_app.localizedName() or None
    except Exception:  # noqa: BLE001
        return None


def _title_linux() -> Optional[str]:
    try:
        return subprocess.check_output(
            ["xdotool", "getactivewindow", "getwindowname"], text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return None


def _get_active_window_title() -> Optional[str]:
    os_name = platform.system()
    if os_name == "Windows":
        return _title_windows()
    if os_name == "Darwin":
        return _title_macos()
    return _title_linux()


# ─── Core helpers ────────────────────────────────────────────────────────


def _extract_filename_from_title(title: str) -> Optional[str]:
    for part in title.split():
        if "." in part and ("/" in part or "\\" in part or part.count(".") == 1):
            return Path(part).name
    return None


# ─── Public API ──────────────────────────────────────────────────────────


def detect_abap_file() -> str:
    abap_files = [
        f
        for f in os.listdir()
        if f.lower().endswith(".abap") and Path(f).is_file()
    ]
    if not abap_files:
        raise FileNotFoundError("No .abap files found in current directory.")

    # 1️⃣ Active-window title
    title = _get_active_window_title()
    if title:
        candidate = _extract_filename_from_title(title)
        if candidate:
            if candidate.lower().endswith(".abap") and candidate in abap_files:
                print(f"[smart-detect] Active window → {candidate}")
                return str(Path(candidate).resolve())
            raise FileNotFoundError(
                "Active window is not an ABAP file. No active ABAP file detected."
            )

    # 2️⃣ Single file
    if len(abap_files) == 1:
        return str(Path(abap_files[0]).resolve())

    # 3️⃣ Recent-access heuristic
    abap_files.sort(key=lambda f: Path(f).stat().st_atime, reverse=True)
    most_recent = abap_files[0]
    if (time.time() - Path(most_recent).stat().st_atime) <= RECENT_THRESHOLD_SECONDS:
        print(f"[recent-access] Using most recent: {most_recent}")
        return str(Path(most_recent).resolve())

    # 4️⃣ Prompt user
    print("Multiple ABAP files found. Choose one:")
    for idx, f in enumerate(abap_files):
        print(f"  [{idx}] {f}")
    while True:
        choice = input("Number: ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(abap_files):
            return str(Path(abap_files[int(choice)]).resolve())
        print("Invalid selection – try again.")


if __name__ == "__main__":
    print(detect_abap_file())
