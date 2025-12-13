# Effects YAML Reference

Complete reference for `effects.yaml` configuration.

---

## File Location

| Location | Purpose |
|----------|---------|
| `core/effects/effects.yaml` | Package defaults |
| `~/.config/wallpaper-effects/effects.yaml` | User overrides |

User configuration is merged with package defaults.

---

## Top-Level Structure

```yaml
version: "1.0"

parameter_types:
  # Reusable parameter type definitions
  ...

effects:
  # Atomic effects (single ImageMagick commands)
  ...

composites:
  # Composite effects (chains of atomic effects)
  ...

presets:
  # Named configurations
  ...
```

---

## Parameter Types

Define reusable parameter types:

```yaml
parameter_types:
  blur_geometry:
    type: string
    pattern: "^\\d+x\\d+$"
    default: "0x8"
    description: "Blur geometry (RADIUSxSIGMA)"

  percent:
    type: integer
    min: -100
    max: 100
    default: 0
    description: "Percentage value"

  color_hex:
    type: string
    pattern: "^#[0-9a-fA-F]{6}$"
    default: "#000000"
    description: "Hex color code"

  opacity:
    type: float
    min: 0.0
    max: 1.0
    default: 0.5
    description: "Opacity value"
```

### Type Properties

| Property | Required | Description |
|----------|----------|-------------|
| `type` | Yes | `string`, `integer`, or `float` |
| `default` | Yes | Default value |
| `description` | No | Human-readable description |
| `pattern` | No | Regex pattern (strings only) |
| `min` | No | Minimum value (numbers only) |
| `max` | No | Maximum value (numbers only) |

---

## Effects

Define atomic effects:

```yaml
effects:
  blur:
    description: "Apply Gaussian blur"
    command: 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
    parameters:
      blur:
        type: blur_geometry
        cli_flag: "--blur"
        description: "Blur geometry"
```

### Effect Properties

| Property | Required | Description |
|----------|----------|-------------|
| `description` | Yes | Human-readable description |
| `command` | Yes | ImageMagick command template |
| `parameters` | No | Parameter definitions |

### Parameter Properties

| Property | Required | Description |
|----------|----------|-------------|
| `type` | Yes | Parameter type name (references `parameter_types`) |
| `cli_flag` | No | CLI flag for overriding (e.g., `--blur`) |
| `default` | No | Override type default |
| `description` | No | Override type description |

---

## Composites

Chain multiple effects:

```yaml
composites:
  blur-brightness80:
    description: "Blur then dim"
    chain:
      - effect: blur
        params: { blur: "0x8" }
      - effect: brightness
        params: { brightness: -20 }
```

### Composite Properties

| Property | Required | Description |
|----------|----------|-------------|
| `description` | Yes | Human-readable description |
| `chain` | Yes | List of effect steps |

### Chain Step Properties

| Property | Required | Description |
|----------|----------|-------------|
| `effect` | Yes | Effect name to apply |
| `params` | No | Parameter overrides |

---

## Presets

Named configurations:

```yaml
presets:
  # Reference an effect
  subtle_blur:
    description: "Gentle blur effect"
    effect: blur
    params: { blur: "0x4" }

  # Reference a composite
  dark_blur:
    description: "Dark blurred background"
    composite: blur-brightness80
```

### Preset Properties

| Property | Required | Description |
|----------|----------|-------------|
| `description` | Yes | Human-readable description |
| `effect` | No* | Effect to apply |
| `composite` | No* | Composite to apply |
| `params` | No | Parameter overrides (for effect presets) |

*Either `effect` or `composite` is required, not both.

---

## Variable Substitution

Commands support these variables:

| Variable | Description |
|----------|-------------|
| `$INPUT` | Input file path |
| `$OUTPUT` | Output file path |
| `$PARAM_NAME` | Parameter value (uppercase) |

---

## See Also

- [Extending Effects](../guides/extending-effects.md)
- [ImageMagick Options](https://imagemagick.org/script/command-line-options.php)

