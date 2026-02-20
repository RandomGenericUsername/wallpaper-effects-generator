"""Tests for UnifiedConfig composition."""

import shutil

from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_orchestrator.config.settings import OrchestratorSettings
from wallpaper_orchestrator.config.unified import UnifiedConfig


def test_unified_config_defaults() -> None:
    """Test UnifiedConfig creates with all defaults."""
    config = UnifiedConfig()

    assert isinstance(config.core, CoreSettings)
    assert isinstance(config.effects, EffectsConfig)
    assert isinstance(config.orchestrator, OrchestratorSettings)


def test_unified_config_access_core() -> None:
    """Test accessing core settings through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.core.execution.parallel is True
    # Should auto-detect either magick (v7) or convert (v6)
    expected = shutil.which("magick") or shutil.which("convert") or "magick"
    assert config.core.backend.binary == expected
    assert config.core.output.verbosity.name == "NORMAL"


def test_unified_config_access_effects() -> None:
    """Test accessing effects config through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.effects.version == "1.0"
    assert isinstance(config.effects.effects, dict)


def test_unified_config_access_orchestrator() -> None:
    """Test accessing orchestrator settings through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.orchestrator.container.engine == "docker"
    assert config.orchestrator.container.image_name == "wallpaper-effects:latest"


def test_unified_config_from_dict() -> None:
    """Test UnifiedConfig from merged dictionaries."""
    data = {
        "core": {
            "execution": {"parallel": False},
        },
        "orchestrator": {
            "container": {"engine": "podman"},
        },
    }

    config = UnifiedConfig(**data)

    assert config.core.execution.parallel is False
    assert config.orchestrator.container.engine == "podman"


def test_unified_config_is_frozen() -> None:
    """Test UnifiedConfig is immutable after creation."""
    config = UnifiedConfig()

    # Config should be frozen (immutable)
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        config.core = CoreSettings()  # type: ignore
