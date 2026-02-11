"""Tests for CoreSettings Pydantic schema."""

import pytest
from pydantic import ValidationError

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)


def test_verbosity_enum_values() -> None:
    """Test Verbosity enum has correct values."""
    assert Verbosity.QUIET == 0
    assert Verbosity.NORMAL == 1
    assert Verbosity.VERBOSE == 2
    assert Verbosity.DEBUG == 3


def test_execution_settings_defaults() -> None:
    """Test ExecutionSettings default values."""
    settings = ExecutionSettings()
    assert settings.parallel is True
    assert settings.strict is True
    assert settings.max_workers == 0


def test_execution_settings_validation() -> None:
    """Test ExecutionSettings validates max_workers."""
    settings = ExecutionSettings(max_workers=4)
    assert settings.max_workers == 4

    # Negative values should fail
    with pytest.raises(ValidationError):
        ExecutionSettings(max_workers=-1)


def test_output_settings_defaults() -> None:
    """Test OutputSettings default values."""
    settings = OutputSettings()
    assert settings.verbosity == Verbosity.NORMAL


def test_output_settings_accepts_int() -> None:
    """Test OutputSettings accepts int for verbosity."""
    settings = OutputSettings(verbosity=2)
    assert settings.verbosity == Verbosity.VERBOSE


def test_processing_settings_defaults() -> None:
    """Test ProcessingSettings defaults to None for temp_dir."""
    settings = ProcessingSettings()
    assert settings.temp_dir is None


def test_processing_settings_converts_string_to_path() -> None:
    """Test ProcessingSettings converts string to Path."""
    settings = ProcessingSettings(temp_dir="/tmp/custom")
    assert settings.temp_dir.as_posix() == "/tmp/custom"


def test_backend_settings_defaults() -> None:
    """Test BackendSettings default binary."""
    settings = BackendSettings()
    assert settings.binary == "magick"


def test_backend_settings_custom_binary() -> None:
    """Test BackendSettings accepts custom binary path."""
    settings = BackendSettings(binary="/usr/local/bin/magick")
    assert settings.binary == "/usr/local/bin/magick"


def test_core_settings_defaults() -> None:
    """Test CoreSettings creates with all defaults."""
    settings = CoreSettings()
    assert settings.version == "1.0"
    assert settings.execution.parallel is True
    assert settings.output.verbosity == Verbosity.NORMAL
    assert settings.processing.temp_dir is None
    assert settings.backend.binary == "magick"


def test_core_settings_from_dict() -> None:
    """Test CoreSettings can be created from dict."""
    data = {
        "execution": {"parallel": False, "max_workers": 4},
        "output": {"verbosity": 2},
        "backend": {"binary": "/usr/bin/magick"},
    }
    settings = CoreSettings(**data)
    assert settings.execution.parallel is False
    assert settings.execution.max_workers == 4
    assert settings.output.verbosity == Verbosity.VERBOSE
    assert settings.backend.binary == "/usr/bin/magick"


def test_core_settings_nested_validation() -> None:
    """Test CoreSettings validates nested settings."""
    with pytest.raises(ValidationError) as exc_info:
        CoreSettings(execution={"max_workers": -5})

    assert "max_workers" in str(exc_info.value)
