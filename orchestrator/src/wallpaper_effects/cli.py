"""CLI interface for wallpaper effects orchestrator."""

import sys
from typing import NoReturn

from wallpaper_effects.commands import run_install, run_process, run_show, run_status
from wallpaper_effects.config import OrchestratorConfig
from wallpaper_effects.utils.passthrough import (
    filter_orchestrator_args,
    parse_core_arguments,
)


USAGE = """
Wallpaper Effects Orchestrator - Apply effects to wallpapers via containers

Usage:
  wallpaper-effects <command> [options]

Commands:
  install     Build container images for backends
  process     Apply effects to a wallpaper
  show        Show available effects, presets, or backends
  status      Show container and image status

Options:
  --runtime <docker|podman>   Container runtime to use
  --backend <name>            Backend to use (imagemagick, pil)
  --verbose, -v               Enable verbose output
  --debug, -d                 Enable debug output
  --help, -h                  Show this help message

Examples:
  # Install container images
  wallpaper-effects install
  wallpaper-effects install --backend imagemagick

  # Apply effects
  wallpaper-effects process -i input.jpg -o output.jpg -e blur --sigma 8
  wallpaper-effects process -i input.jpg -o output.jpg --preset dark_blur

  # Show available options
  wallpaper-effects show effects
  wallpaper-effects show presets
  wallpaper-effects show backends

  # Check status
  wallpaper-effects status
"""


def print_usage() -> NoReturn:
    """Print usage and exit."""
    print(USAGE)
    sys.exit(0)


def main() -> None:
    """Main CLI entry point."""
    args = sys.argv[1:]

    # Handle help
    if not args or args[0] in ("--help", "-h", "help"):
        print_usage()

    # Parse command
    try:
        command, remaining_args = parse_core_arguments(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter orchestrator args from passthrough args
    orchestrator_args, core_args = filter_orchestrator_args(remaining_args)

    # Build config
    config = OrchestratorConfig(
        runtime=orchestrator_args.get("runtime"),
        backend=orchestrator_args.get("backend", "imagemagick"),
        output_dir=orchestrator_args.get("output_dir"),
        config_dir=orchestrator_args.get("config_dir"),
        verbose=orchestrator_args.get("verbose", False),
        debug=orchestrator_args.get("debug", False),
    )

    # Execute command
    if command == "install":
        # Parse install-specific args
        force = "--force" in core_args or "-f" in core_args
        backends = None

        # Extract --backend from core_args if present
        backend = orchestrator_args.get("backend")
        if backend:
            backends = [backend]

        exit_code = run_install(config, backends=backends, force=force)

    elif command == "process":
        exit_code = run_process(
            config,
            args=core_args,
            backend=orchestrator_args.get("backend"),
        )

    elif command == "show":
        # Determine what to show
        if not core_args:
            print("Usage: wallpaper-effects show <effects|presets|backends>")
            sys.exit(1)
        what = core_args[0]
        exit_code = run_show(config, what)

    elif command == "status":
        exit_code = run_status(config)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_usage()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

