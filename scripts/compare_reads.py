"""Compare two read-only JSON snapshots."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
from pathlib import Path

from forge.cli_common import console
from forge.capture.read_diff import compare_reads


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara dos snapshots safe READ")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    console.print(compare_reads(args.before, args.after))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
