# Extending Effects

Add custom effects, composites, and presets.

---

## Overview

Effects are defined in YAML configuration files:

- **Package defaults**: `core/effects/effects.yaml`
- **User overrides**: `~/.config/wallpaper-effects/effects.yaml`

User configuration merges with package defaults, allowing you to add or override effects.

---

## Effects Configuration Structure

```yaml
version: "1.0"

# Reusable parameter types
parameter_types:
  my_param_type:
    type: string|integer|float
    default: "value"
    description: "Description"

# Atomic effects (single ImageMagick command)
effects:
  effect_name:
    description: "What this effect does"
    command: 'magick "$INPUT" -operation "$PARAM" "$OUTPUT"'
    parameters:
      param_name:
        type: my_param_type
        cli_flag: "--param"
        description: "Parameter description"

# Composite effects (chains of atomic effects)
composites:
  composite_name:
    description: "Chain description"
    chain:
      - effect: effect1
        params: { param: value }
      - effect: effect2

# Presets (named configurations)
presets:
  preset_name:
    description: "Preset description"
    effect: effect_name
    params: { param: value }
```

---

## Adding a New Effect

### Step 1: Create User Config File

```bash
mkdir -p ~/.config/wallpaper-effects
touch ~/.config/wallpaper-effects/effects.yaml
```

### Step 2: Define the Effect

```yaml
# ~/.config/wallpaper-effects/effects.yaml
version: "1.0"

effects:
  sharpen:
    description: "Sharpen the image"
    command: 'magick "$INPUT" -sharpen 0x"$SHARPEN" "$OUTPUT"'
    parameters:
      sharpen:
        type: integer
        cli_flag: "--sharpen"
        default: 2
        description: "Sharpen strength (0-10)"
```

### Step 3: Use the Effect

```bash
# Verify it appears in the list
wallpaper-effects-process show effects

# Apply the effect
wallpaper-effects-process process effect input.png output.png -e sharpen

# With custom parameter
wallpaper-effects-process process effect input.png output.png -e sharpen --sharpen 5
```

---

## Variable Substitution

Commands support these variables:

| Variable | Description |
|----------|-------------|
| `$INPUT` | Input file path |
| `$OUTPUT` | Output file path |
| `$PARAM_NAME` | Parameter value (uppercase) |

Example:

```yaml
effects:
  resize:
    command: 'magick "$INPUT" -resize "$WIDTH"x"$HEIGHT" "$OUTPUT"'
    parameters:
      width:
        type: integer
        default: 1920
      height:
        type: integer
        default: 1080
```

---

## Adding a Composite

Chain multiple effects:

```yaml
composites:
  sharpen-blur:
    description: "Sharpen then blur"
    chain:
      - effect: sharpen
        params: { sharpen: 3 }
      - effect: blur
        params: { blur: "0x4" }
```

---

## Adding a Preset

Reference an effect or composite with fixed parameters:

```yaml
presets:
  # Reference an effect
  strong_sharpen:
    description: "Strong sharpening"
    effect: sharpen
    params: { sharpen: 8 }

  # Reference a composite
  sharpen_blur_combo:
    description: "Sharpen then blur preset"
    composite: sharpen-blur
```

---

## Parameter Types

### Built-in Types

```yaml
parameter_types:
  blur_geometry:
    type: string
    pattern: "^\\d+x\\d+$"
    default: "0x8"

  percent:
    type: integer
    min: -100
    max: 100
    default: 0

  opacity:
    type: float
    min: 0.0
    max: 1.0
    default: 0.5

  color_hex:
    type: string
    pattern: "^#[0-9a-fA-F]{6}$"
    default: "#000000"
```

### Reference Existing Types

```yaml
effects:
  my_effect:
    parameters:
      color:
        type: color_hex  # References parameter_types.color_hex
```

---

## Best Practices

1. **Test commands manually** before adding to YAML
2. **Use descriptive names** for effects and presets
3. **Document parameters** with clear descriptions
4. **Quote variables** in commands: `"$INPUT"` not `$INPUT`
5. **Use parameter types** for validation

---

## See Also

- [Effects YAML Reference](../configuration/effects-yaml.md)
- [ImageMagick Documentation](https://imagemagick.org/script/command-line-options.php)

