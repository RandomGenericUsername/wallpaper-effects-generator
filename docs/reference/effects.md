# Reference: Built-in Effects, Composites, and Presets

All effects, composites, and presets are defined in `packages/core/effects/effects.yaml`. Users can add to or override these definitions in `./effects.yaml` (project) or `~/.config/wallpaper-effects-generator/effects.yaml` (user). (BHV-0031, BHV-0036, BHV-0043)

<!-- BHV IDs: BHV-0031, BHV-0032, BHV-0035, BHV-0036, BHV-0043 -->

---

## Effects

Atomic effects execute a single `magick` command. Effects that expose configurable parameters list their CLI flags below.

### blur

- **Description:** Apply Gaussian blur.
- **Command template:** `magick "$INPUT" -blur "$BLUR" "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `blur` | `--blur` | string (RADIUSxSIGMA) | `"0x8"` | Blur geometry, e.g., `0x8`, `0x16`. Pattern: `^\d+x\d+$`. |

Example override:
```bash
wallpaper-core process effect input.jpg --effect blur --blur 0x16
```

---

### blackwhite

- **Description:** Convert to grayscale.
- **Command template:** `magick "$INPUT" -grayscale Average "$OUTPUT"`
- **Parameters:** none.

---

### negate

- **Description:** Invert colors.
- **Command template:** `magick "$INPUT" -channel RGB -negate +channel "$OUTPUT"`
- **Parameters:** none.

---

### brightness

- **Description:** Adjust brightness/contrast.
- **Command template:** `magick "$INPUT" -brightness-contrast "$BRIGHTNESS"% "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `brightness` | `--brightness` | integer | `-20` | Brightness adjustment (-100 to 100). |

---

### contrast

- **Description:** Adjust contrast.
- **Command template:** `magick "$INPUT" -brightness-contrast 0x"$CONTRAST"% "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `contrast` | `--contrast` | integer | `20` | Contrast adjustment (-100 to 100). |

---

### saturation

- **Description:** Adjust color saturation.
- **Command template:** `magick "$INPUT" -modulate 100,"$SATURATION",100 "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `saturation` | `--saturation` | integer | `100` | Saturation level. `100`=normal, `0`=grayscale, `200`=double. |

---

### sepia

- **Description:** Apply sepia tone effect.
- **Command template:** `magick "$INPUT" -sepia-tone 80% "$OUTPUT"`
- **Parameters:** none.

---

### vignette

- **Description:** Apply vignette effect.
- **Command template:** `magick "$INPUT" -vignette 0x"$STRENGTH" "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `strength` | `--strength` | integer | `50` | Vignette strength. |

---

### color_overlay

- **Description:** Apply color overlay.
- **Command template:** `magick "$INPUT" -fill "$COLOR" -colorize "$OPACITY"% "$OUTPUT"`
- **Parameters:**

| Parameter | CLI flag | Type | Default | Description |
|---|---|---|---|---|
| `color` | `--color` | string (hex) | `"#000000"` | Overlay color. Pattern: `^#[0-9a-fA-F]{6}$`. |
| `opacity` | `--opacity` | integer | `30` | Overlay opacity percentage (0-100). |

---

## Composites

Composites chain multiple effects in sequence. Each step uses a specific effect with fixed parameter values (which can be overridden in user `effects.yaml`).

### blur-brightness80

- **Description:** Blur then dim to 80% brightness.
- **Chain:** `blur (0x8) -> brightness (-20)`

### blackwhite-blur

- **Description:** Convert to grayscale then blur.
- **Chain:** `blackwhite -> blur (0x8)`

### blackwhite-brightness80

- **Description:** Convert to grayscale then dim.
- **Chain:** `blackwhite -> brightness (-20)`

### negate-brightness80

- **Description:** Invert colors then adjust brightness.
- **Chain:** `negate -> brightness (+20)`

---

## Presets

Presets are named configurations that resolve to either a single effect (with fixed parameters) or a composite.

### dark_blur

- **Description:** Dark blurred background for overlays.
- **Type:** composite
- **Target:** `blur-brightness80`

### subtle_blur

- **Description:** Gentle blur effect.
- **Type:** effect
- **Target:** `blur`
- **Params:** `blur: "0x4"`

### dim

- **Description:** Slightly dimmed image.
- **Type:** effect
- **Target:** `brightness`
- **Params:** `brightness: -30`

### high_contrast

- **Description:** High contrast effect.
- **Type:** effect
- **Target:** `contrast`
- **Params:** `contrast: 40`

### desaturated

- **Description:** Reduced color saturation.
- **Type:** effect
- **Target:** `saturation`
- **Params:** `saturation: 50`

### warm_overlay

- **Description:** Warm orange tint.
- **Type:** effect
- **Target:** `color_overlay`
- **Params:** `color: "#ff8800"`, `opacity: 20`

### cool_overlay

- **Description:** Cool blue tint.
- **Type:** effect
- **Target:** `color_overlay`
- **Params:** `color: "#0088ff"`, `opacity: 20`

---

## User-defined effects

To add your own effect, create or extend `effects.yaml` in your project root or user config directory. (BHV-0036)

Example user `~/.config/wallpaper-effects-generator/effects.yaml`:

```yaml
version: "1.0"

effects:
  my_effect:
    description: "Custom sharpening effect"
    command: 'magick "$INPUT" -sharpen 0x2 "$OUTPUT"'
```

> **Note:** The `version` field in project and user `effects.yaml` files is optional.
> The merge logic always restores the package layer's `version` as the canonical value,
> so any `version` you specify in an override file is ignored.

The user layer has the highest precedence. To override a built-in effect's default parameters, redefine only the parameter block:

```yaml
effects:
  blur:
    description: "Apply Gaussian blur (stronger default)"
    command: 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
    parameters:
      blur:
        type: blur_geometry
        cli_flag: "--blur"
        default: "0x16"
        description: "Blur geometry (RADIUSxSIGMA)"
```

(BHV-0036, BHV-0043)

---

## Effects load API (for library consumers)

The `layered-effects` package provides:

- `configure(package_effects_file, project_root=None, user_effects_file=None)` — must be called once at startup to configure paths and clear any cached result. (BHV-0031)
- `load_effects()` — loads and merges all three layers, returning an `EffectsConfig` instance. The result is cached; subsequent calls return the same instance unless `configure()` is called again. (BHV-0032)

**Error types:** (BHV-0035)

| Exception | Attributes | When raised |
|---|---|---|
| `EffectsLoadError` | `file_path`, `reason` | A layer's YAML file cannot be read or parsed. |
| `EffectsValidationError` | `message`, `layer` | The merged effects configuration fails validation. |

Both inherit from `EffectsError` (catch-all base class).
