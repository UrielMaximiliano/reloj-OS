"""Subscribe to GATT notifications and record raw packets as JSONL."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
import asyncio
from pathlib import Path

from forge.cli_common import console, device_arguments, runtime
from forge.ble.connector import connected_client
from forge.ble.gatt import enumerate_gatt
from forge.ble.notifier import monitor_notifications
from forge.capture.recorder import CaptureRecorder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitorea NOTIFY y guarda una captura JSONL")
    device_arguments(parser)
    parser.add_argument("--label", default="session", help="Etiqueta de la sesión")
    parser.add_argument("--duration", type=float, help="Duración en segundos; sin valor espera hasta Ctrl+C")
    parser.add_argument("--output", help="Archivo JSONL de salida")
    parser.add_argument("--all", action="store_true", help="Suscribirse a todas las characteristics NOTIFY (opción explícita)")
    return parser


async def run(args: argparse.Namespace) -> int:
    config = runtime(args.config, args.log_level)
    async with connected_client(config, address=args.address, name=args.device_name) as (client, device):
        snapshot = await enumerate_gatt(client, device.name, device.address)
        output = None if not args.output else Path(args.output)
        with CaptureRecorder(config.captures_dir, label=args.label, output=output) as recorder:
            recorder.write_event({
                "event": "gatt_snapshot",
                "timestamp": snapshot.captured_at,
                "device_name": device.name,
                "device_address": device.address,
                "notify_characteristics": [
                    char.uuid for char in snapshot.characteristics() if "notify" in char.properties
                ],
            })

            async def on_record(record: object) -> None:
                recorder.record_notification(record)  # type: ignore[arg-type]
                console.print(f"[{record.timestamp}] {record.characteristic_uuid} LEN={record.length} HEX={record.raw_hex}")  # type: ignore[attr-defined]

            notify_count = sum("notify" in char.properties for char in snapshot.characteristics())
            console.print(f"Connected: YES | NOTIFY characteristics: {notify_count}")
            if not args.all:
                console.print("Monitoring all NOTIFY characteristics by default; --all documents the intent explicitly.")
            await monitor_notifications(client, snapshot, duration=args.duration, on_record=on_record)
            console.print(f"Capture: {recorder.path}")
    return 0


def main() -> int:
    try:
        return asyncio.run(run(build_parser().parse_args()))
    except KeyboardInterrupt:
        console.print("\nMonitor stopped; capture was closed safely.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
