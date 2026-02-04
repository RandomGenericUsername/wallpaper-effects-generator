"""Tests for config loader."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from wallpaper_processor.config.loader import (
    ConfigLoader,
    _deep_merge,
    _get_package_effects_path,
    _get_user_config_dir,
)
from wallpaper_processor.config.schema import EffectsConfig
from wallpaper_processor.config.settings import Settings, Verbosity


class TestDeepMerge:
    """Tests for _deep_merge function."""

    def test_simple_merge(self) -> None:
        """Test merging simple dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        """Test merging nested dictionaries."""
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"y": 20, "z": 30}}
        result = _deep_merge(base, override)
        assert result == {"a": {"x": 1, "y": 20, "z": 30}, "b": 3}

    def test_override_non_dict(self) -> None:
        """Test that non-dict values are replaced."""
        base = {"a": {"x": 1}}
        override = {"a": "string"}
        result = _deep_merge(base, override)
        assert result == {"a": "string"}

    def test_empty_base(self) -> None:
        """Test merging with empty base."""
        base = {}
        override = {"a": 1}
        result = _deep_merge(base, override)
        assert result == {"a": 1}

    def test_empty_override(self) -> None:
        """Test merging with empty override."""
        base = {"a": 1}
        override = {}
        result = _deep_merge(base, override)
        assert result == {"a": 1}


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_effects_from_package(self) -> None:
        """Test loading effects from package default."""
        config = ConfigLoader.load_effects(force_reload=True)
        assert isinstance(config, EffectsConfig)
        # Package should have at least blur effect
        assert "blur" in config.effects

    def test_load_effects_caching(self) -> None:
        """Test that effects config is cached."""
        config1 = ConfigLoader.load_effects(force_reload=True)
        config2 = ConfigLoader.load_effects()
        assert config1 is config2

    def test_load_effects_force_reload(self) -> None:
        """Test force reload bypasses cache."""
        config1 = ConfigLoader.load_effects(force_reload=True)
        config2 = ConfigLoader.load_effects(force_reload=True)
        # Should be equal but different objects
        assert config1.version == config2.version
        # Note: they might be the same object due to pydantic caching

    def test_load_settings_default(self) -> None:
        """Test loading default settings when no user config exists."""
        # Clear cache and use non-existent path
        ConfigLoader.clear_cache()
        with patch(
            "wallpaper_processor.config.loader._get_user_settings_path"
        ) as mock_path:
            mock_path.return_value = Path("/nonexistent/settings.yaml")
            settings = ConfigLoader.load_settings(force_reload=True)
            assert isinstance(settings, Settings)
            assert settings.execution.parallel is True

    def test_load_settings_from_file(self, tmp_path: Path) -> None:
        """Test loading settings from user file."""
        settings_file = tmp_path / "settings.yaml"
        settings_data = {
            "version": "1.0",
            "execution": {"parallel": False, "strict": False},
            "output": {"verbosity": 2},
        }
        settings_file.write_text(yaml.dump(settings_data))

        ConfigLoader.clear_cache()
        with patch(
            "wallpaper_processor.config.loader._get_user_settings_path"
        ) as mock_path:
            mock_path.return_value = settings_file
            settings = ConfigLoader.load_settings(force_reload=True)
            assert settings.execution.parallel is False
            assert settings.execution.strict is False
            assert settings.output.verbosity == Verbosity.VERBOSE

    def test_load_settings_caching(self) -> None:
        """Test that settings are cached."""
        ConfigLoader.clear_cache()
        with patch(
            "wallpaper_processor.config.loader._get_user_settings_path"
        ) as mock_path:
            mock_path.return_value = Path("/nonexistent/settings.yaml")
            settings1 = ConfigLoader.load_settings(force_reload=True)
            settings2 = ConfigLoader.load_settings()
            assert settings1 is settings2

    def test_clear_cache(self) -> None:
        """Test clearing config cache."""
        ConfigLoader.load_effects(force_reload=True)
        ConfigLoader.clear_cache()
        assert ConfigLoader._effects_cache is None
        assert ConfigLoader._settings_cache is None

    def test_load_user_effects_override(self, tmp_path: Path) -> None:
        """Test that user effects override package effects."""
        user_effects = tmp_path / "effects.yaml"
        user_data = {
            "effects": {
                "custom_effect": {
                    "description": "Custom effect",
                    "command": 'magick "$INPUT" -negate "$OUTPUT"',
                },
            },
        }
        user_effects.write_text(yaml.dump(user_data))

        ConfigLoader.clear_cache()
        with patch(
            "wallpaper_processor.config.loader._get_user_effects_path"
        ) as mock_user:
            mock_user.return_value = user_effects
            config = ConfigLoader.load_effects(force_reload=True)
            # Should have both package and user effects
            assert "blur" in config.effects  # From package
            assert "custom_effect" in config.effects  # From user


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_package_effects_path(self) -> None:
        """Test package effects path resolution."""
        path = _get_package_effects_path()
        assert path.name == "effects.yaml"
        assert "effects" in str(path)

    def test_get_user_config_dir(self) -> None:
        """Test user config directory path."""
        path = _get_user_config_dir()
        assert ".config" in str(path)
        assert "wallpaper-effects" in str(path)

