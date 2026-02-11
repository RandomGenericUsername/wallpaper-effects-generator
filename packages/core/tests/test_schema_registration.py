"""Tests for schema registration with layered_settings."""

from layered_settings import SchemaRegistry

from wallpaper_core.config.schema import CoreSettings


def test_core_settings_registered() -> None:
    """Test CoreSettings is registered with 'core' namespace."""
    entry = SchemaRegistry.get("core")
    assert entry.namespace == "core"
    assert entry.model == CoreSettings
    assert entry.defaults_file.name == "settings.toml"
    assert entry.defaults_file.exists()


def test_effects_config_registered() -> None:
    """Test EffectsConfig is NO LONGER registered (Phase 2 change)."""
    # In Phase 2, effects are handled by layered_effects package
    # EffectsConfig is no longer registered in SchemaRegistry
    entry = SchemaRegistry.get("effects")
    assert entry is None  # Should not be registered


def test_defaults_files_exist() -> None:
    """Test defaults file exists and is readable."""
    core_entry = SchemaRegistry.get("core")

    assert core_entry.defaults_file.is_file()

    # Verify it's not empty
    assert core_entry.defaults_file.stat().st_size > 0

    # Effects defaults are now managed by layered_effects package
    # and are NOT in SchemaRegistry
