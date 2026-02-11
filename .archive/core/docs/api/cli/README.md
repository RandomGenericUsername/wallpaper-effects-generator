# CLI Reference

Command-line interface reference for `wallpaper-effects-process`.

---

## Global Options

| Option | Description |
|--------|-------------|
| `-q`, `--quiet` | Quiet mode (errors only) |
| `-v`, `--verbose` | Verbose mode (show commands) |
| `-vv` | Debug mode (all details) |
| `--help` | Show help message |

---

## Commands

### version

Show version information.

```bash
wallpaper-effects-process version
```

---

### show

List available effects, composites, and presets.

```bash
wallpaper-effects-process show [effects|composites|presets|all]
```

| Argument | Description |
|----------|-------------|
| `effects` | List atomic effects |
| `composites` | List composite effects |
| `presets` | List preset configurations |
| `all` | List everything |

---

### process

Apply a single effect, composite, or preset.

#### process effect

```bash
wallpaper-effects-process process effect INPUT OUTPUT -e EFFECT_NAME [OPTIONS]
```

| Argument | Description |
|----------|-------------|
| `INPUT` | Input image path |
| `OUTPUT` | Output image path |
| `-e`, `--effect` | Effect name (required) |
| `--PARAM` | Override effect parameters |

Example:

```bash
wallpaper-effects-process process effect in.png out.png -e blur --blur 0x12
```

#### process composite

```bash
wallpaper-effects-process process composite INPUT OUTPUT -c COMPOSITE_NAME
```

| Argument | Description |
|----------|-------------|
| `INPUT` | Input image path |
| `OUTPUT` | Output image path |
| `-c`, `--composite` | Composite name (required) |

#### process preset

```bash
wallpaper-effects-process process preset INPUT OUTPUT -p PRESET_NAME
```

| Argument | Description |
|----------|-------------|
| `INPUT` | Input image path |
| `OUTPUT` | Output image path |
| `-p`, `--preset` | Preset name (required) |

---

### batch

Generate multiple effects at once.

```bash
wallpaper-effects-process batch [effects|composites|presets|all] INPUT OUTPUT_DIR [OPTIONS]
```

| Argument | Description |
|----------|-------------|
| `effects` | Generate all atomic effects |
| `composites` | Generate all composite effects |
| `presets` | Generate all preset configurations |
| `all` | Generate everything |
| `INPUT` | Input image path |
| `OUTPUT_DIR` | Output directory |

| Option | Description |
|--------|-------------|
| `--flat` | Disable categorized subdirectories |
| `--sequential` | Disable parallel processing |
| `--no-strict` | Continue on errors |

Example:

```bash
wallpaper-effects-process batch all wallpaper.png /output --flat --no-strict
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |

---

## See Also

- [Usage Guide](../../guides/usage.md)
- [Python API](../python/)
