"""Bluetooth SIG UUID names used for labeling, never for protocol assumptions."""

from __future__ import annotations

import re


SIG_BASE = "0000{short}-0000-1000-8000-00805f9b34fb"

SERVICES: dict[str, str] = {
    "1800": "Generic Access",
    "1801": "Generic Attribute",
    "1805": "Current Time",
    "180a": "Device Information",
    "180d": "Heart Rate",
    "180f": "Battery Service",
    "181c": "User Data",
    "181d": "Weight Scale",
}

CHARACTERISTICS: dict[str, str] = {
    "2a00": "Device Name",
    "2a01": "Appearance",
    "2a04": "Peripheral Preferred Connection Parameters",
    "2a05": "Service Changed",
    "2a06": "Alert Level",
    "2a19": "Battery Level",
    "2a23": "System ID",
    "2a24": "Model Number String",
    "2a25": "Serial Number String",
    "2a26": "Firmware Revision String",
    "2a27": "Hardware Revision String",
    "2a28": "Software Revision String",
    "2a29": "Manufacturer Name String",
    "2a2a": "IEEE 11073-20601 Regulatory Certification Data List",
    "2a2b": "Current Time",
    "2a37": "Heart Rate Measurement",
    "2a38": "Body Sensor Location",
    "2a39": "Heart Rate Control Point",
    "2a8a": "First Name",
    "2a8c": "Last Name",
    "2a8e": "Gender",
    "2a9d": "Weight Measurement",
    "2a9e": "Weight Scale Feature",
    "2a9f": "User Control Point",
    "2a50": "PnP ID",
}

OTA_KEYWORDS = ("ota", "dfu", "firmware", "update", "jieli", "jiel", "jl", "moyoung", "crp", "da fit")


def normalize_uuid(uuid: str) -> str:
    return str(uuid).lower()


def short_uuid(uuid: str) -> str | None:
    normalized = normalize_uuid(uuid)
    match = re.fullmatch(r"(?:0000)?([0-9a-f]{4})-0000-1000-8000-00805f9b34fb", normalized)
    if match:
        return match.group(1)
    if re.fullmatch(r"[0-9a-f]{4}", normalized):
        return normalized
    return None


def is_standard_uuid(uuid: str) -> bool:
    return short_uuid(uuid) is not None


def service_name(uuid: str) -> str | None:
    short = short_uuid(uuid)
    return SERVICES.get(short) if short else None


def characteristic_name(uuid: str) -> str | None:
    short = short_uuid(uuid)
    return CHARACTERISTICS.get(short) if short else None


def classify_service(uuid: str) -> tuple[str | None, str]:
    name = service_name(uuid)
    # Only services in our explicit SIG registry are marked STANDARD. A
    # 16-bit UUID shape by itself is not enough to identify a service.
    return name, "STANDARD" if name else "CUSTOM"


def looks_like_ota(*values: str | None) -> bool:
    haystack = " ".join(value.lower() for value in values if value)
    return any(keyword in haystack for keyword in OTA_KEYWORDS)
