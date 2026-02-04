# layered-effects

Layered effects configuration system for wallpaper-effects-generator.

## Overview

This package provides a layered configuration system for `effects.yaml`, allowing users
to define custom effects at multiple levels with deep merging behavior.

## Layer Precedence

1. **Package defaults** (lowest): Bundled with wallpaper-core
2. **Project root**: `{project_root}/effects.yaml`
3. **User config** (highest): `~/.config/wallpaper-effects-generator/effects.yaml`

## Usage

```python
from layered_effects import configure, load_effects

# Configure at application startup
configure(project_root=Path.cwd())

# Load merged effects configuration
effects_config = load_effects()  # Returns EffectsConfig instance

# Access effects
blur_effect = effects_config.effects["blur"]
```

## Deep Merge Behavior

Higher layers override lower layers via deep merge:
- Effects, composites, presets, parameter_types merge independently
- Users can override specific effects while inheriting others
- Users can add new effects not in package defaults

## Example

```yaml
# User's ~/.config/wallpaper-effects-generator/effects.yaml
effects:
  blur:  # Override package blur with custom parameters
    command: 'magick "$INPUT" -blur 0x12 "$OUTPUT"'
    description: "Custom strong blur"

  neon:  # Add new effect not in package
    command: 'magick "$INPUT" -negate -blur 0x2 "$OUTPUT"'
    description: "Neon glow effect"
```
