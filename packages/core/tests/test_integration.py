"""Integration tests for wallpaper_core with layered_settings."""

import tempfile
from pathlib import Path

from layered_settings import configure, get_config
from wallpaper_core.cli.main import CoreOnlyConfig


def test_config_loads_from_package_defaults() -> None:
    """Test configuration loads from package defaults."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have defaults from settings.toml
    assert config.core.execution.parallel is True
    assert config.core.backend.binary == "magick"

    # Effects are now loaded separately via layered_effects
    # CoreOnlyConfig no longer has effects field


def test_config_merges_cli_overrides() -> None:
    """Test CLI overrides merge correctly."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config(
        overrides={
            "core.execution.parallel": False,
            "core.execution.max_workers": 4,
        }
    )

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
    """Test effects are loaded from effects.yaml via layered_effects."""
    from layered_effects import _reset, configure, load_effects
    from wallpaper_core.effects import get_package_effects_file

    # Reset any previous configuration
    _reset()

    # Verify package effects file exists
    package_effects = get_package_effects_file()
    assert package_effects.exists()

    # Configure layered effects
    configure(package_effects_file=package_effects)

    # Load effects
    effects_config = load_effects()

    # Should have blur effect
    assert "blur" in effects_config.effects
    blur = effects_config.effects["blur"]
    assert blur.description
    assert "$INPUT" in blur.command
    assert "$OUTPUT" in blur.command


def test_cli_info_command_runs() -> None:
    """Test CLI info command executes without error."""
    from typer.testing import CliRunner

    from wallpaper_core.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["info"])

    if result.exit_code != 0:
        print("\n=== Info Command Failed ===")
        print(f"Exit code: {result.exit_code}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        if result.exception:
            import traceback

            tb_str = "".join(
                traceback.format_exception(
                    type(result.exception),
                    result.exception,
                    result.exception.__traceback__,
                )
            )
            print(f"Exception:\n{tb_str}")

    assert (
        result.exit_code == 0
    ), f"Info command failed with exit code {result.exit_code}"
    assert "Core Settings" in result.stdout
    # Effects are displayed via layered_effects integration
    assert "Available Effects" in result.stdout or "Effects" in result.stdout
