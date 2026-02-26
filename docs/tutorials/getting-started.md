# Tutorial: Getting Started with wallpaper-effects-generator

## Goal

By the end of this tutorial you will have:

1. Installed `wallpaper-core` from source using `uv`.
2. Applied a built-in effect to a real image.
3. Verified that the output file was written to disk.
4. Listed all available effects so you know what else is possible.

<!-- BHV IDs: BHV-0037, BHV-0038, BHV-0047, BHV-0049, BHV-0044, BHV-0045, BHV-0046 -->

---

## Prerequisites

- Python 3.12 or later is installed.
- `uv` is installed (`pip install uv` or see https://docs.astral.sh/uv/).
- ImageMagick is installed and the `magick` binary is on your PATH. Verify with:
  ```bash
  magick --version
  ```
- You have cloned the repository:
  ```bash
  git clone <repo-url>
  cd wallpaper-effects-generator
  ```

---

## Steps

### 1. Install the development environment

Run the following from the repository root:

```bash
make dev
```

This installs all packages in editable mode and sets up pre-commit hooks.

Alternatively, install only `wallpaper-core`:

```bash
uv pip install -e packages/core
```

### 2. Verify the installation

Confirm that `wallpaper-core` is available:

```bash
wallpaper-core --help
```

You should see the top-level help listing the `process`, `batch`, `show`, `info`, and `version` subcommands. (BHV-0037)

Check the installed version:

```bash
wallpaper-core version
```

This prints the version string, for example `wallpaper-effects v0.1.0`. (BHV-0046)

### 3. Inspect the current configuration

Before processing any image, check that settings and effects are loaded correctly:

```bash
wallpaper-core info
```

The output shows the current core settings (parallel, strict, max workers, verbosity, backend binary) and the count of available effects. (BHV-0045)

### 4. List available effects

```bash
wallpaper-core show effects
```

This prints a table of all built-in effect names, their descriptions, and any configurable parameters. (BHV-0044)

### 5. Apply an effect to an image

Apply the `blur` effect to a JPEG image:

```bash
wallpaper-core process effect /path/to/input.jpg --effect blur
```

Because `-o` is omitted, the output is written to the configured default output directory (`/tmp/wallpaper-effects` by default). The output file path follows the hierarchical convention: (BHV-0047, BHV-0049)

```
/tmp/wallpaper-effects/input/effects/blur.jpg
```

To write to a specific directory instead:

```bash
wallpaper-core process effect /path/to/input.jpg --effect blur -o ~/my-wallpapers
```

Output will be at `~/my-wallpapers/input/effects/blur.jpg`. (BHV-0047)

### 6. Apply an effect with a custom parameter

The `blur` effect exposes a `--blur` flag for overriding the blur geometry:

```bash
wallpaper-core process effect input.jpg --effect blur --blur 0x16
```

This applies a stronger blur (`0x16`) instead of the default (`0x8`). (BHV-0048)

---

## Verification

Confirm the output file exists:

```bash
ls /tmp/wallpaper-effects/input/effects/
```

You should see `blur.jpg` (or whichever extension matches your input image).

If the output directory did not exist, `wallpaper-core` created it automatically.

---

## Next steps

- See [Apply a Single Effect](../how-to/apply-single-effect.md) for more per-effect options.
- See [Batch-Process Images](../how-to/batch-process.md) to generate all effects at once.
- See [wallpaper-core CLI Reference](../reference/cli-core.md) for a full flag listing.
- See [Built-in Effects, Composites, and Presets](../reference/effects.md) for what effects are available.
