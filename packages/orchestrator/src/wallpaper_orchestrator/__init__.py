"""Wallpaper effects orchestrator with container management."""

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # Config
    "OrchestratorSettings",
    "ContainerSettings",
    "UnifiedConfig",
    # Container
    "ContainerManager",
]
