"""Manual-event to packet timeline correlation for controlled experiments."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .packet import RawPacket


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class TimelineEvent:
    timestamp: str
    label: str
    notes: str = ""
    result: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_events(path: Path) -> list[TimelineEvent]:
    """Load a JSON array or JSONL manual-event file."""

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    decoded: Any = json.loads(text) if text.startswith("[") else [json.loads(line) for line in text.splitlines() if line.strip()]
    return [TimelineEvent(str(row["timestamp"]), str(row["label"]), str(row.get("notes", "")), dict(row.get("result", {}))) for row in decoded]


def correlate_events(events: Iterable[TimelineEvent], packets: Iterable[RawPacket], window_seconds: float = 3.0) -> list[dict[str, Any]]:
    packet_rows = [(packet, parse_time(packet.timestamp)) for packet in packets if packet.timestamp]
    correlations: list[dict[str, Any]] = []
    for event in events:
        event_time = parse_time(event.timestamp)
        nearby = [
            packet
            for packet, packet_time in packet_rows
            if 0 <= (packet_time - event_time).total_seconds() <= window_seconds
        ]
        correlations.append(
            {
                "event": event.to_dict(),
                "packets": [
                    {
                        "timestamp": packet.timestamp,
                        "characteristic_uuid": packet.characteristic_uuid,
                        "raw_hex": packet.hex,
                        "length": packet.length,
                    }
                    for packet in nearby
                ],
                "confidence": "POSSIBLE" if nearby else "UNKNOWN",
                "warning": "Temporal proximity is not causal proof; repeat the event and compare controls.",
            }
        )
    return correlations


def timeline_markdown(correlations: Iterable[dict[str, Any]]) -> str:
    lines = ["# Experiment timeline", "", "> Temporal proximity is evidence for follow-up only, not proof of causality.", ""]
    for item in correlations:
        event = item["event"]
        lines += [f"## {event['timestamp']} — {event['label']}", "", f"- Notes: {event.get('notes') or '—'}", f"- Result: `{json.dumps(event.get('result', {}), ensure_ascii=False)}`", f"- Confidence: **{item['confidence']}**", ""]
        if item["packets"]:
            lines.append("Nearby packets:")
            lines.extend(f"- `{packet['timestamp']}` `{packet['characteristic_uuid']}` `{packet['raw_hex']}`" for packet in item["packets"])
        else:
            lines.append("No packet within the configured window.")
        lines += [f"- {item['warning']}", ""]
    return "\n".join(lines)
