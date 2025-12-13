# Settings Reference

Configuration via `settings.yaml`.

---

## Configuration File Location

**Default:**

```
~/.config/wallpaper-effects/settings.yaml
```

---

## Configuration Structure

```yaml
execution:
  parallel: true
  strict: true

output:
  format: png
  quality: 95
  categorized: true

paths:
  effects_file: ""  # Empty = use package defaults
```

---

## Execution Settings

### `parallel`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

Controls batch processing mode. When `true`, effects are processed concurrently.

CLI override: `--sequential` (sets to `false`)

### `strict`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

When `true`, batch processing aborts on first failure.

CLI override: `--no-strict` (sets to `false`)

---

## Output Settings

### `format`

| Property | Value |
|----------|-------|
| Type | String |
| Default | `"png"` |
| Options | `"png"`, `"jpg"`, `"jpeg"` |

Default output format when not specified.

### `quality`

| Property | Value |
|----------|-------|
| Type | Integer |
| Default | `95` |
| Range | `1` - `100` |

JPEG quality (only used for JPEG output).

### `categorized`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

When `true`, batch output is organized into `effects/`, `composites/`, `presets/` subdirectories.

CLI override: `--flat` (sets to `false`)

---

## Path Settings

### `effects_file`

| Property | Value |
|----------|-------|
| Type | Path |
| Default | `""` (empty) |

Path to custom effects YAML file. When empty, uses package defaults merged with user overrides at `~/.config/wallpaper-effects/effects.yaml`.

---

## Configuration Precedence

```
CLI Arguments  →  Settings File  →  Defaults
   (highest)                       (lowest)
```

---

## Complete Example

```yaml
# ~/.config/wallpaper-effects/settings.yaml

execution:
  parallel: true
  strict: true

output:
  format: png
  quality: 95
  categorized: true

paths:
  effects_file: ""
```

---

## See Also

- [Effects YAML Reference](effects-yaml.md)
- [Extending Effects](../guides/extending-effects.md)

