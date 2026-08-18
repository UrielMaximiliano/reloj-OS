"""Comparison of two read-only snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .exporter import read_json


def _payload(path: Path) -> dict[str, Any]:
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"Read snapshot must be a JSON object: {path}")
    return value


def _bytes(result: dict[str, Any] | None) -> bytes:
    if not result:
        return b""
    return bytes.fromhex(str(result.get("raw_hex", "")).replace(" ", ""))


def compare_reads(path_before: Path, path_after: Path) -> str:
    before = {str(row.get("characteristic_uuid")): row for row in _payload(path_before).get("results", [])}
    after = {str(row.get("characteristic_uuid")): row for row in _payload(path_after).get("results", [])}
    lines = [
        "Forge safe-read comparison",
        f"Before: {path_before}",
        f"After: {path_after}",
        "",
        "No writes were executed; interpretations remain descriptive.",
        "",
    ]
    for uuid in sorted(set(before) | set(after)):
        left, right = before.get(uuid), after.get(uuid)
        left_bytes, right_bytes = _bytes(left), _bytes(right)
        changed_offsets = [
            index
            for index in range(max(len(left_bytes), len(right_bytes)))
            if (left_bytes[index] if index < len(left_bytes) else None) != (right_bytes[index] if index < len(right_bytes) else None)
        ]
        lines += [
            f"Characteristic: {uuid}",
            f"- Before raw: `{left.get('raw_hex', 'missing') if left else 'missing'}`",
            f"- After raw: `{right.get('raw_hex', 'missing') if right else 'missing'}`",
            f"- Changed offsets: `{changed_offsets or 'none'}`",
        ]
        if left and right:
            lines.append(f"- Before numeric: uint8={left.get('uint8')}, uint16_le={left.get('uint16_le')}, uint16_be={left.get('uint16_be')}, uint32_le={left.get('uint32_le')}, uint32_be={left.get('uint32_be')}")
            lines.append(f"- After numeric: uint8={right.get('uint8')}, uint16_le={right.get('uint16_le')}, uint16_be={right.get('uint16_be')}, uint32_le={right.get('uint32_le')}, uint32_be={right.get('uint32_be')}")
        lines.append("")
    return "\n".join(lines)
