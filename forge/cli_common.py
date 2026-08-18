"""Shared CLI helpers kept outside ``scripts`` to avoid stdlib name collisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

from forge.config import Config, load_config
from forge.logging_config import setup_logging


console = Console()


def runtime(config_path: str | None, log_level: str = "INFO") -> Config:
    config = load_config(config_path)
    config.ensure_runtime_dirs()
    setup_logging(config.logs_dir, log_level)
    return config


def choose_output(config: Config, requested: str | None, default_name: str) -> Path:
    return Path(requested) if requested else config.captures_dir / default_name


def device_arguments(parser: Any) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--device", "--name", dest="device_name", help="Nombre o fragmento del nombre BLE")
    group.add_argument("--address", help="Address/identifier devuelto por Bleak")
    parser.add_argument("--config", help="Ruta a config.json; por defecto se usa el archivo del repositorio")
    parser.add_argument("--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR"))
