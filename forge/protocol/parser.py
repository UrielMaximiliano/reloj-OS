"""Intentionally modest packet parsing helpers.

The project starts from observations and does not assign command meanings
without captures that support them.
"""

from __future__ import annotations

from .packet import RawPacket


def packet_from_row(row: dict[str, object]) -> RawPacket:
    raw = str(row.get("raw_hex", ""))
    return RawPacket(
        characteristic_uuid=str(row.get("characteristic_uuid", "unknown")),
        payload=bytes.fromhex(raw.replace(" ", "")),
        timestamp=str(row.get("timestamp")) if row.get("timestamp") else None,
    )
