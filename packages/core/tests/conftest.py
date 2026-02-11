"""Shared fixtures for wallpaper_core tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from wallpaper_core.config.schema import Verbosity
from wallpaper_core.console.output import RichOutput
from wallpaper_core.effects.schema import (
    ChainStep,
    CompositeEffect,
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    Preset,
)

# ============================================================================
# Image Fixtures
# ============================================================================


@pytest.fixture
def test_image_file(tmp_path: Path) -> Path:
    """Create a simple test image file (mocked)."""
    image_path = tmp_path / "test_image.png"
    # Create a minimal valid PNG file (mocked, no external dependencies)
    # PNG magic bytes followed by minimal IHDR chunk
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d"
        b"\x08\x02\x00\x00\x00\xf6B\xc8n\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return image_path


@pytest.fixture
def test_image_large_file(tmp_path: Path) -> Path:
    """Create a larger test image file (mocked)."""
    image_path = tmp_path / "test_image_large.png"
    # Create a minimal valid PNG file (mocked, no external dependencies)
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8\x00\x00\x00\xc8"
        b"\x08\x02\x00\x00\x00\xf6B\xc8n\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return image_path


@pytest.fixture
def colorful_test_image_file(tmp_path: Path) -> Path:
    """Create a colorful gradient test image (mocked)."""
    image_path = tmp_path / "colorful.png"
    # Create a minimal valid PNG file (mocked, no external dependencies)
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d"
        b"\x08\x02\x00\x00\x00\xf6B\xc8n\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return image_path


# ============================================================================
# Config Schema Fixtures
# ============================================================================


@pytest.fixture
def sample_parameter_types() -> dict[str, ParameterType]:
    """Create sample parameter type definitions."""
    return {
        "blur_geometry": ParameterType(
            type="string",
            pattern=r"^\d+x\d+$",
            default="0x8",
            description="Blur in format RADIUSxSIGMA",
        ),
        "percent": ParameterType(
            type="integer",
            min=-100,
            max=100,
            default=0,
            description="Percentage value",
        ),
    }


@pytest.fixture
def sample_effects() -> dict[str, Effect]:
    """Create sample effect definitions."""
    return {
        "blur": Effect(
            description="Apply Gaussian blur",
            command='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
            parameters={
                "blur": ParameterDefinition(
                    type="blur_geometry",
                    cli_flag="--blur",
                    default="0x8",
                ),
            },
        ),
        "blackwhite": Effect(
            description="Convert to grayscale",
            command='magick "$INPUT" -grayscale Average "$OUTPUT"',
            parameters={},
        ),
        "brightness": Effect(
            description="Adjust brightness",
            command='magick "$INPUT" -brightness-contrast "$BRIGHTNESS"% "$OUTPUT"',
            parameters={
                "brightness": ParameterDefinition(
                    type="percent",
                    cli_flag="--brightness",
                    default=-20,
                ),
            },
        ),
    }


@pytest.fixture
def sample_composites() -> dict[str, CompositeEffect]:
    """Create sample composite definitions."""
    return {
        "blur-brightness": CompositeEffect(
            description="Blur then adjust brightness",
            chain=[
                ChainStep(effect="blur", params={"blur": "0x8"}),
                ChainStep(effect="brightness", params={"brightness": -20}),
            ],
        ),
        "blackwhite-blur": CompositeEffect(
            description="Convert to grayscale then blur",
            chain=[
                ChainStep(effect="blackwhite"),
                ChainStep(effect="blur", params={"blur": "0x5"}),
            ],
        ),
    }


@pytest.fixture
def sample_presets() -> dict[str, Preset]:
    """Create sample preset definitions."""
    return {
        "dark_blur": Preset(
            description="Dark blurred background",
            composite="blur-brightness",
        ),
        "subtle_blur": Preset(
            description="Gentle blur effect",
            effect="blur",
            params={"blur": "0x3"},
        ),
    }


@pytest.fixture
def sample_effects_config(
    sample_parameter_types: dict[str, ParameterType],
    sample_effects: dict[str, Effect],
    sample_composites: dict[str, CompositeEffect],
    sample_presets: dict[str, Preset],
) -> EffectsConfig:
    """Create a complete sample EffectsConfig."""
    return EffectsConfig(
        version="1.0",
        parameter_types=sample_parameter_types,
        effects=sample_effects,
        composites=sample_composites,
        presets=sample_presets,
    )


@pytest.fixture
def minimal_effects_config() -> EffectsConfig:
    """Create minimal effects config for simple tests."""
    return EffectsConfig(
        version="1.0",
        effects={
            "blur": Effect(
                description="Blur",
                command='magick "$INPUT" -blur 0x8 "$OUTPUT"',
            ),
        },
    )


# ============================================================================
# Console Fixtures
# ============================================================================


@pytest.fixture
def quiet_output() -> RichOutput:
    """Create a quiet RichOutput."""
    return RichOutput(verbosity=Verbosity.QUIET)


@pytest.fixture
def normal_output() -> RichOutput:
    """Create a normal RichOutput."""
    return RichOutput(verbosity=Verbosity.NORMAL)


@pytest.fixture
def verbose_output() -> RichOutput:
    """Create a verbose RichOutput."""
    return RichOutput(verbosity=Verbosity.VERBOSE)


@pytest.fixture
def debug_output() -> RichOutput:
    """Create a debug RichOutput."""
    return RichOutput(verbosity=Verbosity.DEBUG)


# ============================================================================
# Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory structure."""
    config_dir = tmp_path / ".config" / "wallpaper-effects"
    config_dir.mkdir(parents=True)
    return config_dir


# ============================================================================
# Subprocess Mocking for Integration Tests
# ============================================================================


def _mock_subprocess_run(command, **kwargs):
    """
    Mock subprocess.run that simulates magick command execution.

    Creates output files for magick commands that specify an output path,
    so tests can verify file creation without needing ImageMagick installed.
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
    command_str = (
        " ".join(command) if isinstance(command, list) else str(command)
    )

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
                    mock_result.stderr = (
                        f"magick: unable to open image `{input_file}'"
                    )
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
    Auto-use fixture that mocks subprocess.run for all tests.

    This allows integration tests to run without ImageMagick installed
    by simulating command execution and file creation.
    """
    with patch(
        "wallpaper_core.engine.executor.subprocess.run",
        side_effect=_mock_subprocess_run,
    ):
        yield
