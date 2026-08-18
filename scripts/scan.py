"""Scan BLE and export advertising packets."""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from rich.table import Table

from forge.cli_common import console, runtime
from forge.ble.scanner import filter_devices, scan_devices


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Escanea dispositivos BLE y muestra sus advertising packets")
    parser.add_argument("--timeout", type=float, default=None, help="Duración del escaneo en segundos (default: config/15)")
    parser.add_argument("--name", help="Filtrar por nombre o local name")
    parser.add_argument("--min-rssi", type=int, help="Mostrar solamente RSSI >= valor")
    parser.add_argument("--json", dest="json_path", help="Exportar resultados a este archivo JSON")
    parser.add_argument("--config", help="Ruta a config.json")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return parser


async def run(args: argparse.Namespace) -> int:
    config = runtime(args.config, args.log_level)
    records = await scan_devices(args.timeout or config.scan_timeout)
    records = filter_devices(records, name=args.name, min_rssi=args.min_rssi)

    table = Table(title=f"BLE devices ({len(records)})")
    table.add_column("Candidate")
    table.add_column("Name")
    table.add_column("Address / identifier")
    table.add_column("RSSI")
    table.add_column("Local name")
    table.add_column("Service UUIDs")
    for record in records:
        table.add_row(
            "YES" if record.possible_candidate else "",
            record.name or "—",
            record.address or "—",
            str(record.rssi) if record.rssi is not None else "—",
            record.local_name or "—",
            ", ".join(record.service_uuids) or "—",
        )
    console.print(table)
    for record in records:
        console.print(f"\n[bold]{record.name or record.local_name or 'Unnamed'}[/bold]")
        console.print(f"Address/identifier: {record.address}")
        console.print(f"RSSI: {record.rssi if record.rssi is not None else '—'}")
        console.print(f"Manufacturer data: {json.dumps(record.manufacturer_data, ensure_ascii=False)}")
        console.print(f"Service data: {json.dumps(record.service_data, ensure_ascii=False)}")
        console.print(f"TX power: {record.tx_power if record.tx_power is not None else '—'}")
        if record.possible_candidate:
            console.print("[green]Possible JOOG Forge candidate[/green]")

    if args.json_path:
        path = Path(args.json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "timeout_seconds": args.timeout or config.scan_timeout,
            "filters": {"name": args.name, "min_rssi": args.min_rssi},
            "devices": [record.to_dict() for record in records],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        console.print(f"\nExported JSON: {path}")
    return 0


def main() -> int:
    return asyncio.run(run(build_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
