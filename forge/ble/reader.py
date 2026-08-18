"""Read-only GATT characteristic reader."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from .models import CharacteristicInfo, GattSnapshot, ReadResult
from forge.protocol.known_services import characteristic_name, service_name


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _utf8(data: bytes) -> str | None:
    try:
        value = data.decode("utf-8").rstrip("\x00")
        return value if value and all(char.isprintable() or char in "\r\n\t" for char in value) else None
    except UnicodeDecodeError:
        return None


def _interpreted(service_uuid: str, characteristic_uuid: str, data: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {}
    service = service_name(service_uuid)
    characteristic = characteristic_name(characteristic_uuid)
    if service:
        result["service"] = service
    if characteristic:
        result["characteristic"] = characteristic
    if characteristic == "Battery Level" and len(data) >= 1:
        result["battery_percent"] = data[0]
    return result


def _result(service_uuid: str, characteristic_uuid: str, data: bytes, error: str | None = None) -> ReadResult:
    return ReadResult(
        timestamp=_now(),
        service_uuid=service_uuid,
        characteristic_uuid=characteristic_uuid,
        raw_hex=data.hex(" "),
        length=len(data),
        utf8=_utf8(data),
        uint8=data[0] if len(data) >= 1 else None,
        uint16_le=int.from_bytes(data[:2], "little") if len(data) >= 2 else None,
        uint16_be=int.from_bytes(data[:2], "big") if len(data) >= 2 else None,
        uint32_le=int.from_bytes(data[:4], "little") if len(data) >= 4 else None,
        uint32_be=int.from_bytes(data[:4], "big") if len(data) >= 4 else None,
        interpreted=_interpreted(service_uuid, characteristic_uuid, data),
        error=error,
    )


async def read_characteristic(client: Any, characteristic: CharacteristicInfo, timeout: float = 10.0) -> ReadResult:
    """Read one characteristic, with a bounded timeout and no write fallback."""

    try:
        raw = await asyncio.wait_for(client.read_gatt_char(characteristic.uuid), timeout=timeout)
        data = bytes(raw)
        result = _result(characteristic.service_uuid, characteristic.uuid, data)
        result.interpreted.update(_interpreted(characteristic.service_uuid, characteristic.uuid, data))
        return result
    except Exception as exc:  # BLE backends expose several platform-specific exception types.
        return _result(characteristic.service_uuid, characteristic.uuid, b"", error=f"{type(exc).__name__}: {exc}")


async def read_safe_characteristics(client: Any, snapshot: GattSnapshot, timeout: float = 10.0) -> list[ReadResult]:
    """Read only characteristics whose properties explicitly contain ``read``."""

    results: list[ReadResult] = []
    for characteristic in snapshot.characteristics():
        if "read" not in characteristic.properties:
            continue
        results.append(await read_characteristic(client, characteristic, timeout=timeout))
    return results
