"""Safe BLE device resolution and connection lifecycle."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, TYPE_CHECKING

if TYPE_CHECKING:
    from bleak import BleakClient
    from bleak.backends.device import BLEDevice

from forge.config import Config

logger = logging.getLogger(__name__)


async def resolve_device(
    *,
    address: str | None = None,
    name: str | None = None,
    timeout: float = 15.0,
) -> Any:
    """Resolve a BLEDevice by address/identifier or by a name from a fresh scan."""

    from bleak import BleakScanner

    if address:
        device = await BleakScanner.find_device_by_address(address, timeout=timeout)
        if device is not None:
            return device
        raise RuntimeError(
            f"No se encontró el identificador BLE {address!r}. En Windows puede no coincidir con la MAC visible."
        )

    if not name:
        raise ValueError("Debe indicar --device/--name o device_address/device_name en config.json")

    devices = await BleakScanner.discover(timeout=timeout)
    wanted = name.casefold()
    exact: list[BLEDevice] = []
    partial: list[BLEDevice] = []
    for device in devices:
        device_name = (getattr(device, "name", None) or "").casefold()
        if device_name == wanted:
            exact.append(device)
        elif wanted in device_name:
            partial.append(device)
    matches = exact or partial
    if not matches:
        raise RuntimeError(f"No se encontró un dispositivo BLE cuyo nombre contenga {name!r}")
    if len(matches) > 1:
        logger.warning("Multiple devices matched %r; using strongest first result", name)
    return matches[0]


@asynccontextmanager
async def connected_client(
    config: Config,
    *,
    address: str | None = None,
    name: str | None = None,
) -> AsyncIterator[tuple[Any, Any]]:
    """Resolve and connect, always attempting a clean disconnect."""

    from bleak import BleakClient

    device = await resolve_device(
        address=address or config.device_address,
        name=name or config.device_name,
        timeout=config.scan_timeout,
    )
    client = BleakClient(device, timeout=config.connect_timeout)
    try:
        logger.info("Connecting to %s (%s)", device.name, device.address)
        await client.connect()
        if not client.is_connected:
            raise ConnectionError(f"BLE connection did not become active for {device.address}")
        yield client, device
    finally:
        if client.is_connected:
            logger.info("Disconnecting from %s", device.address)
            await client.disconnect()
