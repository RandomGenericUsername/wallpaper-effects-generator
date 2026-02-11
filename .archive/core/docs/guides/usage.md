# Usage Guide

Complete usage guide for `wallpaper-effects-process`.

---

## Commands Overview

| Command | Description |
|---------|-------------|
| `show` | List available effects, composites, presets |
| `process` | Apply a single effect/composite/preset |
| `batch` | Generate multiple effects at once |
| `version` | Show version information |

---

## Show Command

List available effects:

```bash
# List effects only
wallpaper-effects-process show effects

# List composites only
wallpaper-effects-process show composites

# List presets only
wallpaper-effects-process show presets

# List everything
wallpaper-effects-process show all
```

---

## Process Command

Apply individual effects:

```bash
# Apply an effect
wallpaper-effects-process process effect INPUT OUTPUT -e EFFECT_NAME

# Apply a composite (chain of effects)
wallpaper-effects-process process composite INPUT OUTPUT -c COMPOSITE_NAME

# Apply a preset (named configuration)
wallpaper-effects-process process preset INPUT OUTPUT -p PRESET_NAME
```

### Effect Parameters

Override effect parameters with CLI flags:

```bash
# Blur with custom strength
wallpaper-effects-process process effect in.png out.png -e blur --blur 0x15

# Brightness adjustment
wallpaper-effects-process process effect in.png out.png -e brightness --brightness -40

# Color overlay
wallpaper-effects-process process effect in.png out.png -e color_overlay --color "#ff0000" --opacity 50
```

---

## Batch Command

Generate multiple effects at once:

```bash
# Generate all effects
wallpaper-effects-process batch effects INPUT OUTPUT_DIR

# Generate all composites
wallpaper-effects-process batch composites INPUT OUTPUT_DIR

# Generate all presets
wallpaper-effects-process batch presets INPUT OUTPUT_DIR

# Generate everything
wallpaper-effects-process batch all INPUT OUTPUT_DIR
```

### Batch Options

| Option | Description |
|--------|-------------|
| `--flat` | No subdirectories (effects/, composites/, presets/) |
| `--sequential` | Disable parallel processing |
| `--no-strict` | Continue on errors |

```bash
# Flat output (no categorized subdirs)
wallpaper-effects-process batch all input.png /output --flat

# Sequential processing
wallpaper-effects-process batch all input.png /output --sequential

# Continue despite errors
wallpaper-effects-process batch all input.png /output --no-strict
```

---

## Verbosity Flags

| Flag | Level | Description |
|------|-------|-------------|
| `-q` | Quiet | Errors only |
| (none) | Normal | Standard output |
| `-v` | Verbose | Show commands being executed |
| `-vv` | Debug | All details including parameters |

```bash
# Quiet mode
wallpaper-effects-process -q batch all input.png /output

# Debug mode
wallpaper-effects-process -vv process effect input.png output.png -e blur
```

---

## See Also

- [Extending Effects](extending-effects.md)
- [Configuration](../configuration/settings.md)
