import argparse
import sys
from pathlib import Path

from .converter import convert_active_file

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="abap-converter",
        description="Convert legacy ABAP code (open in IDE) to modern ABAP 7.5+ using Groq LLM.",
    )
    p.add_argument(
        "--backup",
        metavar="EXT",
        help="Make a safety copy alongside the file (e.g. --backup .bak). "
             "If omitted, no backup is created.",
    )
    return p

def main() -> None:
    args = _build_parser().parse_args()
    try:
        convert_active_file(backup_ext=args.backup)
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":  # allow `python -m abap_converter`
    main()
