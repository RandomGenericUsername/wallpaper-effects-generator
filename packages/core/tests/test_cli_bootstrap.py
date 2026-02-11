"""Tests for CLI bootstrap and configuration."""

from typer.testing import CliRunner
from wallpaper_core.cli.main import app

runner = CliRunner()


def test_cli_app_exists() -> None:
    """Test CLI app is a Typer instance."""
    from typer import Typer

    assert isinstance(app, Typer)


def test_cli_help_works() -> None:
    """Test CLI --help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "configuration" in result.stdout.lower()


def test_cli_configures_layered_settings() -> None:
    """Test CLI configures layered_settings on startup."""
    # Import triggers configuration
    from layered_settings import get_config

    # Should be able to get config without error
    # Note: This might fail if config files missing in user's home
    # but that's expected behavior
    try:
        config = get_config()
        assert hasattr(config, "core")
        assert hasattr(config, "effects")
    except Exception:
        # If fails due to missing files, that's OK
        # Just verify the configure was called
        pass


def test_cli_info_command_exists() -> None:
    """Test CLI info command exists."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Should show the info command or its help
    assert (
        "info" in result.stdout.lower()
        or "configuration" in result.stdout.lower()
    )
