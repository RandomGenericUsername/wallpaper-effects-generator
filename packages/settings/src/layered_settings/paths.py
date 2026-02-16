"""Centralized path discovery for wallpaper-effects-generator.

This module is the SINGLE SOURCE OF TRUTH for all filesystem paths
used by the settings and effects packages.

Environment Variables:
    XDG_CONFIG_HOME: Base config directory (default: ~/.config)

Layer Structure:
    Both settings and effects follow the same 3-layer structure:
    1. Package defaults (lowest priority)
    2. Project-level configuration
    3. User-level configuration (highest priority)
"""

import os
from pathlib import Path

from layered_settings.constants import APP_NAME, EFFECTS_FILENAME, SETTINGS_FILENAME


# =============================================================================
# XDG Base Directory Specification
# =============================================================================

XDG_CONFIG_HOME = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
"""XDG config home directory. Respects XDG_CONFIG_HOME environment variable."""

# =============================================================================
# User Layer Paths
# =============================================================================

USER_CONFIG_DIR = XDG_CONFIG_HOME / APP_NAME
"""User's config directory: ~/.config/wallpaper-effects-generator/"""

USER_SETTINGS_FILE = USER_CONFIG_DIR / SETTINGS_FILENAME
"""User's settings file: ~/.config/wallpaper-effects-generator/settings.toml"""

USER_EFFECTS_FILE = USER_CONFIG_DIR / EFFECTS_FILENAME
"""User's effects file: ~/.config/wallpaper-effects-generator/effects.yaml"""

# =============================================================================
# Project Layer Path Functions
# =============================================================================


def get_project_settings_file(project_root: Path) -> Path:
    """Get the settings file path for a project.

    Args:
        project_root: Root directory of the project.

    Returns:
        Path to {project_root}/settings.toml
    """
    return project_root / SETTINGS_FILENAME


def get_project_effects_file(project_root: Path) -> Path:
    """Get the effects file path for a project.

    Args:
        project_root: Root directory of the project.

    Returns:
        Path to {project_root}/effects.yaml
    """
    return project_root / EFFECTS_FILENAME
