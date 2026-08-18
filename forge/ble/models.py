"""JSON-friendly models used by the BLE and capture layers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def bytes_to_hex(value: bytes | bytearray | None) -> str:
    return bytes(value or b"").hex(" ")


@dataclass
class AdvertisementRecord:
    name: str | None
    address: str
    rssi: int | None
    local_name: str | None
    service_uuids: list[str] = field(default_factory=list)
    manufacturer_data: dict[str, str] = field(default_factory=dict)
    service_data: dict[str, str] = field(default_factory=dict)
    tx_power: int | None = None
    possible_candidate: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DescriptorInfo:
    uuid: str
    description: str | None = None


@dataclass
class CharacteristicInfo:
    service_uuid: str
    uuid: str
    description: str | None
    properties: list[str]
    descriptors: list[DescriptorInfo] = field(default_factory=list)
    service_name: str | None = None
    service_type: str = "CUSTOM"

    @property
    def is_custom(self) -> bool:
        return self.service_type == "CUSTOM"

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_uuid": self.service_uuid,
            "uuid": self.uuid,
            "description": self.description,
            "properties": self.properties,
            "descriptors": [asdict(item) for item in self.descriptors],
            "service_name": self.service_name,
            "service_type": self.service_type,
        }


@dataclass
class ServiceInfo:
    uuid: str
    description: str | None
    name: str | None
    service_type: str
    characteristics: list[CharacteristicInfo] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "description": self.description,
            "name": self.name,
            "service_type": self.service_type,
            "characteristics": [item.to_dict() for item in self.characteristics],
        }


@dataclass
class GattSnapshot:
    captured_at: str
    device_name: str | None
    device_address: str
    services: list[ServiceInfo]

    def to_dict(self) -> dict[str, Any]:
        return {
            "captured_at": self.captured_at,
            "device_name": self.device_name,
            "device_address": self.device_address,
            "services": [service.to_dict() for service in self.services],
            "summary": {
                "services": len(self.services),
                "custom_services": sum(service.service_type == "CUSTOM" for service in self.services),
                "characteristics": sum(len(service.characteristics) for service in self.services),
                "read": sum("read" in char.properties for service in self.services for char in service.characteristics),
                "write": sum(
                    any(prop in char.properties for prop in ("write", "write-without-response"))
                    for service in self.services
                    for char in service.characteristics
                ),
                "notify": sum("notify" in char.properties for service in self.services for char in service.characteristics),
                "indicate": sum("indicate" in char.properties for service in self.services for char in service.characteristics),
            },
        }

    def characteristics(self) -> list[CharacteristicInfo]:
        return [char for service in self.services for char in service.characteristics]


@dataclass
class ReadResult:
    timestamp: str
    service_uuid: str
    characteristic_uuid: str
    raw_hex: str
    length: int
    utf8: str | None
    uint8: int | None
    uint16_le: int | None
    uint16_be: int | None
    uint32_le: int | None
    uint32_be: int | None
    interpreted: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NotificationRecord:
    timestamp: str
    service_uuid: str
    characteristic_uuid: str
    raw_hex: str
    length: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
