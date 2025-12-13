"""Container runner service for executing effects in containers."""

from pathlib import Path

from container_manager import ContainerEngine, RunConfig, VolumeMount

from wallpaper_effects.config import (
    CONTAINER_CONFIG_DIR,
    CONTAINER_INPUT_DIR,
    CONTAINER_OUTPUT_DIR,
    OrchestratorConfig,
)


class ContainerRunner:
    """Runs wallpaper effects processing in containers."""

    def __init__(
        self,
        config: OrchestratorConfig,
        engine: ContainerEngine,
    ):
        """
        Initialize the container runner.

        Args:
            config: Orchestrator configuration
            engine: Container engine instance
        """
        self.config = config
        self.engine = engine

    def run_process(
        self,
        input_path: Path,
        output_path: Path,
        passthrough_args: list[str],
        backend: str = "imagemagick",
    ) -> str:
        """
        Run effect processing in container.

        Args:
            input_path: Path to input image on host
            output_path: Path for output image on host
            passthrough_args: Arguments to pass to core CLI
            backend: Backend to use (imagemagick, pil)

        Returns:
            Container output/logs

        Raises:
            ContainerError: If container execution fails
        """
        # Resolve paths to absolute
        input_path = input_path.resolve()
        output_path = output_path.resolve()

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build volume mounts
        volumes = self._prepare_volume_mounts(input_path, output_path)

        # Translate paths for container
        container_input = f"{CONTAINER_INPUT_DIR}/{input_path.name}"
        container_output = f"{CONTAINER_OUTPUT_DIR}/{output_path.name}"

        # Build command with translated paths
        command = self._build_command(
            container_input,
            container_output,
            passthrough_args,
        )

        if self.config.verbose:
            print(f"Running container with command: {' '.join(command)}")

        # Create run configuration
        run_config = RunConfig(
            image=f"wallpaper-effects-{backend}:latest",
            command=command,
            volumes=volumes,
            remove=True,
            detach=False,
            memory_limit=self.config.container_memory_limit,
            working_dir="/workspace",
        )

        # Run the container
        # When detach=False, run() returns stdout directly
        output = self.engine.containers.run(run_config)

        return output

    def _prepare_volume_mounts(
        self,
        input_path: Path,
        output_path: Path,
    ) -> list[VolumeMount]:
        """
        Prepare volume mounts for container.

        Args:
            input_path: Absolute path to input image
            output_path: Absolute path for output image

        Returns:
            List of VolumeMount objects
        """
        volumes = []

        # Mount input image (read-only)
        volumes.append(
            VolumeMount(
                source=str(input_path),
                target=f"{CONTAINER_INPUT_DIR}/{input_path.name}",
                read_only=True,
            )
        )

        # Mount output directory (read-write)
        volumes.append(
            VolumeMount(
                source=str(output_path.parent),
                target=CONTAINER_OUTPUT_DIR,
                read_only=False,
            )
        )

        # Mount config directory if it exists (read-only)
        if self.config.config_dir.exists():
            volumes.append(
                VolumeMount(
                    source=str(self.config.config_dir),
                    target=CONTAINER_CONFIG_DIR,
                    read_only=True,
                )
            )

        return volumes

    def _build_command(
        self,
        container_input: str,
        container_output: str,
        passthrough_args: list[str],
    ) -> list[str]:
        """
        Build command for container execution.

        Args:
            container_input: Input path inside container
            container_output: Output path inside container
            passthrough_args: Additional arguments to pass through

        Returns:
            Command list for container
        """
        # The entrypoint is wallpaper-effects-process, so we just need args
        command = [
            "-i", container_input,
            "-o", container_output,
        ]
        command.extend(passthrough_args)
        return command

