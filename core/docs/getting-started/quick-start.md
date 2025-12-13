# Quick Start

Your first wallpaper effect in under 2 minutes.

---

## Prerequisites

- Core tool installed (see [Installation](installation.md))
- A wallpaper image (PNG, JPG, JPEG)

---

## Step 1: List Available Effects

```bash
wallpaper-effects-process show all
```

Output:

```
Effects (9):
  blur          - Apply Gaussian blur
  blackwhite    - Convert to grayscale
  negate        - Invert colors
  brightness    - Adjust brightness/contrast
  contrast      - Adjust contrast
  saturation    - Adjust color saturation
  sepia         - Apply sepia tone effect
  vignette      - Apply vignette effect
  color_overlay - Apply color overlay

Composites (4):
  blur-brightness80     - Blur then dim to 80% brightness
  blackwhite-blur       - Convert to grayscale then blur
  ...

Presets (7):
  dark_blur, subtle_blur, dim, ...
```

---

## Step 2: Apply a Single Effect

```bash
# Apply blur effect
wallpaper-effects-process process effect wallpaper.png blurred.png -e blur

# Apply with custom parameter
wallpaper-effects-process process effect wallpaper.png blurred.png -e blur --blur 0x12
```

---

## Step 3: Batch Generate All Effects

```bash
# Generate all effects, composites, and presets
wallpaper-effects-process batch all wallpaper.png /output/dir
```

Output structure:

```
/output/dir/
└── wallpaper/
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

---

## Step 4: Use Verbosity Options

```bash
# Quiet mode (errors only)
wallpaper-effects-process -q batch all wallpaper.png /output

# Verbose mode (show commands)
wallpaper-effects-process -v batch all wallpaper.png /output

# Debug mode (all details)
wallpaper-effects-process -vv batch all wallpaper.png /output
```

---

## Next Steps

- [Usage Guide](../guides/usage.md) - Detailed usage instructions
- [Extending Effects](../guides/extending-effects.md) - Add your own effects
- [Configuration](../configuration/settings.md) - Customize settings

