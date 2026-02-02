"""Configuration module for wallpaper_core."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)

# Register CoreSettings with layered_settings
SchemaRegistry.register(
    namespace="core",
    model=CoreSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = [
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
]
