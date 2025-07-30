"""
Detect file ➔ call Groq ➔ overwrite the file once (no streaming).
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .utils.file_detector import detect_abap_file
from .llm_providers.groq_provider import GroqProvider

load_dotenv()


def _backup_file(path: Path, ext: Optional[str]) -> None:
    if ext:
        backup = path.with_suffix(path.suffix + ext)
        path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"🔐 Backup created → {backup}")


# -----------------------------------------------------------------------

def convert_active_file(*, backup_ext: Optional[str] = None) -> None:
    """CLI entry-point."""
    abap_path = Path(detect_abap_file())
    print(f"📄 Converting {abap_path.name} …")

    legacy_code = abap_path.read_text(encoding="utf-8")
    _backup_file(abap_path, backup_ext)

    provider = GroqProvider()
    start = time.perf_counter()
    modern_code = provider.modernise_code(legacy_code)
    elapsed = time.perf_counter() - start

    abap_path.write_text(modern_code, encoding="utf-8")
    print(f"✅ Done. Updated in {elapsed:,.1f}s.")
