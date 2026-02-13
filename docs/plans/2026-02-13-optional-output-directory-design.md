# Optional Output Directory - Design Document

**Date:** 2026-02-13
**Status:** Approved
**Breaking Change:** Yes

## Overview

Standardize output behavior across all commands by making the output directory optional with configurable defaults from layered settings. This eliminates inconsistency between process and batch commands and enables users to run commands without specifying output locations.

## Current State

**Process commands** require explicit output file path:
```bash
wallpaper-core process effect input.jpg /tmp/output.jpg --effect blur
```

**Batch commands** require explicit output directory:
```bash
wallpaper-core batch effects input.jpg /tmp/output
```

**Problems:**
1. Inconsistent: process takes file path, batch takes directory
2. Always mandatory - cannot omit output
3. No default location configured
4. Process output structure differs from batch

## Desired State

**All commands** use optional output directory with standardized structure:

```bash
# Use default from settings:
wallpaper-core process effect input.jpg --effect blur
→ ./wallpapers-output/input/effects/blur.jpg

# Specify custom output:
wallpaper-core process effect input.jpg -o /custom/out --effect blur
→ /custom/out/input/effects/blur.jpg

# Use flat structure:
wallpaper-core process effect input.jpg -o /out --effect blur --flat
→ /out/input/blur.jpg

# Same for batch:
wallpaper-core batch effects input.jpg
→ ./wallpapers-output/input/effects/...

wallpaper-core batch effects input.jpg -o /out --flat
→ /out/input/...
```

**Benefits:**
- ✅ Consistent behavior across all commands
- ✅ Optional output (uses configured default)
- ✅ Organized output structure
- ✅ Respects layered settings architecture
- ✅ No new architecture - wires to existing system

## Architecture

### Settings Schema

**Add to OutputSettings** (`packages/core/src/wallpaper_core/config/schema.py`):

```python
from enum import Enum

class ItemType(str, Enum):
    """Type of wallpaper item for output path resolution."""

    EFFECT = "effect"
    COMPOSITE = "composite"
    PRESET = "preset"

    @property
    def subdir_name(self) -> str:
        """Get the plural subdirectory name for this item type."""
        return {
            ItemType.EFFECT: "effects",
            ItemType.COMPOSITE: "composites",
            ItemType.PRESET: "presets",
        }[self]


class OutputSettings(BaseModel):
    """Output and display settings."""

    verbosity: Verbosity = Field(
        default=Verbosity.NORMAL, description="Output verbosity level"
    )

    default_dir: Path = Field(
        default=Path("./wallpapers-output"),
        description="Default output directory when -o/--output-dir not specified",
    )

    @field_validator("default_dir", mode="before")
    @classmethod
    def convert_str_to_path(cls, v: str | Path) -> Path:
        """Convert string to Path if needed."""
        if isinstance(v, Path):
            return v
        return Path(v)
```

**Package Default** (`packages/core/src/wallpaper_core/config/settings.toml`):

```toml
[output]
verbosity = 1
default_dir = "./wallpapers-output"
```

**Layered Settings Priority:**
1. CLI flag `-o/--output-dir` (highest)
2. User config `~/.config/wallpaper-effects-generator/settings.toml`
3. Project config `./settings.toml`
4. Package default `./wallpapers-output` (lowest)

### CLI Signatures

**Process Commands** - Change from file to directory:

```python
# BEFORE (DELETE):
def apply_effect(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(...)],
    output_file: Annotated[Path, typer.Argument(...)],  # ❌ DELETE
    effect: Annotated[str, typer.Option("-e", "--effect", ...)],
    dry_run: bool = False,
) -> None:

# AFTER (NEW):
def apply_effect(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(...)],
    output_dir: Annotated[
        Path | None,
        typer.Option("-o", "--output-dir", help="Output directory (uses settings default if not specified)")
    ] = None,
    effect: Annotated[str, typer.Option("-e", "--effect", ...)],
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: bool = False,
) -> None:
    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    # Build output path
    output_file = resolve_output_path(
        output_dir=output_dir,
        input_file=input_file,
        item_name=effect,
        item_type=ItemType.EFFECT,
        flat=flat,
    )

    # Execute (rest unchanged)
    executor.execute(effect_def.command, input_file, output_file, final_params)
```

