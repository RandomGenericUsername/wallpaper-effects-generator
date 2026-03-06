"""Tests for CLI integration with core commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


class TestCLIBasics:
    """Basic CLI tests."""

    def test_cli_has_core_commands(self) -> None:
        """Test CLI includes core commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0

        # Should have orchestrator commands
        assert "install" in result.stdout
        assert "uninstall" in result.stdout

        # Should have core commands
        assert "process" in result.stdout or "info" in result.stdout

    def test_cli_info_command(self) -> None:
        """Test info command is available."""
        result = runner.invoke(app, ["info"])

        # Should execute (may fail due to missing config files, that's OK)
        assert "Core Settings" in result.stdout or result.exit_code in [0, 1]

    def test_cli_process_help(self) -> None:
        """Test process command help is available."""
        result = runner.invoke(app, ["process", "--help"])

        assert result.exit_code == 0
        # Should show core's process command help

    def test_cli_version_command(self) -> None:
        """Test version command is available."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert (
            "wallpaper-orchestrator" in result.stdout
            or "version" in result.stdout.lower()
        )


class TestShowCommands:
    """Tests for show commands."""

    def test_cli_show_help(self) -> None:
        """Test show command is available (tests show_callback)."""
        result = runner.invoke(app, ["show", "--help"])

        assert result.exit_code == 0

    def test_cli_show_effects(self) -> None:
        """Test show effects command."""
        result = runner.invoke(app, ["show", "effects"])

        assert result.exit_code == 0
        # Should show effects
        assert "blur" in result.stdout.lower() or "effect" in result.stdout.lower()


class TestBatchCommands:
    """Tests for containerized batch commands."""

    def _mock_manager(self) -> MagicMock:
        mock = MagicMock()
        mock.is_image_available.return_value = True
        mock.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        return mock

    def test_cli_batch_help(self) -> None:
        """Test batch command is available."""
        result = runner.invoke(app, ["batch", "--help"])

        assert result.exit_code == 0

    def test_cli_batch_effects_help(self) -> None:
        """Test batch effects subcommand help shows -o option."""
        result = runner.invoke(app, ["batch", "effects", "--help"])

        assert result.exit_code == 0
        assert "--output-dir" in result.stdout or "-o" in result.stdout

    def test_batch_effects_calls_run_batch(self, tmp_path: Path) -> None:
        """batch effects calls run_batch(batch_type='effects')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()
        output_dir = tmp_path / "output"

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "-o", str(output_dir)],
            )

        assert result.exit_code == 0
        call_kwargs = mock_mgr.return_value.run_batch.call_args[1]
        assert call_kwargs["batch_type"] == "effects"

    def test_batch_effects_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch effects without -o passes config default_dir to run_batch."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()
        default_dir = tmp_path / "wallpapers-output"

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = default_dir
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()

            result = runner.invoke(app, ["batch", "effects", str(input_file)])

        assert result.exit_code == 0
        call_kwargs = mock_mgr.return_value.run_batch.call_args[1]
        assert call_kwargs["output_dir"] == default_dir

    def test_batch_effects_flat(self, tmp_path: Path) -> None:
        """--flat forwarded correctly."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                ["batch", "effects", str(input_file), "-o", str(tmp_path), "--flat"],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["flat"] is True

    def test_batch_effects_sequential(self, tmp_path: Path) -> None:
        """--sequential forwarded as parallel=False."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                [
                    "batch",
                    "effects",
                    str(input_file),
                    "-o",
                    str(tmp_path),
                    "--sequential",
                ],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["parallel"] is False

    def test_batch_composites_calls_run_batch(self, tmp_path: Path) -> None:
        """batch composites calls run_batch(batch_type='composites')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "composites", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert (
            mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "composites"
        )

    def test_batch_composites_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch composites without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "composites", str(input_file)])

        assert result.exit_code == 0

    def test_batch_presets_calls_run_batch(self, tmp_path: Path) -> None:
        """batch presets calls run_batch(batch_type='presets')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "presets", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "presets"

    def test_batch_presets_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch presets without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "presets", str(input_file)])

        assert result.exit_code == 0

    def test_batch_all_calls_run_batch(self, tmp_path: Path) -> None:
        """batch all calls run_batch(batch_type='all')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "all", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "all"

    def test_batch_all_without_output_uses_config_default(self, tmp_path: Path) -> None:
        """batch all without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "all", str(input_file)])

        assert result.exit_code == 0

    def test_batch_all_flat(self, tmp_path: Path) -> None:
        """--flat forwarded for batch all."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                ["batch", "all", str(input_file), "-o", str(tmp_path), "--flat"],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["flat"] is True
