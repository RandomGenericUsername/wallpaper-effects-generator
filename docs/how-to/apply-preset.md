# How-to: Apply a Preset

Apply a named preset to an image using `wallpaper-core process preset`. Presets are named configurations that point to either an effect (with fixed parameters) or a composite.

<!-- BHV IDs: BHV-0053, BHV-0049, BHV-0050, BHV-0054 -->

---

## Prerequisites

- `wallpaper-core` is installed.
- You know the name of the preset to apply. Run `wallpaper-core show presets` to list all presets, their descriptions, and what they resolve to.

---

## Steps

### Basic usage

```bash
wallpaper-core process preset <input-image> --preset <preset-name>
```

Example:

```bash
wallpaper-core process preset wallpaper.jpg --preset dark_blur
```

The `dark_blur` preset applies the `blur-brightness80` composite. Output is written to:

```
/tmp/wallpaper-effects/wallpaper/presets/dark_blur.jpg
```

(BHV-0053, BHV-0049)

### Specify an output directory

```bash
wallpaper-core process preset wallpaper.jpg --preset subtle_blur -o ~/wallpapers-out
```

Output: `~/wallpapers-out/wallpaper/presets/subtle_blur.jpg`

### Use a flat output structure

```bash
wallpaper-core process preset wallpaper.jpg --preset dim --flat
```

Output: `/tmp/wallpaper-effects/wallpaper/dim.jpg` (no `presets/` subdirectory). (BHV-0050)

### Preview without executing

```bash
wallpaper-core process preset wallpaper.jpg --preset dark_blur --dry-run
```

Prints the resolved command(s) without executing. For composite-backed presets, each step in the chain is shown. (BHV-0054)

---

## See also

- [Apply a Single Effect](apply-single-effect.md)
- [Apply a Composite Effect](apply-composite.md)
- [Built-in Effects, Composites, and Presets](../reference/effects.md)
- [wallpaper-core CLI Reference](../reference/cli-core.md)
