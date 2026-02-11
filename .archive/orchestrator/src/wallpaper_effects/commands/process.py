"""Process command - apply effects via container."""

import sys

from wallpaper_effects.config import DEFAULT_BACKEND, OrchestratorConfig
from wallpaper_effects.services import ContainerRunner, ImageBuilder
from wallpaper_effects.utils.passthrough import extract_input_output_from_args
from wallpaper_effects.utils.runtime import get_runtime_engine


def run_process(
    config: OrchestratorConfig,
    args: list[str],
    backend: str | None = None,
) -> int:
    """
    Apply effects to wallpaper via container.

    Args:
        config: Orchestrator configuration
        args: Arguments to pass to core CLI
        backend: Backend to use (default from config)

    Returns:
        Exit code (0 for success)
    """
    backend = backend or config.backend or DEFAULT_BACKEND

    # Extract input/output paths from args
    input_path, output_path, passthrough_args = extract_input_output_from_args(
        args
    )

    if not input_path:
        print("Error: Input path (-i/--input) is required", file=sys.stderr)
        return 1

    if not output_path:
        print("Error: Output path (-o/--output) is required", file=sys.stderr)
        return 1

    # Validate input exists
    input_path = input_path.resolve()
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    # Create container engine
    try:
        engine = get_runtime_engine(config.runtime)
    except Exception as e:
        print(f"Error: Failed to initialize container runtime: {e}")
        return 1

    # Check if image exists, offer to build if not
    builder = ImageBuilder(config, engine)
    if not builder.image_exists(backend):
        print(f"Image for backend '{backend}' not found.")
        print(f"Run 'wallpaper-effects install --backend {backend}' first.")
        return 1

    # Create runner and execute
    runner = ContainerRunner(config, engine)

    try:
        if config.verbose:
            print(f"Processing {input_path} -> {output_path}")
            print(f"Backend: {backend}")
            print(f"Passthrough args: {passthrough_args}")

        output = runner.run_process(
            input_path=input_path,
            output_path=output_path.resolve(),
            passthrough_args=passthrough_args,
            backend=backend,
        )

        if output:
            print(output)

        print(f"✓ Processing complete: {output_path}")
        return 0

    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        if config.debug:
            import traceback

            traceback.print_exc()
        return 1
