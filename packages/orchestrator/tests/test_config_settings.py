"""Tests for OrchestratorSettings Pydantic schema."""

import pytest
from pydantic import ValidationError

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)


def test_container_settings_defaults() -> None:
    """Test ContainerSettings default values."""
    settings = ContainerSettings()
    assert settings.engine == "docker"
    assert settings.image_name == "wallpaper-effects:latest"
    assert settings.image_registry is None


def test_container_settings_validates_engine() -> None:
    """Test ContainerSettings validates engine."""
    # Valid engines
    settings = ContainerSettings(engine="docker")
    assert settings.engine == "docker"

    settings = ContainerSettings(engine="podman")
    assert settings.engine == "podman"

    # Invalid engine
    with pytest.raises(ValidationError) as exc_info:
        ContainerSettings(engine="invalid")

    assert "Invalid container engine" in str(exc_info.value)


def test_container_settings_normalizes_registry() -> None:
    """Test ContainerSettings normalizes registry."""
    settings = ContainerSettings(image_registry="registry.example.com/")
    assert settings.image_registry == "registry.example.com"

    settings = ContainerSettings(image_registry="registry.example.com")
    assert settings.image_registry == "registry.example.com"


def test_orchestrator_settings_defaults() -> None:
    """Test OrchestratorSettings creates with defaults."""
    settings = OrchestratorSettings()
    assert settings.version == "1.0"
    assert settings.container.engine == "docker"
    assert settings.container.image_name == "wallpaper-effects:latest"


def test_orchestrator_settings_from_dict() -> None:
    """Test OrchestratorSettings can be created from dict."""
    data = {
        "container": {
            "engine": "podman",
            "image_registry": "ghcr.io/user",
        }
    }
    settings = OrchestratorSettings(**data)
    assert settings.container.engine == "podman"
    assert settings.container.image_registry == "ghcr.io/user"
