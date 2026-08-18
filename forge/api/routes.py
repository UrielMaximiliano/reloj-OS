"""Read-only FastAPI routes for local BLE observation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from forge.ble.connector import connected_client, resolve_device
from forge.ble.gatt import enumerate_gatt
from forge.ble.reader import read_safe_characteristics
from forge.ble.scanner import scan_devices
from forge.config import Config, load_config


router = APIRouter()
config: Config = load_config()


def _capture_path(capture_id: str) -> Path:
    # Do not allow the capture endpoint to escape the configured directory.
    if Path(capture_id).name != capture_id or Path(capture_id).suffix.lower() not in {".json", ".jsonl"}:
        raise HTTPException(status_code=400, detail="Invalid capture id")
    path = (config.captures_dir / capture_id).resolve()
    if config.captures_dir.resolve() not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid capture path")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Capture not found")
    return path


@router.get("/devices")
async def devices() -> list[dict[str, Any]]:
    """Scan for nearby devices; this does not connect or write."""

    return [record.to_dict() for record in await scan_devices(config.scan_timeout)]


@router.get("/devices/{device_id}")
async def device_detail(device_id: str) -> dict[str, Any]:
    try:
        device = await resolve_device(address=device_id, timeout=config.scan_timeout)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"name": device.name, "address": device.address, "connected": False}


async def _snapshot(device_id: str):
    try:
        async with connected_client(config, address=device_id) as (client, device):
            return await enumerate_gatt(client, device.name, device.address)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"BLE observation failed: {exc}") from exc


@router.get("/devices/{device_id}/services")
async def services(device_id: str) -> dict[str, Any]:
    snapshot = await _snapshot(device_id)
    return {"device": snapshot.device_address, "services": [item.to_dict() for item in snapshot.services], "summary": snapshot.to_dict()["summary"]}


@router.get("/devices/{device_id}/characteristics")
async def characteristics(device_id: str) -> dict[str, Any]:
    snapshot = await _snapshot(device_id)
    return {"device": snapshot.device_address, "characteristics": [item.to_dict() for item in snapshot.characteristics()]}


@router.get("/devices/{device_id}/battery")
async def battery(device_id: str) -> dict[str, Any]:
    try:
        async with connected_client(config, address=device_id) as (client, device):
            snapshot = await enumerate_gatt(client, device.name, device.address)
            battery_chars = [
                item
                for item in snapshot.characteristics()
                if item.uuid == "00002a19-0000-1000-8000-00805f9b34fb" and "read" in item.properties
            ]
            if not battery_chars:
                return {"device": device.address, "available": False, "reason": "Battery Level is not READ"}
            results = await read_safe_characteristics(client, snapshot, timeout=config.read_timeout)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"BLE observation failed: {exc}") from exc
    result = next((item for item in results if item.characteristic_uuid == battery_chars[0].uuid), None)
    if result is None:
        return {"device": device.address, "available": False, "reason": "No result"}
    return {"device": device.address, "available": result.error is None, **result.to_dict()}


@router.get("/captures")
async def captures() -> list[dict[str, Any]]:
    config.captures_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for path in sorted(config.captures_dir.iterdir()):
        if path.suffix.lower() not in {".json", ".jsonl"} or not path.is_file():
            continue
        stat = path.stat()
        result.append({"id": path.name, "type": path.suffix.lower()[1:], "size": stat.st_size, "modified": stat.st_mtime})
    return result


@router.get("/captures/{capture_id}")
async def capture(capture_id: str) -> Any:
    path = _capture_path(capture_id)
    if path.suffix.lower() == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return {"id": path.name, "format": "jsonl", "rows": rows}
    return {"id": path.name, "format": "json", "data": json.loads(path.read_text(encoding="utf-8"))}
