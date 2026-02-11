"""Shared fixtures for wallpaper processor tests."""

import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from wallpaper_processor.config.schema import (
    ChainStep,
    CompositeDefinition,
    EffectDefinition,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    PresetDefinition,
)
from wallpaper_processor.config.settings import (
    ExecutionSettings,
    OutputSettings,
    PathSettings,
    Settings,
    Verbosity,
)
from wallpaper_processor.console.output import RichOutput

# ============================================================================
# Image Fixtures
# ============================================================================


@pytest.fixture
def test_image_file(tmp_path: Path) -> Path:
    """Create a simple test image using ImageMagick."""
    image_path = tmp_path / "test_image.png"
    # Create a 100x100 gray image using magick
    subprocess.run(
        ["magick", "-size", "100x100", "xc:#808080", str(image_path)],
        check=True,
        capture_output=True,
    )
    return image_path


@pytest.fixture
def test_image_large_file(tmp_path: Path) -> Path:
    """Create a larger test image file using ImageMagick."""
    image_path = tmp_path / "test_image_large.png"
    subprocess.run(
        ["magick", "-size", "200x200", "xc:#404040", str(image_path)],
        check=True,
        capture_output=True,
    )
    return image_path


@pytest.fixture
def colorful_test_image_file(tmp_path: Path) -> Path:
    """Create a colorful gradient test image."""
    image_path = tmp_path / "colorful.png"
    subprocess.run(
        [
            "magick",
            "-size",
            "100x100",
            "gradient:red-blue",
            str(image_path),
        ],
        check=True,
        capture_output=True,
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
def sample_effects() -> dict[str, EffectDefinition]:
    """Create sample effect definitions."""
    return {
        "blur": EffectDefinition(
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
        "blackwhite": EffectDefinition(
            description="Convert to grayscale",
            command='magick "$INPUT" -grayscale Average "$OUTPUT"',
            parameters={},
        ),
        "brightness": EffectDefinition(
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
def sample_composites() -> dict[str, CompositeDefinition]:
    """Create sample composite definitions."""
    return {
        "blur-brightness": CompositeDefinition(
            description="Blur then adjust brightness",
            chain=[
                ChainStep(effect="blur", params={"blur": "0x8"}),
                ChainStep(effect="brightness", params={"brightness": -20}),
            ],
        ),
        "blackwhite-blur": CompositeDefinition(
            description="Convert to grayscale then blur",
            chain=[
                ChainStep(effect="blackwhite"),
                ChainStep(effect="blur", params={"blur": "0x5"}),
            ],
        ),
    }


@pytest.fixture
def sample_presets() -> dict[str, PresetDefinition]:
    """Create sample preset definitions."""
    return {
        "dark_blur": PresetDefinition(
            description="Dark blurred background",
            composite="blur-brightness",
        ),
        "subtle_blur": PresetDefinition(
            description="Gentle blur effect",
            effect="blur",
            params={"blur": "0x3"},
        ),
    }


@pytest.fixture
def sample_effects_config(
    sample_parameter_types: dict[str, ParameterType],
    sample_effects: dict[str, EffectDefinition],
    sample_composites: dict[str, CompositeDefinition],
    sample_presets: dict[str, PresetDefinition],
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
            "blur": EffectDefinition(
                description="Blur",
                command='magick "$INPUT" -blur 0x8 "$OUTPUT"',
            ),
        },
    )


# ============================================================================
# Settings Fixtures
# ============================================================================


@pytest.fixture
def default_settings() -> Settings:
    """Create default settings."""
    return Settings.default()


@pytest.fixture
def custom_settings() -> Settings:
    """Create custom settings for testing."""
    return Settings(
        version="1.0",
        execution=ExecutionSettings(
            parallel=False,
            strict=False,
            max_workers=2,
        ),
        output=OutputSettings(
            verbosity=Verbosity.VERBOSE,
            format="jpg",
            quality=85,
        ),
        paths=PathSettings(),
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
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_subprocess_run() -> Mock:
    """Mock subprocess.run for testing."""
    mock = Mock()
    mock.return_value = Mock(returncode=0, stdout="", stderr="")
    return mock


@pytest.fixture
def mock_subprocess_run_failure() -> Mock:
    """Mock subprocess.run that returns failure."""
    mock = Mock()
    mock.return_value = Mock(returncode=1, stdout="", stderr="Error occurred")
    return mock


@pytest.fixture
def mock_shutil_which() -> Mock:
    """Mock shutil.which for availability checks."""
    mock = Mock()
    mock.return_value = "/usr/bin/magick"
    return mock


@pytest.fixture
def mock_shutil_which_not_found() -> Mock:
    """Mock shutil.which returning None (not found)."""
    mock = Mock()
    mock.return_value = None
    return mock


# ============================================================================
# Cleanup
# ============================================================================


@pytest.fixture(autouse=True)
def clear_config_cache() -> None:
    """Clear config cache before each test."""
    from wallpaper_processor.config.loader import ConfigLoader

    ConfigLoader.clear_cache()
    yield
    ConfigLoader.clear_cache()