**Apply same pattern to:**
- `apply_composite()` → ItemType.COMPOSITE
- `apply_preset()` → ItemType.PRESET

**Batch Commands** - Make output_dir optional:

```python
# BEFORE:
def batch_effects(
    ctx: typer.Context,
    input_file: Path,
    output_dir: Path,  # Was required positional
    ...
)

# AFTER:
def batch_effects(
    ctx: typer.Context,
    input_file: Path,
    output_dir: Annotated[
        Path | None,
        typer.Option("-o", "--output-dir", ...)
    ] = None,
    ...
):
    settings: CoreSettings = ctx.obj["settings"]

    if output_dir is None:
        output_dir = settings.output.default_dir

    # Rest unchanged
```

**Apply to all batch commands:**
- `batch_effects()`
- `batch_composites()`
- `batch_presets()`
- `batch_all()`

**Orchestrator commands** - Same pattern for all `wallpaper-process` commands.

### Output Path Resolution

**New helper function** (add to `packages/core/src/wallpaper_core/cli/process.py`):

```python
def resolve_output_path(
    output_dir: Path,
    input_file: Path,
    item_name: str,
    item_type: ItemType,
    flat: bool = False,
) -> Path:
    """Resolve output file path using standardized structure.

    Args:
        output_dir: Base output directory
        input_file: Input image file
        item_name: Name of effect/composite/preset
        item_type: Type of item (ItemType enum)
        flat: If True, skip type subdirectory

    Returns:
        Path: output_dir/input_stem/[type_subdir/]item_name.ext

    Examples:
        resolve_output_path(Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=False)
        → /out/wall/effects/blur.jpg

        resolve_output_path(Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=True)
        → /out/wall/blur.jpg
    """
    suffix = input_file.suffix or ".png"
    base_dir = output_dir / input_file.stem

    if flat:
        return base_dir / f"{item_name}{suffix}"
    else:
        return base_dir / item_type.subdir_name / f"{item_name}{suffix}"
```

**BatchGenerator update:** Refactor `_get_output_path()` to use ItemType enum instead of string.

### Error Handling

**Type Safety:**
```python
# Use context for typed settings access (no type: ignore needed)
settings: CoreSettings = ctx.obj["settings"]
output_dir = settings.output.default_dir  # Fully typed
```

**Path Validation:**
- Output directory creation handled by existing `CommandExecutor` (creates parent dirs)
- Settings validation handled by Pydantic in schema
- Path expansion (~ and relative paths) handled during resolution

**No additional error handling needed** - existing mechanisms cover all cases.

### Data Flow

```
User runs command
    ↓
CLI parses arguments
    ↓
output_dir provided? → YES → use that
    ↓ NO
Get settings from context (ctx.obj["settings"])
    ↓
settings.output.default_dir
    ↓ (layered settings already resolved priority)
Resolve output file path:
  output_dir / input_stem / [type_subdir/] / item_name.ext
    ↓
CommandExecutor.execute()
  - Creates parent directories
  - Executes ImageMagick command
  - Writes output file
```

## Testing Strategy (TDD)

### Order of Execution

1. **DELETE** obsolete tests (old positional syntax)
2. **UPDATE** existing tests to new syntax
3. **ADD** new tests for new features
4. **RUN** tests - all should FAIL
5. **IMPLEMENT** changes
6. **RUN** tests - all should PASS

### Test Categories

#### 1. Unit Tests - Settings Schema

**File:** `packages/core/tests/test_config_schema.py`

```python
def test_output_settings_has_default_dir()
def test_output_settings_default_dir_is_path()
def test_output_settings_validates_default_dir()
def test_item_type_enum_values()
def test_item_type_subdir_names()
```

#### 2. Unit Tests - Path Resolution

**File:** `packages/core/tests/test_path_resolution.py` (NEW)

```python
def test_resolve_output_path_effect_not_flat()
def test_resolve_output_path_effect_flat()
def test_resolve_output_path_composite()
def test_resolve_output_path_preset()
def test_resolve_output_path_no_extension_defaults_png()
```

#### 3. CLI Tests - Process Commands

**File:** `packages/core/tests/test_cli.py`

**DELETE:**
- All tests expecting positional `output_file` argument

