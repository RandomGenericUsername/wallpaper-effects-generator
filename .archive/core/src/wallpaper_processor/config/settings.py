"""Pydantic models for settings.yaml schema."""

from __future__ import annotations

from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, Field


class Verbosity(IntEnum):
    """Verbosity levels for output."""

    QUIET = 0  # Errors only
    NORMAL = 1  # Progress + results
    VERBOSE = 2  # + command details
    DEBUG = 3  # + full command output


class ExecutionSettings(BaseModel):
    """Execution-related settings."""

    parallel: bool = Field(
        default=True, description="Run batch operations in parallel"
    )
    strict: bool = Field(default=True, description="Abort on first failure")
    max_workers: int = Field(
        default=0,
        description="Max parallel workers (0 = auto, based on CPU count)",
    )


class OutputSettings(BaseModel):
    """Output-related settings."""

    verbosity: Verbosity = Field(
        default=Verbosity.NORMAL, description="Output verbosity"
    )
    format: str = Field(
        default="preserve",
        description="Output format: preserve, jpg, png, webp",
    )
    quality: int = Field(
        default=90, ge=1, le=100, description="JPEG/WebP quality"
    )


class PathSettings(BaseModel):
    """Path-related settings."""

    effects_config: Path | None = Field(
        default=None, description="Custom effects.yaml path"
    )
    user_effects_dir: Path | None = Field(
        default=None, description="Directory for user-defined effects"
    )


class Settings(BaseModel):
    """Root settings configuration."""

    version: str = Field(default="1.0", description="Settings schema version")
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    paths: PathSettings = Field(default_factory=PathSettings)

    @classmethod
    def default(cls) -> Settings:
        """Create settings with all defaults."""
        return cls()
