"""Project-level UnifiedConfig composing all schemas."""

from typing import Any

from layered_settings import SchemaRegistry
from layered_settings.loader import FileLoader
from pydantic import BaseModel, ConfigDict, Field
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig

from wallpaper_orchestrator.config.settings import OrchestratorSettings


def _load_effects_defaults() -> EffectsConfig:
    """Load EffectsConfig from registered defaults file.

    This is needed because EffectsConfig requires a version field
    and cannot be instantiated with no arguments.
    """
    # Ensure effects schema is registered (trigger import)
    import wallpaper_core.effects  # noqa: F401

    reg = SchemaRegistry.get("effects")
    if reg is None or reg.defaults_file is None:
        # Fallback to minimal valid config if not registered
        return EffectsConfig(version="1.0")

    data: dict[str, Any] = FileLoader.load(reg.defaults_file)
    return EffectsConfig(**data)


class UnifiedConfig(BaseModel):
    """Root configuration composing all registered namespaces.

    Access pattern:
        config.core.execution.parallel
        config.core.backend.binary
        config.effects.effects["blur"]
        config.orchestrator.container.engine
    """

    model_config = ConfigDict(frozen=True)

    core: CoreSettings = Field(default_factory=CoreSettings)
    effects: EffectsConfig = Field(default_factory=_load_effects_defaults)
    orchestrator: OrchestratorSettings = Field(
        default_factory=OrchestratorSettings
    )
