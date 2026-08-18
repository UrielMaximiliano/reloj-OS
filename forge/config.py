"""Configuration and safety gates for the Forge research toolkit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Config:
    """Runtime configuration.

    The first release intentionally has no write operation. ``allow_write`` is
    retained as an explicit safety gate for future work and defaults to false.
    """

    device_name: str | None = "FRG"
    device_address: str | None = None
    known_firmware: str | None = "MOY-8QJ4-2.0.8"
    known_display: str | None = "360x360"
    soc: str | None = "JL7012F6"
    allow_write: bool = False
    scan_timeout: float = 15.0
    connect_timeout: float = 15.0
    read_timeout: float = 10.0
    captures_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "captures")
    logs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], project_root: Path = PROJECT_ROOT) -> "Config":
        def path_value(name: str, default: str) -> Path:
            value = raw.get(name, default)
            path = Path(str(value))
            return path if path.is_absolute() else project_root / path

        raw_allow_write = raw.get("allow_write", False)
        if not isinstance(raw_allow_write, bool):
            raw_allow_write = False

        return cls(
            device_name=raw.get("device_name"),
            device_address=raw.get("device_address"),
            known_firmware=raw.get("known_firmware"),
            known_display=raw.get("known_display"),
            soc=raw.get("soc"),
            # Never turn this on accidentally through a malformed config.
            allow_write=raw_allow_write,
            scan_timeout=float(raw.get("scan_timeout", 15.0)),
            connect_timeout=float(raw.get("connect_timeout", 15.0)),
            read_timeout=float(raw.get("read_timeout", 10.0)),
            captures_dir=path_value("captures_dir", "captures"),
            logs_dir=path_value("logs_dir", "logs"),
        )

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["captures_dir"] = str(self.captures_dir)
        result["logs_dir"] = str(self.logs_dir)
        return result

    def ensure_runtime_dirs(self) -> None:
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


def load_config(path: str | Path | None = None) -> Config:
    """Load ``config.json`` if present, otherwise return safe defaults."""

    config_path = Path(path) if path else PROJECT_ROOT / "config.json"
    if not config_path.exists():
        return Config()
    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"Configuration must be a JSON object: {config_path}")
    return Config.from_mapping(raw, PROJECT_ROOT)


def assert_write_enabled(config: Config) -> None:
    """Central future-proof guard for any operation that could write BLE data."""

    if not config.allow_write:
        raise PermissionError("BLE writes are disabled")
