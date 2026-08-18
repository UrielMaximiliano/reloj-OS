"""Make ``python scripts\\tool.py`` import the repository package."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ``scripts/inspect.py`` is a required user-facing filename, but it must not
# shadow Python's standard-library ``inspect`` when Rich or another dependency
# imports it. The bootstrap has already loaded, so the scripts directory is no
# longer needed on the import path.
SCRIPT_DIR = Path(__file__).resolve().parent
for entry in list(sys.path):
    try:
        if Path(entry or ".").resolve() == SCRIPT_DIR:
            sys.path.remove(entry)
    except OSError:
        continue
