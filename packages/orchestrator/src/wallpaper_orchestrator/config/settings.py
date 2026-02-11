"""Pydantic schemas for orchestrator settings."""

from pydantic import BaseModel, Field, field_validator


class ContainerSettings(BaseModel):
    """Container engine configuration."""

    engine: str = Field(
        default="docker",
        description="Container engine to use (docker or podman)",
    )
    image_name: str = Field(
        default="wallpaper-effects:latest",
        description="Container image name",
    )
    image_registry: str | None = Field(
        default=None,
        description="Registry prefix for container images",
    )

    @field_validator("engine", mode="before")
    @classmethod
    def validate_engine(cls, v: str) -> str:
        """Validate container engine is valid."""
        valid_engines = {"docker", "podman"}
        v_lower = v.lower()
        if v_lower not in valid_engines:
            raise ValueError(
                f"Invalid container engine: {v}. "
                f"Must be one of: {', '.join(sorted(valid_engines))}"
            )
        return v_lower

    @field_validator("image_registry", mode="before")
    @classmethod
    def normalize_registry(cls, v: str | None) -> str | None:
        """Normalize registry by removing trailing slashes."""
        if v:
            return v.rstrip("/")
        return v


class OrchestratorSettings(BaseModel):
    """Root settings for wallpaper_orchestrator."""

    version: str = Field(default="1.0", description="Settings schema version")
    container: ContainerSettings = Field(default_factory=ContainerSettings)
