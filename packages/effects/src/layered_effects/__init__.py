"""Layered effects configuration system.

Public API:
    configure() - Configure the effects system
    load_effects() - Load and merge effects from all layers
"""

from pathlib import Path

from layered_effects.errors import (
    EffectsError,
    EffectsLoadError,
    EffectsValidationError,
)
from layered_effects.loader import EffectsLoader

from wallpaper_core.effects.schema import EffectsConfig

__version__ = "0.1.0"

# Module-level state
_package_effects_file: Path | None = None
_project_root: Path | None = None
_user_effects_file: Path | None = None
_config_cache = None


def configure(
    package_effects_file: Path,
    project_root: Path | None = None,
    user_effects_file: Path | None = None,
) -> None:
    """Configure the layered effects system.

    This function must be called before load_effects(). It stores the paths
    to effects files and clears any cached configuration.

    Args:
        package_effects_file: Path to package default effects.yaml
        project_root: Optional project root directory
        user_effects_file: Optional user effects file path

    Example:
        >>> from pathlib import Path
        >>> configure(
        ...     package_effects_file=Path("effects/effects.yaml"),
        ...     project_root=Path.cwd(),
        ... )
    """
    global _package_effects_file, _project_root, _user_effects_file, _config_cache

    _package_effects_file = package_effects_file
    _project_root = project_root
    _user_effects_file = user_effects_file
    _config_cache = None  # Clear cache on reconfiguration


def load_effects() -> EffectsConfig:
    """Load and merge effects from all configured layers.

    This function discovers effects.yaml files, deep merges them, and
    validates the result with the EffectsConfig Pydantic model.

    The result is cached after the first call. Subsequent calls return
    the cached instance.

    Returns:
        Validated EffectsConfig instance

    Raises:
        RuntimeError: If configure() has not been called
        EffectsLoadError: If loading fails
        EffectsValidationError: If validation fails

    Example:
        >>> effects_config = load_effects()
        >>> blur_effect = effects_config.effects["blur"]
    """
    global _config_cache

    # Check if configure() was called
    if _package_effects_file is None:
        raise RuntimeError(
            "configure() must be called before load_effects(). "
            "Call configure(package_effects_file=...) first."
        )

    # Return cached config if available
    if _config_cache is not None:
        return _config_cache

    # Load and merge all layers
    loader = EffectsLoader(
        package_effects_file=_package_effects_file,
        project_root=_project_root,
        user_effects_file=_user_effects_file,
    )

    try:
        merged_data = loader.load_and_merge()
    except EffectsLoadError:
        raise

    # Validate with EffectsConfig schema
    try:
        _config_cache = EffectsConfig(**merged_data)
    except Exception as e:
        raise EffectsValidationError(
            message=str(e),
            layer="merged",
        ) from e

    return _config_cache


def _reset() -> None:
    """Reset module state. For testing only."""
    global _package_effects_file, _project_root, _user_effects_file, _config_cache
    _package_effects_file = None
    _project_root = None
    _user_effects_file = None
    _config_cache = None


__all__ = [
    "__version__",
    "configure",
    "load_effects",
    # Errors
    "EffectsError",
    "EffectsLoadError",
    "EffectsValidationError",
]
