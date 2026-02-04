# Layered Effects System Design

**Date:** 2026-02-04
**Status:** Implemented
**Author:** Claude (via brainstorming session)

## Overview

This design introduces a layered configuration system for `effects.yaml`, allowing users to define custom effects at multiple levels (package, project, user) with deep merging behavior. The system mirrors the existing layered-settings architecture and follows the same patterns as the color-scheme project's unified paths and templates package.

## Goals

1. Enable users to define custom effects without modifying package files
2. Support project-specific effect libraries that extend defaults
3. Allow personal effect libraries in user home directory
4. Provide centralized path management for all configuration files
5. Reuse existing layered-settings infrastructure
6. Maintain backward compatibility with existing code

## Architecture

### Package Structure

```
packages/
├── settings/
│   └── src/layered_settings/
│       ├── constants.py        # NEW: Shared constants (APP_NAME, etc.)
│       ├── paths.py            # NEW: Centralized path discovery
│       ├── merger.py           # EXISTING: deep_merge algorithm
│       ├── loader.py           # EXISTING: File loading utilities
│       └── ...
│
└── effects/                    # NEW PACKAGE
    ├── pyproject.toml
    ├── README.md
    └── src/layered_effects/
        ├── __init__.py         # Public API
        ├── loader.py           # Effects discovery and loading
        ├── errors.py           # Effect-specific exceptions
        └── py.typed
```

### Dependency Graph

```
┌─────────────────┐
│  wallpaper-core │
└────────┬────────┘
         │ uses
         ▼
┌─────────────────┐
│ layered-effects │
└────────┬────────┘
         │ depends on
         ▼
┌──────────────────┐
│ layered-settings │ (provides: paths, merger, constants)
└──────────────────┘
```

## Layer Discovery

### Layer Priority (Lowest to Highest)

1. **Package defaults**: `packages/core/src/wallpaper_core/effects/effects.yaml`
2. **Project root**: `{project_root}/effects.yaml`
3. **User config**: `~/.config/wallpaper-effects-generator/effects.yaml`

Higher layers override lower layers via deep merge.

### Discovery Rules

- All existing layers are discovered and merged
- Missing layers are skipped (not an error)
- At least package layer must exist
- Layers are merged in order: package → project → user

## Deep Merge Behavior

### Merge Strategy

Each top-level section of `effects.yaml` is merged independently:

```yaml
# Package layer
version: "1.0"
parameter_types:
  blur_geometry: {...}
  percent: {...}
effects:
  blur: {...}
  brightness: {...}
composites:
  blur-brightness80: {...}
presets:
  dark_blur: {...}

# User layer
version: "1.0"
parameter_types:
  opacity_range: {...}        # Added
effects:
  blur: {...custom...}        # Overridden
  neon: {...}                 # Added
presets:
  dark_blur: {...custom...}   # Overridden

# Merged result
version: "1.0"                # Package version (canonical)
parameter_types:
  blur_geometry: {...}        # From package
  percent: {...}              # From package
  opacity_range: {...}        # From user
effects:
  blur: {...custom...}        # From user (overridden)
  brightness: {...}           # From package
  neon: {...}                 # From user (new)
composites:
  blur-brightness80: {...}    # From package
presets:
  dark_blur: {...custom...}   # From user (overridden)
```

### Deep Merge Rules

- **Dictionaries**: Recursively merge; higher layer wins for conflicts
- **Lists/Arrays**: Replaced entirely (not appended)
- **Scalars**: Replaced entirely
- **Version field**: Package version is canonical (used for validation)

## Constants Module

### File: `packages/settings/src/layered_settings/constants.py`

```python
"""Shared constants for wallpaper-effects-generator."""

APP_NAME = "wallpaper-effects-generator"
"""Application name used for config directory paths."""

SETTINGS_FILENAME = "settings.toml"
"""Standard filename for settings across all layers."""

EFFECTS_FILENAME = "effects.yaml"
"""Standard filename for effects across all layers."""
```

