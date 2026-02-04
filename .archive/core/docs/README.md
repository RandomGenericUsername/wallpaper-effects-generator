# Core Tool Documentation

Documentation for `wallpaper-effects-process` - the standalone wallpaper effects processor.

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/) | Installation and first steps |
| [Guides](guides/) | Usage guides and workflows |
| [Configuration](configuration/) | Settings and effects customization |
| [Architecture](architecture/) | Technical design |
| [API Reference](api/) | CLI and library reference |
| [Examples](examples/) | Usage examples |
| [Development](development/) | Contributing and development |
| [Troubleshooting](troubleshooting/) | Common issues and solutions |
| [Errors](errors/) | Error log and incident history |

---

## What is wallpaper-effects-process?

`wallpaper-effects-process` is a standalone command-line tool that applies image effects to wallpapers using ImageMagick. Effects are defined in YAML configuration files.

### Key Features

- **YAML-driven**: All effects defined in `effects/effects.yaml`
- **ImageMagick only**: Pure shell commands, no Python image libraries
- **Composites**: Chain multiple effects together
- **Presets**: Named configurations for common use cases
- **Batch generation**: Generate all effects at once
- **Parallel execution**: Concurrent processing for speed
- **Rich output**: Configurable verbosity, progress bars

### Quick Example

```bash
cd core

# List all available effects
uv run wallpaper-effects-process show all

# Apply a single effect
uv run wallpaper-effects-process process effect input.jpg output.jpg -e blur

# Batch generate all effects
uv run wallpaper-effects-process batch all input.jpg /output/dir
```

Output is organized into `effects/`, `composites/`, and `presets/` subdirectories.

---

## Getting Help

- [Troubleshooting Guide](troubleshooting/common-issues.md)
- [Error Reference](troubleshooting/error-reference.md)

