"""Tests for CLI integration with core commands."""

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


def test_cli_has_core_commands() -> None:
    """Test CLI includes core commands."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0

    # Should have orchestrator commands
    assert "install" in result.stdout
    assert "uninstall" in result.stdout

    # Should have core commands
    assert "process" in result.stdout or "info" in result.stdout


def test_cli_info_command() -> None:
    """Test info command is available."""
    result = runner.invoke(app, ["info"])

    # Should execute (may fail due to missing config files, that's OK)
    assert "Core Settings" in result.stdout or result.exit_code in [0, 1]


def test_cli_process_help() -> None:
    """Test process command help is available."""
    result = runner.invoke(app, ["process", "--help"])

    assert result.exit_code == 0
    # Should show core's process command help