### Usage

This module provides a single source of truth for:
- Application name (used in `~/.config/{APP_NAME}/`)
- Configuration file names
- Shared between settings and effects packages

## Paths Module

### File: `packages/settings/src/layered_settings/paths.py`

```python
"""Centralized path discovery for wallpaper-effects-generator.

This module is the SINGLE SOURCE OF TRUTH for all filesystem paths
used by settings and effects packages.
"""

import os
from pathlib import Path
from layered_settings.constants import (
    APP_NAME,
    SETTINGS_FILENAME,
    EFFECTS_FILENAME,
)

# XDG Base Directory
XDG_CONFIG_HOME = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

# User layer paths
USER_CONFIG_DIR = XDG_CONFIG_HOME / APP_NAME
USER_SETTINGS_FILE = USER_CONFIG_DIR / SETTINGS_FILENAME
USER_EFFECTS_FILE = USER_CONFIG_DIR / EFFECTS_FILENAME

# Project layer path functions
def get_project_settings_file(project_root: Path) -> Path:
    return project_root / SETTINGS_FILENAME

def get_project_effects_file(project_root: Path) -> Path:
    return project_root / EFFECTS_FILENAME
```

### Benefits

- Single source of truth for all paths
- Eliminates hardcoded paths scattered across packages
- Easy to change app name or directory structure
- Shared by both settings and effects systems

## Layered-Effects Package

### Public API

```python
from layered_effects import configure, load_effects

# Configure at application startup
configure(project_root=Path.cwd())

# Load effects configuration (cached)
effects_config = load_effects()  # Returns EffectsConfig instance

# Access merged data
blur_effect = effects_config.effects["blur"]
all_presets = effects_config.presets
```

### Core Implementation

```python
# layered_effects/loader.py
from pathlib import Path
import yaml
from layered_settings.paths import USER_EFFECTS_FILE, get_project_effects_file
from layered_settings.merger import deep_merge
from wallpaper_core.effects.schema import EffectsConfig

class EffectsLoader:
    """Discovers and loads effects.yaml files from all layers."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root

    def discover_layers(self) -> list[Path]:
        """Discover effects.yaml files from all layers.

        Returns:
            List of paths in priority order (lowest to highest).
        """
        layers = []

        # Layer 1: Package defaults
        package_effects = self._get_package_effects_path()
        if package_effects.exists():
            layers.append(package_effects)

        # Layer 2: Project
        if self.project_root is not None:
            project_effects = get_project_effects_file(self.project_root)
            if project_effects.exists():
                layers.append(project_effects)

        # Layer 3: User
        if USER_EFFECTS_FILE.exists():
            layers.append(USER_EFFECTS_FILE)

        return layers

    def load_and_merge(self) -> EffectsConfig:
        """Load all layers and deep merge into validated config.

        Returns:
            Validated EffectsConfig instance.

        Raises:
            EffectsLoadError: If loading fails
            EffectsValidationError: If validation fails
        """
        layers = self.discover_layers()

        if not layers:
            raise EffectsLoadError("No effects.yaml found in any layer")

        # Deep merge all layers
        merged = {}
        for layer_path in layers:
            try:
                data = yaml.safe_load(layer_path.read_text())
                merged = deep_merge(merged, data)
            except Exception as e:
                raise EffectsLoadError(
                    f"Failed to load {layer_path}: {e}"
                ) from e

        # Validate with Pydantic
        try:
            return EffectsConfig(**merged)
        except Exception as e:
            raise EffectsValidationError(
                f"Validation failed for merged effects: {e}"
            ) from e
```

### Error Handling

```python
# layered_effects/errors.py

class EffectsError(Exception):
    """Base exception for effects system."""
    pass

class EffectsLoadError(EffectsError):
    """Raised when effects.yaml cannot be loaded."""
    pass

class EffectsValidationError(EffectsError):
    """Raised when merged effects fail Pydantic validation."""
    pass
```

