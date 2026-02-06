"""Project-level UnifiedConfig composing all schemas."""

from layered_effects import load_effects
from pydantic import BaseModel, ConfigDict, Field
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig

from wallpaper_orchestrator.config.settings import OrchestratorSettings


def _load_effects_defaults() -> EffectsConfig:
    """Load EffectsConfig via layered-effects system.

    Uses the layered-effects package to load and merge effects
    from package, project, and user layers.
    """
    return load_effects()


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
