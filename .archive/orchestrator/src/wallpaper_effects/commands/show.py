"""Show command - display available effects and presets."""

import sys

from wallpaper_effects.config import BACKEND_VERSIONS, OrchestratorConfig

# Known effects (mirrors what's in core)
AVAILABLE_EFFECTS = {
    "blur": "Apply Gaussian blur to the image",
    "brightness": "Adjust image brightness",
    "saturation": "Adjust color saturation",
    "vignette": "Add vignette effect (darken edges)",
    "color_overlay": "Apply color overlay with opacity",
    "grayscale": "Convert to grayscale",
    "negate": "Invert colors",
}

# Known presets (mirrors what's in core config)
AVAILABLE_PRESETS = {
    "dark_blur": "Blur with reduced brightness for dark themes",
    "light_blur": "Blur with increased brightness for light themes",
    "dramatic": "High contrast with vignette",
    "muted": "Reduced saturation for subtle backgrounds",
}


def run_show(
    config: OrchestratorConfig,
    what: str,
) -> int:
    """
    Show available effects, presets, or backends.

    Args:
        config: Orchestrator configuration
        what: What to show (effects, presets, backends)

    Returns:
        Exit code (0 for success)
    """
    if what == "effects":
        return _show_effects(config)
    elif what == "presets":
        return _show_presets(config)
    elif what == "backends":
        return _show_backends(config)
    else:
        print(
            f"Unknown option: {what}. "
            "Use 'effects', 'presets', or 'backends'.",
            file=sys.stderr,
        )
        return 1


def _show_effects(config: OrchestratorConfig) -> int:
    """Show available effects."""
    print("Available Effects:")
    print("-" * 50)
    for name, description in AVAILABLE_EFFECTS.items():
        print(f"  {name:15} - {description}")
    print()
    print("Use: wallpaper-effects process -e <effect> [options]")
    return 0


def _show_presets(config: OrchestratorConfig) -> int:
    """Show available presets."""
    print("Available Presets:")
    print("-" * 50)
    for name, description in AVAILABLE_PRESETS.items():
        print(f"  {name:15} - {description}")
    print()
    print("Use: wallpaper-effects process --preset <name>")
    return 0


def _show_backends(config: OrchestratorConfig) -> int:
    """Show available backends."""
    print("Available Backends:")
    print("-" * 50)
    for name, info in BACKEND_VERSIONS.items():
        version = info.get("version", "unknown")
        print(f"  {name:15} - version {version}")
    print()
    print("Use: wallpaper-effects install --backend <name>")
    return 0
