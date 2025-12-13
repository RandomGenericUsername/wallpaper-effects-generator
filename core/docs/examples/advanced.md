# Advanced Examples

Complex workflows and integrations.

---

## Custom Effect Definition

Create a custom sharpen effect:

```yaml
# ~/.config/wallpaper-effects/effects.yaml
version: "1.0"

effects:
  sharpen:
    description: "Sharpen the image"
    command: 'magick "$INPUT" -sharpen 0x"$SHARPEN" "$OUTPUT"'
    parameters:
      sharpen:
        type: integer
        cli_flag: "--sharpen"
        default: 2
        description: "Sharpen strength"
```

Use it:

```bash
wallpaper-effects-process process effect in.png out.png -e sharpen --sharpen 5
```

---

## Custom Composite

Chain multiple effects:

```yaml
# ~/.config/wallpaper-effects/effects.yaml
version: "1.0"

composites:
  sharpen-blur-dim:
    description: "Sharpen, blur, then dim"
    chain:
      - effect: sharpen
        params: { sharpen: 3 }
      - effect: blur
        params: { blur: "0x4" }
      - effect: brightness
        params: { brightness: -20 }
```

---

## Batch Processing Script

Process multiple wallpapers:

```bash
#!/bin/bash
# process_wallpapers.sh

INPUT_DIR="$1"
OUTPUT_DIR="$2"

for wallpaper in "$INPUT_DIR"/*.{jpg,png,jpeg}; do
    [ -f "$wallpaper" ] || continue
    echo "Processing: $wallpaper"
    wallpaper-effects-process -q batch all "$wallpaper" "$OUTPUT_DIR"
done
```

---

## Integration with i3/Sway

Set wallpaper with effect:

```bash
#!/bin/bash
# set_wallpaper.sh

ORIGINAL="$HOME/Pictures/wallpaper.png"
PROCESSED="/tmp/wallpaper_processed.png"

# Apply dark blur effect
wallpaper-effects-process -q process preset "$ORIGINAL" "$PROCESSED" -p dark_blur

# Set wallpaper (sway)
swaymsg output '*' bg "$PROCESSED" fill

# Or for i3 with feh
# feh --bg-fill "$PROCESSED"
```

---

## Python Integration

Use as a library:

```python
from pathlib import Path
from wallpaper_processor.config import ConfigLoader
from wallpaper_processor.engine import BatchGenerator

def generate_wallpaper_variants(input_path: str, output_dir: str):
    """Generate all effect variants for a wallpaper."""
    loader = ConfigLoader()
    config = loader.load_effects()
    
    generator = BatchGenerator(
        config=config,
        parallel=True,
        strict=False,
    )
    
    result = generator.generate_all(
        input_path=Path(input_path),
        output_dir=Path(output_dir),
    )
    
    print(f"Generated {result.succeeded}/{result.total} variants")
    return result

if __name__ == "__main__":
    generate_wallpaper_variants(
        "/path/to/wallpaper.png",
        "/output/dir",
    )
```

---

## CI/CD Integration

GitHub Actions example:

```yaml
name: Generate Wallpaper Effects

on:
  push:
    paths:
      - 'wallpapers/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install ImageMagick
        run: sudo apt-get install -y imagemagick
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Install tool
        run: |
          cd wallpaper-effects-generator/core
          uv sync
      
      - name: Generate effects
        run: |
          for img in wallpapers/*.png; do
            uv run wallpaper-effects-process batch all "$img" output/
          done
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: wallpaper-effects
          path: output/
```

---

## See Also

- [Basic Examples](basic.md)
- [Extending Effects](../guides/extending-effects.md)

