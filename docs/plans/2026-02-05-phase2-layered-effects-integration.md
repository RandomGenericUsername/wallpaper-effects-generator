# Phase 2: Layered Effects Integration into wallpaper-core

**Date:** 2026-02-05
**Status:** Approved
**Author:** Claude (via brainstorming session)
**Depends on:** Phase 1 (layered-effects infrastructure) - Complete

## Overview

Integrate the layered-effects package into wallpaper-core CLI, replacing the current SchemaRegistry-based effects loading with the 3-layer configuration system (package → project → user). This enables users to define custom effects and override package defaults without modifying package files.

## Goals

1. Replace SchemaRegistry effects loading with layered-effects package
2. Enable 3-layer effects configuration (package/project/user)
3. Provide comprehensive error messages for configuration issues
4. Maintain zero breaking changes for CLI users
5. Pass all existing tests plus 5 new layered effects integration tests

## Architecture

### Current State

- `CoreOnlyConfig` includes both `core: CoreSettings` and `effects: EffectsConfig`
- `SchemaRegistry.register()` loads effects.yaml from package directory
- `get_config()` returns unified config object
- CLI accesses effects via `config_obj.effects`

### New State

- `CoreOnlyConfig` contains **only** `core: CoreSettings` (remove effects field)
- Remove `SchemaRegistry.register()` call for effects in `effects/__init__.py`
- `layered_effects.configure()` initializes the layered system at module level
- `layered_effects.load_effects()` returns `EffectsConfig` directly
- CLI accesses effects from layered-effects, not layered-settings

### Key Principle

Clean separation - settings (TOML) via layered-settings, effects (YAML) via layered-effects.

## Design Decisions

### 1. Integration Approach: Clean Break (A1)

**Decision:** Remove `effects: EffectsConfig` field from `CoreOnlyConfig` entirely.

**Rationale:**
- Pre-1.0 version (v0.x), breaking changes acceptable
- Simpler code with no dual-path complexity
- Comprehensive tests catch issues
- Clear migration path

**Alternatives considered:**
- A2: Keep compatibility period with optional field (rejected - adds complexity)

### 2. Initialization Location: Module-level in main.py

**Decision:** Initialize layered-effects at module level alongside layered-settings.

**Rationale:**
- Consistent with current layered-settings pattern
- Early initialization before any command runs
- Clear centralized app initialization

**Alternatives considered:**
- In main() callback (rejected - later initialization)
- In effects/__init__.py (rejected - scattered initialization)

### 3. Package Effects Path: Helper Function (Option 3)

**Decision:** Add `get_package_effects_file()` helper to effects module.

**Rationale:**
- Encapsulation - effects module owns its data location
- Clean import from caller's perspective
- Flexibility to change implementation without affecting callers
- Self-documenting intent

**Implementation:**
```python
def get_package_effects_file() -> Path:
    """Get the path to the package's default effects.yaml."""
    from importlib import resources
    return Path(resources.files("wallpaper_core.effects") / "effects.yaml")
```

**Alternatives considered:**
- __file__ relative path (rejected - less robust)
- importlib.resources directly in main.py (rejected - less encapsulated)

### 4. Project Root: Always cwd()

**Decision:** Always use `Path.cwd()` for project root, no override option.

**Rationale:**
- Follows conventions (git, npm, etc.)
- Simple - just `cd` to your project
- YAGNI - no evidence users need override

**Alternatives considered:**
- CLI flag --project-root (rejected - adds complexity)
- Environment variable (rejected - not needed)

### 5. Error Handling: Fail Fast with Comprehensive Reports

**Decision:** Exit immediately on configuration errors with detailed, actionable messages.

**Rationale:**
- Clear feedback when configuration is broken
- Prevents silent failures
- Matches behavior of modern CLI tools (eslint, prettier)
- Easy for users to understand and fix issues

**Error message format:**
```
Error: Failed to load effects configuration

Layer: user
File: /home/user/.config/wallpaper-effects-generator/effects.yaml
Problem: Validation error - effect 'my_blur' references undefined parameter type 'blur_radius'

Available parameter types: blur_geometry, percent, opacity_range

Suggestion: Define 'blur_radius' in parameter_types section or use an existing type
```

**Alternatives considered:**
- Fall back to package defaults (rejected - hides errors)
- Partial loading with warnings (rejected - unpredictable behavior)

## Implementation

### File Changes

#### 1. `packages/core/src/wallpaper_core/effects/__init__.py`

**Remove:**
```python
# DELETE lines 20-24:
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_effects_dir / "effects.yaml",
)
```

**Add:**
```python
def get_package_effects_file() -> Path:
    """Get the path to the package's default effects.yaml file.

    Returns:
        Path to effects.yaml in the wallpaper_core.effects package.
    """
    from importlib import resources
    return Path(resources.files("wallpaper_core.effects") / "effects.yaml")
```

**Update exports:**
```python
__all__ = [
    "ChainStep",
    "CompositeEffect",
    "Effect",
    "EffectsConfig",
    "get_package_effects_file",  # NEW
    "ParameterDefinition",
    "ParameterType",
    "Preset",
]
```

#### 2. `packages/core/src/wallpaper_core/cli/main.py`

**Add imports:**
```python
from pathlib import Path
from layered_effects import configure as configure_effects, load_effects
from layered_effects.errors import EffectsError, EffectsLoadError, EffectsValidationError
from wallpaper_core.effects import get_package_effects_file
```

**Update CoreOnlyConfig:**
```python
class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    # REMOVED: effects: EffectsConfig
```

