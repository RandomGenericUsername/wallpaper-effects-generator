"""Tests for settings.toml package defaults."""

import tomllib
from pathlib import Path

from wallpaper_core.config.schema import CoreSettings


def test_settings_toml_exists() -> None:
    """Test settings.toml file exists in package."""
    config_dir = (
        Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    )
    settings_file = config_dir / "settings.toml"
    assert settings_file.exists(), "settings.toml not found in package"


def test_settings_toml_is_valid() -> None:
    """Test settings.toml contains valid TOML."""
    config_dir = (
        Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    )
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomllib.load(f)

    assert isinstance(data, dict)
    assert len(data) > 0


def test_settings_toml_validates_against_schema() -> None:
    """Test settings.toml can be loaded into CoreSettings."""
    config_dir = (
        Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    )
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomllib.load(f)

    settings = CoreSettings(**data)
    assert settings.execution.parallel is True
    assert settings.execution.strict is True
    assert settings.execution.max_workers == 0
    assert settings.output.verbosity == 1  # NORMAL
    assert settings.backend.binary == "magick"


def test_settings_toml_uses_flat_format() -> None:
    """Test settings.toml uses flat format (not namespaced)."""
    config_dir = (
        Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    )
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomllib.load(f)

    # Should have top-level sections, not nested under "core"
    assert "execution" in data
    assert "output" in data
    assert "backend" in data
    assert "core" not in data  # Should NOT be namespaced
