"""Tests for config settings models."""

import pytest
from wallpaper_processor.config.settings import (
    ExecutionSettings,
    OutputSettings,
    PathSettings,
    Settings,
    Verbosity,
)


class TestVerbosity:
    """Tests for Verbosity enum."""

    def test_values(self) -> None:
        """Test verbosity level values."""
        assert Verbosity.QUIET == 0
        assert Verbosity.NORMAL == 1
        assert Verbosity.VERBOSE == 2
        assert Verbosity.DEBUG == 3

    def test_comparison(self) -> None:
        """Test verbosity level comparisons."""
        assert Verbosity.QUIET < Verbosity.NORMAL
        assert Verbosity.NORMAL < Verbosity.VERBOSE
        assert Verbosity.VERBOSE < Verbosity.DEBUG
        assert Verbosity.DEBUG >= Verbosity.VERBOSE


class TestExecutionSettings:
    """Tests for ExecutionSettings model."""

    def test_defaults(self) -> None:
        """Test default execution settings."""
        settings = ExecutionSettings()
        assert settings.parallel is True
        assert settings.strict is True
        assert settings.max_workers == 0

    def test_custom_values(self) -> None:
        """Test custom execution settings."""
        settings = ExecutionSettings(
            parallel=False,
            strict=False,
            max_workers=4,
        )
        assert settings.parallel is False
        assert settings.strict is False
        assert settings.max_workers == 4


class TestOutputSettings:
    """Tests for OutputSettings model."""

    def test_defaults(self) -> None:
        """Test default output settings."""
        settings = OutputSettings()
        assert settings.verbosity == Verbosity.NORMAL
        assert settings.format == "preserve"
        assert settings.quality == 90

    def test_custom_values(self) -> None:
        """Test custom output settings."""
        settings = OutputSettings(
            verbosity=Verbosity.DEBUG,
            format="jpg",
            quality=85,
        )
        assert settings.verbosity == Verbosity.DEBUG
        assert settings.format == "jpg"
        assert settings.quality == 85

    def test_quality_bounds(self) -> None:
        """Test quality validation."""
        # Valid range
        settings = OutputSettings(quality=1)
        assert settings.quality == 1
        settings = OutputSettings(quality=100)
        assert settings.quality == 100

        # Invalid range should raise
        with pytest.raises(Exception):
            OutputSettings(quality=0)
        with pytest.raises(Exception):
            OutputSettings(quality=101)


class TestPathSettings:
    """Tests for PathSettings model."""

    def test_defaults(self) -> None:
        """Test default path settings."""
        settings = PathSettings()
        assert settings.effects_config is None
        assert settings.user_effects_dir is None


class TestSettings:
    """Tests for Settings model."""

    def test_defaults(self) -> None:
        """Test default settings."""
        settings = Settings.default()
        assert settings.version == "1.0"
        assert settings.execution.parallel is True
        assert settings.output.verbosity == Verbosity.NORMAL
        assert settings.paths.effects_config is None

    def test_custom_settings(self, custom_settings: Settings) -> None:
        """Test custom settings from fixture."""
        assert custom_settings.execution.parallel is False
        assert custom_settings.execution.strict is False
        assert custom_settings.output.verbosity == Verbosity.VERBOSE
        assert custom_settings.output.format == "jpg"

    def test_from_dict(self) -> None:
        """Test creating settings from dictionary (like YAML load)."""
        data = {
            "version": "1.0",
            "execution": {
                "parallel": False,
                "strict": True,
            },
            "output": {
                "verbosity": 2,  # VERBOSE
                "quality": 80,
            },
        }
        settings = Settings(**data)
        assert settings.execution.parallel is False
        assert settings.execution.strict is True
        assert settings.output.verbosity == Verbosity.VERBOSE
        assert settings.output.quality == 80

    def test_nested_defaults(self) -> None:
        """Test that nested models get defaults when not specified."""
        settings = Settings()
        assert settings.execution is not None
        assert settings.output is not None
        assert settings.paths is not None
