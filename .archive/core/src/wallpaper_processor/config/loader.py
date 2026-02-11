"""Configuration loader for effects and settings."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from wallpaper_processor.config.schema import EffectsConfig
    from wallpaper_processor.config.settings import Settings


def _get_package_effects_path() -> Path:
    """Get path to bundled effects.yaml."""
    # effects/ directory is at package root level
    package_dir = Path(__file__).parent.parent.parent.parent
    return package_dir / "effects" / "effects.yaml"


def _get_user_config_dir() -> Path:
    """Get user config directory."""
    return Path.home() / ".config" / "wallpaper-effects"


def _get_user_effects_path() -> Path:
    """Get path to user effects.yaml."""
    return _get_user_config_dir() / "effects.yaml"


def _get_user_settings_path() -> Path:
    """Get path to user settings.yaml."""
    return _get_user_config_dir() / "settings.yaml"


def _get_user_effects_dir() -> Path:
    """Get path to user effects.d/ directory."""
    return _get_user_config_dir() / "effects.d"


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigLoader:
    """Loader for effects and settings configuration."""

    _effects_cache: EffectsConfig | None = None
    _settings_cache: Settings | None = None

    @classmethod
    def load_effects(cls, force_reload: bool = False) -> EffectsConfig:
        """Load effects configuration from all sources.

        Load order (later overrides earlier):
        1. Package default: {package}/effects/effects.yaml
        2. User config: ~/.config/wallpaper-effects/effects.yaml
        3. User custom: ~/.config/wallpaper-effects/effects.d/*.yaml

        Args:
            force_reload: Force reload from disk, ignoring cache

        Returns:
            Merged EffectsConfig
        """
        from wallpaper_processor.config.schema import EffectsConfig

        if cls._effects_cache is not None and not force_reload:
            return cls._effects_cache

        merged_data: dict = {}

        # 1. Load package default
        package_path = _get_package_effects_path()
        if package_path.exists():
            with open(package_path) as f:
                merged_data = yaml.safe_load(f) or {}

        # 2. Load user config
        user_path = _get_user_effects_path()
        if user_path.exists():
            with open(user_path) as f:
                user_data = yaml.safe_load(f) or {}
                merged_data = _deep_merge(merged_data, user_data)

        # 3. Load user effects.d/*.yaml files
        effects_dir = _get_user_effects_dir()
        if effects_dir.exists():
            for yaml_file in sorted(effects_dir.glob("*.yaml")):
                with open(yaml_file) as f:
                    extra_data = yaml.safe_load(f) or {}
                    merged_data = _deep_merge(merged_data, extra_data)

        cls._effects_cache = EffectsConfig(**merged_data)
        return cls._effects_cache

    @classmethod
    def load_settings(cls, force_reload: bool = False) -> Settings:
        """Load settings configuration.

        Args:
            force_reload: Force reload from disk, ignoring cache

        Returns:
            Settings instance
        """
        from wallpaper_processor.config.settings import Settings

        if cls._settings_cache is not None and not force_reload:
            return cls._settings_cache

        settings_path = _get_user_settings_path()
        if settings_path.exists():
            with open(settings_path) as f:
                data = yaml.safe_load(f) or {}
                cls._settings_cache = Settings(**data)
        else:
            cls._settings_cache = Settings.default()

        return cls._settings_cache

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached configurations."""
        cls._effects_cache = None
        cls._settings_cache = None
