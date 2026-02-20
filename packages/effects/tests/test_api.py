"""Tests for public API."""

from pathlib import Path

import pytest


def test_configure_stores_settings(tmp_path: Path):
    """configure() should store configuration."""
    from layered_effects import configure

    package_file = tmp_path / "effects.yaml"
    package_file.write_text("version: '1.0'\neffects: {}")

    # Should not raise
    configure(
        package_effects_file=package_file,
        project_root=tmp_path,
    )


def test_load_effects_without_configure_raises():
    """load_effects() should raise if configure() not called."""
    from layered_effects import _reset, load_effects

    # Reset state
    _reset()

    with pytest.raises(RuntimeError, match="configure.*must be called"):
        load_effects()


def test_load_effects_returns_effects_config(tmp_path: Path):
    """load_effects() should return validated EffectsConfig."""
    from layered_effects import configure, load_effects

    package_file = tmp_path / "effects.yaml"
    package_file.write_text("""
version: "1.0"
parameter_types:
  test_type:
    type: string
    default: "test"
effects:
  test_effect:
    description: "Test"
    command: 'echo "test"'
composites: {}
presets: {}
""")

    configure(package_effects_file=package_file)
    config = load_effects()

    # Should be EffectsConfig instance
    assert hasattr(config, "effects")
    assert hasattr(config, "version")
    assert "test_effect" in config.effects


def test_load_effects_caches_result(tmp_path: Path):
    """load_effects() should cache and return same instance."""
    from layered_effects import configure, load_effects

    package_file = tmp_path / "effects.yaml"
    package_file.write_text("""
version: "1.0"
effects:
  test:
    description: "Test"
    command: "test"
""")

    configure(package_effects_file=package_file)

    config1 = load_effects()
    config2 = load_effects()

    assert config1 is config2


def test_load_effects_raises_on_validation_error(tmp_path: Path):
    """load_effects() should raise on invalid effects YAML."""
    from layered_effects import configure, load_effects
    from layered_effects.errors import EffectsValidationError

    package_file = tmp_path / "effects.yaml"
    # Missing required fields
    package_file.write_text("version: '1.0'\neffects:\n  bad: {}")

    configure(package_effects_file=package_file)

    with pytest.raises(EffectsValidationError):
        load_effects()
