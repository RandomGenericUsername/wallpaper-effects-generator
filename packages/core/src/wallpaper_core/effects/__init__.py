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
# effects.yaml is in the same directory as this file
_effects_dir = Path(__file__).parent
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_effects_dir / "effects.yaml",
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