**ADD:**
```python
def test_process_effect_with_output_dir_creates_subdirectory()
def test_process_effect_without_output_uses_default()
def test_process_effect_with_flat_flag()
def test_process_composite_with_output_dir()
def test_process_composite_without_output_uses_default()
def test_process_composite_with_flat_flag()
def test_process_preset_with_output_dir()
def test_process_preset_without_output_uses_default()
def test_process_preset_with_flat_flag()
```

#### 4. CLI Tests - Batch Commands

**File:** `packages/core/tests/test_cli.py`

**UPDATE:**
- Change positional `output_dir` to `-o/--output-dir` option

**ADD:**
```python
def test_batch_effects_without_output_uses_default()
def test_batch_composites_without_output_uses_default()
def test_batch_presets_without_output_uses_default()
def test_batch_all_without_output_uses_default()
```

#### 5. Integration Tests

**File:** `packages/core/tests/test_integration.py`

**ADD:**
```python
def test_project_settings_override_default_output()
def test_user_settings_override_project()
def test_cli_flag_overrides_all_settings()
def test_full_layering_priority_chain()
```

#### 6. Dry-run Tests

**File:** `packages/core/tests/test_cli_dry_run.py`

**UPDATE:** All dry-run tests to use new syntax and verify resolved paths shown

#### 7. Orchestrator Tests

**Files:**
- `packages/orchestrator/tests/test_cli_process.py`
- `packages/orchestrator/tests/test_cli_dry_run.py`
- `packages/orchestrator/tests/test_container_execution.py`

**Same pattern as core tests** - delete old, update existing, add new

#### 8. Smoke Tests (CRITICAL)

**File:** `tests/smoke/run-smoke-tests.sh` (2077 lines)

**UPDATE ~50+ command invocations:**

```bash
# OLD (DELETE):
wallpaper-core process effect "$IMAGE" "$OUTPUT_FILE" --effect blur
wallpaper-core batch effects "$IMAGE" "$OUTPUT_DIR"

# NEW (UPDATE):
wallpaper-core process effect "$IMAGE" -o "$OUTPUT_DIR" --effect blur
wallpaper-core batch effects "$IMAGE" -o "$OUTPUT_DIR"
```

**UPDATE ~20+ output validation checks:**

```bash
# OLD: Check for specific file
[ -f "$OUTPUT_FILE" ]

# NEW: Check for resolved path
[ -f "$OUTPUT_DIR/$(basename "$IMAGE" .jpg)/effects/blur.jpg" ]
```

**ADD new smoke tests:**
- Commands without `-o` flag (uses default)
- Commands with `--flat` flag
- Layered settings overrides

### Test Execution Plan

```bash
# 1. Update all tests (will fail)
pytest packages/core/tests/
pytest packages/orchestrator/tests/

# 2. Implement changes

# 3. Run tests (should pass)
pytest packages/core/tests/ -v
pytest packages/orchestrator/tests/ -v

# 4. Run smoke tests
./tests/smoke/run-smoke-tests.sh wallpaper.jpg

# 5. Verify all pass
```

## Documentation Updates

### Files to Update

