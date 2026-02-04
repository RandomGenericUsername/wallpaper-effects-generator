# Basic Examples

Simple usage examples.

---

## Apply Blur Effect

```bash
wallpaper-effects-process process effect wallpaper.png blurred.png -e blur
```

---

## Apply Blur with Custom Strength

```bash
wallpaper-effects-process process effect wallpaper.png blurred.png -e blur --blur 0x15
```

---

## Convert to Grayscale

```bash
wallpaper-effects-process process effect wallpaper.png grayscale.png -e blackwhite
```

---

## Dim the Image

```bash
wallpaper-effects-process process effect wallpaper.png dimmed.png -e brightness --brightness -30
```

---

## Apply Warm Overlay

```bash
wallpaper-effects-process process effect wallpaper.png warm.png -e color_overlay --color "#ff8800" --opacity 25
```

---

## Apply a Composite (Chain)

```bash
# Blur then dim
wallpaper-effects-process process composite wallpaper.png dark_blurred.png -c blur-brightness80
```

---

## Apply a Preset

```bash
# Use predefined dark_blur preset
wallpaper-effects-process process preset wallpaper.png output.png -p dark_blur
```

---

## Generate All Effects

```bash
wallpaper-effects-process batch all wallpaper.png /output/dir
```

Output:

```
/output/dir/
└── wallpaper/
    ├── effects/
    │   ├── blur.png
    │   ├── blackwhite.png
    │   └── ...
    ├── composites/
    │   └── ...
    └── presets/
        └── ...
```

---

## List Available Effects

```bash
wallpaper-effects-process show all
```

---

## Quiet Mode

```bash
wallpaper-effects-process -q batch all wallpaper.png /output
```

---

## Verbose Mode

```bash
wallpaper-effects-process -v process effect wallpaper.png out.png -e blur
```

Output shows the ImageMagick command being executed.

---

## See Also

- [Advanced Examples](advanced.md)
- [Usage Guide](../guides/usage.md)

