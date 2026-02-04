"""Tests for uninstall command."""

from unittest.mock import MagicMock, patch

import pytest
from click.exceptions import Exit

from wallpaper_orchestrator.cli.commands.uninstall import uninstall


def test_uninstall_with_confirmation() -> None:
    """Test uninstall with user confirmation."""
    with patch("wallpaper_orchestrator.cli.commands.uninstall.subprocess.run") as mock_run, \
         patch("wallpaper_orchestrator.cli.commands.uninstall.typer.confirm") as mock_confirm:

        mock_run.return_value = MagicMock(returncode=0)
        mock_confirm.return_value = True

        with pytest.raises(Exit) as exc_info:
            uninstall(yes=False, engine=None)

        assert exc_info.value.exit_code == 0
        mock_confirm.assert_called_once()
        mock_run.assert_called_once()


def test_uninstall_cancelled() -> None:
    """Test uninstall when user cancels."""
    with patch("wallpaper_orchestrator.cli.commands.uninstall.typer.confirm") as mock_confirm:
        mock_confirm.return_value = False

        with pytest.raises(Exit) as exc_info:
            uninstall(yes=False, engine=None)

        assert exc_info.value.exit_code == 0
        mock_confirm.assert_called_once()


def test_uninstall_skip_confirmation() -> None:
    """Test uninstall with --yes flag."""
    with patch("wallpaper_orchestrator.cli.commands.uninstall.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(Exit) as exc_info:
            uninstall(yes=True, engine=None)

        assert exc_info.value.exit_code == 0
        mock_run.assert_called_once()


def test_uninstall_image_not_found() -> None:
    """Test uninstall when image doesn't exist."""
    with patch("wallpaper_orchestrator.cli.commands.uninstall.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="no such image"
        )

        with pytest.raises(Exit) as exc_info:
            uninstall(yes=True, engine=None)

        # Should still exit successfully (image already gone)
        assert exc_info.value.exit_code == 0


def test_uninstall_with_podman() -> None:
    """Test uninstall with podman engine."""
    with patch("wallpaper_orchestrator.cli.commands.uninstall.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(Exit) as exc_info:
            uninstall(yes=True, engine="podman")

        assert exc_info.value.exit_code == 0

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"
