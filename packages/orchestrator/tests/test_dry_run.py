"""Tests for OrchestratorDryRun rendering and validation."""

from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from wallpaper_orchestrator.dry_run import OrchestratorDryRun


@pytest.fixture
def console_output():
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120, highlight=False)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    console, _ = console_output
    return OrchestratorDryRun(console=console)


class TestContainerValidation:
    def test_validate_engine_found(self, dry_run):
        with patch("shutil.which", return_value="/usr/bin/podman"):
            checks = dry_run.validate_container(engine="podman")
        engine_check = next(
            c
            for c in checks
            if "podman" in c.name.lower() or "engine" in c.name.lower()
        )
        assert engine_check.passed is True

    def test_validate_engine_missing(self, dry_run):
        with patch("shutil.which", return_value=None):
            checks = dry_run.validate_container(engine="podman")
        engine_check = next(
            c
            for c in checks
            if "podman" in c.name.lower() or "engine" in c.name.lower()
        )
        assert engine_check.passed is False

    def test_validate_image_available(self, dry_run):
        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0)
            checks = dry_run.validate_container(
                engine="docker", image_name="wallpaper-effects:latest"
            )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is True

    def test_validate_image_missing(self, dry_run):
        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=1)
            checks = dry_run.validate_container(
                engine="docker", image_name="wallpaper-effects:latest"
            )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is False

    def test_validate_image_subprocess_error(self, dry_run):
        """Test validate_container handles subprocess errors."""
        import subprocess

        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.side_effect = subprocess.SubprocessError("Docker error")
            checks = dry_run.validate_container(
                engine="docker", image_name="wallpaper-effects:latest"
            )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is False

    def test_validate_image_file_not_found(self, dry_run):
        """Test validate_container handles FileNotFoundError."""
        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.side_effect = FileNotFoundError("Docker not found")
            checks = dry_run.validate_container(
                engine="docker", image_name="wallpaper-effects:latest"
            )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is False


class TestContainerRenderProcess:
    def test_render_container_process_shows_both_commands(
        self, dry_run, console_output
    ):
        _, string_io = console_output
        dry_run.render_container_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/home/user/wallpaper.jpg"),
            output_path=Path("/home/user/output/blur.jpg"),
            engine="podman",
            image_name="wallpaper-effects:latest",
            host_command="podman run --rm ...",
            inner_command='magick "/input/image.jpg" -blur 0x8 "/output/blur.jpg"',
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "magick" in output
        assert "Host" in output or "host" in output
        assert "Inner" in output or "inner" in output or "Inside" in output.lower()

    def test_render_install(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_install(
            engine="podman",
            image_name="wallpaper-effects:latest",
            dockerfile=Path("/path/to/Dockerfile.imagemagick"),
            build_command="podman build -f ... -t wallpaper-effects:latest .",
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "wallpaper-effects" in output
        assert "Dockerfile" in output

    def test_render_uninstall(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_uninstall(
            engine="podman",
            image_name="wallpaper-effects:latest",
            command="podman rmi wallpaper-effects:latest",
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "rmi" in output
