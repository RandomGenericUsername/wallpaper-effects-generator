"""Tests for CoreDryRun rendering and validation."""

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from wallpaper_core.dry_run import CoreDryRun


@pytest.fixture
def console_output():
    """Capture console output."""
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120, highlight=False)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    """Create CoreDryRun with captured output."""
    console, _ = console_output
    return CoreDryRun(console=console)


class TestCoreValidation:
    def test_validate_input_exists(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(input_path=input_file)
        input_check = next(c for c in checks if "Input file" in c.name)
        assert input_check.passed is True

    def test_validate_input_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "nonexistent.jpg"
        checks = dry_run.validate_core(input_path=input_file)
        input_check = next(c for c in checks if "Input file" in c.name)
        assert input_check.passed is False

    def test_validate_magick_found(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        with patch("shutil.which", return_value="/usr/bin/magick"):
            checks = dry_run.validate_core(input_path=input_file)
        magick_check = next(c for c in checks if "magick" in c.name.lower())
        assert magick_check.passed is True

    def test_validate_magick_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        with patch("shutil.which", return_value=None):
            checks = dry_run.validate_core(input_path=input_file)
        magick_check = next(c for c in checks if "magick" in c.name.lower())
        assert magick_check.passed is False

    def test_validate_effect_found(self, dry_run, tmp_path, sample_effects_config):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(
            input_path=input_file,
            item_name="blur",
            item_type="effect",
            config=sample_effects_config,
        )
        effect_check = next(
            c for c in checks if "blur" in c.name.lower() or "found" in c.name.lower()
        )
        assert effect_check.passed is True

    def test_validate_effect_not_found(self, dry_run, tmp_path, sample_effects_config):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(
            input_path=input_file,
            item_name="nonexistent",
            item_type="effect",
            config=sample_effects_config,
        )
        effect_check = next(
            c for c in checks if not c.passed and "effect" in c.name.lower()
        )
        assert effect_check.passed is False

    def test_validate_output_dir_exists(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output" / "result.jpg"
        (tmp_path / "output").mkdir()
        checks = dry_run.validate_core(input_path=input_file, output_path=output_file)
        dir_check = next(
            c for c in checks if "Output" in c.name or "directory" in c.name.lower()
        )
        assert dir_check.passed is True

    def test_validate_output_dir_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "nonexistent_dir" / "result.jpg"
        checks = dry_run.validate_core(input_path=input_file, output_path=output_file)
        dir_check = next(
            c for c in checks if "Output" in c.name or "directory" in c.name.lower()
        )
        assert dir_check.passed is False
        assert "would be created" in dir_check.detail.lower()


class TestCoreRenderProcess:
    def test_render_process_shows_effect(self, dry_run, console_output):
        _, string_io = console_output
        cmd = 'magick "/home/user/wallpaper.jpg" -blur 0x8 "/home/user/output/blur.jpg"'
        dry_run.render_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/home/user/wallpaper.jpg"),
            output_path=Path("/home/user/output/blur.jpg"),
            params={"blur": "0x8"},
            resolved_command=cmd,
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "/home/user/wallpaper.jpg" in output
        assert "/home/user/output/blur.jpg" in output
        assert "0x8" in output

    def test_render_process_shows_command(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/input.jpg"),
            output_path=Path("/output.jpg"),
            params={"blur": "0x8"},
            resolved_command='magick "/input.jpg" -blur 0x8 "/output.jpg"',
        )
        output = string_io.getvalue()
        assert "magick" in output

    def test_render_process_composite_shows_chain(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_process(
            item_name="blur-brightness80",
            item_type="composite",
            input_path=Path("/input.jpg"),
            output_path=Path("/output.jpg"),
            params={},
            resolved_command="chain: blur -> brightness",
            chain_commands=[
                'magick "/input.jpg" -blur 0x8 "/tmp/step_0.jpg"',
                'magick "/tmp/step_0.jpg" -brightness-contrast -20% "/output.jpg"',
            ],
        )
        output = string_io.getvalue()
        assert "blur-brightness80" in output
        assert "1." in output or "step" in output.lower()


class TestCoreRenderBatch:
    def test_render_batch_shows_table(self, dry_run, console_output):
        _, string_io = console_output
        items = [
            {
                "name": "blur",
                "type": "effect",
                "output_path": "/output/blur.jpg",
                "params": "blur=0x8",
                "command": 'magick "in.jpg" -blur 0x8 "/output/blur.jpg"',
            },
            {
                "name": "blackwhite",
                "type": "effect",
                "output_path": "/output/blackwhite.jpg",
                "params": "\u2014",
                "command": (
                    'magick "in.jpg" -grayscale Average "/output/blackwhite.jpg"'
                ),
            },
        ]
        dry_run.render_batch(
            input_path=Path("/home/user/wallpaper.jpg"),
            output_dir=Path("/output/"),
            items=items,
            parallel=True,
            max_workers=4,
            strict=True,
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "blackwhite" in output
        assert "2" in output
