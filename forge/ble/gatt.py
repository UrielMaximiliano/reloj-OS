"""GATT enumeration and documentation export."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import CharacteristicInfo, DescriptorInfo, GattSnapshot, ReadResult, ServiceInfo
from forge.protocol.known_services import classify_service, characteristic_name, looks_like_ota, service_name


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _description(item: Any) -> str | None:
    value = getattr(item, "description", None)
    return str(value) if value else None


async def enumerate_gatt(client: Any, device_name: str | None, device_address: str) -> GattSnapshot:
    """Enumerate services, characteristics and descriptors after connection."""

    services_collection = getattr(client, "services", None)
    if services_collection is None and hasattr(client, "get_services"):
        services_collection = await client.get_services()
    if services_collection is None:
        raise RuntimeError("Bleak no expuso la colección de servicios después de conectar")

    services: list[ServiceInfo] = []
    for service in services_collection:
        service_uuid = str(service.uuid).lower()
        known_name, service_type = classify_service(service_uuid)
        chars: list[CharacteristicInfo] = []
        for characteristic in service.characteristics:
            char_uuid = str(characteristic.uuid).lower()
            descriptors = [
                DescriptorInfo(uuid=str(descriptor.uuid).lower(), description=_description(descriptor))
                for descriptor in (getattr(characteristic, "descriptors", None) or [])
            ]
            properties = sorted({str(prop).lower() for prop in (characteristic.properties or [])})
            chars.append(
                CharacteristicInfo(
                    service_uuid=service_uuid,
                    uuid=char_uuid,
                    description=_description(characteristic) or characteristic_name(char_uuid),
                    properties=properties,
                    descriptors=descriptors,
                    service_name=known_name,
                    service_type=service_type,
                )
            )
        services.append(
            ServiceInfo(
                uuid=service_uuid,
                description=_description(service),
                name=known_name,
                service_type=service_type,
                characteristics=chars,
            )
        )
    return GattSnapshot(utc_now(), device_name, device_address, services)


def possible_ota_items(snapshot: GattSnapshot) -> list[dict[str, Any]]:
    """Return only evidence-bearing labels; this function never writes to BLE."""

    candidates: list[dict[str, Any]] = []
    for service in snapshot.services:
        if looks_like_ota(service.uuid, service.name, service.description):
            candidates.append({"kind": "service", "uuid": service.uuid, "name": service.name, "evidence": "UUID/name/description keyword"})
        for characteristic in service.characteristics:
            # A standard Device Information firmware/software revision is
            # useful evidence about versioning, but is not an OTA channel.
            if service_name(service.uuid) and characteristic_name(characteristic.uuid):
                continue
            if looks_like_ota(characteristic.uuid, characteristic.description):
                candidates.append({"kind": "characteristic", "uuid": characteristic.uuid, "service_uuid": service.uuid, "name": characteristic.description, "evidence": "UUID/name keyword"})
    return candidates


def possible_command_channels(snapshot: GattSnapshot) -> list[dict[str, Any]]:
    """Find custom services exposing both a write path and a notify path.

    This is a structural observation only. It must never trigger a write.
    """

    candidates: list[dict[str, Any]] = []
    for service in snapshot.services:
        if service.service_type != "CUSTOM":
            continue
        write_chars = [
            char.uuid
            for char in service.characteristics
            if any(prop in char.properties for prop in ("write", "write-without-response"))
        ]
        notify_chars = [
            char.uuid
            for char in service.characteristics
            if any(prop in char.properties for prop in ("notify", "indicate"))
        ]
        if write_chars and notify_chars:
            candidates.append(
                {
                    "service_uuid": service.uuid,
                    "write_characteristics": write_chars,
                    "notification_characteristics": notify_chars,
                    "status": "POSSIBLE / UNCONFIRMED",
                }
            )
    return candidates


def characteristic_role(characteristic: CharacteristicInfo) -> tuple[str, str]:
    """Classify direction from GATT properties only.

    The role is deliberately a candidate, because properties do not prove that
    the endpoint is used by the Da Fit app or that a packet has been exchanged.
    """

    props = set(characteristic.properties)
    has_write = bool(props & {"write", "write-without-response"})
    has_rx = bool(props & {"notify", "indicate"})
    if has_write and has_rx:
        return "bidirectional candidate", "POSSIBLE"
    if has_write:
        return "TX candidate (PC -> watch)", "POSSIBLE"
    if has_rx and "read" in props:
        return "telemetry candidate (watch -> PC)", "POSSIBLE"
    if has_rx:
        return "RX candidate (watch -> PC)", "POSSIBLE"
    if "read" in props:
        return "readable state", "UNKNOWN"
    return "unknown", "UNKNOWN"


def _read_result_map(read_results: list[ReadResult] | None) -> dict[str, ReadResult]:
    return {result.characteristic_uuid.lower(): result for result in (read_results or [])}


def snapshot_document(
    snapshot: GattSnapshot,
    read_results: list[ReadResult] | None = None,
    observed_notification_uuids: set[str] | None = None,
) -> dict[str, Any]:
    """Return an exhaustive, evidence-aware GATT document."""

    document = snapshot.to_dict()
    result_map = _read_result_map(read_results)
    observed = {value.lower() for value in (observed_notification_uuids or set())}
    for service in document["services"]:
        for characteristic in service["characteristics"]:
            uuid = characteristic["uuid"].lower()
            model = next(item for item in snapshot.characteristics() if item.uuid == uuid)
            role, confidence = characteristic_role(model)
            result = result_map.get(uuid)
            characteristic.update(
                {
                    "current_read": result.to_dict() if result else None,
                    "notification_observed": uuid in observed,
                    "write_available": any(prop in model.properties for prop in ("write", "write-without-response")),
                    "interpretation": role,
                    "confidence": confidence,
                }
            )
    document["read_results"] = [result.to_dict() for result in (read_results or [])]
    document["observed_notification_uuids"] = sorted(observed)
    document["safety"] = {"read_only": True, "writes_attempted": False}
    return document


def snapshot_markdown(
    snapshot: GattSnapshot,
    read_results: list[ReadResult] | None = None,
    observed_notification_uuids: set[str] | None = None,
) -> str:
    lines = [
        "# BLE map",
        "",
        "> Generated from a live GATT enumeration. No BLE writes are performed by the exporter.",
        "",
        f"- Captured: `{snapshot.captured_at}`",
        f"- Device: `{snapshot.device_name or 'unknown'}`",
        f"- Address/identifier: `{snapshot.device_address}`",
        "",
        "## Summary",
        "",
        f"- Services: **{len(snapshot.services)}**",
        f"- Custom services: **{sum(item.service_type == 'CUSTOM' for item in snapshot.services)}**",
        f"- Characteristics: **{len(snapshot.characteristics())}**",
        f"- READ values captured: **{len(read_results or [])}**",
        "",
    ]
    result_map = _read_result_map(read_results)
    observed = {value.lower() for value in (observed_notification_uuids or set())}
    for service in snapshot.services:
        lines += [
            f"## Service `{service.uuid}`",
            "",
            f"- Name: {service.name or 'Unknown'}",
            f"- Type: **{service.service_type}**",
            f"- Description: {service.description or '—'}",
            "",
        ]
        lines += [
            "| Characteristic UUID | Properties | Descriptors | Current readable value | Notification observed | Write available | Interpretation | Confidence |",
            "|---|---|---:|---|---|---|---|---|",
        ]
        for characteristic in service.characteristics:
            result = result_map.get(characteristic.uuid)
            role, confidence = characteristic_role(characteristic)
            lines.append(
                f"| `{characteristic.uuid}` | `{', '.join(characteristic.properties) or 'none'}` | {len(characteristic.descriptors)} | `{result.raw_hex if result else 'not read'}` | {'YES' if characteristic.uuid in observed else 'NO'} | {'YES' if any(prop in characteristic.properties for prop in ('write', 'write-without-response')) else 'NO'} | {role} | {confidence} |"
            )
        lines.append("")
        for characteristic in service.characteristics:
            lines += [
                f"### Characteristic `{characteristic.uuid}`",
                "",
                f"- Description: {characteristic.description or 'Unknown'}",
                f"- Properties: `{', '.join(characteristic.properties) or 'none'}`",
                f"- Descriptors: {len(characteristic.descriptors)}",
                f"- Interpretation: **{characteristic_role(characteristic)[0]}**",
                f"- Confidence: **{characteristic_role(characteristic)[1]}**",
                "",
            ]
            result = result_map.get(characteristic.uuid)
            if result:
                lines += [
                    f"- Current readable value: `{result.raw_hex or 'empty'}`",
                    f"- UTF-8: `{result.utf8 or '—'}`",
                    f"- Numeric: uint8=`{result.uint8 if result.uint8 is not None else '—'}`, uint16 LE=`{result.uint16_le if result.uint16_le is not None else '—'}`, uint16 BE=`{result.uint16_be if result.uint16_be is not None else '—'}`, uint32 LE=`{result.uint32_le if result.uint32_le is not None else '—'}`, uint32 BE=`{result.uint32_be if result.uint32_be is not None else '—'}`",
                ]
            else:
                lines.append("- Current readable value: `not read in this inspection`")
            lines.append(f"- Notification observed: **{'YES' if characteristic.uuid in observed else 'NO / not observed in this session'}**")
            lines.append(f"- Write available: **{'YES' if any(prop in characteristic.properties for prop in ('write', 'write-without-response')) else 'NO'}**")
            lines.append("")
            for descriptor in characteristic.descriptors:
                lines.append(f"  - Descriptor `{descriptor.uuid}`: {descriptor.description or 'Unknown'}")
            lines.append("")
    command_channels = possible_command_channels(snapshot)
    ota = possible_ota_items(snapshot)
    if command_channels:
        lines += ["## Possible command channels", "", "- Structural candidate only; no writes were attempted.", ""]
        for item in command_channels:
            lines.append(
                f"- Service `{item['service_uuid']}` — WRITE: `{', '.join(item['write_characteristics'])}`; NOTIFY/INDICATE: `{', '.join(item['notification_characteristics'])}` — **POSSIBLE / UNCONFIRMED**"
            )
        lines.append("")
    lines += ["## OTA / DFU observation", "", "- Status: **UNKNOWN unless the enumerated evidence below exists.**", ""]
    if ota:
        lines += ["Possible evidence (not verified and not exercised):", ""]
        lines.extend(f"- `{item['kind']}` `{item['uuid']}` — {item.get('name') or item['evidence']}" for item in ota)
    else:
        lines.append("- No service or characteristic name/UUID matched the conservative OTA keyword screen.")
    lines.append("")
    return "\n".join(lines)


def update_ble_map(
    snapshot: GattSnapshot,
    path: Path,
    read_results: list[ReadResult] | None = None,
    observed_notification_uuids: set[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(snapshot_markdown(snapshot, read_results, observed_notification_uuids), encoding="utf-8")
