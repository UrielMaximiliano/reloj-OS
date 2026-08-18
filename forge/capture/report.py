"""Generate a concise reverse-engineering status report from local evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from forge.protocol.analyzer import analyze_captures
from .exporter import read_json, read_jsonl
from .indexer import write_capture_index


def _latest(captures_dir: Path, pattern: str) -> Path | None:
    paths = list(captures_dir.glob(pattern))
    return max(paths, key=lambda path: path.stat().st_mtime) if paths else None


def _traffic(captures_dir: Path) -> tuple[int, set[str]]:
    packets = 0
    uuids: set[str] = set()
    for path in captures_dir.glob("*.jsonl"):
        for row in read_jsonl(path):
            if row.get("event") == "notification":
                packets += 1
                if row.get("characteristic_uuid"):
                    uuids.add(str(row["characteristic_uuid"]))
    return packets, uuids


def generate_report(root: Path) -> Path:
    captures_dir = root / "captures"
    docs_dir = root / "docs"
    gatt_path = _latest(captures_dir, "gatt_*.json")
    safe_path = _latest(captures_dir, "safe_read*.json")
    gatt: dict[str, Any] = read_json(gatt_path) if gatt_path else {}
    safe: dict[str, Any] = read_json(safe_path) if safe_path else {}
    write_capture_index(captures_dir, captures_dir / "index.json", "MOY-8QJ4-2.0.8")
    jsonl_paths = sorted(captures_dir.glob("*.jsonl"))
    protocol_path = docs_dir / "protocol.md"
    if jsonl_paths:
        analyze_captures(jsonl_paths, protocol_path)
    packets, packet_uuids = _traffic(captures_dir)
    services = gatt.get("services", [])
    custom = [service for service in services if service.get("service_type") == "CUSTOM"]
    candidate_channels = []
    for service in custom:
        writes = [char["uuid"] for char in service.get("characteristics", []) if any(prop in char.get("properties", []) for prop in ("write", "write-without-response"))]
        receives = [char["uuid"] for char in service.get("characteristics", []) if any(prop in char.get("properties", []) for prop in ("notify", "indicate"))]
        if writes and receives:
            candidate_channels.append((service["uuid"], writes, receives))

    lines = [
        "# JOOG Forge reverse-engineering report",
        "",
        "> Generated from local GATT, safe-read and capture evidence. No BLE write is performed by report generation.",
        "",
        "## Device",
        "",
        "- Name: `FRG`",
        "- Identifier: `41:88:11:E2:88:31`",
        "- Firmware: `MOY-8QJ4-2.0.8`",
        "- Software/manufacturer: `MOYOUNG-V2`",
        "- SoC: `JL7012F6` (reported hardware context)",
        "",
        "## GATT map",
        "",
        f"- Services: **{gatt.get('summary', {}).get('services', 'UNKNOWN')}**",
        f"- Custom/unknown services: **{gatt.get('summary', {}).get('custom_services', 'UNKNOWN')}**",
        f"- Characteristics: **{gatt.get('summary', {}).get('characteristics', 'UNKNOWN')}**",
        f"- READ: **{gatt.get('summary', {}).get('read', 'UNKNOWN')}**; WRITE: **{gatt.get('summary', {}).get('write', 'UNKNOWN')}**; NOTIFY: **{gatt.get('summary', {}).get('notify', 'UNKNOWN')}**; INDICATE: **{gatt.get('summary', {}).get('indicate', 'UNKNOWN')}**",
        "- Detailed map: [docs/ble-map.md](ble-map.md)",
        "",
        "## Safe-read evidence",
        "",
        f"- Snapshot: `{safe_path.name if safe_path else 'not available'}`",
        f"- Read values: **{len(safe.get('results', [])) if isinstance(safe.get('results', []), list) else 'UNKNOWN'}**",
        "- Writes attempted: **false**",
        "",
        "## Observed traffic",
        "",
        f"- Notification packets across local JSONL captures: **{packets}**",
        f"- Characteristics with packets: `{sorted(packet_uuids) or 'none'}`",
        "- Protocol analysis: [docs/protocol.md](protocol.md)",
        "",
        "## Candidate protocol channels",
        "",
    ]
    if candidate_channels:
        for service_uuid, writes, receives in candidate_channels:
            lines.append(f"- `{service_uuid}` — TX candidates `{writes}`; RX candidates `{receives}` — **POSSIBLE / UNCONFIRMED**")
    else:
        lines.append("- None observed structurally.")
    lines += [
        "",
        "## External research",
        "",
        "- [docs/external-protocol-research.md](external-protocol-research.md)",
        "- FEEA layout and MOYOUNG-V2 identity have a strong family-level match to Gadgetbridge, but no real command packet has been captured.",
        "- AE00 and 190E remain unknown for this watch.",
        "",
        "## OTA assessment",
        "",
        "- [docs/ota-analysis.md](ota-analysis.md)",
        "- Status: **UNKNOWN**; no write or OTA channel has been exercised.",
        "",
        "## Open questions",
        "",
        "- Which notifications appear when the watch itself starts HR or SpO2?",
        "- Do FEEA FEE1/FEE3 packets appear spontaneously during steps or measurement?",
        "- Are 190E and AE00 active protocol channels or unrelated/vendor helper services?",
        "- Is the public Moyoung V2 frame format identical on this firmware?",
        "",
        "## Next safe experiments",
        "",
        "- Repeat idle for 30 seconds.",
        "- Run HR and SpO2 three times each with manual event timestamps.",
        "- Compare safe-read snapshots before/after each measurement.",
        "- Do not enable WRITE until a real request/response trace or independently verified matching implementation exists.",
        "",
        "## Capture index",
        "",
        "- [captures/index.json](../captures/index.json)",
        "",
    ]
    output = docs_dir / "reverse-engineering-report.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
