"""Connect and enumerate the complete GATT database without writing."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
import asyncio
from pathlib import Path

from rich.console import Group
from rich.panel import Panel

from forge.cli_common import choose_output, console, device_arguments, runtime
from forge.ble.connector import connected_client
from forge.ble.gatt import enumerate_gatt, possible_command_channels, possible_ota_items, snapshot_document, update_ble_map
from forge.ble.reader import read_safe_characteristics
from forge.capture.exporter import filename_timestamp, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspecciona servicios GATT, characteristics y descriptors")
    device_arguments(parser)
    parser.add_argument("--output", help="Archivo JSON de salida")
    return parser


async def run(args: argparse.Namespace) -> int:
    config = runtime(args.config, args.log_level)
    async with connected_client(config, address=args.address, name=args.device_name) as (client, device):
        snapshot = await enumerate_gatt(client, device.name, device.address)
        read_results = await read_safe_characteristics(client, snapshot, timeout=config.read_timeout)

    output = choose_output(config, args.output, f"gatt_{filename_timestamp()}.json")
    write_json(output, snapshot_document(snapshot, read_results))
    update_ble_map(snapshot, Path(__file__).resolve().parents[1] / "docs" / "ble-map.md", read_results)

    summary = snapshot.to_dict()["summary"]
    console.print(Panel(
        Group(
            f"Connected: YES",
            f"Device: {device.name or 'Unnamed'}",
            f"Address/identifier: {device.address}",
            f"Services: {summary['services']}",
            f"Custom services: {summary['custom_services']}",
            f"Characteristics: {summary['characteristics']}",
            f"READ: {summary['read']} | WRITE: {summary['write']} | NOTIFY: {summary['notify']} | INDICATE: {summary['indicate']}",
            f"Safe READ values captured: {len(read_results)}",
        ),
        title="GATT inspection",
    ))
    for service in snapshot.services:
        console.print(f"\n[bold]SERVICE[/bold] {service.uuid} | {service.name or 'Unknown'} | {service.service_type}")
        for characteristic in service.characteristics:
            console.print(f"  CHARACTERISTIC {characteristic.uuid} | {characteristic.description or 'Unknown'}")
            console.print(f"    Properties: {', '.join(characteristic.properties) or 'none'}")
            for descriptor in characteristic.descriptors:
                console.print(f"    Descriptor: {descriptor.uuid} | {descriptor.description or 'Unknown'}")
    ota = possible_ota_items(snapshot)
    command_channels = possible_command_channels(snapshot)
    console.print(f"\nPossible command channel: {len(command_channels)} custom service(s) with WRITE + NOTIFY/INDICATE; unconfirmed")
    for item in command_channels:
        console.print(f"  Service {item['service_uuid']} | WRITE={', '.join(item['write_characteristics'])} | NOTIFY/INDICATE={', '.join(item['notification_characteristics'])}")
    console.print(f"Possible OTA/DFU: {'nominal evidence found; not exercised' if ota else 'UNKNOWN'}")
    console.print(f"JSON: {output}")
    console.print("BLE map: docs/ble-map.md")
    return 0


def main() -> int:
    return asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
