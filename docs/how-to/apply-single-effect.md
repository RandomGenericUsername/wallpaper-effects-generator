# How-to: Apply a Single Effect

Apply one named effect to an image using `wallpaper-core process effect`.

<!-- BHV IDs: BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0054 -->

---

## Prerequisites

- `wallpaper-core` is installed (see [Getting Started](../tutorials/getting-started.md)).
- ImageMagick is installed and the `magick` binary is on PATH.
- You know the name of the effect to apply. Run `wallpaper-core show effects` to list all available effects. (BHV-0044)

---

## Steps

### Basic usage

```bash
wallpaper-core process effect <input-image> --effect <effect-name>
```

Example:

```bash
wallpaper-core process effect wallpaper.jpg --effect blur
```

Output is written to the configured default directory (`/tmp/wallpaper-effects` by default), under a hierarchical path:

```
/tmp/wallpaper-effects/wallpaper/effects/blur.jpg
```

(BHV-0047, BHV-0049)

### Specify an output directory

Use `-o` or `--output-dir` to write results to a specific directory:

```bash
wallpaper-core process effect wallpaper.jpg --effect blur -o ~/wallpapers-out
```

Output will be at `~/wallpapers-out/wallpaper/effects/blur.jpg`. (BHV-0047)

### Use a flat output structure

By default, output is organized into type subdirectories (`effects/`, `composites/`, `presets/`). Pass `--flat` to omit the type subdirectory:

```bash
wallpaper-core process effect wallpaper.jpg --effect blur --flat
```

Output will be at `/tmp/wallpaper-effects/wallpaper/blur.jpg` (no `effects/` subdirectory). (BHV-0050)

### Override per-effect parameters

Effects that declare parameters expose named CLI flags. Pass the flag to override the default value:

```bash
# Override blur geometry (default: 0x8)
wallpaper-core process effect wallpaper.jpg --effect blur --blur 0x16

# Override brightness level (default: -20)
wallpaper-core process effect wallpaper.jpg --effect brightness --brightness -40

# Override contrast level (default: 20)
wallpaper-core process effect wallpaper.jpg --effect contrast --contrast 50

# Override saturation level (default: 100)
wallpaper-core process effect wallpaper.jpg --effect saturation --saturation 50

# Override vignette strength (default: 50)
wallpaper-core process effect wallpaper.jpg --effect vignette --strength 80

# Override color overlay color and opacity
wallpaper-core process effect wallpaper.jpg --effect color_overlay --color "#ff5500" --opacity 40
```

(BHV-0048)

### Preview the command without executing

Use `--dry-run` to see the ImageMagick command that would be run, without actually executing it:

```bash
wallpaper-core process effect wallpaper.jpg --effect blur --dry-run
```

No file is written. The resolved `magick ...` command is printed. (BHV-0054)

---

## See also

- [Apply a Composite Effect](apply-composite.md)
- [Apply a Preset](apply-preset.md)
- [Preview Commands Without Executing](dry-run.md)
- [wallpaper-core CLI Reference](../reference/cli-core.md)
- [Built-in Effects, Composites, and Presets](../reference/effects.md)
