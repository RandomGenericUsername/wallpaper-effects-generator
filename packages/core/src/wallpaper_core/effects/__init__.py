"""Effects configuration schema and models."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_core.effects.schema import (
    ChainStep,
    CompositeEffect,
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    Preset,
)

# Register EffectsConfig with layered_settings
# Note: effects.yaml is outside src/, go up to package root
_package_root = Path(__file__).parent.parent.parent.parent
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_package_root / "effects" / "effects.yaml",
)

__all__ = [
    "ChainStep",
    "CompositeEffect",
    "Effect",
    "EffectsConfig",
    "ParameterDefinition",
    "ParameterType",
    "Preset",
]
