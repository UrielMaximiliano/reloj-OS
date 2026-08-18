"""Conservative comparison of two notification captures."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .exporter import notification_rows, read_jsonl


def _packets(path: Path) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = defaultdict(list)
    for row in notification_rows(read_jsonl(path)):
        uuid = str(row.get("characteristic_uuid", "unknown"))
        raw = str(row.get("raw_hex", ""))
        try:
            result[uuid].append(bytes.fromhex(raw.replace(" ", "")))
        except ValueError:
            continue
    return dict(result)


def _offset_summary(packets: list[bytes]) -> tuple[list[int], list[int], list[int]]:
    if not packets:
        return [], [], []
    max_length = max(len(packet) for packet in packets)
    constants: list[int] = []
    variable: list[int] = []
    missing: list[int] = []
    for offset in range(max_length):
        values = {packet[offset] for packet in packets if offset < len(packet)}
        if not values:
            missing.append(offset)
        elif len(values) == 1:
            constants.append(offset)
        else:
            variable.append(offset)
    return constants, variable, missing


def _hex_byte(packets: list[bytes], offset: int) -> str:
    values = {packet[offset] for packet in packets if offset < len(packet)}
    return ", ".join(f"{value:02x}" for value in sorted(values))


def compare_captures(path_a: Path, path_b: Path) -> str:
    """Return a human-readable report and avoid naming hypotheses as facts."""

    first, second = _packets(path_a), _packets(path_b)
    lines = [
        "Forge capture comparison",
        f"A: {path_a}",
        f"B: {path_b}",
        "",
        "Evidence is byte-level only; protocol meanings remain unconfirmed.",
        "",
    ]
    for uuid in sorted(set(first) | set(second)):
        a_packets, b_packets = first.get(uuid, []), second.get(uuid, [])
        lines += [f"Characteristic: {uuid}", ""]
        if not a_packets:
            lines += ["- Appears only in B.", ""]
        if not b_packets:
            lines += ["- Appears only in A.", ""]
        if not a_packets or not b_packets:
            continue
        lengths_a = sorted({len(packet) for packet in a_packets})
        lengths_b = sorted({len(packet) for packet in b_packets})
        lines += [f"- Lengths A: {lengths_a}", f"- Lengths B: {lengths_b}"]
        max_length = max(max(lengths_a, default=0), max(lengths_b, default=0))
        changed = []
        for offset in range(max_length):
            values_a = {packet[offset] for packet in a_packets if offset < len(packet)}
            values_b = {packet[offset] for packet in b_packets if offset < len(packet)}
            if values_a != values_b:
                changed.append(offset)
        lines.append(f"- Offsets whose observed value set changes: {changed or 'none'}")
        constants_a, variable_a, _ = _offset_summary(a_packets)
        constants_b, variable_b, _ = _offset_summary(b_packets)
        if constants_a:
            lines.append(f"- Constant offsets in A: {', '.join(f'{i}={_hex_byte(a_packets, i)}' for i in constants_a)}")
        if constants_b:
            lines.append(f"- Constant offsets in B: {', '.join(f'{i}={_hex_byte(b_packets, i)}' for i in constants_b)}")
        lines.append(f"- Variable offsets in A: {variable_a or 'none'}")
        lines.append(f"- Variable offsets in B: {variable_b or 'none'}")
        lines.append("")
    return "\n".join(lines)
