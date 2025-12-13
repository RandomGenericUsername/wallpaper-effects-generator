"""Status command - show container and image status."""

from wallpaper_effects.config import DEFAULT_BACKENDS, OrchestratorConfig
from wallpaper_effects.services import ImageBuilder
from wallpaper_effects.utils.runtime import get_runtime_engine


def run_status(config: OrchestratorConfig) -> int:
    """
    Show status of container images and runtime.

    Args:
        config: Orchestrator configuration

    Returns:
        Exit code (0 for success)
    """
    # Detect container runtime
    print("Container Runtime Status")
    print("=" * 50)

    try:
        engine = get_runtime_engine(config.runtime)
        runtime_name = config.runtime or "auto-detected"
        print(f"Runtime: {runtime_name}")

        version = engine.version()
        print(f"Version: {version}")
        print(f"Available: ✓")
    except Exception as e:
        print(f"Runtime: Not available")
        print(f"Error: {e}")
        return 1

    print()
    print("Container Images")
    print("=" * 50)

    builder = ImageBuilder(config, engine)

    for backend in DEFAULT_BACKENDS:
        info = builder.get_image_info(backend)
        if info:
            size_mb = info.get("size", 0) / (1024 * 1024)
            print(f"  {backend:15} ✓ installed")
            print(f"    ID: {info['id'][:12]}")
            print(f"    Size: {size_mb:.1f} MB")
            if info.get("created"):
                print(f"    Created: {info['created']}")
        else:
            print(f"  {backend:15} ✗ not installed")
        print()

    print("Configuration")
    print("=" * 50)
    print(f"  Config dir:  {config.config_dir}")
    print(f"  Output dir:  {config.output_dir}")
    print(f"  Default backend: {config.backend}")
    print(f"  Memory limit: {config.container_memory_limit}")
    print(f"  Timeout: {config.container_timeout}s")

    return 0

