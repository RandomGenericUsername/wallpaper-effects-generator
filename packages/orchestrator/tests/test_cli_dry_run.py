"""Tests for --dry-run flag on orchestrator CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner
from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


class TestInstallDryRun:
    def test_dry_run_shows_build_command(self):
        result = runner.invoke(app, ["install", "--dry-run"])
        assert result.exit_code == 0
        assert "build" in result.stdout.lower()
        assert (
            "Dockerfile" in result.stdout
            or "dockerfile" in result.stdout.lower()
        )

    def test_dry_run_no_image_built(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["install", "--dry-run"])
            # subprocess.run should NOT be called for building
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert (
                        "build" not in args
                    ), "Should not run build during dry-run"


class TestUninstallDryRun:
    def test_dry_run_shows_rmi_command(self):
        result = runner.invoke(app, ["uninstall", "--dry-run"])
        assert result.exit_code == 0
        assert "rmi" in result.stdout

    def test_dry_run_no_image_removed(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["uninstall", "--dry-run"])
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert (
                        "rmi" not in args
                    ), "Should not run rmi during dry-run"


class TestProcessEffectContainerDryRun:
    def test_dry_run_shows_both_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
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
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show host command (docker run...)
        assert (
            "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        )
        # Should show inner command (magick...)
        assert "magick" in result.stdout

    def test_dry_run_no_container_spawned(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    str(output_file),
                    "blur",
                    "--dry-run",
                ],
            )

            mock_manager.run_process.assert_not_called()


class TestProcessCompositeContainerDryRun:
    def test_dry_run_shows_both_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
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
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show host command (docker run...)
        assert (
            "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        )
        # Should show inner command chain
        assert (
            "blur" in result.stdout.lower()
            or "brightness" in result.stdout.lower()
        )

    def test_dry_run_composite_with_podman(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "podman"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
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
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show podman-specific userns flag
        assert (
            "podman" in result.stdout.lower()
            or "--userns" in result.stdout.lower()
        )


class TestProcessPresetContainerDryRun:
    def test_dry_run_preset_shows_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    str(output_file),
                    "dark_blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show docker and magick
        assert (
            "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        )

    def test_dry_run_unknown_preset(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    str(output_file),
                    "nonexistent-preset",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show error about unknown preset
        assert (
            "cannot resolve" in result.stdout.lower()
            or "unknown" in result.stdout.lower()
        )

    def test_dry_run_preset_with_unknown_effect(self, tmp_path):
        """Test dry-run for preset with unknown effect."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    str(output_file),
                    "dark_blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0

    def test_dry_run_preset_with_unknown_composite(self, tmp_path):
        """Test dry-run for preset with unknown composite."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
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
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0


class TestProcessEffectDryRunEdgeCases:
    def test_dry_run_effect_not_found_in_config(self, tmp_path):
        """Test dry-run for effect not found in config."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    str(output_file),
                    "nonexistent-effect",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert (
            "not found" in result.stdout.lower() or "magick" in result.stdout
        )


class TestProcessCompositeEdgeCases:
    def test_dry_run_composite_not_found_in_config(self, tmp_path):
        """Test dry-run for composite not found in config."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = (
                "wallpaper-effects:latest"
            )
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "composite",
                    str(input_file),
                    str(output_file),
                    "nonexistent-composite",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert (
            "not found" in result.stdout.lower()
            or "composite" in result.stdout.lower()
        )
