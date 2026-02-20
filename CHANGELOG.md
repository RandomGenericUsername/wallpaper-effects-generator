# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed (Dev Setup)

- Added `.python-version` pinning Python to 3.12 for tool auto-detection (uv, pyenv, mise)
- Updated pre-commit hook versions: black `24.1.1→24.10.0`, ruff `v0.2.1→v0.8.4`, mypy `v1.8.0→v1.13.0`, bandit `1.7.5→1.8.0`
- Added `ruff-format` hook to pre-commit config
- Removed `--ignore=I` from ruff pre-commit args; ruff now enforces import sorting consistently
- Fixed root `pyproject.toml` ruff config: removed contradictory `ignore = ["I"]` and dead `[tool.ruff.lint.isort]` block
- Migrated `packages/core`, `packages/orchestrator`, `packages/settings` dev deps from `[project.optional-dependencies]` to `[dependency-groups]` for correct `uv sync --dev` resolution
- Added `ruff check` step to all 4 CI lint jobs (`ci-core`, `ci-settings`, `ci-effects`, `ci-orchestrator`)
- Added `-ll` severity filter to bandit in all 4 CI security jobs
- Added `-n auto` parallel execution to `ci-core` test step (was the only workflow missing it)
- Added coverage threshold check (`--fail-under=95`) to `ci-orchestrator` (was missing)
- Fixed `make push` color output: restored `echo -e` with color vars for all phase headers
- Added `.github/pull_request_template.md` with design compliance checklist
- Fixed `packages/effects/pyproject.toml` ruff isort: removed `lines-after-imports = 2`, added `known_first_party` to `[tool.isort]`
- Aligned `known-first-party` across `packages/core` and `packages/orchestrator`: added `layered_effects` to both ruff and isort configs
- Added `known_first_party` to per-package `[tool.isort]` sections (core, orchestrator, effects) so standalone isort and ruff agree on import sections
- Added `[tool.ruff.lint.isort].known-first-party` to workspace root `pyproject.toml`
- Changed CI ruff check steps to run from workspace root (`uv run ruff check packages/<pkg>`) for consistent config resolution
- Added `[tool.ruff]` section to `packages/settings/pyproject.toml` with per-file ignores for E501/N813 in tests and examples


### Breaking Changes

#### Output Directory Now Optional

The most significant change in this release: **the output directory is now optional** for all commands across both `wallpaper-core` and `wallpaper-orchestrator` packages. Instead of requiring a positional argument, the output directory is now specified via the `-o/--output-dir` flag, with a sensible default fallback.

**Affected Commands:**

All **process** commands:
- `wallpaper-core process effect <image> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-core process composite <images> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-core process preset <image> <preset> -o <output_dir>`
- `wallpaper-orchestrator process effect <image> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-orchestrator process composite <images> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-orchestrator process preset <image> <preset> -o <output_dir>`

All **batch** commands:
- `wallpaper-core batch effects <directory> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-core batch composites <directories> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-core batch presets <directory> <preset> -o <output_dir>`
- `wallpaper-core batch all <directory> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-orchestrator batch effects <directory> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-orchestrator batch composites <directories> [--effects EFFECTS] -o <output_dir>`
- `wallpaper-orchestrator batch presets <directory> <preset> -o <output_dir>`
- `wallpaper-orchestrator batch all <directory> [--effects EFFECTS] -o <output_dir>`

**Migration Required:**

Old syntax:
```bash
wallpaper-core process effect image.jpg ./output
wallpaper-core batch effects input_dir output_dir
```

New syntax:
```bash
wallpaper-core process effect image.jpg -o ./output
wallpaper-core batch effects input_dir -o output_dir
```

Or rely on the default output directory configured via `core.output.default_dir`:
```bash
wallpaper-core process effect image.jpg
wallpaper-core batch effects input_dir
```

For complete migration instructions, see [docs/MIGRATION.md](docs/MIGRATION.md).

### Added

#### Optional Output Directory Flag

- New `-o/--output-dir` flag for all process and batch commands
- Output directory is now optional; if not provided, uses configured default directory
- Provides flexibility for scripting and automation workflows

#### Configuration: `core.output.default_dir`

- New configuration setting: `core.output.default_dir`
- Default value: `./wallpapers-output`
- Applies to both `wallpaper-core` and `wallpaper-orchestrator` packages
- Can be overridden via:
  - User configuration: `~/.config/wallpaper-effects-generator/settings.toml` (or `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml`)
  - Project-level settings: `./settings.toml` in the current working directory
  - Command-line flag: `-o/--output-dir`

