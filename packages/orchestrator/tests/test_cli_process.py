"""Tests for orchestrator process commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


def test_process_effect_with_output_dir(tmp_path: Path) -> None:
    """Test process effect with -o flag (hierarchical)."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--effect",
                "blur",
            ],
        )

        assert result.exit_code == 0
        # Verify the call was made with a resolved path
        mock_manager.run_process.assert_called_once()
        call_args = mock_manager.run_process.call_args
        assert call_args[1]["command_type"] == "effect"
        assert call_args[1]["command_name"] == "blur"
        assert call_args[1]["input_path"] == input_file
        # Output path should be hierarchical: output_dir/input_stem/effects/blur.jpg
        output_path = call_args[1]["output_path"]
        assert output_path.parent.name == "effects"
        assert output_path.parent.parent.name == "input"
        assert output_path.name == "blur.jpg"


def test_process_effect_without_output_dir(tmp_path: Path) -> None:
    """Test process effect without -o flag (uses default from settings)."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
    ):
        # Mock config with default output dir
        mock_settings = MagicMock()
        mock_settings.core.output.default_dir = tmp_path / "default_output"
        mock_config.return_value = mock_settings

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
                "--effect",
                "blur",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once()


def test_process_effect_with_flat_flag(tmp_path: Path) -> None:
    """Test process effect with --flat flag."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--effect",
                "blur",
                "--flat",
            ],
        )

        assert result.exit_code == 0
        # Verify the call was made with a flat path
        call_args = mock_manager.run_process.call_args
        output_path = call_args[1]["output_path"]
        # Flat structure: output_dir/input_stem/blur.jpg
        assert output_path.parent.name == "input"
        assert output_path.parent.parent == output_dir
        assert output_path.name == "blur.jpg"


def test_process_effect_dry_run(tmp_path: Path) -> None:
    """Test process effect with --dry-run."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load,
    ):
        mock_manager = MagicMock()
        mock_manager.get_image_name.return_value = "test-image:latest"
        mock_manager.engine = "docker"
        mock_mgr.return_value = mock_manager

        # Mock effects config
        mock_effect = MagicMock()
        mock_effect.command = 'magick "$INPUT" -blur 0x8 "$OUTPUT"'
        mock_effects_config = MagicMock()
        mock_effects_config.effects.get.return_value = mock_effect
        mock_load.return_value = mock_effects_config

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                "-o",
                str(output_dir),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        # Should not call run_process in dry-run mode
        mock_manager.run_process.assert_not_called()
        # Should display dry-run output
        assert "blur" in result.output.lower()


def test_process_composite_with_output_dir(tmp_path: Path) -> None:
    """Test process composite with -o flag (hierarchical)."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--composite",
                "dark",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_manager.run_process.call_args
        assert call_args[1]["command_type"] == "composite"
        assert call_args[1]["command_name"] == "dark"
        output_path = call_args[1]["output_path"]
        assert output_path.parent.name == "composites"
        assert output_path.parent.parent.name == "input"
        assert output_path.name == "dark.jpg"


def test_process_composite_without_output_dir(tmp_path: Path) -> None:
    """Test process composite without -o flag (uses default)."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
    ):
        mock_settings = MagicMock()
        mock_settings.core.output.default_dir = tmp_path / "default_output"
        mock_config.return_value = mock_settings

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
                "--composite",
                "dark",
            ],
        )

        assert result.exit_code == 0


def test_process_composite_with_flat_flag(tmp_path: Path) -> None:
    """Test process composite with --flat flag."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--composite",
                "dark",
                "--flat",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_manager.run_process.call_args
        output_path = call_args[1]["output_path"]
        assert output_path.parent.name == "input"
        assert output_path.parent.parent == output_dir
        assert output_path.name == "dark.jpg"


def test_process_composite_dry_run(tmp_path: Path) -> None:
    """Test process composite with --dry-run."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load,
    ):
        mock_manager = MagicMock()
        mock_manager.get_image_name.return_value = "test-image:latest"
        mock_manager.engine = "docker"
        mock_mgr.return_value = mock_manager

        mock_composite = MagicMock()
        mock_composite.chain = []
        mock_effects_config = MagicMock()
        mock_effects_config.composites.get.return_value = mock_composite
        mock_load.return_value = mock_effects_config

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                "-o",
                str(output_dir),
                "--composite",
                "dark",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_not_called()


def test_process_preset_with_output_dir(tmp_path: Path) -> None:
    """Test process preset with -o flag (hierarchical)."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--preset",
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_manager.run_process.call_args
        assert call_args[1]["command_type"] == "preset"
        assert call_args[1]["command_name"] == "dark_vibrant"
        output_path = call_args[1]["output_path"]
        assert output_path.parent.name == "presets"
        assert output_path.parent.parent.name == "input"
        assert output_path.name == "dark_vibrant.jpg"


def test_process_preset_without_output_dir(tmp_path: Path) -> None:
    """Test process preset without -o flag (uses default)."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
    ):
        mock_settings = MagicMock()
        mock_settings.core.output.default_dir = tmp_path / "default_output"
        mock_config.return_value = mock_settings

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
                "--preset",
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 0


def test_process_preset_with_flat_flag(tmp_path: Path) -> None:
    """Test process preset with --flat flag."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--preset",
                "dark_vibrant",
                "--flat",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_manager.run_process.call_args
        output_path = call_args[1]["output_path"]
        assert output_path.parent.name == "input"
        assert output_path.parent.parent == output_dir
        assert output_path.name == "dark_vibrant.jpg"


def test_process_preset_dry_run(tmp_path: Path) -> None:
    """Test process preset with --dry-run."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load,
    ):
        mock_manager = MagicMock()
        mock_manager.get_image_name.return_value = "test-image:latest"
        mock_manager.engine = "docker"
        mock_mgr.return_value = mock_manager

        mock_preset = MagicMock()
        mock_preset.effect = "blur"
        mock_preset.composite = None
        mock_preset.params = {}
        mock_effect = MagicMock()
        mock_effect.command = 'magick "$INPUT" -blur 0x8 "$OUTPUT"'
        mock_effects_config = MagicMock()
        mock_effects_config.presets.get.return_value = mock_preset
        mock_effects_config.effects.get.return_value = mock_effect
        mock_load.return_value = mock_effects_config

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                "-o",
                str(output_dir),
                "--preset",
                "dark_vibrant",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_not_called()


def test_process_effect_checks_image_available(tmp_path: Path) -> None:
    """Test process effect checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--effect",
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
        assert "wallpaper-process install" in result.output


def test_process_effect_handles_container_failure(tmp_path: Path) -> None:
    """Test process effect handles container execution failure."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--effect",
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_composite_missing_image(tmp_path: Path) -> None:
    """Test process composite checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--composite",
                "dark",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_process_composite_execution_failure(tmp_path: Path) -> None:
    """Test process composite handles execution failure."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--composite",
                "dark",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_preset_missing_image(tmp_path: Path) -> None:
    """Test process preset checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--preset",
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_process_preset_execution_failure(tmp_path: Path) -> None:
    """Test process preset handles execution failure."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--preset",
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_effect_runtime_error(tmp_path: Path) -> None:
    """Test process effect handles RuntimeError."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
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
                "-o",
                str(output_dir),
                "--effect",
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()
