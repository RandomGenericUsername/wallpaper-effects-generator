"""Container manager for orchestrating wallpaper effects processing."""

import subprocess  # nosec: necessary for container management
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
        # Preserve original filename so output paths use correct image stem
        mounts.append(f"{image_path.absolute()}:/input/{image_path.name}:ro")

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
            result = subprocess.run(  # nosec: B603
                [self.engine, "inspect", image_name],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def run_process(
        self,
        command_type: str,
        command_name: str,
        input_path: Path,
        output_dir: Path,
        flat: bool = False,
        additional_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Execute wallpaper-core command inside container.

        Args:
            command_type: Type of command (effect/composite/preset)
            command_name: Name of effect/composite/preset
            input_path: Path to input image on host
            output_dir: Output directory on host
            flat: Use flat output structure
            additional_args: Additional CLI arguments to pass

        Returns:
            CompletedProcess with returncode, stdout, stderr

        Raises:
            RuntimeError: If container image not available
            FileNotFoundError: If input file doesn't exist
        """
        # Validate parameters
        valid_types = {"effect", "composite", "preset"}
        if command_type not in valid_types:
            raise ValueError(
                f"Invalid command_type: {command_type}. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )

        if not command_name:
            raise ValueError("command_name cannot be empty")

        # Validate container image exists
        if not self.is_image_available():
            raise RuntimeError(
                "Container image not found. "
                "Install the image first: wallpaper-process install"
            )

        # Validate input file exists
        if not input_path.exists():
            raise FileNotFoundError(
                f"Input file not found: {input_path}\n"
                "Please check the file path is correct."
            )

        # Ensure output directory exists and is writable by the container user
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            # Make writable by any user so the container's non-root user
            # (wallpaper, UID 1000) can create subdirectories in the mount
            abs_output_dir = output_dir.absolute()
            abs_output_dir.chmod(0o777)
        except PermissionError as e:
            raise PermissionError(
                f"Cannot create output directory: {output_dir}\n"
                "Please check directory permissions."
            ) from e

        # Convert input path to absolute
        abs_input = input_path.absolute()

        # Build volume mounts
        # Preserve original filename so output paths use correct image stem
        input_mount = f"{abs_input}:/input/{input_path.name}:ro"
        output_mount = f"{abs_output_dir}:/output:rw"

        # Build container command
        # Note: ENTRYPOINT in Dockerfile is "wallpaper-core"
        cmd = [
            self.engine,
            "run",
            "--rm",
        ]

        # Rootless podman needs --userns=keep-id for correct
        # UID mapping with host-mounted volumes
        if self.engine == "podman":
            cmd.append("--userns=keep-id")

        cmd.extend(
            [
                "-v",
                input_mount,
                "-v",
                output_mount,
                self.get_image_name(),
                "process",
                command_type,
                f"/input/{input_path.name}",
                f"--{command_type}",
                command_name,
                "-o",
                "/output",
            ]
        )

        # Add --flat flag if requested
        if flat:
            cmd.append("--flat")

        # Add additional arguments if provided
        if additional_args:
            cmd.extend(additional_args)

        # Execute container
        result = subprocess.run(  # nosec: B603
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        return result
