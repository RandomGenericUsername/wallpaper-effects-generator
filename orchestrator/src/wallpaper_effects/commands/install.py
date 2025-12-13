"""Install command - build container images."""

import sys
from typing import Optional

from wallpaper_effects.config import DEFAULT_BACKENDS, OrchestratorConfig
from wallpaper_effects.services import ImageBuilder
from wallpaper_effects.utils.runtime import get_runtime_engine


def run_install(
    config: OrchestratorConfig,
    backends: Optional[list[str]] = None,
    force: bool = False,
) -> int:
    """
    Build container images for specified backends.

    Args:
        config: Orchestrator configuration
        backends: List of backends to build (default: all)
        force: Force rebuild even if images exist

    Returns:
        Exit code (0 for success)
    """
    backends_to_build = backends or DEFAULT_BACKENDS

    # Create container engine
    try:
        engine = get_runtime_engine(config.runtime)
    except Exception as e:
        print(f"Error: Failed to initialize container runtime: {e}")
        return 1

    # Create image builder
    builder = ImageBuilder(config, engine)

    success_count = 0
    fail_count = 0

    for backend in backends_to_build:
        try:
            print(f"Building image for backend: {backend}")
            image_id = builder.build_backend_image(
                backend=backend,
                force=force,
            )
            print(f"  ✓ Successfully built: {image_id[:12]}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed to build {backend}: {e}", file=sys.stderr)
            fail_count += 1

    print()
    print(f"Build complete: {success_count} succeeded, {fail_count} failed")

    return 0 if fail_count == 0 else 1

