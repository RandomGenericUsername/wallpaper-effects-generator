"""Container manager for orchestrating wallpaper effects processing."""

import subprocess
from pathlib import Path

from wallpaper_orchestrator.config.unified import UnifiedConfig


class ContainerManager:
    """Manages container lifecycle for wallpaper effects processing.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (build, inspect, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, config: UnifiedConfig):
        """Initialize container manager.

        Args:
            config: Unified application configuration
        """
        self.config: UnifiedConfig = config
        self.engine: str = config.orchestrator.container.engine

    def get_image_name(self) -> str:
        """Get full image name.

        Returns:
            Full image name (with registry if configured)
        """
        image_name = self.config.orchestrator.container.image_name

        # Add registry prefix if configured
        if self.config.orchestrator.container.image_registry:
            registry = self.config.orchestrator.container.image_registry
            image_name = f"{registry}/{image_name}"

        return image_name

    def build_volume_mounts(
        self,
        image_path: Path,
        output_dir: Path,
    ) -> list[str]:
        """Build volume mount specifications for container.

        Args:
            image_path: Path to source image on host
            output_dir: Path to output directory on host

        Returns:
            List of volume mount strings in Docker -v format
        """
        mounts = []

        # Input image file (read-only)
        mounts.append(f"{image_path.absolute()}:/input/image.png:ro")

        # Output directory (read-write)
        mounts.append(f"{output_dir.absolute()}:/output:rw")

        return mounts

    def is_image_available(self) -> bool:
        """Check if container image exists.

        Returns:
            True if image exists, False otherwise
        """
        image_name = self.get_image_name()

        try:
            result = subprocess.run(
                [self.engine, "inspect", image_name],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
