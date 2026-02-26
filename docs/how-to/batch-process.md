# How-to: Batch-Process Images

Generate multiple effects, composites, or presets for an image in one command using `wallpaper-core batch`.

<!-- BHV IDs: BHV-0057, BHV-0058, BHV-0059 -->

---

## Prerequisites

- `wallpaper-core` is installed.
- ImageMagick is installed.

---

## Steps

### Generate all effects

```bash
wallpaper-core batch effects wallpaper.jpg
```

Runs every effect in `effects.yaml` against `wallpaper.jpg`. By default, processing runs in parallel. Output is written to:

```
/tmp/wallpaper-effects/wallpaper/effects/<effect-name>.jpg
```

(BHV-0057)

### Generate all composites

```bash
wallpaper-core batch composites wallpaper.jpg
```

Output: `/tmp/wallpaper-effects/wallpaper/composites/<composite-name>.jpg`

### Generate all presets

```bash
wallpaper-core batch presets wallpaper.jpg
```

Output: `/tmp/wallpaper-effects/wallpaper/presets/<preset-name>.jpg`

### Generate everything at once

```bash
wallpaper-core batch all wallpaper.jpg
```

Runs all effects, composites, and presets. Output is organized into three subdirectories under the image stem directory. (BHV-0057)

### Specify an output directory

```bash
wallpaper-core batch all wallpaper.jpg -o ~/my-wallpapers
```

### Use flat output (no type subdirectories)

```bash
wallpaper-core batch all wallpaper.jpg --flat
```

All output files are placed directly under `/tmp/wallpaper-effects/wallpaper/` without `effects/`, `composites/`, or `presets/` subdirectories. (BHV-0058)

### Run sequentially instead of in parallel

By default, batch runs in parallel using multiple workers. Disable this with:

```bash
wallpaper-core batch all wallpaper.jpg --sequential
```

Or using the long form:

```bash
wallpaper-core batch all wallpaper.jpg --no-parallel
```

(BHV-0057)

### Continue on errors (non-strict mode)

By default, batch aborts on the first error (`--strict`). To continue processing remaining items even when some fail:

```bash
wallpaper-core batch all wallpaper.jpg --no-strict
```

(BHV-0057)

### Preview all planned commands without executing

```bash
wallpaper-core batch all wallpaper.jpg --dry-run
```

Prints the full table of planned commands and output paths for every item without executing any of them. (BHV-0059)

---

## See also

- [Preview Commands Without Executing](dry-run.md)
- [Run Effects in a Container](run-in-container.md) — for `wallpaper-process batch`
- [wallpaper-core CLI Reference](../reference/cli-core.md)
- [Configuration Reference](../reference/config.md) — to set parallel/worker defaults
