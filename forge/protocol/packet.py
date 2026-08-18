"""Raw packet primitives used by offline analysis only."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RawPacket:
    characteristic_uuid: str
    payload: bytes
    timestamp: str | None = None

    @property
    def length(self) -> int:
        return len(self.payload)

    @property
    def hex(self) -> str:
        return self.payload.hex(" ")


def xor8(data: bytes) -> int:
    result = 0
    for value in data:
        result ^= value
    return result


def sum8(data: bytes) -> int:
    return sum(data) & 0xFF


def parse_hex(value: str) -> bytes:
    return bytes.fromhex(value.replace(" ", "").replace(":", ""))
