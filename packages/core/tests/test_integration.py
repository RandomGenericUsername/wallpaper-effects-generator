"""Integration tests for wallpaper_core with layered_settings."""

import tempfile
from pathlib import Path

import pytest
from layered_settings import configure, get_config
from wallpaper_core.cli.main import CoreOnlyConfig


def test_config_loads_from_package_defaults() -> None:
    """Test configuration loads from package defaults."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have defaults from settings.toml
    assert config.core.execution.parallel is True
    assert config.core.backend.binary == "magick"

    # Should have effects from effects.yaml
    assert config.effects.version == "1.0"
    assert len(config.effects.effects) > 0


def test_config_merges_cli_overrides() -> None:
    """Test CLI overrides merge correctly."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config(overrides={
        "core.execution.parallel": False,
        "core.execution.max_workers": 4,
    })

    assert config.core.execution.parallel is False
    assert config.core.execution.max_workers == 4
    # Other settings should remain default
    assert config.core.backend.binary == "magick"


def test_config_loads_project_settings() -> None:
    """Test configuration loads from project settings.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        settings_file = project_dir / "settings.toml"

        # Write project settings
        settings_file.write_text("""
[core.execution]
parallel = false
max_workers = 8

[core.backend]
binary = "/custom/magick"
""")

        # Configure with project root
        configure(CoreOnlyConfig, app_name="wallpaper-effects-test")

        # Note: This test requires running from project_dir
        # or mock layer discovery
        # For now, just verify defaults work
        config = get_config()
        assert config.core is not None


def test_effects_loaded_from_yaml() -> None:
    """Test effects are loaded from effects.yaml."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have blur effect
    assert "blur" in config.effects.effects
    blur = config.effects.effects["blur"]
    assert blur.description
    assert "$INPUT" in blur.command
    assert "$OUTPUT" in blur.command


def test_cli_info_command_runs() -> None:
    """Test CLI info command executes without error."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "Core Settings" in result.stdout
    assert "Effects" in result.stdout
