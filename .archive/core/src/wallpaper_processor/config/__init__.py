"""Configuration module for wallpaper effects processor."""

from wallpaper_processor.config.loader import ConfigLoader
from wallpaper_processor.config.schema import (
    ChainStep,
    CompositeDefinition,
    EffectDefinition,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    PresetDefinition,
)
from wallpaper_processor.config.settings import (
    ExecutionSettings,
    OutputSettings,
    PathSettings,
    Settings,
    Verbosity,
)

__all__ = [
    # Schema
    "ParameterType",
    "ParameterDefinition",
    "EffectDefinition",
    "ChainStep",
    "CompositeDefinition",
    "PresetDefinition",
    "EffectsConfig",
    # Settings
    "Verbosity",
    "ExecutionSettings",
    "OutputSettings",
    "PathSettings",
    "Settings",
    # Loader
    "ConfigLoader",
]
