# How Layered Configuration Works

An explanation of the four-layer configuration system used by both `wallpaper-core` and `wallpaper-process`, why it exists, and how precedence works.

<!-- BHV IDs: BHV-0019, BHV-0020, BHV-0022, BHV-0023, BHV-0024, BHV-0025 -->

---

## The four layers

Every time you run `wallpaper-core` or `wallpaper-process`, the configuration system merges four layers in this order (lower number = lower priority):

```
1. Package defaults      — shipped with the package, always present
2. Project-level config  — ./settings.toml (project root)
3. User-level config     — ~/.config/wallpaper-effects-generator/settings.toml
4. CLI flags             — highest priority, always wins
```

(BHV-0025)

Merging happens key-by-key: if a key is set in layer 3 but not layer 2, the layer 3 value is used. If set in both, layer 3 wins. A CLI flag always overrides whatever is in any file.

---

## Why four layers?

**Package defaults** give the application a sensible starting state. No configuration file is required to run the tool.

**Project-level config** lets a project team share consistent settings (for example, a fixed output directory or parallel=false for reproducible results). The file sits at the project root alongside the images being processed.

**User-level config** lets individual developers personalize their experience without touching the shared project file — for example, setting their preferred verbosity level or pointing the backend binary at a non-standard ImageMagick path.

**CLI flags** provide one-shot overrides for experimentation or scripting without permanently changing any file.

---

## How configure() and get_config() work

At import time, the CLI modules call:

```python
configure(CoreOnlyConfig, app_name=APP_NAME)  # APP_NAME = "wallpaper-effects-generator"
```

This registers the root Pydantic model and the application name. `app_name` is used to derive the user config path (`~/.config/wallpaper-effects-generator/`). Both `wallpaper-core` and `wallpaper-process` pass `app_name=APP_NAME` from `layered_settings.constants`, so settings and effects are loaded from the same directory. (BHV-0022)

When a subcommand runs, it calls:

```python
config = get_config()
```

On the first call, `get_config()` discovers and merges all available layers, validates the result against the Pydantic model, and caches the result. Subsequent calls return the cached instance. (BHV-0023)

If you pass overrides:

```python
config = get_config(overrides={"core.output.verbosity": 2})
```

A fresh merge is performed (bypassing the cache) with the override applied at the highest layer. This is how CLI flags (like `-v`) are implemented internally. (BHV-0024)

---

## SchemaRegistry and namespaces

The `layered-settings` library uses a `SchemaRegistry` to support multiple namespaces within a single config file. Each namespace maps to a Pydantic model. (BHV-0019, BHV-0020)

For `wallpaper-core`, the registry has one namespace: `core`.

For `wallpaper-process`, the registry has three namespaces: `core`, `effects`, and `orchestrator`. This is why orchestrator-specific settings can be placed in the same `settings.toml` under `[orchestrator.container]` alongside `[core.output]`.

---

## The unified config namespace (wallpaper-process)

`wallpaper-process` uses a `UnifiedConfig` root model:

```python
class UnifiedConfig(BaseModel):
    core: CoreSettings
    effects: EffectsConfig
    orchestrator: OrchestratorSettings
```

This means a single `settings.toml` file can configure all three subsystems:

```toml
[core.output]
default_dir = "/home/user/wallpapers"

[core.execution]
parallel = false

[orchestrator.container]
engine = "podman"
image_registry = "ghcr.io/myusername"
```

(F-0009 — previously undocumented)

---

## Effects have their own layered system

`effects.yaml` uses a parallel three-layer system (no CLI layer):

```
1. Package defaults — packages/core/effects/effects.yaml
2. Project-level   — ./effects.yaml
3. User-level      — ~/.config/wallpaper-effects-generator/effects.yaml
```

Deep merging is used: individual effects, composites, or presets can be overridden at a higher layer without replacing the entire file. A user can add a new effect while inheriting all package defaults.

---

## Caching and invalidation

- `get_config()` returns a cached instance. The cache is cleared by calling `configure()` again.
- `get_config(overrides=...)` always creates a fresh instance and does not store it in the cache.
- `load_effects()` similarly caches the merged `EffectsConfig`. Calling `configure_effects()` again clears the cache.

This design ensures consistent configuration throughout a command's lifetime while keeping startup fast on repeated calls.
