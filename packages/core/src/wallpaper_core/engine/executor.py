"""Shell command executor for ImageMagick effects."""

from __future__ import annotations

import shutil
import subprocess  # nosec: necessary for command execution
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wallpaper_core.console.output import RichOutput


@dataclass
class ExecutionResult:
    """Result of command execution."""

    success: bool
    command: str
    stdout: str
    stderr: str
    return_code: int
    duration: float = 0.0


class CommandExecutor:
    """Execute shell commands for effects."""

    def __init__(self, output: RichOutput | None = None) -> None:
        """Initialize CommandExecutor.

        Args:
            output: RichOutput instance for logging
        """
        self.output = output

    def is_magick_available(self) -> bool:
        """Check if ImageMagick is available."""
        return shutil.which("magick") is not None

    def execute(
        self,
        command_template: str,
        input_path: Path,
        output_path: Path,
        params: dict[str, str | int | float] | None = None,
    ) -> ExecutionResult:
        """Execute a single magick command.

        Substitutes variables in command template:
        - $INPUT: Input file path
        - $OUTPUT: Output file path
        - $PARAM_NAME: Parameter values (uppercase)

        Args:
            command_template: Command template with variables
            input_path: Path to input image
            output_path: Path to output image
            params: Parameter values

        Returns:
            ExecutionResult with success status and details
        """
        import time

        params = params or {}

        # Build substitution map
        substitutions = {
            "INPUT": str(input_path),
            "OUTPUT": str(output_path),
        }

        # Add parameters (uppercase keys)
        for key, value in params.items():
            substitutions[key.upper()] = str(value)

        # Substitute variables in command
        command = command_template
        for key, value in substitutions.items():
            command = command.replace(f'"${key}"', f'"{value}"')
            command = command.replace(f"${key}", value)

        if self.output:
            self.output.command(command)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                shell=True,  # nosec B602: Required for executing user-defined effect commands
                capture_output=True,
                text=True,
                check=False,
            )
            duration = time.time() - start_time

            if self.output and result.stdout:
                self.output.debug(f"stdout: {result.stdout}")
            if self.output and result.stderr:
                self.output.debug(f"stderr: {result.stderr}")

            return ExecutionResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr=str(e),
                return_code=-1,
                duration=duration,
            )
