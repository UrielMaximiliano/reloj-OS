"""Diagnose the local Python, Windows Bluetooth and read-only BLE path.

This command is intentionally conservative: it may scan and connect/read when
requested, but it never writes to a GATT characteristic.
"""

from __future__ import annotations

from _bootstrap import ROOT  # noqa: F401

import argparse
import asyncio
import importlib
import importlib.metadata as metadata
import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Check:
    name: str
    status: str
    detail: str


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _status(checks: list[Check], name: str, status: str, detail: str) -> None:
    checks.append(Check(name, status, detail))
    print(f"[{status:<4}] {name}: {detail}")


def _run(command: list[str], timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _powershell(script: str) -> tuple[int, str, str]:
    try:
        result = _run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            timeout=15.0,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _version_text(distribution: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return "not installed"


def _check_python(checks: list[Check]) -> None:
    version = sys.version_info
    version_text = platform.python_version()
    if (version.major, version.minor) in {(3, 12), (3, 13)}:
        _status(checks, "python", "PASS", f"{version_text} ({sys.executable})")
    elif (version.major, version.minor) == (3, 14):
        _status(
            checks,
            "python",
            "WARN",
            f"{version_text} ({sys.executable}); 3.12/3.13 is preferred, but installed Bleak will be tested",
        )
    else:
        _status(checks, "python", "FAIL", f"{version_text} ({sys.executable}); use Python 3.12 or 3.13")

    venv_root = (ROOT / ".venv").resolve()
    active_root = Path(sys.prefix).resolve()
    if sys.prefix != sys.base_prefix and active_root == venv_root:
        _status(checks, "venv", "PASS", str(active_root))
    elif sys.prefix != sys.base_prefix:
        _status(checks, "venv", "WARN", f"active environment is {active_root}, expected {venv_root}")
    else:
        _status(checks, "venv", "FAIL", "the project interpreter is not active; use .venv\\Scripts\\python.exe")

    pip_result = _run([sys.executable, "-m", "pip", "--version"])
    if pip_result.returncode == 0:
        _status(checks, "pip", "PASS", pip_result.stdout.strip())
    else:
        _status(checks, "pip", "FAIL", pip_result.stderr.strip() or "python -m pip failed")


def _check_dependencies(checks: list[Check]) -> None:
    packages = ("bleak", "fastapi", "pydantic", "rich", "uvicorn")
    for package in packages:
        version = _version_text(package)
        if version == "not installed":
            _status(checks, f"dependency:{package}", "FAIL", "not installed")
            continue
        try:
            module = importlib.import_module(package)
            location = getattr(module, "__file__", "loaded")
            _status(checks, f"dependency:{package}", "PASS", f"{version} ({location})")
        except Exception as exc:  # pragma: no cover - depends on local native packages
            _status(checks, f"dependency:{package}", "FAIL", f"{version}, import error: {exc}")


def _check_project_imports(checks: list[Check]) -> None:
    modules = (
        "forge",
        "forge.ble.scanner",
        "forge.ble.gatt",
        "forge.capture.recorder",
        "forge.protocol.analyzer",
        "forge.api.app",
    )
    for name in modules:
        try:
            module = importlib.import_module(name)
            _status(checks, f"project:{name}", "PASS", str(getattr(module, "__file__", "loaded")))
        except Exception as exc:
            _status(checks, f"project:{name}", "FAIL", repr(exc))


def _check_pip(checks: list[Check]) -> None:
    result = _run([sys.executable, "-m", "pip", "check"])
    if result.returncode == 0:
        _status(checks, "pip-check", "PASS", result.stdout.strip() or "No broken requirements found")
    else:
        _status(checks, "pip-check", "FAIL", result.stdout.strip() or result.stderr.strip())


def _check_cli_help(checks: list[Check]) -> None:
    for script in ("scan.py", "inspect.py", "read_safe.py", "monitor.py"):
        path = ROOT / "scripts" / script
        result = _run([sys.executable, str(path), "--help"])
        if result.returncode == 0:
            _status(checks, f"cli-help:{script}", "PASS", "--help completed")
        else:
            detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
            _status(checks, f"cli-help:{script}", "FAIL", detail.splitlines()[-1])


def _check_config(checks: list[Check]) -> None:
    path = ROOT / "config.json"
    if not path.exists():
        _status(checks, "config", "WARN", "config.json is absent; safe defaults are active")
        _status(checks, "allow_write", "PASS", "false by safe default")
        return
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _status(checks, "config", "FAIL", repr(exc))
        _status(checks, "allow_write", "FAIL", "cannot verify safety gate")
        return
    if not isinstance(raw, dict):
        _status(checks, "config", "FAIL", "config.json must contain a JSON object")
        _status(checks, "allow_write", "FAIL", "cannot verify safety gate")
        return
    _status(checks, "config", "PASS", str(path))
    if raw.get("allow_write") is False:
        _status(checks, "allow_write", "PASS", "false")
    else:
        _status(checks, "allow_write", "FAIL", "must be explicitly false")


def _check_windows_bluetooth(checks: list[Check]) -> None:
    pnp_code, pnp_out, pnp_err = _powershell(
        "Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | "
        "Select-Object Status,FriendlyName,InstanceId | ConvertTo-Json -Compress"
    )
    if pnp_code == 0 and pnp_out:
        try:
            devices: Any = json.loads(pnp_out)
            if isinstance(devices, dict):
                devices = [devices]
            good = [d for d in devices if str(d.get("Status", "")).lower() == "ok"]
            adapter = [d for d in good if "adapter" in str(d.get("FriendlyName", "")).lower()]
            if adapter:
                names = ", ".join(str(d.get("FriendlyName")) for d in adapter)
                _status(checks, "bluetooth-adapter", "PASS", f"{names}; OK devices={len(good)}")
            elif good:
                _status(checks, "bluetooth-adapter", "WARN", f"Bluetooth devices are OK; adapter name was not identified")
            else:
                _status(checks, "bluetooth-adapter", "FAIL", "no Bluetooth PnP device is OK")
        except json.JSONDecodeError:
            _status(checks, "bluetooth-adapter", "WARN", pnp_out[:300])
    else:
        _status(checks, "bluetooth-adapter", "FAIL", pnp_err or "Get-PnpDevice returned no Bluetooth devices")

    service_code, service_out, service_err = _powershell(
        "Get-Service bthserv -ErrorAction SilentlyContinue | "
        "Select-Object Status,StartType,Name | ConvertTo-Json -Compress"
    )
    if service_code == 0 and service_out:
        try:
            service = json.loads(service_out)
            status = service.get("Status", "")
            # ConvertTo-Json may serialize the PowerShell ServiceControllerStatus
            # enum as its numeric value (4 == Running) on some Windows builds.
            if str(status).lower() == "running" or str(status) == "4":
                _status(checks, "bthserv", "PASS", "Running")
            else:
                _status(checks, "bthserv", "FAIL", str(service))
        except json.JSONDecodeError:
            _status(checks, "bthserv", "WARN", service_out[:300])
    else:
        _status(checks, "bthserv", "FAIL", service_err or "Bluetooth Support Service was not found")


async def _scan(device_name: str, timeout: float) -> tuple[int, str, list[dict[str, Any]]]:
    from forge.ble.scanner import filter_devices, scan_devices

    records = await scan_devices(timeout)
    matches = filter_devices(records, name=device_name)
    return len(records), device_name, [record.to_dict() for record in matches]


def _check_ble_scan(checks: list[Check], device_name: str, timeout: float) -> None:
    try:
        total, requested, matches = asyncio.run(_scan(device_name, timeout))
    except Exception as exc:
        _status(checks, "ble-scan", "FAIL", repr(exc))
        return
    if matches:
        addresses = ", ".join(str(item.get("address")) for item in matches)
        _status(checks, "ble-scan", "PASS", f"{requested} detected; {len(matches)} match(es), address={addresses}; total={total}")
    else:
        _status(checks, "ble-scan", "WARN", f"{requested} not detected in {timeout:.1f}s; total devices={total}")


def _write_log(checks: list[Check]) -> Path:
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"doctor_{_stamp()}.log"
    path.write_text(
        "\n".join(f"[{item.status}] {item.name}: {item.detail}" for item in checks) + "\n",
        encoding="utf-8",
    )
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnostico del entorno Python, Bluetooth y BLE read-only")
    parser.add_argument("--no-scan", action="store_true", help="no ejecutar el escaneo BLE independiente")
    parser.add_argument("--scan-timeout", type=float, default=5.0, help="duracion del escaneo BLE (default: 5s)")
    parser.add_argument("--device", default="FRG", help="nombre del dispositivo BLE que se busca")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    checks: list[Check] = []
    print(f"forge-research doctor | Python {platform.python_version()} | {sys.executable}")
    _check_python(checks)
    _check_dependencies(checks)
    _check_project_imports(checks)
    _check_pip(checks)
    _check_cli_help(checks)
    _check_config(checks)
    _check_windows_bluetooth(checks)
    if not args.no_scan:
        _check_ble_scan(checks, args.device, args.scan_timeout)
    log_path = _write_log(checks)
    failures = sum(item.status == "FAIL" for item in checks)
    warnings = sum(item.status == "WARN" for item in checks)
    print(f"\nSummary: FAIL={failures} WARN={warnings} log={log_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
