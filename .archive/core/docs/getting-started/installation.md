# Installation

Step-by-step installation guide for `wallpaper-effects-process`.

---

## Standard Installation

```bash
# Clone the repository
git clone <repository-url>
cd wallpaper-effects-generator/core

# Install with uv
uv sync

# Verify installation
uv run wallpaper-effects-process version
```

---

## Development Installation

For development with editable mode:

```bash
cd wallpaper-effects-generator/core
uv sync --dev
```

---

## pip Installation

If you prefer pip:

```bash
cd wallpaper-effects-generator/core
pip install -e .
```

---

## Verify Installation

```bash
# Check version
wallpaper-effects-process version

# List available effects
wallpaper-effects-process show all

# Expected output:
# Effects (9):
#   blur, blackwhite, negate, brightness, contrast, saturation, sepia, vignette, color_overlay
# Composites (4):
#   blur-brightness80, blackwhite-blur, blackwhite-brightness80, negate-brightness80
# Presets (7):
#   dark_blur, subtle_blur, dim, high_contrast, desaturated, warm_overlay, cool_overlay
```

---

## Troubleshooting

### Command not found

If `wallpaper-effects-process` is not found after pip install:

```bash
# Check if ~/.local/bin is in PATH
echo $PATH | grep -q ".local/bin" || echo "Add ~/.local/bin to PATH"

# Add to PATH (bash)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### ImageMagick not found

```bash
# Verify ImageMagick is installed
which magick || echo "ImageMagick not installed"

# Install it (see prerequisites.md)
```

---

## Next Steps

- [Quick Start](quick-start.md) - Run your first effect

