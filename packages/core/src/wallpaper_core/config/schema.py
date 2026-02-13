"""Pydantic schemas for core settings."""

import shutil
from enum import Enum, IntEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ItemType(str, Enum):
    """Type of wallpaper item for output path resolution."""

    EFFECT = "effect"
    COMPOSITE = "composite"
    PRESET = "preset"

    @property
    def subdir_name(self) -> str:
        """Get the plural subdirectory name for this item type."""
        return {
            ItemType.EFFECT: "effects",
            ItemType.COMPOSITE: "composites",
            ItemType.PRESET: "presets",
        }[self]


class Verbosity(IntEnum):
    """Output verbosity levels."""

    QUIET = 0  # Errors only
    NORMAL = 1  # Progress + results
    VERBOSE = 2  # + command details
    DEBUG = 3  # + full command output


class ExecutionSettings(BaseModel):
    """Batch execution settings."""

    parallel: bool = Field(default=True, description="Run batch operations in parallel")
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
        default_factory=lambda: shutil.which("magick")
        or shutil.which("convert")
        or "magick",
        description="Path to ImageMagick binary (auto-detects magick or convert)",
    )


class CoreSettings(BaseModel):
    """Root settings for wallpaper_core."""

    version: str = Field(default="1.0", description="Settings schema version")
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    backend: BackendSettings = Field(default_factory=BackendSettings)
