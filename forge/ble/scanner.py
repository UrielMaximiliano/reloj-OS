"""BLE scanning with JSON-friendly advertising data."""

from __future__ import annotations

import logging
from typing import Any

from .models import AdvertisementRecord

logger = logging.getLogger(__name__)


CANDIDATE_WORDS = ("frg", "joog", "forge", "moy", "moyoung", "watch", "da fit")


def _hex_mapping(values: Any) -> dict[str, str]:
    if not values:
        return {}
    result: dict[str, str] = {}
    for key, value in values.items():
        if isinstance(value, (bytes, bytearray)):
            result[str(key)] = bytes(value).hex(" ")
        else:
            result[str(key)] = str(value)
    return result


def _is_candidate(name: str | None, local_name: str | None) -> bool:
    text = " ".join(value or "" for value in (name, local_name)).lower()
    return any(word in text for word in CANDIDATE_WORDS)


def _record_from_pair(device: Any, advertisement: Any) -> AdvertisementRecord:
    name = getattr(device, "name", None)
    local_name = getattr(advertisement, "local_name", None) or name
    rssi = getattr(advertisement, "rssi", None)
    if rssi is None:
        rssi = getattr(device, "rssi", None)
    return AdvertisementRecord(
        name=name,
        address=str(getattr(device, "address", "")),
        rssi=int(rssi) if rssi is not None else None,
        local_name=local_name,
        service_uuids=[str(item) for item in (getattr(advertisement, "service_uuids", None) or [])],
        manufacturer_data=_hex_mapping(getattr(advertisement, "manufacturer_data", None)),
        service_data=_hex_mapping(getattr(advertisement, "service_data", None)),
        tx_power=getattr(advertisement, "tx_power", None),
        possible_candidate=_is_candidate(name, local_name),
    )


async def scan_devices(timeout: float = 15.0) -> list[AdvertisementRecord]:
    """Discover nearby BLE devices and retain their advertising metadata."""

    from bleak import BleakScanner

    logger.info("Starting BLE scan for %.1f seconds", timeout)
    discovered = await BleakScanner.discover(timeout=timeout, return_adv=True)
    records: list[AdvertisementRecord] = []
    for _address, value in discovered.items():
        if isinstance(value, tuple) and len(value) == 2:
            device, advertisement = value
        else:
            # Compatibility fallback for older Bleak versions.
            device, advertisement = value, None
        if advertisement is None:
            advertisement = type("AdvertisementFallback", (), {})()
        records.append(_record_from_pair(device, advertisement))
    return sorted(records, key=lambda item: (not item.possible_candidate, -(item.rssi or -999), item.address))


def filter_devices(
    records: list[AdvertisementRecord],
    name: str | None = None,
    min_rssi: int | None = None,
) -> list[AdvertisementRecord]:
    """Apply case-insensitive name/local-name and minimum RSSI filters."""

    wanted = name.lower() if name else None
    return [
        record
        for record in records
        if (not wanted or wanted in " ".join(filter(None, (record.name, record.local_name))).lower())
        and (min_rssi is None or (record.rssi is not None and record.rssi >= min_rssi))
    ]