## Integration with Core Package

### Registration

```python
# packages/core/src/wallpaper_core/__init__.py
from pathlib import Path
from layered_effects import configure

# Auto-configure on import
_project_root = Path.cwd()
configure(project_root=_project_root)
```

### Usage in CLI

```python
# packages/core/src/wallpaper_core/cli/commands.py
from layered_effects import load_effects

def process_effect(input_path, output_path, effect_name):
    # Load merged effects configuration
    effects_config = load_effects()

    # Access effect as before (same EffectsConfig interface)
    effect = effects_config.effects.get(effect_name)
    if not effect:
        raise ValueError(f"Unknown effect: {effect_name}")

    # Process as normal
    ...
```

### Backward Compatibility

- `load_effects()` returns same `EffectsConfig` type as before
- Existing code continues to work without changes
- Enhanced behavior is transparent to consumers

## Testing Strategy

### Unit Tests

```python
# tests/test_loader.py

def test_discovers_package_layer():
    """Should find package effects.yaml."""

def test_discovers_project_layer(tmp_path):
    """Should find project effects.yaml when it exists."""

def test_discovers_user_layer(tmp_path):
    """Should find user effects.yaml when it exists."""

def test_discovers_all_layers(tmp_path):
    """Should find all three layers in correct order."""

def test_deep_merges_effects():
    """Should deep merge effects from all layers."""
    # Package: blur, brightness
    # User: blur (override), neon (new)
    # Result: blur (user), brightness (package), neon (user)

def test_deep_merges_parameter_types():
    """Should deep merge parameter_types."""

def test_deep_merges_composites():
    """Should deep merge composites."""

def test_deep_merges_presets():
    """Should deep merge presets."""

def test_validates_merged_config():
    """Should validate merged result with Pydantic."""

def test_raises_on_invalid_yaml():
    """Should raise clear error for malformed YAML."""

def test_raises_on_validation_failure():
    """Should raise clear error for Pydantic validation failure."""

def test_works_with_only_package_layer():
    """Should work when only package layer exists."""
```

### Integration Tests

```python
# tests/test_integration.py

def test_full_stack_package_to_user():
    """End-to-end test with all three layers."""

def test_cli_uses_merged_effects():
    """Test CLI commands use merged effects."""

def test_user_overrides_package_effect():
    """Test user can override package effect definition."""

def test_user_adds_new_effect():
    """Test user can add new effects not in package."""
```

## Migration Path

### Phase 1: Add Infrastructure (No Breaking Changes)

1. Add `constants.py` to layered-settings
2. Add `paths.py` to layered-settings
3. Create layered-effects package
4. Add tests for new code

### Phase 2: Update Core Package

1. Add dependency on layered-effects
2. Replace direct file loading with `load_effects()`
3. Verify all tests pass

### Phase 3: Documentation

1. Update README with layered effects usage
2. Document how to create user/project effects
3. Add examples of effect customization

## Benefits

1. **User Flexibility**: Users can customize effects without modifying package
2. **Project Isolation**: Different projects can have different effect libraries
3. **Personal Defaults**: Users can maintain personal effect libraries
4. **Centralized Paths**: Single source of truth for all file locations
5. **Code Reuse**: Leverages existing layered-settings infrastructure
6. **Zero Breaking Changes**: Existing code continues to work

## Future Enhancements

- CLI command to show which layer provides each effect
- CLI command to validate user effects.yaml
- Hot-reload effects during development
- Effect composition helpers
- Effect documentation generation from YAML

## References

- Color-scheme unified paths design: `/home/inumaki/Development/color-scheme/docs/plans/2026-02-04-unified-paths-templates-package.md`
- Existing layered-settings package: `packages/settings/`
- Existing effects schema: `packages/core/src/wallpaper_core/effects/schema.py`
