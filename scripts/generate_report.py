"""Generate the reverse-engineering report and refresh offline analysis."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

from forge.capture.report import generate_report
from forge.cli_common import console


def main() -> int:
    output = generate_report(ROOT)
    console.print(f"Report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
