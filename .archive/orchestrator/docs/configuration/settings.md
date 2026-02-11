# Settings Reference

Configuration via `settings.yaml`.

---

## Configuration File Location

```
~/.config/wallpaper-effects/settings.yaml
```

---

## Configuration Structure

```yaml
container:
  runtime: auto
  image: wallpaper-effects

execution:
  parallel: true
  strict: true

output:
  format: png
  quality: 95
  categorized: true
```

---

## Container Settings

### `runtime`

| Property | Value |
|----------|-------|
| Type | String |
| Default | `"auto"` |
| Options | `"auto"`, `"docker"`, `"podman"` |

CLI override: `--runtime`

### `image`

| Property | Value |
|----------|-------|
| Type | String |
| Default | `"wallpaper-effects"` |

Container image name/tag.

---

## Execution Settings

### `parallel`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

CLI override: `--sequential`

### `strict`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

CLI override: `--no-strict`

---

## Output Settings

### `format`

| Property | Value |
|----------|-------|
| Type | String |
| Default | `"png"` |

### `quality`

| Property | Value |
|----------|-------|
| Type | Integer |
| Default | `95` |

### `categorized`

| Property | Value |
|----------|-------|
| Type | Boolean |
| Default | `true` |

CLI override: `--flat`

---

## Configuration Precedence

```
CLI Arguments  →  Settings File  →  Defaults
   (highest)                       (lowest)
```

---

## See Also

- [Container Settings](container-settings.md)
