"""Orchestrator configuration management."""

import os
from dataclasses import dataclass
from pathlib import Path

from wallpaper_effects.config.constants import (
    CONTAINER_CPUSET_CPUS,
    CONTAINER_MEMORY_LIMIT,
    CONTAINER_TIMEOUT,
    DEFAULT_BACKEND,
    DEFAULT_BACKENDS,
    DEFAULT_CONFIG_DIR,
    DEFAULT_OUTPUT_DIR,
)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""

    # Runtime configuration
    runtime: str | None = None  # "docker" or "podman", None for auto-detect
    runtime_path: str | None = None  # Custom path to docker/podman binary

    # Backend configuration
    backend: str = DEFAULT_BACKEND  # Default to imagemagick
    backends: list[str] = None  # type: ignore

    # Directory configuration
    output_dir: Path = None  # type: ignore  # Where processed files go
    config_dir: Path = None  # type: ignore  # For user settings

    # Container configuration
    container_timeout: int = CONTAINER_TIMEOUT
    container_memory_limit: str | None = CONTAINER_MEMORY_LIMIT
    container_cpuset_cpus: str | None = CONTAINER_CPUSET_CPUS

    # Logging configuration
    verbose: bool = False
    debug: bool = False

    def __post_init__(self) -> None:
        """Initialize default values after dataclass initialization."""
        if self.backends is None:
            self.backends = DEFAULT_BACKENDS.copy()

        if self.output_dir is None:
            self.output_dir = Path(DEFAULT_OUTPUT_DIR).expanduser()
        else:
            self.output_dir = Path(self.output_dir).expanduser()

        if self.config_dir is None:
            self.config_dir = Path(DEFAULT_CONFIG_DIR).expanduser()
        else:
            self.config_dir = Path(self.config_dir).expanduser()

        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def from_env() -> "OrchestratorConfig":
        """Create config from environment variables."""
        return OrchestratorConfig(
            runtime=os.getenv("WALLPAPER_EFFECTS_RUNTIME"),
            runtime_path=os.getenv("WALLPAPER_EFFECTS_RUNTIME_PATH"),
            backend=os.getenv("WALLPAPER_EFFECTS_BACKEND", DEFAULT_BACKEND),
            output_dir=os.getenv("WALLPAPER_EFFECTS_OUTPUT_DIR"),
            config_dir=os.getenv("WALLPAPER_EFFECTS_CONFIG_DIR"),
            container_timeout=int(
                os.getenv(
                    "WALLPAPER_EFFECTS_CONTAINER_TIMEOUT",
                    str(CONTAINER_TIMEOUT),
                )
            ),
            container_memory_limit=os.getenv(
                "WALLPAPER_EFFECTS_CONTAINER_MEMORY_LIMIT",
                CONTAINER_MEMORY_LIMIT,
            ),
            verbose=os.getenv("WALLPAPER_EFFECTS_VERBOSE", "").lower()
            == "true",
            debug=os.getenv("WALLPAPER_EFFECTS_DEBUG", "").lower() == "true",
        )

    @staticmethod
    def default() -> "OrchestratorConfig":
        """Create default configuration."""
        return OrchestratorConfig()
