"""Argument passthrough utilities for delegating to core tool."""

from pathlib import Path
from typing import Any, Optional

from container_manager import VolumeMount


def parse_core_arguments(args: list[str]) -> tuple[str, list[str]]:
    """
    Parse arguments to separate command from flags.

    Args:
        args: Command line arguments (without program name)

    Returns:
        Tuple of (command, remaining_args)

    Raises:
        ValueError: If no valid command is found
    """
    valid_commands = {"install", "process", "show", "status"}

    if not args:
        raise ValueError(
            "No command specified. Use 'install', 'process', 'show', or 'status'"
        )

    command = args[0] if args[0] in valid_commands else None

    if not command:
        raise ValueError(
            f"Invalid command: {args[0]}. "
            f"Must be one of: {', '.join(valid_commands)}"
        )

    return command, args[1:]


def build_passthrough_command(
    additional_args: list[str],
) -> list[str]:
    """
    Build the complete command to pass to core tool inside container.

    Args:
        additional_args: Additional arguments to pass through

    Returns:
        Complete command list for container execution

    Note:
        The Docker images have ENTRYPOINT set to wallpaper-effects-process,
        so we only need to pass the arguments.
    """
    return additional_args


def format_volume_mount(
    source: Path,
    target: str,
    read_only: bool = False,
) -> VolumeMount:
    """
    Create a VolumeMount from source and target paths.

    Args:
        source: Host path
        target: Container path
        read_only: Whether mount should be read-only

    Returns:
        VolumeMount instance for container-manager
    """
    return VolumeMount(
        source=str(source),
        target=target,
        read_only=read_only,
    )


def get_backend_dockerfile(backend_name: str) -> Path:
    """
    Get the path to the Dockerfile for a backend.

    Args:
        backend_name: Name of the backend (imagemagick, pil)

    Returns:
        Path to the Dockerfile

    Raises:
        ValueError: If backend is not recognized
    """
    valid_backends = {"imagemagick", "pil"}

    if backend_name not in valid_backends:
        raise ValueError(
            f"Unknown backend: {backend_name}. "
            f"Must be one of: {', '.join(valid_backends)}"
        )

    # Get the orchestrator's docker directory
    # Path: src/wallpaper_effects/utils/passthrough.py -> go up 4 levels
    orchestrator_dir = Path(__file__).parent.parent.parent.parent
    dockerfile = orchestrator_dir / "docker" / f"Dockerfile.{backend_name}"

    if not dockerfile.exists():
        raise FileNotFoundError(f"Dockerfile not found: {dockerfile}")

    return dockerfile


def extract_backend_from_args(args: list[str]) -> Optional[str]:
    """
    Extract backend name from arguments if specified.

    Args:
        args: Parsed arguments from the user

    Returns:
        Backend name if specified, None otherwise
    """
    for i, arg in enumerate(args):
        if arg in ("--backend", "-b"):
            if i + 1 < len(args):
                return args[i + 1]
        elif arg.startswith("--backend="):
            return arg.split("=", 1)[1]

    return None


def extract_input_output_from_args(
    args: list[str],
) -> tuple[Optional[Path], Optional[Path], list[str]]:
    """
    Extract input and output paths from arguments.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (input_path, output_path, remaining_args)
    """
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    remaining: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("-i", "--input"):
            if i + 1 < len(args):
                input_path = Path(args[i + 1])
                i += 2
            else:
                i += 1
        elif arg.startswith("--input="):
            input_path = Path(arg.split("=", 1)[1])
            i += 1
        elif arg in ("-o", "--output"):
            if i + 1 < len(args):
                output_path = Path(args[i + 1])
                i += 2
            else:
                i += 1
        elif arg.startswith("--output="):
            output_path = Path(arg.split("=", 1)[1])
            i += 1
        else:
            remaining.append(arg)
            i += 1

    return input_path, output_path, remaining


def filter_orchestrator_args(
    args: list[str],
) -> tuple[dict[str, Any], list[str]]:
    """
    Filter out orchestrator-specific arguments from user arguments.

    Orchestrator-specific arguments are those that control the orchestrator
    behavior (e.g., --runtime, --backend) rather than passed to core.

    Args:
        args: All arguments provided

    Returns:
        Tuple of (orchestrator_args, core_passthrough_args)
    """
    orchestrator_args: dict[str, Any] = {}
    core_args: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]

        # Orchestrator-specific flags
        if arg == "--runtime":
            if i + 1 < len(args):
                orchestrator_args["runtime"] = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg.startswith("--runtime="):
            orchestrator_args["runtime"] = arg.split("=", 1)[1]
            i += 1
        elif arg in ("--backend", "-b"):
            if i + 1 < len(args):
                orchestrator_args["backend"] = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg.startswith("--backend="):
            orchestrator_args["backend"] = arg.split("=", 1)[1]
            i += 1
        elif arg == "--output-dir":
            if i + 1 < len(args):
                orchestrator_args["output_dir"] = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg.startswith("--output-dir="):
            orchestrator_args["output_dir"] = arg.split("=", 1)[1]
            i += 1
        elif arg == "--config-dir":
            if i + 1 < len(args):
                orchestrator_args["config_dir"] = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg.startswith("--config-dir="):
            orchestrator_args["config_dir"] = arg.split("=", 1)[1]
            i += 1
        elif arg in ("--verbose", "-v"):
            orchestrator_args["verbose"] = True
            i += 1
        elif arg in ("--debug", "-d"):
            orchestrator_args["debug"] = True
            i += 1
        else:
            # Pass through to core
            core_args.append(arg)
            i += 1

    return orchestrator_args, core_args

