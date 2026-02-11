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
