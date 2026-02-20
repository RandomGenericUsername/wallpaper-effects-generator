"""Configuration module for wallpaper_orchestrator."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)
from wallpaper_orchestrator.config.unified import UnifiedConfig

# Register OrchestratorSettings with layered_settings
SchemaRegistry.register(
    namespace="orchestrator",
    model=OrchestratorSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = [
    "OrchestratorSettings",
    "ContainerSettings",
    "UnifiedConfig",
]
