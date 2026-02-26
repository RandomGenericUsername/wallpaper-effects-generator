# Project Architecture

An overview of how `wallpaper-effects-generator` is structured, what each package does, and why the project is organized as a monorepo.

---

## Monorepo structure

The repository contains four Python packages under `packages/`:

```
packages/
  settings/      — layered-settings: generic multi-layer config with Pydantic validation
  effects/       — layered-effects: effects.yaml loader with deep-merge layering
  core/          — wallpaper-core: CLI + ImageMagick execution engine
  orchestrator/  — wallpaper-orchestrator: container orchestration CLI
```

Each package is an independently installable Python package. `core` depends on `settings` and `effects`. `orchestrator` depends on `core`, `settings`, and `effects`.

---

## Package responsibilities

### layered-settings (`packages/settings/`)

A generic configuration library. It provides:

- `SchemaRegistry` — maps namespaces to Pydantic models and their defaults files.
- `configure()` / `get_config()` — the public API for initializing and retrieving configuration.
- `DryRunBase` — a base class for rendering dry-run output (used by both `core` and `orchestrator`).
- XDG path helpers — resolves platform-appropriate config directories.
- Error types: `SettingsFileError`, `SettingsRegistryError`, `SettingsValidationError`.

This package knows nothing about wallpaper effects. It is a reusable config-layering library.

### layered-effects (`packages/effects/`)

A domain-specific library for loading `effects.yaml` files with three-layer deep merging. It provides:

- `configure()` / `load_effects()` — analogous to the settings API but for effects.
- `EffectsConfig` — the validated effects model (effects, composites, presets, parameter types).
- Error types: `EffectsError`, `EffectsLoadError`, `EffectsValidationError`.

### wallpaper-core (`packages/core/`)

The main CLI and execution engine. It provides:

- `wallpaper-core` CLI — `process`, `batch`, `show`, `info`, `version` commands.
- `CommandExecutor` — runs `magick` commands via subprocess.
- `ChainExecutor` — executes composite effect chains with temporary files.
- `BatchGenerator` — parallel/sequential batch processing engine.
- `CoreSettings` Pydantic model — defines the `core.*` config namespace.
- `CoreDryRun` — renders dry-run output for core commands.

`wallpaper-core` configures both `layered-settings` (with `CoreSettings`) and `layered-effects` at import time.

### wallpaper-orchestrator (`packages/orchestrator/`)

The container-orchestration layer. It provides:

- `wallpaper-process` CLI — `install`, `uninstall`, `process`, `batch`, `show`, `info`, `version`.
- `ContainerManager` — builds and executes `docker`/`podman run` commands.
- `UnifiedConfig` — a root Pydantic model combining `CoreSettings`, `EffectsConfig`, and `OrchestratorSettings` under three namespaces.
- `OrchestratorDryRun` — renders dry-run output showing both host and container commands.

---

## Design decisions

### Why a monorepo?

Each package has a clearly defined responsibility and can be used independently. `layered-settings` is a general-purpose config library that could be used outside this project. `layered-effects` is domain-specific but still decoupled from the CLI. Keeping them in one repository simplifies development iteration and ensures all packages stay in sync.

### Why Pydantic for configuration?

Pydantic provides automatic type coercion, validation, and error messages that make configuration mistakes immediately obvious rather than silently failing at runtime.

### Why the `configure()` / `get_config()` pattern?

This mirrors the "initialize once, access everywhere" pattern common in application frameworks. `configure()` must be called once at startup (done at module import in both `core` and `orchestrator`), and subsequent `get_config()` calls return the cached, fully-merged configuration.

### Why is effects.yaml separate from settings.toml?

Effects and settings have different structures and different use cases. Settings control runtime behavior (verbosity, parallelism, output directory). Effects define what ImageMagick commands to run and their parameter schemas. Separating them allows users to override effects independently of runtime settings.

### Why does orchestrator run batch on the host?

The container image is optimized for single-image processing. Batch processing uses Python's parallel executor (`ThreadPoolExecutor`) to coordinate multiple subprocess invocations. Keeping batch on the host avoids the overhead of spawning a separate container for each batch item and simplifies output path management.

---

## Data flow (host mode)

```
User invokes wallpaper-core process effect input.jpg --effect blur
                          |
                   [Startup: configure() called at import]
                          |
                   layered-settings merges:
                     pkg defaults / ./settings.toml / ~/.config/.../settings.toml
                          |
                   layered-effects merges:
                     pkg effects.yaml / ./effects.yaml / ~/.config/.../effects.yaml
                          |
                   process effect command:
                     resolve output path
                     look up effect definition
                     substitute $INPUT, $OUTPUT, $BLUR in command template
                     execute: magick "input.jpg" -blur "0x8" "output.png"
```

## Data flow (container mode)

```
User invokes wallpaper-process process effect input.jpg --effect blur
                          |
                   ContainerManager builds:
                     docker run --rm
                       -v /abs/input.jpg:/input/image.jpg:ro
                       -v /abs/output-dir:/output:rw
                       wallpaper-effects:latest
                       process effect /input/image.jpg --effect blur -o /output
                          |
                   Inside container:
                     wallpaper-core resolves command
                     executes: magick "/input/image.jpg" -blur "0x8" "/output/..."
```
