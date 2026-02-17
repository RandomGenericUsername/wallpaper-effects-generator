"""Tests for DryRunBase formatting utilities."""

from io import StringIO

import pytest
from rich.console import Console

from layered_settings.dry_run import DryRunBase, ValidationCheck


@pytest.fixture
def console_output():
    """Capture console output."""
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120, highlight=False)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    """Create DryRunBase with captured output."""
    console, _ = console_output
    return DryRunBase(console=console)


class TestValidationCheck:
    def test_passed_check(self):
        check = ValidationCheck(name="Input file exists", passed=True)
        assert check.passed is True
        assert check.name == "Input file exists"
        assert check.detail == ""

    def test_failed_check_with_detail(self):
        check = ValidationCheck(
            name="magick binary found",
            passed=False,
            detail="not found on PATH",
        )
        assert check.passed is False
        assert check.detail == "not found on PATH"


class TestDryRunBaseRendering:
    def test_render_header(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_header("process effect")
        output = string_io.getvalue()
        assert "Dry Run" in output
        assert "process effect" in output

    def test_render_field(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_field("Input", "/path/to/image.jpg")
        output = string_io.getvalue()
        assert "Input" in output
        assert "/path/to/image.jpg" in output

    def test_render_command(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_command("Command", 'magick "input.jpg" -blur 0x8 "output.jpg"')
        output = string_io.getvalue()
        assert "magick" in output
        assert "input.jpg" in output

    def test_render_validation_passed(self, dry_run, console_output):
        _, string_io = console_output
        checks = [
            ValidationCheck(name="Input file exists", passed=True),
            ValidationCheck(name="magick binary found", passed=True),
        ]
        dry_run.render_validation(checks)
        output = string_io.getvalue()
        assert "Input file exists" in output
        assert "magick binary found" in output

    def test_render_validation_failed(self, dry_run, console_output):
        _, string_io = console_output
        checks = [
            ValidationCheck(
                name="Input file exists", passed=False, detail="file not found"
            ),
        ]
        dry_run.render_validation(checks)
        output = string_io.getvalue()
        assert "Input file exists" in output
        assert "file not found" in output

    def test_render_table(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_table(
            title="Effects (2)",
            columns=["Name", "Output Path", "Params"],
            rows=[
                ["blur", "/output/blur.jpg", "blur=0x8"],
                ["blackwhite", "/output/blackwhite.jpg", "—"],
            ],
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "blackwhite" in output

    def test_render_commands_list(self, dry_run, console_output):
        _, string_io = console_output
        commands = [
            'magick "input.jpg" -blur 0x8 "output.jpg"',
            'magick "input.jpg" -grayscale Average "output2.jpg"',
        ]
        dry_run.render_commands_list(commands)
        output = string_io.getvalue()
        assert "1." in output
        assert "2." in output
        assert "-blur" in output
        assert "-grayscale" in output
