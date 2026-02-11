"""Tests for install command."""

from unittest.mock import MagicMock, patch

import pytest
from click.exceptions import Exit
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.commands.install import install

runner = CliRunner()


def test_install_default_engine() -> None:
    """Test install with default docker engine."""
    with patch(
        "wallpaper_orchestrator.cli.commands.install.subprocess.run"
    ) as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        # Call install function directly
        with pytest.raises(Exit) as exc_info:
            install(engine=None, dry_run=False)

        # Should exit successfully
        assert exc_info.value.exit_code == 0

        # Should call docker build
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert "build" in call_args


def test_install_with_podman() -> None:
    """Test install with podman engine."""
    with patch(
        "wallpaper_orchestrator.cli.commands.install.subprocess.run"
    ) as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(Exit) as exc_info:
            install(engine="podman", dry_run=False)

        assert exc_info.value.exit_code == 0

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"


def test_install_build_failure() -> None:
    """Test install handles build failure."""
    with patch(
        "wallpaper_orchestrator.cli.commands.install.subprocess.run"
    ) as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="Build failed")

        with pytest.raises(Exit) as exc_info:
            install(engine=None, dry_run=False)

        # Should exit with error code
        assert exc_info.value.exit_code == 1


def test_install_invalid_engine() -> None:
    """Test install rejects invalid engine."""
    with pytest.raises(Exit) as exc_info:
        install(engine="invalid", dry_run=False)

    assert exc_info.value.exit_code == 1
