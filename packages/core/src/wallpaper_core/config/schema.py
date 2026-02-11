"""Pydantic schemas for core settings."""

from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class Verbosity(IntEnum):
    """Output verbosity levels."""

    QUIET = 0  # Errors only
    NORMAL = 1  # Progress + results
    VERBOSE = 2  # + command details
    DEBUG = 3  # + full command output


class ExecutionSettings(BaseModel):
    """Batch execution settings."""

    parallel: bool = Field(
        default=True, description="Run batch operations in parallel"
    )
    strict: bool = Field(default=True, description="Abort on first failure")
    max_workers: int = Field(
        default=0,
        description="Max parallel workers (0=auto based on CPU count)",
        ge=0,
    )


class OutputSettings(BaseModel):
    """Output and display settings."""

    verbosity: Verbosity = Field(
        default=Verbosity.NORMAL, description="Output verbosity level"
    )


class ProcessingSettings(BaseModel):
    """Processing behavior settings."""

    temp_dir: Path | None = Field(
        default=None,
        description="Temp directory for intermediate files (None=system default)",
    )

    @field_validator("temp_dir", mode="before")
    @classmethod
    def convert_str_to_path(cls, v: str | Path | None) -> Path | None:
        """Convert string to Path if needed."""
        if v is None or isinstance(v, Path):
            return v
        return Path(v)


class BackendSettings(BaseModel):
    """ImageMagick backend settings."""

    binary: str = Field(
        default="magick", description="Path to ImageMagick binary"
    )


class CoreSettings(BaseModel):
    """Root settings for wallpaper_core."""

    version: str = Field(default="1.0", description="Settings schema version")
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    backend: BackendSettings = Field(default_factory=BackendSettings)
