"""Tests for passthrough utilities."""

from pathlib import Path

import pytest
from wallpaper_effects.utils.passthrough import (
    extract_input_output_from_args,
    filter_orchestrator_args,
    get_backend_dockerfile,
    parse_core_arguments,
)


class TestGetBackendDockerfile:
    """Tests for get_backend_dockerfile."""

    def test_imagemagick_backend(self) -> None:
        """Test getting Dockerfile for imagemagick backend."""
        dockerfile = get_backend_dockerfile("imagemagick")
        # Returns a Path object to the Dockerfile
        assert dockerfile.name == "Dockerfile.imagemagick"
        assert dockerfile.exists()

    def test_pil_backend(self) -> None:
        """Test getting Dockerfile for pil backend."""
        dockerfile = get_backend_dockerfile("pil")
        assert dockerfile.name == "Dockerfile.pil"
        assert dockerfile.exists()

    def test_unknown_backend(self) -> None:
        """Test getting Dockerfile for unknown backend raises."""
        with pytest.raises(ValueError, match="Unknown backend"):
            get_backend_dockerfile("unknown")


class TestExtractInputOutputFromArgs:
    """Tests for extract_input_output_from_args."""

    def test_short_flags(self) -> None:
        """Test extracting paths with short flags."""
        args = ["-i", "input.jpg", "-o", "output.png", "-e", "blur"]
        input_path, output_path, remaining = extract_input_output_from_args(
            args
        )

        assert input_path == Path("input.jpg")
        assert output_path == Path("output.png")
        assert remaining == ["-e", "blur"]

    def test_long_flags(self) -> None:
        """Test extracting paths with long flags."""
        args = ["--input", "image.jpg", "--output", "result.png"]
        input_path, output_path, remaining = extract_input_output_from_args(
            args
        )

        assert input_path == Path("image.jpg")
        assert output_path == Path("result.png")

    def test_absolute_paths(self) -> None:
        """Test extracting absolute paths."""
        args = ["-i", "/home/user/image.jpg", "-o", "/tmp/output.png"]
        input_path, output_path, remaining = extract_input_output_from_args(
            args
        )

        assert input_path == Path("/home/user/image.jpg")
        assert output_path == Path("/tmp/output.png")

    def test_missing_input_returns_none(self) -> None:
        """Test missing input returns None (no error)."""
        args = ["-o", "output.png"]
        input_path, output_path, remaining = extract_input_output_from_args(
            args
        )

        assert input_path is None
        assert output_path == Path("output.png")

    def test_missing_output_returns_none(self) -> None:
        """Test missing output returns None (no error)."""
        args = ["-i", "input.jpg"]
        input_path, output_path, remaining = extract_input_output_from_args(
            args
        )

        assert input_path == Path("input.jpg")
        assert output_path is None


class TestFilterOrchestratorArgs:
    """Tests for filter_orchestrator_args."""

    def test_removes_backend_flag(self) -> None:
        """Test that --backend is filtered out."""
        args = ["-i", "in.jpg", "-o", "out.png", "--backend", "imagemagick"]
        orchestrator_args, core_args = filter_orchestrator_args(args)

        assert "--backend" not in core_args
        assert "imagemagick" not in core_args
        assert "-i" in core_args
        assert orchestrator_args.get("backend") == "imagemagick"

    def test_removes_verbose_flag(self) -> None:
        """Test that --verbose is filtered out."""
        args = ["-i", "in.jpg", "--verbose", "-o", "out.png"]
        orchestrator_args, core_args = filter_orchestrator_args(args)

        assert "--verbose" not in core_args
        assert orchestrator_args.get("verbose") is True

    def test_keeps_core_args(self) -> None:
        """Test that core args are preserved."""
        args = ["-e", "blur", "--sigma", "5"]
        orchestrator_args, core_args = filter_orchestrator_args(args)

        assert core_args == args
        assert orchestrator_args == {}


class TestParseCoreArguments:
    """Tests for parse_core_arguments."""

    def test_process_command(self) -> None:
        """Test parsing process command."""
        args = ["process", "-i", "in.jpg", "-o", "out.png"]
        command, remaining = parse_core_arguments(args)

        assert command == "process"
        assert "-i" in remaining
        assert "-o" in remaining

    def test_install_command(self) -> None:
        """Test parsing install command."""
        args = ["install", "--backend", "pil"]
        command, remaining = parse_core_arguments(args)

        assert command == "install"
        assert "--backend" in remaining

    def test_invalid_command_raises(self) -> None:
        """Test invalid command raises error."""
        args = ["-i", "in.jpg"]  # Missing command
        with pytest.raises(ValueError, match="Invalid command"):
            parse_core_arguments(args)
