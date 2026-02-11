"""Tests for orchestrator process commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


def test_process_effect_calls_container_manager(tmp_path: Path) -> None:
    """Test process effect command calls ContainerManager.run_process."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )


def test_process_effect_checks_image_available(tmp_path: Path) -> None:
    """Test process effect checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
        assert "wallpaper-process install" in result.output


def test_process_effect_handles_container_failure(
    tmp_path: Path,
) -> None:
    """Test process effect handles container execution failure."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=1, stdout="", stderr="magick: invalid parameter"
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_composite_calls_container_manager(
    tmp_path: Path,
) -> None:
    """Test process composite command calls ContainerManager."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "dark",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="composite",
            command_name="dark",
            input_path=input_file,
            output_path=output_file,
        )


def test_process_preset_calls_container_manager(tmp_path: Path) -> None:
    """Test process preset command calls ContainerManager."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="preset",
            command_name="dark_vibrant",
            input_path=input_file,
            output_path=output_file,
        )


def test_process_composite_missing_image(tmp_path: Path) -> None:
    """Test process composite checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "blur-brightness80",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_process_composite_execution_failure(tmp_path: Path) -> None:
    """Test process composite handles execution failure."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=1, stdout="", stderr="chain failed"
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "blur-brightness80",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_preset_missing_image(tmp_path: Path) -> None:
    """Test process preset checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_process_preset_execution_failure(tmp_path: Path) -> None:
    """Test process preset handles execution failure."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=1, stdout="", stderr="preset failed"
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_effect_runtime_error(tmp_path: Path) -> None:
    """Test process effect handles RuntimeError."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = RuntimeError("Container error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()


def test_process_effect_file_not_found_error(tmp_path: Path) -> None:
    """Test process effect handles FileNotFoundError."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = FileNotFoundError("File not found")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1


def test_process_effect_permission_error(tmp_path: Path) -> None:
    """Test process effect handles PermissionError."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = PermissionError("Permission denied")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1


def test_process_effect_generic_exception(tmp_path: Path) -> None:
    """Test process effect handles generic Exception."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = Exception("Unexpected error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Unexpected error" in result.output or "error" in result.output.lower()


def test_process_composite_runtime_error(tmp_path: Path) -> None:
    """Test process composite handles RuntimeError."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = RuntimeError("Container error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "blur-brightness80",
            ],
        )

        assert result.exit_code == 1


def test_process_preset_runtime_error(tmp_path: Path) -> None:
    """Test process preset handles RuntimeError."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = RuntimeError("Container error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1


def test_process_composite_generic_exception(tmp_path):
    """Test process composite handles generic exception."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = Exception("Unknown error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "blur-brightness80",
            ],
        )

        assert result.exit_code == 1


def test_process_preset_generic_exception(tmp_path):
    """Test process preset handles generic exception."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.side_effect = Exception("Unknown error")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1
