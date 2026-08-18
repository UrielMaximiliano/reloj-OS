"""Build a searchable catalogue of local captures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .exporter import read_json, read_jsonl, write_json


def _firmware_from_results(rows: list[dict[str, Any]], default: str | None) -> str | None:
    for row in rows:
        if row.get("characteristic_uuid", "").lower() == "00002a28-0000-1000-8000-00805f9b34fb":
            return row.get("utf8") or default
    return default


def build_capture_index(captures_dir: Path, firmware: str | None = None) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(captures_dir.iterdir() if captures_dir.exists() else []):
        if not path.is_file() or path.name == "index.json" or path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        if path.suffix.lower() == ".jsonl":
            rows = read_jsonl(path)
            start = next((row for row in rows if row.get("event") == "session_start"), {})
            notifications = [row for row in rows if row.get("event") == "notification"]
            entries.append(
                {
                    "label": start.get("label") or path.stem,
                    "timestamp": start.get("timestamp") or None,
                    "firmware": firmware,
                    "result": {},
                    "file": path.name,
                    "notes": f"{len(notifications)} notification packets; raw JSONL session",
                }
            )
            continue
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        results = payload.get("results", []) if isinstance(payload.get("results", []), list) else []
        entries.append(
            {
                "label": payload.get("label") or path.stem,
                "timestamp": payload.get("captured_at"),
                "firmware": _firmware_from_results(results, firmware),
                "result": {row.get("characteristic_uuid"): row.get("interpreted", {}) for row in results if row.get("interpreted")},
                "file": path.name,
                "notes": "safe READ snapshot" if payload.get("read_only") else "JSON capture",
            }
        )
    return entries


def write_capture_index(captures_dir: Path, output: Path, firmware: str | None = None) -> Path:
    return write_json(output, build_capture_index(captures_dir, firmware))
