# CLI Reference

Command-line interface reference for `wallpaper-effects`.

---

## Global Options

| Option | Description |
|--------|-------------|
| `--runtime` | Container runtime (`docker`, `podman`, `auto`) |
| `-q`, `--quiet` | Quiet mode (errors only) |
| `-v`, `--verbose` | Verbose mode (show commands) |
| `-vv` | Debug mode (all details) |
| `--help` | Show help message |

---

## Commands

### version

Show version information.

```bash
wallpaper-effects version
```

---

### show

List available effects, composites, and presets.

```bash
wallpaper-effects show [effects|composites|presets|all]
```

---

### process

Apply a single effect, composite, or preset.

#### process effect

```bash
wallpaper-effects process effect INPUT OUTPUT -e EFFECT_NAME [--PARAM VALUE]
```

#### process composite

```bash
wallpaper-effects process composite INPUT OUTPUT -c COMPOSITE_NAME
```

#### process preset

```bash
wallpaper-effects process preset INPUT OUTPUT -p PRESET_NAME
```

---

### batch

Generate multiple effects at once.

```bash
wallpaper-effects batch [effects|composites|presets|all] INPUT OUTPUT_DIR [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--flat` | Disable categorized subdirectories |
| `--sequential` | Disable parallel processing |
| `--no-strict` | Continue on errors |

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | Container error |

---

## Examples

```bash
# Use specific runtime
wallpaper-effects --runtime podman batch all input.png /output

# Verbose with Docker
wallpaper-effects --runtime docker -v process effect in.png out.png -e blur
```

---

## See Also

- [Usage Guide](../../guides/usage.md)
- [Core CLI Reference](../../../../core/docs/api/cli/)

