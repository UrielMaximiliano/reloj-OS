"""Read only GATT characteristics explicitly advertising the READ property."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
import asyncio

from forge.cli_common import choose_output, console, device_arguments, runtime
from forge.ble.connector import connected_client
from forge.ble.gatt import enumerate_gatt
from forge.ble.reader import read_safe_characteristics
from forge.capture.exporter import filename_timestamp, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lee exclusivamente characteristics con propiedad READ")
    device_arguments(parser)
    parser.add_argument("--label", help="Etiqueta del snapshot, por ejemplo before_hr o after_hr")
    parser.add_argument("--output", help="Archivo JSON de salida")
    return parser


async def run(args: argparse.Namespace) -> int:
    config = runtime(args.config, args.log_level)
    async with connected_client(config, address=args.address, name=args.device_name) as (client, device):
        snapshot = await enumerate_gatt(client, device.name, device.address)
        results = await read_safe_characteristics(client, snapshot, timeout=config.read_timeout)

    label = f"_{args.label}" if args.label else ""
    output = choose_output(config, args.output, f"safe_read{label}_{filename_timestamp()}.json")
    payload = {
        "captured_at": snapshot.captured_at,
        "device_name": device.name,
        "device_address": device.address,
        "label": args.label,
        "firmware_hint": config.known_firmware,
        "read_only": True,
        "writes_attempted": False,
        "results": [result.to_dict() for result in results],
    }
    write_json(output, payload)
    console.print(f"Connected: YES | safe READ results: {len(results)}")
    for result in results:
        text = f"{result.characteristic_uuid} | {result.raw_hex or '—'} | UTF-8={result.utf8 or '—'} | UINT8={result.uint8 if result.uint8 is not None else '—'}"
        if result.error:
            text += f" | ERROR={result.error}"
        console.print(text)
    console.print(f"JSON: {output}")
    return 0


def main() -> int:
    return asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
