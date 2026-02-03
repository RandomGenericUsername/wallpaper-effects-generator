"""Wallpaper effects processor with layered configuration."""

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)
from wallpaper_core.effects.schema import (
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
)

__version__ = "0.3.0"

__all__ = [
    "__version__",
    # Config
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
    # Effects
    "EffectsConfig",
    "Effect",
    "ParameterType",
    "ParameterDefinition",
]