1. **README.md** - Update all examples to new syntax
2. **docs/configuration.md** - Document `core.output.default_dir` setting
3. **docs/MIGRATION.md** (NEW) - Breaking changes migration guide
4. **CLI help text** - Update docstrings with examples
5. **examples/** - Update all example scripts
6. **CHANGELOG.md** - Document breaking changes

### Example Updates

**README.md:**

```markdown
## Usage

### Process a Single Effect

```bash
# Use default output directory
wallpaper-core process effect wallpaper.jpg --effect blur

# Specify custom output
wallpaper-core process effect wallpaper.jpg -o /custom/out --effect blur

# Use flat structure
wallpaper-core process effect wallpaper.jpg --effect blur --flat
```

Output structure:
- Default: `./wallpapers-output/wallpaper/effects/blur.jpg`
- Custom: `/custom/out/wallpaper/effects/blur.jpg`
- Flat: `./wallpapers-output/wallpaper/blur.jpg`

### Configure Default Output

**Project settings** (`./settings.toml`):
```toml
[core.output]
default_dir = "./output"
```

**User settings** (`~/.config/wallpaper-effects-generator/settings.toml`):
```toml
[core.output]
default_dir = "~/Pictures/wallpapers"
```

Priority: CLI `-o` > User config > Project config > Package default
```

**CHANGELOG.md:**

```markdown
## [Unreleased]

### Breaking Changes

**Output directory is now optional with configurable defaults**

- Process commands: `INPUT OUTPUT_FILE` → `INPUT -o OUTPUT_DIR [--flat]`
- Batch commands: `INPUT OUTPUT_DIR` → `INPUT -o OUTPUT_DIR`
- Output argument now accepts directory (not file) for all commands
- When omitted, uses `core.output.default_dir` from settings (default: `./wallpapers-output`)
- All commands create standardized structure: `{output_dir}/{input_name}/[type]/{item}.ext`

See `docs/MIGRATION.md` for migration guide.

### Added

- `core.output.default_dir` setting for configurable default output directory
- `--flat` flag to process commands (matches batch behavior)
- `ItemType` enum for type-safe output path resolution

### Changed

- Process commands now create organized directory structure like batch commands
- Standardized output behavior across all commands
```

## Implementation Checklist

### Phase 1: Settings & Schema
- [ ] Add `ItemType` enum to schema
- [ ] Add `default_dir` to `OutputSettings`
- [ ] Add default to package `settings.toml`
- [ ] Add unit tests for settings
- [ ] Add unit tests for enum

### Phase 2: Path Resolution
- [ ] Implement `resolve_output_path()` helper
- [ ] Add unit tests for path resolution
- [ ] Update `BatchGenerator._get_output_path()` to use enum

### Phase 3: CLI - Process Commands
- [ ] Update `apply_effect()` signature and logic
- [ ] Update `apply_composite()` signature and logic
- [ ] Update `apply_preset()` signature and logic
- [ ] Delete obsolete CLI tests
- [ ] Add new CLI tests (with -o, without, --flat)
- [ ] Update dry-run handling

### Phase 4: CLI - Batch Commands
- [ ] Update `batch_effects()` signature
- [ ] Update `batch_composites()` signature
- [ ] Update `batch_presets()` signature
- [ ] Update `batch_all()` signature
- [ ] Update batch CLI tests
- [ ] Update batch dry-run tests

### Phase 5: Orchestrator
- [ ] Update orchestrator process commands
- [ ] Update orchestrator CLI tests
- [ ] Verify container mounting still works

### Phase 6: Integration & Smoke Tests
- [ ] Add settings layering integration tests
- [ ] Update ALL smoke test command invocations (~50+ lines)
- [ ] Update ALL smoke test validations (~20+ lines)
- [ ] Add new smoke tests (defaults, --flat)

### Phase 7: Documentation
- [ ] Update README.md examples
- [ ] Create docs/MIGRATION.md
- [ ] Update CLI help text
- [ ] Update examples/ scripts
- [ ] Update CHANGELOG.md
- [ ] Create/update docs/configuration.md

### Phase 8: Validation
- [ ] Run all unit tests: `pytest packages/*/tests/ -v`
- [ ] Run smoke tests: `./tests/smoke/run-smoke-tests.sh wallpaper.jpg`
- [ ] Manual testing of all commands
- [ ] Verify layered settings work correctly

## Breaking Changes Summary

**Commands Affected:** ALL process and batch commands in both `wallpaper-core` and `wallpaper-process`.

**Migration Required:**

```bash
# OLD → NEW
wallpaper-core process effect input.jpg output.jpg --effect blur
wallpaper-core process effect input.jpg -o /out --effect blur

wallpaper-core batch effects input.jpg /out
wallpaper-core batch effects input.jpg -o /out

# Or omit -o to use default:
wallpaper-core process effect input.jpg --effect blur
wallpaper-core batch effects input.jpg
```

**No Backward Compatibility:** This is an intentional breaking change to standardize behavior.

## Future Considerations

- **Default output location:** Users may request XDG-compliant default (e.g., `~/Pictures/wallpapers`). Currently using CWD-relative for project-awareness.
- **Multiple inputs:** Future support for batch processing multiple input files in one command.
- **Output templates:** Allow users to customize output path patterns via settings.

## Design Approval

✅ Settings Schema Changes
✅ CLI Signature Changes
✅ Output Path Resolution Logic
✅ Error Handling
✅ Testing Strategy
✅ Documentation Updates

**Approved:** 2026-02-13
**Ready for Implementation:** Yes