Example configuration:
```toml
[core.output]
default_dir = "/var/wallpapers"
```

#### Flat Output Structure Flag

- New `--flat` flag for all process and batch commands
- Enables flat output structure instead of default nested directory structure
- Useful for workflows requiring a flat file organization

#### ItemType Enum

- New `ItemType` enum for type-safe path resolution
- Provides clear distinction between effect, composite, and preset items
- Used internally by `BatchGenerator` for improved type safety and code clarity
- Reduces potential for path resolution errors

#### Output Path Resolution Helper

- New `resolve_output_path()` helper function
- Centralizes logic for resolving output paths with defaults
- Improves consistency across all commands
- Enables flexible output directory handling

#### Comprehensive Migration Guide

- New [docs/MIGRATION.md](docs/MIGRATION.md) document
- Provides complete migration instructions for users
- Includes examples for each affected command type
- Documents new configuration options
- Clarifies the default output directory behavior

### Changed

- **Core CLI Module** (`wallpaper_core.cli`):
  - Updated all process command signatures to accept optional `-o/--output-dir` flag
  - Updated all batch command signatures to accept optional `-o/--output-dir` flag
  - Updated path resolution logic to support default output directory fallback
  - Added support for `--flat` flag in all commands

- **Orchestrator CLI Module** (`wallpaper_orchestrator.cli`):
  - Updated all process command signatures to accept optional `-o/--output-dir` flag
  - Updated all batch command signatures to accept optional `-o/--output-dir` flag
  - Updated path resolution logic to support default output directory fallback
  - Added support for `--flat` flag in all commands

- **BatchGenerator** (`wallpaper_core.batch.BatchGenerator`):
  - Refactored to use `ItemType` enum for type-safe item classification
  - Improved code clarity and maintainability
  - Enhanced path resolution consistency

- **Smoke Tests**:
  - Updated all smoke test commands to use new `-o/--output-dir` syntax
  - Added test coverage for default output directory behavior
  - Added test coverage for `--flat` flag functionality

- **Documentation**:
  - Updated README with new command examples showing `-o` flag usage
  - Added configuration documentation explaining `core.output.default_dir`
  - Updated installation and usage sections with new syntax

- **Dry-run Path Resolution** (`batch.py`):
  - Refactored dry-run batch command path resolution to use `ItemType` enum
  - Improved consistency with main batch processing logic

### Technical Details

#### CLI Implementation

The `-o/--output-dir` flag is implemented as an optional argument across all affected commands. When not provided, the CLI resolves the output directory using the following precedence:

1. Command-line flag: `-o/--output-dir` (highest priority)
2. Project-level settings: `./settings.toml` in current working directory
3. User configuration: `~/.config/wallpaper-effects-generator/settings.toml` (or `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml`)
4. Package defaults: `./wallpapers-output` (lowest priority)

#### Configuration Discovery

The `layered_settings` package handles configuration layering with the following lookup order:

- Package-level defaults: `core.output.default_dir = "./wallpapers-output"`
- Project-level overrides: Values in `./settings.toml`
- User-level overrides: Values in `~/.config/wallpaper-effects-generator/settings.toml`

#### Type Safety with ItemType Enum

The new `ItemType` enum ensures type-safe handling of different item types in batch operations:

```python
class ItemType(Enum):
    EFFECT = "effect"
    COMPOSITE = "composite"
    PRESET = "preset"
```

This enum is used throughout `BatchGenerator` to eliminate string-based type checking and improve code maintainability.

### Deprecations

None. This is a major breaking change release. No features are deprecated; instead, old command signatures are no longer supported.

### Security

No security-related changes in this release.

### Known Issues

None known at this time.

### Migration Resources

- [Complete Migration Guide](docs/MIGRATION.md) - Detailed instructions for upgrading to this version
- Command-line help: Use `--help` flag on any command for updated usage information

---

## [0.1.0] - 2025-02-15

### Added

- Initial release
- Wallpaper effects generator with layered configuration system
- Support for single-image and batch processing
- Effect, composite, and preset item types
- Configurable effects pipeline
- Container support via Podman/Docker

### Packages

- `layered-settings`: 3-layer configuration system (package defaults → project → user)
- `wallpaper-core`: Core effects processing engine
- `wallpaper-orchestrator`: Container orchestration and advanced processing
- `layered-effects`: Effects definition and management system

[Unreleased]: https://github.com/yourusername/wallpaper-effects-generator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/wallpaper-effects-generator/releases/tag/v0.1.0
