# Usage Guide

Complete usage guide for `wallpaper-effects`.

---

## Commands Overview

| Command | Description |
|---------|-------------|
| `show` | List available effects, composites, presets |
| `process` | Apply a single effect/composite/preset |
| `batch` | Generate multiple effects at once |
| `version` | Show version information |

---

## Global Options

| Option | Description |
|--------|-------------|
| `--runtime` | Container runtime (`docker` or `podman`) |
| `-q`, `--quiet` | Quiet mode (errors only) |
| `-v`, `--verbose` | Verbose mode |
| `-vv` | Debug mode |

---

## Show Command

```bash
wallpaper-effects show [effects|composites|presets|all]
```

---

## Process Command

### Apply Effect

```bash
wallpaper-effects process effect INPUT OUTPUT -e EFFECT_NAME [--PARAM VALUE]
```

### Apply Composite

```bash
wallpaper-effects process composite INPUT OUTPUT -c COMPOSITE_NAME
```

### Apply Preset

```bash
wallpaper-effects process preset INPUT OUTPUT -p PRESET_NAME
```

---

## Batch Command

```bash
wallpaper-effects batch [effects|composites|presets|all] INPUT OUTPUT_DIR [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--flat` | No subdirectories |
| `--sequential` | Disable parallel processing |
| `--no-strict` | Continue on errors |

---

## Container Runtime Selection

Auto-detection order:

1. Docker
2. Podman

Override:

```bash
wallpaper-effects --runtime podman batch all input.png /output
```

---

## Volume Mounting

The orchestrator automatically mounts:

- Input file directory (read-only)
- Output directory (read-write)

Paths are converted to absolute paths for container mounting.

---

## See Also

- [Container Management](containers.md)
- [Configuration](../configuration/settings.md)
