"""Offline statistical packet analysis with explicit confidence limits."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from forge.capture.exporter import notification_rows, read_jsonl
from .packet import RawPacket, sum8, xor8
from .parser import packet_from_row


def load_packets(paths: Iterable[Path]) -> list[RawPacket]:
    packets: list[RawPacket] = []
    for path in paths:
        packets.extend(packet_from_row(row) for row in notification_rows(read_jsonl(path)))
    return packets


def _observations(packets: list[RawPacket]) -> dict[str, list[RawPacket]]:
    grouped: dict[str, list[RawPacket]] = defaultdict(list)
    for packet in packets:
        grouped[packet.characteristic_uuid].append(packet)
    return dict(grouped)


def _crc8(data: bytes, polynomial: int, initial: int = 0) -> int:
    crc = initial
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = ((crc << 1) ^ polynomial) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def _crc16(data: bytes, polynomial: int, initial: int, reflected: bool = False) -> int:
    crc = initial
    for value in data:
        if reflected:
            crc ^= value
            for _ in range(8):
                crc = (crc >> 1) ^ polynomial if crc & 1 else crc >> 1
        else:
            crc ^= value << 8
            for _ in range(8):
                crc = ((crc << 1) ^ polynomial) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc & 0xFFFF


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _timestamp_candidates(packets: list[RawPacket]) -> list[str]:
    candidates: list[str] = []
    dated = [(packet, _parse_timestamp(packet.timestamp)) for packet in packets]
    dated = [(packet, timestamp) for packet, timestamp in dated if timestamp]
    if len(dated) < 3:
        return candidates
    for offset in range(max((packet.length for packet, _ in dated), default=0)):
        for width in (4, 8):
            for endian in ("little", "big"):
                for scale, label in ((1, "Unix seconds"), (1000, "Unix milliseconds")):
                    matches = 0
                    total = 0
                    for packet, timestamp in dated:
                        if offset + width > packet.length:
                            continue
                        total += 1
                        raw = int.from_bytes(packet.payload[offset : offset + width], endian)
                        try:
                            observed = datetime.fromtimestamp(raw / scale, timezone.utc)
                        except (OverflowError, OSError, ValueError):
                            continue
                        if abs((observed - timestamp).total_seconds()) <= 86400:
                            matches += 1
                    if total >= 3 and matches == total:
                        candidates.append(f"offset {offset}, width {width}, {endian}-endian, {label}: {matches}/{total} matches (HYPOTHESIS)")
    return candidates


def _checksum_candidates(packets: list[RawPacket]) -> list[str]:
    checks: list[tuple[str, Callable[[bytes], int], int]] = [
        ("XOR8 preceding bytes", lambda data: xor8(data[:-1]), 1),
        ("SUM8 preceding bytes", lambda data: sum8(data[:-1]), 1),
        ("CRC8/0x07 preceding bytes", lambda data: _crc8(data[:-1], 0x07), 1),
        ("CRC8/0x31 preceding bytes", lambda data: _crc8(data[:-1], 0x31), 1),
        ("CRC16-CCITT preceding bytes", lambda data: _crc16(data[:-2], 0x1021, 0xFFFF), 2),
        ("CRC16-Modbus preceding bytes", lambda data: _crc16(data[:-2], 0xA001, 0xFFFF, reflected=True), 2),
    ]
    findings: list[str] = []
    for name, function, width in checks:
        applicable = [packet for packet in packets if packet.length > width]
        if len(applicable) < 2:
            continue
        matches = 0
        for packet in applicable:
            expected = function(packet.payload)
            actual = int.from_bytes(packet.payload[-width:], "little")
            actual_be = int.from_bytes(packet.payload[-width:], "big")
            matches += int(expected in {actual, actual_be})
        if matches:
            confidence = "POSSIBLE" if len(applicable) < 3 else "LIKELY" if matches == len(applicable) else "UNKNOWN"
            findings.append(f"{name}: {matches}/{len(applicable)} matches ({confidence}; one match is insufficient)")
    return findings


def _counter_candidates(packets: list[RawPacket]) -> list[str]:
    findings: list[str] = []
    for offset in range(max((packet.length for packet in packets), default=0)):
        values = [packet.payload[offset] for packet in packets if offset < packet.length]
        if len(values) < 3:
            continue
        diffs = [(right - left) & 0xFF for left, right in zip(values, values[1:])]
        if diffs and all(diff == 1 for diff in diffs):
            findings.append(f"offset {offset}: byte increases by +1 in {len(values)} ordered packets (POSSIBLE counter)")
    return findings


def _discriminator_candidates(packets: list[RawPacket]) -> list[str]:
    findings: list[str] = []
    for offset in range(max((packet.length for packet in packets), default=0)):
        values = [packet.payload[offset] for packet in packets if offset < packet.length]
        unique = sorted(set(values))
        if 2 <= len(unique) <= min(16, len(values)) and len(values) >= 3:
            findings.append(f"offset {offset}: values {', '.join(f'{value:02x}' for value in unique)} (POSSIBLE discriminator/command ID; semantics UNKNOWN)")
    return findings


def _offset_summary(packets: list[RawPacket]) -> tuple[list[int], list[int]]:
    constants: list[int] = []
    variables: list[int] = []
    for offset in range(max((packet.length for packet in packets), default=0)):
        values = {packet.payload[offset] for packet in packets if offset < packet.length}
        if len(values) == 1:
            constants.append(offset)
        elif len(values) > 1:
            variables.append(offset)
    return constants, variables


def analyze_packets(packets: list[RawPacket]) -> str:
    lines = [
        "# Protocol analysis",
        "",
        "> This report is observational. It does not prove command semantics or firmware compatibility.",
        "",
        f"- Packets analyzed: **{len(packets)}**",
        "- Confidence labels: **CONFIRMED** is reserved for repeated byte-level facts; **LIKELY**, **POSSIBLE**, **HYPOTHESIS** and **UNKNOWN** do not authorize writes.",
        "",
    ]
    for uuid, values in sorted(_observations(packets).items()):
        lengths = sorted({item.length for item in values})
        constants, variables = _offset_summary(values)
        lines += [f"## Characteristic `{uuid}`", "", f"- Packets: **{len(values)}**", f"- Packet lengths: `{lengths}`"]
        if constants:
            lines.append(f"- Constant offsets across this sample: `{constants}` (CONFIRMED as an observation only).")
        lines.append(f"- Variable offsets: `{variables or 'none'}`.")
        for finding in _discriminator_candidates(values):
            lines.append(f"- {finding}")
        for finding in _counter_candidates(values):
            lines.append(f"- {finding}")
        for finding in _timestamp_candidates(values):
            lines.append(f"- {finding}")
        for finding in _checksum_candidates(values):
            lines.append(f"- {finding}")
        lines += ["", "No packet meaning, command ID, timestamp field or checksum is promoted to CONFIRMED without repeated controlled captures.", ""]
    if not packets:
        lines += ["## No notification packets", "", "No raw notification packets were available for analysis. This is a valid idle observation.", ""]
    return "\n".join(lines)


def analyze_captures(paths: Iterable[Path], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(analyze_packets(load_packets(paths)), encoding="utf-8")
    return output
