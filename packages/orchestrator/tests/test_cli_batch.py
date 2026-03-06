"""Tests for containerized batch commands in wallpaper-process CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


# ── batch effects ──────────────────────────────────────────────────────────


def test_batch_effects_with_output_dir(tmp_path: Path) -> None:
    """batch effects -o calls run_batch with correct args."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(output_dir)],
        )

        assert result.exit_code == 0
        mock_manager.run_batch.assert_called_once()
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "effects"
        assert kwargs["input_path"] == input_file
        assert kwargs["output_dir"] == output_dir
        assert kwargs["flat"] is False


def test_batch_effects_without_output_dir(tmp_path: Path) -> None:
    """batch effects without -o resolves default from config."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
    ):
        mock_settings = MagicMock()
        mock_settings.core.output.default_dir = tmp_path / "default"
        mock_config.return_value = mock_settings

        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(app, ["batch", "effects", str(input_file)])

        assert result.exit_code == 0
        mock_manager.run_batch.assert_called_once()


def test_batch_effects_flat_flag(tmp_path: Path) -> None:
    """--flat forwarded to run_batch."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--flat"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["flat"] is True


def test_batch_effects_sequential_flag(tmp_path: Path) -> None:
    """--sequential forwarded as parallel=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--sequential"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["parallel"] is False


def test_batch_effects_no_strict_flag(tmp_path: Path) -> None:
    """--no-strict forwarded as strict=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--no-strict"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["strict"] is False


def test_batch_effects_image_not_available(tmp_path: Path) -> None:
    """Missing container image exits 1 with install hint."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
        assert "wallpaper-process install" in result.output
        mock_manager.run_batch.assert_not_called()


def test_batch_effects_container_failure(tmp_path: Path) -> None:
    """Non-zero returncode from container exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(
            returncode=1, stdout="", stderr="magick: error"
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_batch_effects_runtime_error(tmp_path: Path) -> None:
    """RuntimeError from run_batch exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.side_effect = RuntimeError("container exploded")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch composites ───────────────────────────────────────────────────────


def test_batch_composites_with_output_dir(tmp_path: Path) -> None:
    """batch composites -o calls run_batch with batch_type=composites."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "composites"


def test_batch_composites_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_batch_composites_container_failure(tmp_path: Path) -> None:
    """Non-zero returncode exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=1, stdout="", stderr="err")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch presets ──────────────────────────────────────────────────────────


def test_batch_presets_with_output_dir(tmp_path: Path) -> None:
    """batch presets -o calls run_batch with batch_type=presets."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "presets", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "presets"


def test_batch_presets_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "presets", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch all ──────────────────────────────────────────────────────────────


def test_batch_all_with_output_dir(tmp_path: Path) -> None:
    """batch all -o calls run_batch with batch_type=all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "all"


def test_batch_all_flat_flag(tmp_path: Path) -> None:
    """--flat forwarded to run_batch for all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path), "--flat"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["flat"] is True


def test_batch_all_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1 for all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
