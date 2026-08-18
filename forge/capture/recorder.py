"""Durable JSONL session recorder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from forge.ble.models import NotificationRecord
from .exporter import filename_timestamp, safe_label, utc_now


class CaptureRecorder:
    """Write one metadata line and raw notification events to a JSONL file."""

    def __init__(self, captures_dir: Path, label: str = "session", output: Path | None = None):
        captures_dir.mkdir(parents=True, exist_ok=True)
        self.label = safe_label(label)
        self.path = output or captures_dir / f"{self.label}_{filename_timestamp()}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", encoding="utf-8", newline="\n")
        self.write_event(
            {
                "event": "session_start",
                "timestamp": utc_now(),
                "label": self.label,
                "format": "forge-capture-jsonl-v1",
            }
        )

    def write_event(self, payload: dict[str, Any]) -> None:
        self._handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        self._handle.flush()

    def record_notification(self, record: NotificationRecord) -> None:
        payload = {"event": "notification", **record.to_dict()}
        self.write_event(payload)

    def close(self) -> None:
        if not self._handle.closed:
            self.write_event({"event": "session_end", "timestamp": utc_now()})
            self._handle.close()

    def __enter__(self) -> "CaptureRecorder":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
