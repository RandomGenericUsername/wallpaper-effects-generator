"""Tests for effects error classes."""

import pytest


def test_effects_error_base():
    """EffectsError should be base exception."""
    from layered_effects.errors import EffectsError

    error = EffectsError("test message")

    assert isinstance(error, Exception)
    assert str(error) == "test message"


def test_effects_load_error():
    """EffectsLoadError should include file path."""
    from layered_effects.errors import EffectsLoadError
    from pathlib import Path

    error = EffectsLoadError(
        file_path=Path("/path/to/effects.yaml"),
        reason="file not found"
    )

    assert "effects.yaml" in str(error)
    assert "file not found" in str(error)


def test_effects_validation_error():
    """EffectsValidationError should include validation details."""
    from layered_effects.errors import EffectsValidationError

    error = EffectsValidationError(
        message="Invalid effect definition",
        layer="user",
    )

    assert "Invalid effect definition" in str(error)
    assert "user" in str(error)
