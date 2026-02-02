"""Configuration module for wallpaper_core."""

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)

__all__ = [
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
]
