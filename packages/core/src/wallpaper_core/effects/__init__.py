"""Effects configuration schema and models."""

from pathlib import Path

from wallpaper_core.effects.schema import (
    ChainStep,
    CompositeEffect,
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    Preset,
)


def get_package_effects_file() -> Path:
    """Get the path to the package's default effects.yaml file.

    Returns:
        Path to effects.yaml in the wallpaper_core.effects package.
    """
    from importlib import resources

    return Path(resources.files("wallpaper_core.effects") / "effects.yaml")


__all__ = [
    "ChainStep",
    "CompositeEffect",
    "Effect",
    "EffectsConfig",
    "get_package_effects_file",
    "ParameterDefinition",
    "ParameterType",
    "Preset",
]
