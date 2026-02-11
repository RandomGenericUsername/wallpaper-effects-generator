"""Tests for --dry-run flag on core CLI commands."""

from typer.testing import CliRunner

from wallpaper_core.cli.main import app

runner = CliRunner()


class TestProcessEffectDryRun:
    def test_dry_run_shows_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_file),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "magick" in result.stdout

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_file),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )
        assert not output_file.exists()

    def test_dry_run_shows_validation(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(output_file),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Validation" in result.stdout or "\u2713" in result.stdout

    def test_dry_run_missing_input_shows_warning(self, tmp_path):
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(tmp_path / "nonexistent.jpg"),
                str(tmp_path / "output.jpg"),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "\u2717" in result.stdout

    def test_dry_run_unknown_effect_shows_warning(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(tmp_path / "output.jpg"),
                "--effect",
                "nonexistent_effect",
                "--dry-run",
            ],
        )
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "\u2717" in result.stdout

    def test_dry_run_quiet_shows_only_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "effect",
                str(test_image_file),
                str(output_file),
                "--effect",
                "blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "magick" in result.stdout
        assert "Validation" not in result.stdout


class TestProcessCompositeDryRun:
    def test_dry_run_shows_chain(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_file),
                "--composite",
                "blur-brightness80",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "blur" in result.stdout.lower()
        assert "brightness" in result.stdout.lower()

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(
            app,
            [
                "process",
                "composite",
                str(test_image_file),
                str(output_file),
                "--composite",
                "blur-brightness80",
                "--dry-run",
            ],
        )
        assert not output_file.exists()


class TestProcessPresetDryRun:
    def test_dry_run_composite_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_file),
                "--preset",
                "dark_blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "dark_blur" in result.stdout

    def test_dry_run_effect_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(test_image_file),
                str(output_file),
                "--preset",
                "subtle_blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "subtle_blur" in result.stdout


class TestBatchEffectsDryRun:
    def test_dry_run_shows_table(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "blur" in result.stdout
        assert "blackwhite" in result.stdout

    def test_dry_run_no_files_created(self, test_image_file, tmp_path):
        output_dir = tmp_path / "output"
        runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(output_dir),
                "--dry-run",
            ],
        )
        assert not output_dir.exists()

    def test_dry_run_shows_commands(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert "magick" in result.stdout

    def test_dry_run_shows_item_count(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert "items" in result.stdout.lower() or "9" in result.stdout


class TestBatchAllDryRun:
    def test_dry_run_shows_all_types(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "blur" in result.stdout
        assert "dark_blur" in result.stdout or "preset" in result.stdout.lower()

    def test_dry_run_no_files_created(self, test_image_file, tmp_path):
        output_dir = tmp_path / "output"
        runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                str(output_dir),
                "--dry-run",
            ],
        )
        assert not output_dir.exists()

    def test_dry_run_quiet_shows_only_commands(self, test_image_file, tmp_path):
        result = runner.invoke(
            app,
            [
                "-q",
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "magick" in result.stdout
        assert "Validation" not in result.stdout

    def test_dry_run_batch_all_flat(self, test_image_file, tmp_path):
        """Test batch all with flat output in dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                str(tmp_path / "output"),
                "--flat",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_batch_composites(self, test_image_file, tmp_path):
        """Test batch composites dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "composites",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_batch_composites_flat(self, test_image_file, tmp_path):
        """Test batch composites with flat output in dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "composites",
                str(test_image_file),
                str(tmp_path / "output"),
                "--flat",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_batch_presets(self, test_image_file, tmp_path):
        """Test batch presets dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "presets",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_batch_presets_flat(self, test_image_file, tmp_path):
        """Test batch presets with flat output in dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "presets",
                str(test_image_file),
                str(tmp_path / "output"),
                "--flat",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_batch_effects_flat(self, test_image_file, tmp_path):
        """Test batch effects with flat output in dry-run."""
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--flat",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_composite_quiet(self, test_image_file, tmp_path):
        """Test dry-run composite with quiet mode."""
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "composite",
                str(test_image_file),
                str(tmp_path / "output.png"),
                "-c",
                "blur-brightness80",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_preset_quiet(self, test_image_file, tmp_path):
        """Test dry-run preset with quiet mode."""
        result = runner.invoke(
            app,
            [
                "-q",
                "process",
                "preset",
                str(test_image_file),
                str(tmp_path / "output.png"),
                "-p",
                "dark_blur",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_unknown_effect(self, test_image_file, tmp_path):
        """Test dry-run with nonexistent effect."""
        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(test_image_file),
                str(tmp_path / "output.png"),
                "-e",
                "nonexistent-effect",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_verbose_batch(self, test_image_file, tmp_path):
        """Test dry-run batch with verbose mode."""
        result = runner.invoke(
            app,
            [
                "-v",
                "batch",
                "effects",
                str(test_image_file),
                str(tmp_path / "output"),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
