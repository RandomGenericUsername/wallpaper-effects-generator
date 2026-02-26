# How-to: Apply a Composite Effect

Apply a named composite (a chain of multiple effects) to an image using `wallpaper-core process composite`.

<!-- BHV IDs: BHV-0052, BHV-0049, BHV-0050, BHV-0054 -->

---

## Prerequisites

- `wallpaper-core` is installed.
- You know the name of the composite to apply. Run `wallpaper-core show composites` to list all composites with their effect chains.

---

## Steps

### Basic usage

```bash
wallpaper-core process composite <input-image> --composite <composite-name>
```

Example:

```bash
wallpaper-core process composite wallpaper.jpg --composite blur-brightness80
```

The composite chains effects in sequence. For `blur-brightness80` the sequence is `blur -> brightness`. The final output is written under the configured default directory:

```
/tmp/wallpaper-effects/wallpaper/composites/blur-brightness80.jpg
```

(BHV-0052, BHV-0049)

### Specify an output directory

```bash
wallpaper-core process composite wallpaper.jpg --composite blackwhite-blur -o ~/wallpapers-out
```

Output: `~/wallpapers-out/wallpaper/composites/blackwhite-blur.jpg`

### Use a flat output structure

```bash
wallpaper-core process composite wallpaper.jpg --composite blur-brightness80 --flat
```

Output: `/tmp/wallpaper-effects/wallpaper/blur-brightness80.jpg` (no `composites/` subdirectory). (BHV-0050)

### Preview the chain without executing

```bash
wallpaper-core process composite wallpaper.jpg --composite blur-brightness80 --dry-run
```

The `--dry-run` flag prints each step's resolved `magick ...` command without executing any of them. (BHV-0054)

---

## See also

- [Apply a Single Effect](apply-single-effect.md)
- [Apply a Preset](apply-preset.md)
- [Built-in Effects, Composites, and Presets](../reference/effects.md)
- [wallpaper-core CLI Reference](../reference/cli-core.md)
