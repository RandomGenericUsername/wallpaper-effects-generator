# Reference: Configuration

`wallpaper-core` and `wallpaper-process` use a four-layer configuration system. This page documents all configuration keys, their defaults, file locations, and the precedence order.

<!-- BHV IDs: BHV-0022, BHV-0023, BHV-0024, BHV-0025, BHV-0027, BHV-0028 -->

---

## Configuration layers

Settings are merged in this order (later layers override earlier ones): (BHV-0025)

| Layer | Location | Format |
|---|---|---|
| 1. Package defaults (lowest priority) | `packages/core/src/wallpaper_core/config/settings.toml` | Flat TOML (no namespace prefix) |
| 2. Project-level settings | `./settings.toml` (current working directory) | Namespaced TOML |
| 3. User-level settings | `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml` | Namespaced TOML |
| 4. CLI flags (highest priority) | Command-line arguments | — |

On Linux and macOS, `$XDG_CONFIG_HOME` defaults to `~/.config`, making the user settings path `~/.config/wallpaper-effects-generator/settings.toml`. (BHV-0027)

The application name used for the XDG path is `wallpaper-effects-generator`. (BHV-0028)

---

## Configure once at startup

Both `wallpaper-core` and `wallpaper-process` call `configure()` at module import time. `get_config()` then returns a cached, fully-merged configuration instance. Calling `get_config()` without first calling `configure()` raises a `RuntimeError`. (BHV-0022, BHV-0023)

---

## File formats

Package defaults use **flat TOML** (no namespace prefix):

```toml
[execution]
parallel = true
max_workers = 0

[output]
verbosity = 1
default_dir = "/tmp/wallpaper-effects"
```

Project-level and user-level files use **namespaced TOML**:

```toml
[core.execution]
parallel = false
max_workers = 4

[core.output]
verbosity = 2
default_dir = "/home/user/wallpapers"
```

Only **TOML** (`.toml`) is supported for auto-discovered settings files. Layer discovery always looks for `settings.toml` by name. The `FileLoader` can parse YAML internally but no YAML settings file is ever auto-discovered. (BHV-0023)

---

## CLI override notation

CLI flag overrides use dotted-path notation. They are applied as the highest-priority layer and do not update the cache (they create a fresh merged instance). (BHV-0024)

---

## core namespace keys

All keys below are accessed as `core.<section>.<key>` in project/user config.

### core.execution

| Key | Default | Description |
|---|---|---|
| `parallel` | `true` | Enable parallel batch processing. |
| `strict` | `true` | Abort batch on first error. |
| `max_workers` | `0` | Number of parallel workers. `0` = auto-detect CPU count. |

(BHV-0025)

### core.output

| Key | Default | Description |
|---|---|---|
| `verbosity` | `1` | Verbosity level: `0`=QUIET, `1`=NORMAL, `2`=VERBOSE, `3`=DEBUG. String values `"QUIET"`, `"NORMAL"`, `"VERBOSE"`, `"DEBUG"` are also accepted. |
| `default_dir` | `"/tmp/wallpaper-effects"` | Default output directory when `-o` is not specified. |

(BHV-0025)

### core.processing

| Key | Default | Description |
|---|---|---|
| `temp_dir` | (system temp) | Custom temporary directory for intermediate files. Unset by default. |

### core.backend

| Key | Default | Description |
|---|---|---|
| `binary` | auto-detected | ImageMagick binary. At startup, auto-detected via `shutil.which("magick")` then `shutil.which("convert")`; falls back to `"magick"` if neither is found. Override to use a specific path. |

---

## orchestrator namespace keys

The `orchestrator` namespace is only available when using `wallpaper-process`. Project and user config files can include an `[orchestrator.container]` section. (BHV-0068)

### orchestrator.container

| Key | Default | Description |
|---|---|---|
| `engine` | `"docker"` | Container engine: `"docker"` or `"podman"`. |
| `image_name` | `"wallpaper-effects:latest"` | Container image name and tag. Override to use a different local image name. |
| `image_registry` | `""` | Optional registry prefix, e.g., `"ghcr.io/myusername"`. When set, the full image name becomes `<registry>/wallpaper-effects:latest`. |

Example user config for Podman with a custom registry:

```toml
[orchestrator.container]
engine = "podman"
image_registry = "ghcr.io/myusername"
```

(BHV-0068, BHV-0071)

---

## effects layer

Effects (`effects.yaml`) use their own three-layer discovery:

| Layer | Location |
|---|---|
| Package defaults | `packages/core/effects/effects.yaml` |
| Project-level | `./effects.yaml` (current working directory) |
| User-level | `~/.config/wallpaper-effects-generator/effects.yaml` |

Users can override specific effects, add new effects, or add new composites and presets in their project or user `effects.yaml`. (BHV-0036, BHV-0043)

---

## Application constants (BHV-0028)

| Constant | Value |
|---|---|
| `APP_NAME` | `"wallpaper-effects-generator"` |
| `SETTINGS_FILENAME` | `"settings.toml"` |
| `EFFECTS_FILENAME` | `"effects.yaml"` |

These are exported from `layered_settings.constants` and used to construct all configuration file paths.
