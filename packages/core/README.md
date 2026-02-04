# wallpaper_core

Core wallpaper effects processor with local ImageMagick execution.

> **Note:** For containerized execution, see `wallpaper-orchestrator` package.
> This package runs effects locally using your system's ImageMagick installation.

## CLI Command

This package provides the `wallpaper-core` command for local execution.

For containerized execution, install `wallpaper-orchestrator` which provides the `wallpaper-process` command.

## Features

- **Layered Configuration**: Settings merge from package defaults → project → user → CLI
- **TOML Settings**: Runtime behavior configuration (execution, output, backend)
- **YAML Effects**: ImageMagick effect definitions with parameters
- **Type-Safe**: Full Pydantic validation for all configuration
- **CLI**: Simple, powerful command-line interface

## Installation

```bash
# From workspace root
uv sync

# Install just core package
cd packages/core
uv pip install -e .
```

## Quick Start

```bash
# Show current configuration
wallpaper-core info

# Process single image with effect
wallpaper-core process input.jpg output.jpg blur

# Process batch with multiple effects
wallpaper-core batch input.jpg --effects blur,brightness --parallel
```

## Configuration

### Layer Priority

1. **Package defaults** - `packages/core/src/wallpaper_core/config/settings.toml`
2. **Project settings** - `./settings.toml` (root of your project)
3. **User settings** - `~/.config/wallpaper-effects/settings.toml`
4. **CLI overrides** - Command-line flags

### Settings Format

**Package defaults (flat):**
```toml
# packages/core/src/wallpaper_core/config/settings.toml
[execution]
parallel = true
max_workers = 0
```

**Project/User settings (namespaced):**
```toml
# ./settings.toml or ~/.config/wallpaper-effects/settings.toml
[core.execution]
parallel = false
max_workers = 4

[core.backend]
binary = "/usr/local/bin/magick"
```

### Available Settings

**Execution Settings:**
- `parallel` (bool) - Run operations in parallel
- `strict` (bool) - Abort on first failure
- `max_workers` (int) - Max parallel workers (0=auto)

**Output Settings:**
- `verbosity` (int) - 0=QUIET, 1=NORMAL, 2=VERBOSE, 3=DEBUG

**Processing Settings:**
- `temp_dir` (path) - Temp directory (None=system default)

**Backend Settings:**
- `binary` (str) - ImageMagick binary path

## Effects

Effects are defined in `effects.yaml` with layered lookup:
1. Package defaults: `packages/core/effects/effects.yaml`
2. User effects: `~/.config/wallpaper-effects/effects.yaml`

See `effects.yaml` for available effects and parameters.

## Development

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=wallpaper_core --cov-report=term-missing

# Type checking
mypy src/wallpaper_core

# Format code
black src/ tests/
isort src/ tests/
```

## Architecture

Uses `layered_settings` package for configuration management:
- `CoreSettings` - Runtime behavior settings
- `EffectsConfig` - Effect definitions
- Both registered with `SchemaRegistry` at import time

See `docs/plans/2026-01-31-monorepo-refactor-design.md` for complete architecture.
