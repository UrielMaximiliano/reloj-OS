"""Catalogue local captures into captures/index.json."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
from pathlib import Path

from forge.capture.indexer import write_capture_index
from forge.cli_common import console, runtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualiza el indice de capturas")
    parser.add_argument("--config")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    args = parser.parse_args()
    config = runtime(args.config, args.log_level)
    output = args.output or config.captures_dir / "index.json"
    write_capture_index(config.captures_dir, output, config.known_firmware)
    console.print(f"Capture index: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