**Update initialization (after line 23):**
```python
# Configure layered_settings for core settings only
configure(CoreOnlyConfig, app_name="wallpaper-effects")

# Configure layered_effects for effects configuration
configure_effects(
    package_effects_file=get_package_effects_file(),
    project_root=Path.cwd()
)
```

**Update main() callback:**
```python
@app.callback()
def main(
    ctx: typer.Context,
    quiet: Annotated[bool, typer.Option("-q", "--quiet")] = False,
    verbose: Annotated[int, typer.Option("-v", "--verbose", count=True)] = 0,
) -> None:
    """Wallpaper Effects Processor - Apply ImageMagick effects to images."""
    # Get core settings from layered_settings
    config_obj = get_config()

    # Get verbosity early for error output
    verbosity = _get_verbosity(quiet, verbose)
    output = RichOutput(verbosity)

    # Load effects configuration with comprehensive error handling
    try:
        effects_config = load_effects()
    except EffectsLoadError as e:
        output.error(f"[bold red]Failed to load effects configuration[/bold red]")
        output.error(f"Layer: {getattr(e, 'layer', 'unknown')}")
        output.error(f"File: {e.file_path}")
        output.error(f"Reason: {e.reason}")
        raise typer.Exit(1)
    except EffectsValidationError as e:
        output.error(f"[bold red]Effects configuration validation failed[/bold red]")
        output.error(f"Layer: {e.layer or 'merged'}")
        output.error(f"Problem: {e.message}")
        output.newline()
        output.error("[dim]Check your effects.yaml for:[/dim]")
        output.error("  • Undefined parameter types referenced in effects")
        output.error("  • Missing required fields (description, command)")
        output.error("  • Invalid YAML syntax")
        raise typer.Exit(1)
    except EffectsError as e:
        output.error(f"[bold red]Effects error:[/bold red] {e}")
        raise typer.Exit(1)

    # Store context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbosity
    ctx.obj["output"] = output
    ctx.obj["config"] = effects_config  # Changed from config_obj.effects
    ctx.obj["settings"] = config_obj.core
```

## Testing Strategy

### Unit Tests: `packages/core/tests/test_effects_integration.py`

**TestPackageEffects:**
- `test_get_package_effects_file_returns_valid_path()` - Verify helper returns valid path
- `test_package_effects_file_is_valid_yaml()` - Verify package effects.yaml is loadable

**TestLayeredEffectsConfiguration:**
- `test_loads_package_defaults_only()` - Work with only package layer
- `test_project_effects_extend_package()` - Project effects add to package
- `test_user_effects_override_package()` - User effects override package
- `test_parameter_types_merge_across_layers()` - Parameter types from all layers available

**TestErrorHandling:**
- `test_invalid_yaml_raises_load_error()` - Invalid YAML raises EffectsLoadError
- `test_validation_error_shows_helpful_message()` - Validation errors have context
- `test_missing_package_effects_fails()` - Fail if package effects missing

### CLI Integration Tests: `packages/core/tests/test_cli_effects_loading.py`

- `test_cli_shows_package_effects()` - CLI shows package defaults
- `test_cli_shows_composites()` - CLI shows composites
- `test_cli_shows_presets()` - CLI shows presets
- `test_cli_error_on_invalid_user_effects()` - CLI shows helpful error

### Integration Tests (Existing)

The test script `tools/dev/test-all-commands.sh` has 5 layered effects tests that should pass:
1. User config custom effect loaded
2. User config effect override applied
3. Project-level effects loaded
4. User custom effect can be processed
5. Project effect can be processed

### Success Criteria

- ✓ All existing core tests pass
- ✓ All 5 layered effects tests in test-all-commands.sh pass (currently failing)
- ✓ New unit tests pass with >95% coverage
- ✓ Users can create custom effects in `~/.config/wallpaper-effects-generator/effects.yaml`
- ✓ Projects can have local `effects.yaml` that extend defaults
- ✓ Error messages are clear and actionable

## Breaking Changes

### For End Users
None - the layered effects system is transparent to CLI usage.

### For Developers/Library Importers
- `CoreOnlyConfig` no longer has `effects` field
- Cannot access effects via `get_config().effects` anymore
- Must use `layered_effects.load_effects()` directly if importing wallpaper-core as a library

## Migration Path

### Implementation Order

1. Add `get_package_effects_file()` helper to effects/__init__.py
2. Update pyproject.toml dependencies (already done in Phase 1)
3. Modify main.py - update imports, CoreOnlyConfig, initialization
4. Remove SchemaRegistry call from effects/__init__.py
5. Add unit tests to verify integration
6. Run integration tests - 5 failing tests should now pass

### Rollback Plan

If issues arise:
- Git revert the changes (single commit or branch)
- SchemaRegistry approach still works in layered-settings
- No data migration needed (YAML files unchanged)

## Benefits

1. **User Flexibility** - Users can customize effects without modifying package
2. **Project Isolation** - Different projects can have different effect libraries
3. **Personal Defaults** - Users maintain personal effect libraries
4. **Clear Errors** - Comprehensive error messages for configuration issues
5. **Clean Architecture** - Separation of concerns between settings and effects
6. **Zero CLI Breaking Changes** - Transparent to end users

## Future Enhancements

- CLI command to show which layer provides each effect (`wallpaper-core show effect blur --verbose`)
- CLI command to validate effects.yaml (`wallpaper-core validate effects`)
- Environment variable to disable user/project layers for debugging
- Hot-reload effects during development

## References

- Phase 1 Design: `docs/plans/2026-02-04-layered-effects-design.md`
- Layered-effects package: `packages/effects/`
- Test script: `tools/dev/test-all-commands.sh`
