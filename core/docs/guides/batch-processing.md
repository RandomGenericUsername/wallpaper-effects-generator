# Batch Processing

Generate multiple effects efficiently.

---

## Overview

The `batch` command generates multiple effects from a single input image:

```bash
wallpaper-effects-process batch [effects|composites|presets|all] INPUT OUTPUT_DIR
```

---

## Batch Types

| Type | Description |
|------|-------------|
| `effects` | All atomic effects |
| `composites` | All composite effects (chains) |
| `presets` | All preset configurations |
| `all` | Everything |

```bash
# Generate only atomic effects
wallpaper-effects-process batch effects wallpaper.png /output

# Generate everything
wallpaper-effects-process batch all wallpaper.png /output
```

---

## Output Structure

By default, output is categorized:

```
/output/
└── wallpaper/           # Named after input file
    ├── effects/
    │   ├── blur.png
    │   ├── blackwhite.png
    │   └── ...
    ├── composites/
    │   ├── blur-brightness80.png
    │   └── ...
    └── presets/
        ├── dark_blur.png
        └── ...
```

### Flat Output

Use `--flat` to disable categorization:

```bash
wallpaper-effects-process batch all wallpaper.png /output --flat
```

Result:

```
/output/
└── wallpaper/
    ├── blur.png
    ├── blackwhite.png
    ├── blur-brightness80.png
    ├── dark_blur.png
    └── ...
```

---

## Parallel vs Sequential

### Parallel (Default)

Effects are processed concurrently for speed:

```bash
wallpaper-effects-process batch all wallpaper.png /output
```

Default is controlled by `settings.yaml`:

```yaml
execution:
  parallel: true
```

### Sequential

Process one at a time:

```bash
wallpaper-effects-process batch all wallpaper.png /output --sequential
```

Use sequential when:
- Debugging issues
- Limited system resources
- Reproducible ordering needed

---

## Strict Mode

### Strict (Default)

Abort on first failure:

```bash
wallpaper-effects-process batch all wallpaper.png /output
```

### Non-Strict

Continue despite errors:

```bash
wallpaper-effects-process batch all wallpaper.png /output --no-strict
```

---

## Verbosity During Batch

```bash
# Quiet - only show errors
wallpaper-effects-process -q batch all wallpaper.png /output

# Normal - progress bar
wallpaper-effects-process batch all wallpaper.png /output

# Verbose - show each command
wallpaper-effects-process -v batch all wallpaper.png /output

# Debug - full details
wallpaper-effects-process -vv batch all wallpaper.png /output
```

---

## Performance Tips

1. **Use parallel mode** (default) for faster processing
2. **Use SSD** for output directory
3. **Reduce image size** if processing many images
4. **Use `--no-strict`** for fault tolerance in automated pipelines

---

## See Also

- [Usage Guide](usage.md)
- [Settings Reference](../configuration/settings.md)

