"""Test CLI properly loads and uses layered effects."""
from pathlib import Path
from typer.testing import CliRunner
from wallpaper_core.cli.main import app

runner = CliRunner()


def test_cli_shows_package_effects():
    """CLI should show package default effects."""
    result = runner.invoke(app, ["show", "effects"])
    assert result.exit_code == 0
    assert "blur" in result.stdout
    assert "brightness" in result.stdout


def test_cli_shows_composites():
    """CLI should show composites from effects config."""
    result = runner.invoke(app, ["show", "composites"])
    assert result.exit_code == 0
    assert "blackwhite-blur" in result.stdout


def test_cli_shows_presets():
    """CLI should show presets from effects config."""
    result = runner.invoke(app, ["show", "presets"])
    assert result.exit_code == 0
    assert "dark_blur" in result.stdout


def test_cli_error_on_invalid_user_effects(tmp_path, monkeypatch):
    """CLI should show helpful error for invalid user config."""
    from layered_effects import configure as configure_effects, _reset
    from wallpaper_core.effects import get_package_effects_file

    # Create invalid user effects file
    invalid_effects = tmp_path / "effects.yaml"
    invalid_effects.write_text("invalid: yaml: content:")

    # Reset and reconfigure layered-effects to use test file
    _reset()
    configure_effects(
        package_effects_file=get_package_effects_file(),
        project_root=None,
        user_effects_file=invalid_effects
    )

    result = runner.invoke(app, ["show", "effects"])
    assert result.exit_code == 1
    assert "Failed to load" in result.output
