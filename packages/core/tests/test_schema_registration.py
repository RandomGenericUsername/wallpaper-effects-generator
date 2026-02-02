"""Tests for schema registration with layered_settings."""

from pathlib import Path

from layered_settings import SchemaRegistry
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig


def test_core_settings_registered() -> None:
    """Test CoreSettings is registered with 'core' namespace."""
    entry = SchemaRegistry.get("core")
    assert entry.namespace == "core"
    assert entry.model == CoreSettings
    assert entry.defaults_file.name == "settings.toml"
    assert entry.defaults_file.exists()


def test_effects_config_registered() -> None:
    """Test EffectsConfig is registered with 'effects' namespace."""
    entry = SchemaRegistry.get("effects")
    assert entry.namespace == "effects"
    assert entry.model == EffectsConfig
    assert entry.defaults_file.name == "effects.yaml"
    assert entry.defaults_file.exists()


def test_defaults_files_exist() -> None:
    """Test both defaults files exist and are readable."""
    core_entry = SchemaRegistry.get("core")
    effects_entry = SchemaRegistry.get("effects")

    assert core_entry.defaults_file.is_file()
    assert effects_entry.defaults_file.is_file()

    # Verify they're not empty
    assert core_entry.defaults_file.stat().st_size > 0
    assert effects_entry.defaults_file.stat().st_size > 0
