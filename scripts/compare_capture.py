"""Compare two JSONL notification captures."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
from pathlib import Path

from forge.cli_common import console
from forge.capture.diff import compare_captures


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara dos capturas JSONL por characteristic y offset")
    parser.add_argument("capture_a", type=Path)
    parser.add_argument("capture_b", type=Path)
    args = parser.parse_args()
    console.print(compare_captures(args.capture_a, args.capture_b))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
