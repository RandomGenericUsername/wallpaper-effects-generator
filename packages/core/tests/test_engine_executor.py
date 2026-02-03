"""Tests for engine executor module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from wallpaper_core.config.schema import Verbosity
from wallpaper_core.console.output import RichOutput
from wallpaper_core.engine.executor import CommandExecutor, ExecutionResult


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_creation(self) -> None:
        """Test creating ExecutionResult."""
        result = ExecutionResult(
            success=True,
            command="echo test",
            stdout="test\n",
            stderr="",
            return_code=0,
            duration=0.5,
        )
        assert result.success is True
        assert result.command == "echo test"
        assert result.stdout == "test\n"
        assert result.stderr == ""
        assert result.return_code == 0
        assert result.duration == 0.5

    def test_default_duration(self) -> None:
        """Test default duration value."""
        result = ExecutionResult(
            success=True,
            command="",
            stdout="",
            stderr="",
            return_code=0,
        )
        assert result.duration == 0.0


class TestCommandExecutor:
    """Tests for CommandExecutor class."""

    def test_init_without_output(self) -> None:
        """Test initialization without RichOutput."""
        executor = CommandExecutor()
        assert executor.output is None

    def test_init_with_output(self, quiet_output: RichOutput) -> None:
        """Test initialization with RichOutput."""
        executor = CommandExecutor(output=quiet_output)
        assert executor.output is quiet_output

    def test_is_magick_available_true(self) -> None:
        """Test magick availability check when available."""
        executor = CommandExecutor()
        with patch("shutil.which", return_value="/usr/bin/magick"):
            assert executor.is_magick_available() is True

    def test_is_magick_available_false(self) -> None:
        """Test magick availability check when not available."""
        executor = CommandExecutor()
        with patch("shutil.which", return_value=None):
            assert executor.is_magick_available() is False

    def test_execute_simple_command(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test executing a simple command."""
        executor = CommandExecutor()
        output_path = tmp_path / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True
        assert result.return_code == 0
        assert output_path.exists()

    def test_execute_with_params(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test executing command with parameter substitution."""
        executor = CommandExecutor()
        output_path = tmp_path / "blurred.png"

        result = executor.execute(
            command_template='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
            params={"blur": "0x5"},
        )

        assert result.success is True
        assert output_path.exists()
        # Check that blur param was substituted
        assert "-blur" in result.command
        assert "0x5" in result.command

    def test_execute_creates_output_dir(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test that execute creates output directory if needed."""
        executor = CommandExecutor()
        output_path = tmp_path / "nested" / "dir" / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True
        assert output_path.parent.exists()
        assert output_path.exists()

    def test_execute_with_output_logging(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test executing with RichOutput logging."""
        output = RichOutput(verbosity=Verbosity.VERBOSE)
        executor = CommandExecutor(output=output)
        output_path = tmp_path / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True

    def test_execute_failure(self, tmp_path: Path) -> None:
        """Test handling command failure."""
        executor = CommandExecutor()
        input_path = tmp_path / "nonexistent.png"
        output_path = tmp_path / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" "$OUTPUT"',
            input_path=input_path,
            output_path=output_path,
        )

        assert result.success is False
        assert result.return_code != 0

    def test_execute_substitution_quoted(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test that variable substitution works with quotes."""
        executor = CommandExecutor()
        output_path = tmp_path / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" -brightness-contrast "$BRIGHTNESS"% "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
            params={"brightness": -20},
        )

        assert result.success is True
        assert "-20" in result.command

    def test_execute_duration_recorded(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test that execution duration is recorded."""
        executor = CommandExecutor()
        output_path = tmp_path / "output.png"

        result = executor.execute(
            command_template='magick "$INPUT" "$OUTPUT"',
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.duration >= 0

