"""Tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner
from wallpaper_core.cli.main import app

runner = CliRunner()


class TestMainCLI:
    """Tests for main CLI app."""

    def test_version(self) -> None:
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "wallpaper-effects" in result.stdout.lower()

    def test_help(self) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "process" in result.stdout
        assert "batch" in result.stdout
        assert "show" in result.stdout


class TestShowCommands:
    """Tests for show commands."""

    def test_show_effects(self) -> None:
        """Test show effects command."""
        result = runner.invoke(app, ["show", "effects"])
        assert result.exit_code == 0
        assert "blur" in result.stdout.lower()

    def test_show_composites(self) -> None:
        """Test show composites command."""
        result = runner.invoke(app, ["show", "composites"])
        assert result.exit_code == 0

    def test_show_presets(self) -> None:
        """Test show presets command."""
        result = runner.invoke(app, ["show", "presets"])
        assert result.exit_code == 0

    def test_show_all(self) -> None:
        """Test show all command."""
        result = runner.invoke(app, ["show", "all"])
        assert result.exit_code == 0
        assert "Effects" in result.stdout or "effects" in result.stdout.lower()


class TestProcessCommands:
    """Tests for process commands."""

    def test_process_effect(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect command."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "blur",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_effect_with_params(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with parameters."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "blur",
                "--blur",
                "0x10",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_effect_unknown(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process unknown effect fails."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "nonexistent",
            ],
        )
        assert result.exit_code != 0

    def test_process_effect_missing_input(self, tmp_path: Path) -> None:
        """Test process effect with missing input file."""
        missing_file = tmp_path / "nonexistent.jpg"
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(missing_file),
                str(output_path),
                "-e",
                "blur",
            ],
        )
        assert result.exit_code != 0

    def test_process_effect_with_brightness(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with brightness parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "brightness",
                "--brightness",
                "50",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_effect_with_contrast(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with contrast parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "brightness",
                "--contrast",
                "20",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_effect_with_saturation(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with saturation parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "brightness",
                "--saturation",
                "30",
            ],
        )
        assert result.exit_code == 0

    def test_process_effect_with_strength(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with strength parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "blur",
                "--strength",
                "5",
            ],
        )
        assert result.exit_code == 0

    def test_process_effect_with_color(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with color parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "brightness",
                "--color",
                "#FF0000",
            ],
        )
        assert result.exit_code == 0

    def test_process_effect_with_opacity(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect with opacity parameter."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "brightness",
                "--opacity",
                "75",
            ],
        )
        assert result.exit_code == 0

    def test_process_composite(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process composite command."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "blur-brightness80",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_composite_missing_input(self, tmp_path: Path) -> None:
        """Test process composite with missing input file."""
        missing_file = tmp_path / "nonexistent.jpg"
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(missing_file),
                str(output_path),
                "-c",
                "blur-brightness80",
            ],
        )
        assert result.exit_code != 0

    def test_process_composite_unknown(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process unknown composite fails."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "nonexistent-composite",
            ],
        )
        assert result.exit_code != 0

    def test_process_preset(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process preset command."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_path),
                "-p",
                "dark_blur",
            ],
        )
        assert result.exit_code == 0
        assert output_path.exists()

    def test_process_preset_missing_input(self, tmp_path: Path) -> None:
        """Test process preset with missing input file."""
        missing_file = tmp_path / "nonexistent.jpg"
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(missing_file),
                str(output_path),
                "-p",
                "dark_blur",
            ],
        )
        assert result.exit_code != 0

    def test_process_preset_unknown(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process unknown preset fails."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_path),
                "-p",
                "nonexistent-preset",
            ],
        )
        assert result.exit_code != 0


class TestBatchCommands:
    """Tests for batch commands."""

    def test_batch_effects(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch effects command."""
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        # Check that effects directory was created
        effects_dir = tmp_path / test_image_file.stem / "effects"
        assert effects_dir.exists() or (tmp_path / "effects").exists()

    def test_batch_effects_flat(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch effects with flat output."""
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_all(self, test_image_file: Path, tmp_path: Path) -> None:
        """Test batch all command."""
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                str(tmp_path),
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_all_flat(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch all with flat output."""
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                str(tmp_path),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_composites(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch composites command."""
        result = runner.invoke(
            app,
            [
                "batch",
                "composites",
                str(test_image_file),
                str(tmp_path),
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_presets(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch presets command."""
        result = runner.invoke(
            app,
            [
                "batch",
                "presets",
                str(test_image_file),
                str(tmp_path),
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_missing_input(self, tmp_path: Path) -> None:
        """Test batch with missing input file."""
        missing_file = tmp_path / "nonexistent.jpg"
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(missing_file),
                str(tmp_path),
            ],
        )
        assert result.exit_code != 0

    def test_batch_composites_flat(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch composites with flat output."""
        result = runner.invoke(
            app,
            [
                "batch",
                "composites",
                str(test_image_file),
                str(tmp_path),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_presets_flat(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch presets with flat output."""
        result = runner.invoke(
            app,
            [
                "batch",
                "presets",
                str(test_image_file),
                str(tmp_path),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0


class TestInfoCommand:
    """Tests for info command."""

    def test_info_shows_settings(self) -> None:
        """Test info command displays settings."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Core Settings" in result.stdout
        assert "Effects" in result.stdout

    def test_info_shows_effects_count(self) -> None:
        """Test info command shows effects count."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert (
            "Effects defined" in result.stdout
            or "effects" in result.stdout.lower()
        )


class TestVerbosityFlags:
    """Tests for verbosity flags."""

    def test_quiet_flag(self) -> None:
        """Test -q quiet flag."""
        result = runner.invoke(app, ["-q", "show", "effects"])
        assert result.exit_code == 0

    def test_verbose_flag(self) -> None:
        """Test -v verbose flag."""
        result = runner.invoke(app, ["-v", "show", "effects"])
        assert result.exit_code == 0

    def test_debug_flag(self) -> None:
        """Test -vv debug flag."""
        result = runner.invoke(app, ["-vv", "show", "effects"])
        assert result.exit_code == 0


class TestApplyCompositeErrors:
    """Tests for composite error handling."""

    def test_apply_composite_unknown_composite_error(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test apply composite with unknown composite references missing composite."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "nonexistent-composite",
            ],
        )
        assert result.exit_code != 0


class TestApplyPresetErrors:
    """Tests for preset error handling."""

    def test_apply_preset_missing_preset_error(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test apply preset with missing preset."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_path),
                "-p",
                "nonexistent-preset",
            ],
        )
        assert result.exit_code != 0


class TestDryRunErrorCases:
    """Tests for dry-run with error conditions."""

    def test_dry_run_composite_quiet_mode(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test dry-run composite in quiet mode."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "blur-brightness80",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_unknown_composite(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test dry-run with unknown composite."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "nonexistent-composite",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert (
            "cannot resolve" in result.stdout.lower()
            or "unknown" in result.stdout.lower()
        )

    def test_dry_run_unknown_preset(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test dry-run with unknown preset."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_path),
                "-p",
                "nonexistent-preset",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert (
            "cannot resolve" in result.stdout.lower()
            or "unknown" in result.stdout.lower()
        )


class TestExecutorFailures:
    """Tests for executor failure handling."""

    def test_apply_effect_executor_failure(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test apply effect when executor fails."""
        from unittest.mock import MagicMock, patch

        output_path = tmp_path / "output.png"
        with patch(
            "wallpaper_core.cli.process.CommandExecutor"
        ) as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.execute.return_value = MagicMock(
                success=False, stderr="ImageMagick error"
            )
            mock_executor_class.return_value = mock_executor

            result = runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(test_image_file),
                    str(output_path),
                    "-e",
                    "blur",
                ],
            )
            assert result.exit_code == 1

    def test_apply_composite_executor_failure(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test apply composite when executor fails."""
        from unittest.mock import MagicMock, patch

        output_path = tmp_path / "output.png"
        with patch(
            "wallpaper_core.cli.process.ChainExecutor"
        ) as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.execute_chain.return_value = MagicMock(
                success=False, stderr="Chain execution failed"
            )
            mock_executor_class.return_value = mock_executor

            result = runner.invoke(
                app,
                [
                    "process",
                    "composite",
                    str(test_image_file),
                    str(output_path),
                    "-c",
                    "blur-brightness80",
                ],
            )
            assert result.exit_code == 1

    def test_apply_preset_executor_failure_composite(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test apply preset with composite executor failure."""
        from unittest.mock import MagicMock, patch

        output_path = tmp_path / "output.png"
        with patch(
            "wallpaper_core.cli.process.ChainExecutor"
        ) as mock_executor_class:
            mock_executor = MagicMock()
            mock_executor.execute_chain.return_value = MagicMock(
                success=False, stderr="Chain execution failed"
            )
            mock_executor_class.return_value = mock_executor

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(test_image_file),
                    str(output_path),
                    "-p",
                    "dark_blur",
                ],
            )
            assert result.exit_code == 1



class TestCLIExceptionHandlers:
    """Tests for CLI exception handlers in bootstrap."""

    def test_effects_validation_error_handler(self) -> None:
        """Test EffectsValidationError exception handler."""
        from unittest.mock import patch

        from layered_effects.errors import EffectsValidationError

        with patch("wallpaper_core.cli.main.load_effects") as mock_load:
            mock_load.side_effect = EffectsValidationError(
                layer="merged", message="Invalid effect definition"
            )
            result = runner.invoke(app, ["show", "effects"])
            assert result.exit_code == 1

    def test_effects_error_handler(self) -> None:
        """Test generic EffectsError exception handler."""
        from unittest.mock import patch

        from layered_effects.errors import EffectsError

        with patch("wallpaper_core.cli.main.load_effects") as mock_load:
            mock_load.side_effect = EffectsError("Generic effects error")
            result = runner.invoke(app, ["show", "effects"])
            assert result.exit_code == 1


class TestQuietModeProcessing:
    """Tests for quiet mode in processing commands."""

    def test_process_effect_quiet_mode(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process effect in quiet mode."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "effect",
                str(test_image_file),
                str(output_path),
                "-e",
                "blur",
            ],
        )
        assert result.exit_code == 0

    def test_process_composite_quiet_mode(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process composite in quiet mode."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "composite",
                str(test_image_file),
                str(output_path),
                "-c",
                "blur-brightness80",
            ],
        )
        assert result.exit_code == 0

    def test_process_preset_quiet_mode(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test process preset in quiet mode."""
        output_path = tmp_path / "output.png"
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "preset",
                str(test_image_file),
                str(output_path),
                "-p",
                "dark_blur",
            ],
        )
        assert result.exit_code == 0

    def test_batch_quiet_mode(self, test_image_file: Path, tmp_path: Path) -> None:
        """Test batch in quiet mode."""
        result = runner.invoke(
            app,
            [
                "-q",
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--sequential",
            ],
        )
        assert result.exit_code == 0

    def test_batch_all_quiet_mode(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch all in quiet mode."""
        result = runner.invoke(
            app,
            [
                "-q",
                "batch",
                "all",
                str(test_image_file),
                str(tmp_path / "output"),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
