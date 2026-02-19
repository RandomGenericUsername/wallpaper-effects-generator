"""Shared fixtures for wallpaper_orchestrator tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _mock_subprocess_run(command, **kwargs):
    """
    Mock subprocess.run that simulates magick command execution.

    Creates output files for magick commands that specify an output path,
    so tests can run without needing ImageMagick installed.
    Returns failure if input file doesn't exist.

    Args:
        command: Command to execute (string when shell=True, list otherwise)
        **kwargs: Additional subprocess.run arguments
    """
    import re

    # Create a mock result
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    # Convert command to string if it's a list
    command_str = " ".join(command) if isinstance(command, list) else str(command)

    # For magick commands, extract paths and validate/create files
    if "magick" in command_str.lower():
        # Find quoted paths - they're in the format "path/to/file.ext"
        quoted_paths = re.findall(r'"([^"]+)"', command_str)

        if quoted_paths:
            # First quoted path is typically the input file
            input_file = quoted_paths[0]

            # Check if input file exists - if not, fail the command
            if input_file.endswith((".png", ".jpg", ".jpeg")):
                input_path = Path(input_file)
                if not input_path.exists():
                    # Return failure for nonexistent input file
                    mock_result.returncode = 1
                    mock_result.stderr = f"magick: unable to open image `{input_file}'"
                    return mock_result

            # If we have at least 2 quoted paths, create the output file
            if len(quoted_paths) >= 2:
                output_file = quoted_paths[-1]

                if output_file.endswith((".png", ".jpg", ".jpeg")):
                    output_path = Path(output_file)
                    # Create parent directories if needed
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    # Create a minimal valid PNG file
                    output_path.write_bytes(
                        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d"
                        b"\x08\x02\x00\x00\x00\xf6B\xc8n\x00\x00\x00\x00IEND\xaeB`\x82"
                    )

    return mock_result


@pytest.fixture(autouse=True)
def mock_subprocess_for_integration_tests():
    """
    Auto-use fixture that mocks subprocess.run and shutil.which for all tests.

    This allows integration tests to run without ImageMagick installed
    by simulating command execution and file creation. Also mocks shutil.which
    so validation checks pass without requiring the binary to be on PATH.
    """

    def mock_which(cmd):
        """Mock shutil.which to return a fake path for magick."""
        if cmd == "magick":
            return "/usr/bin/magick"  # Fake path for validation checks
        return None

    with (
        patch(
            "wallpaper_core.engine.executor.subprocess.run",
            side_effect=_mock_subprocess_run,
        ),
        patch("shutil.which", side_effect=mock_which),
    ):
        yield


@pytest.fixture(autouse=True)
def reset_effects_configuration():
    """
    Auto-use fixture that resets effects configuration between tests.

    This prevents test pollution where one test's effects configuration
    (especially temporary directories with invalid files) affects other tests.
    Restores default configuration after reset.
    """
    from layered_effects import _reset
    from layered_effects import configure as configure_effects

    from wallpaper_core.effects import get_package_effects_file

    # Reset before each test to ensure clean state
    _reset()

    # Re-configure with default settings (package effects only, no project root)
    # This matches the CLI's default configuration
    configure_effects(package_effects_file=get_package_effects_file())

    yield

    # Reset after each test to clean up
    _reset()

    # Re-configure for next test
    configure_effects(package_effects_file=get_package_effects_file())


@pytest.fixture
def use_tmp_default_output(tmp_path: Path, monkeypatch):
    """
    Fixture that overrides the default output directory with tmp_path.

    This allows tests to verify default output behavior while maintaining
    test isolation, preventing race conditions during parallel execution.
    """
    from layered_settings import get_config

    # Get the current config
    config = get_config()

    # Patch the output.default_dir setting
    test_default = tmp_path / "wallpapers-output"
    original_default = config.core.output.default_dir

    monkeypatch.setattr(config.core.output, "default_dir", test_default)

    yield test_default

    # Restore original
    monkeypatch.setattr(config.core.output, "default_dir", original_default)
