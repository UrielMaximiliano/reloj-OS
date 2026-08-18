"""Read-only notification monitor."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from .models import GattSnapshot, NotificationRecord


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def monitor_notifications(
    client: Any,
    snapshot: GattSnapshot,
    duration: float | None = None,
    on_record: Callable[[NotificationRecord], Awaitable[None] | None] | None = None,
) -> list[NotificationRecord]:
    """Subscribe to every notify characteristic and collect raw events.

    ``start_notify`` is the standard Bleak subscription operation. No value is
    written by this module and no protocol interpretation is applied.
    """

    queue: asyncio.Queue[NotificationRecord] = asyncio.Queue()
    records: list[NotificationRecord] = []
    subscriptions: list[str] = []
    char_to_service = {char.uuid: char.service_uuid for char in snapshot.characteristics()}

    def callback(sender: Any, data: bytearray) -> None:
        uuid = str(getattr(sender, "uuid", sender)).lower()
        record = NotificationRecord(
            timestamp=_now(),
            service_uuid=char_to_service.get(uuid, "unknown"),
            characteristic_uuid=uuid,
            raw_hex=bytes(data).hex(" "),
            length=len(data),
        )
        queue.put_nowait(record)

    notify_chars = [char for char in snapshot.characteristics() if "notify" in char.properties]
    try:
        for characteristic in notify_chars:
            await client.start_notify(characteristic.uuid, callback)
            subscriptions.append(characteristic.uuid)

        if not subscriptions:
            return records

        loop = asyncio.get_running_loop()
        deadline = loop.time() + duration if duration is not None else None
        while True:
            timeout = None if deadline is None else max(0.0, deadline - loop.time())
            try:
                record = await asyncio.wait_for(queue.get(), timeout=timeout) if timeout is not None else await queue.get()
            except asyncio.TimeoutError:
                break
            records.append(record)
            if on_record:
                result = on_record(record)
                if asyncio.iscoroutine(result):
                    await result
    finally:
        for uuid in reversed(subscriptions):
            try:
                await client.stop_notify(uuid)
            except Exception:
                # Disconnect cleanup should continue even if one backend rejects a stop.
                pass
    return records
