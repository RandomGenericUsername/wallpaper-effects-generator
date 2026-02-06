"""Tests for --dry-run flag on core CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from wallpaper_core.cli.main import app

runner = CliRunner()


class TestProcessEffectDryRun:
    def test_dry_run_shows_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "magick" in result.stdout

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert not output_file.exists()

    def test_dry_run_shows_validation(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "Validation" in result.stdout or "\u2713" in result.stdout

    def test_dry_run_missing_input_shows_warning(self, tmp_path):
        result = runner.invoke(app, [
            "process", "effect",
            str(tmp_path / "nonexistent.jpg"), str(tmp_path / "output.jpg"),
            "--effect", "blur", "--dry-run",
        ])
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "\u2717" in result.stdout

    def test_dry_run_unknown_effect_shows_warning(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(tmp_path / "output.jpg"),
            "--effect", "nonexistent_effect", "--dry-run",
        ])
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "\u2717" in result.stdout

    def test_dry_run_quiet_shows_only_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "-q", "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "magick" in result.stdout
        assert "Validation" not in result.stdout


class TestProcessCompositeDryRun:
    def test_dry_run_shows_chain(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "composite",
            str(test_image_file), str(output_file),
            "--composite", "blur-brightness80", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "blur" in result.stdout.lower()
        assert "brightness" in result.stdout.lower()

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(app, [
            "process", "composite",
            str(test_image_file), str(output_file),
            "--composite", "blur-brightness80", "--dry-run",
        ])
        assert not output_file.exists()


class TestProcessPresetDryRun:
    def test_dry_run_composite_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "preset",
            str(test_image_file), str(output_file),
            "--preset", "dark_blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "dark_blur" in result.stdout

    def test_dry_run_effect_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "preset",
            str(test_image_file), str(output_file),
            "--preset", "subtle_blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "subtle_blur" in result.stdout
