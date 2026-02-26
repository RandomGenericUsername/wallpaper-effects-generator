# Wallpaper Effects Generator

A powerful, layered wallpaper effects processor with support for effects, composites (effect chains), and presets. Features configurable output directories, flexible execution modes (host or containerized), and comprehensive dry-run functionality.

## Features

- **Effects System**: Apply single or chained effects with customizable parameters
- **Composites**: Chain multiple effects together with predefined or custom combinations
- **Presets**: Preconfigured combinations for quick processing
- **Flexible Output**: Optional output directory flag (`-o/--output-dir`) with configurable defaults
- **Output Structure**: Organized output with type-based subdirectories or flat layout (`--flat`)
- **Dry-Run Preview**: See exactly what will be executed before running (`--dry-run`)
- **Batch Processing**: Generate all effects, composites, or presets in parallel
- **Layered Configuration**: Package defaults → project-level → user-level settings (XDG_CONFIG_HOME)
- **Container Support**: Run processing in Docker/Podman for consistency
- **Host Mode**: Direct execution on host for quick testing

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/wallpaper-effects-generator.git
cd wallpaper-effects-generator

# Install with uv
uv sync

# Run wallpaper-core directly
uv run wallpaper-core --help

# Or install as command
uv pip install -e packages/core
wallpaper-core --help
```

### Docker/Container Setup

For containerized execution with orchestrator:

```bash
# Install and build container image
uv run wallpaper-process install

# Run commands through container
uv run wallpaper-process process effect image.jpg --effect blur
```

## Quick Start

### Apply a Single Effect

**Without specifying output directory (uses default):**
```bash
wallpaper-core process effect input.jpg --effect blur
# Output: /tmp/wallpaper-effects/input/effect/blur.png
```

**With custom output directory:**
```bash
wallpaper-core process effect input.jpg --effect blur -o /home/user/outputs
# Output: /home/user/outputs/input/effect/blur.png
```

**With flat output structure:**
```bash
wallpaper-core process effect input.jpg --effect blur --flat
# Output: /tmp/wallpaper-effects/input/blur.png
```

### Apply a Composite (Effect Chain)

```bash
# See what will happen before executing
wallpaper-core process composite input.jpg --composite dark --dry-run

# Actually execute
wallpaper-core process composite input.jpg --composite dark -o /output

# Flat output
wallpaper-core process composite input.jpg --composite dark --flat
```

### Apply a Preset

```bash
wallpaper-core process preset input.jpg --preset dark_vibrant

# With custom output directory
wallpaper-core process preset input.jpg --preset dark_vibrant -o /output --flat
```

### Batch Generate All

Generate all effects, composites, and presets for an image:

```bash
# Without output directory (uses default)
wallpaper-core batch all input.jpg

# With output directory
wallpaper-core batch all input.jpg -o /output

# Flat structure (no type subdirectories)
wallpaper-core batch all input.jpg -o /output --flat

# Sequential processing (disable parallelization)
wallpaper-core batch all input.jpg -o /output --no-parallel
```

### Batch Generate Specific Types

```bash
# Generate all effects only
wallpaper-core batch effects input.jpg -o /output

# Generate all composites only
wallpaper-core batch composites input.jpg -o /output

# Generate all presets only
wallpaper-core batch presets input.jpg -o /output
```

## Configuration

### Default Output Directory

The default output directory is `/tmp/wallpaper-effects`. You can customize this globally through configuration.

#### Configuration Hierarchy

Settings are resolved in order (later overrides earlier):

1. **Package Defaults** (`packages/core/src/wallpaper_core/config/settings.toml`)
2. **Project-Level** (`./settings.toml` in your current working directory)
3. **User-Level** (`$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml`)

#### Setting `core.output.default_dir`

Set your preferred default output directory in any configuration file:

```toml
# User level: ~/.config/wallpaper-effects-generator/settings.toml
[core.output]
default_dir = "/home/user/my-wallpapers"
```

Or project level:

```toml
# Project level: ./settings.toml in your project directory
[core.output]
default_dir = "./wallpapers"
```

**Default value:** `/tmp/wallpaper-effects`

#### Example Configurations

```toml
# High verbosity for debugging
[core.output]
verbosity = "DEBUG"  # or "VERBOSE", "NORMAL", "QUIET"

# Disable parallel batch processing
[core.execution]
parallel = false
max_workers = 1

# Custom temporary directory
[core.processing]
temp_dir = "/tmp/wallpaper-processing"
```

### Finding Configuration Files

**Package defaults:**
```
packages/core/src/wallpaper_core/config/settings.toml
```

**User configuration directory:**
```bash
# Linux/macOS
~/.config/wallpaper-effects-generator/settings.toml

# Windows
%APPDATA%\wallpaper-effects-generator\settings.toml
```

**Project configuration:**
```
./settings.toml  # in your current working directory
```

## Command Reference

### Process Commands (Single Image)

```bash
wallpaper-core process effect INPUT_FILE --effect NAME [-o OUTPUT_DIR] [--flat] [--dry-run]
wallpaper-core process composite INPUT_FILE --composite NAME [-o OUTPUT_DIR] [--flat] [--dry-run]
wallpaper-core process preset INPUT_FILE --preset NAME [-o OUTPUT_DIR] [--flat] [--dry-run]
```

**Options:**
- `-o, --output-dir`: Output directory (optional, uses `core.output.default_dir` if not specified)
- `--flat`: Disable type-based subdirectories in output
- `--dry-run`: Preview what would be executed without running it

### Batch Commands

```bash
wallpaper-core batch effects INPUT_FILE [-o OUTPUT_DIR] [--flat] [--parallel] [--strict] [--no-parallel]
wallpaper-core batch composites INPUT_FILE [-o OUTPUT_DIR] [--flat] [--parallel] [--strict] [--no-parallel]
wallpaper-core batch presets INPUT_FILE [-o OUTPUT_DIR] [--flat] [--parallel] [--strict] [--no-parallel]
wallpaper-core batch all INPUT_FILE [-o OUTPUT_DIR] [--flat] [--parallel] [--strict] [--no-parallel]
```

**Options:**
- `-o, --output-dir`: Output directory (optional, uses `core.output.default_dir` if not specified)
- `--flat`: Disable type-based subdirectories
- `--parallel`: Enable parallel processing (default: enabled)
- `--no-parallel`: Disable parallel processing
- `--strict`: Abort on first error (default: true)
- `--no-strict`: Continue on errors

### Container Commands (Orchestrator)

When using the containerized orchestrator (`wallpaper-process`), the same syntax applies but commands run inside a Docker/Podman container:

```bash
wallpaper-process process effect INPUT_FILE --effect NAME [-o OUTPUT_DIR] [--flat] [--dry-run]
wallpaper-process process composite INPUT_FILE --composite NAME [-o OUTPUT_DIR] [--flat] [--dry-run]
wallpaper-process process preset INPUT_FILE --preset NAME [-o OUTPUT_DIR] [--flat] [--dry-run]

wallpaper-process batch effects INPUT_FILE [-o OUTPUT_DIR] [--flat] [--no-parallel]
wallpaper-process batch composites INPUT_FILE [-o OUTPUT_DIR] [--flat] [--no-parallel]
wallpaper-process batch presets INPUT_FILE [-o OUTPUT_DIR] [--flat] [--no-parallel]
wallpaper-process batch all INPUT_FILE [-o OUTPUT_DIR] [--flat] [--no-parallel]

wallpaper-process install    # Build and install container image
wallpaper-process uninstall  # Remove container image
```

## Output Directory Structure

### With Type Subdirectories (Default)

```
/tmp/wallpaper-effects/
└── input/                          # Based on input filename
    ├── effects/
    │   ├── blur.png
    │   ├── brighten.png
    │   └── ...
    ├── composites/
    │   ├── dark.png
    │   ├── vibrant.png
    │   └── ...
    └── presets/
        ├── dark_vibrant.png
        ├── light_minimal.png
        └── ...
```

### With Flat Structure (--flat flag)

```
/tmp/wallpaper-effects/
└── input/                          # Based on input filename
    ├── blur.png
    ├── brighten.png
    ├── dark.png
    ├── vibrant.png
    ├── dark_vibrant.png
    ├── light_minimal.png
    └── ...
```

## Breaking Changes from v0.x

### Output Directory Flag

**Old syntax (no longer works):**
```bash
wallpaper-core process effect input.jpg -e blur /output
```

**New syntax:**
```bash
wallpaper-core process effect input.jpg --effect blur -o /output
```

### Positional Arguments Removed

Output directory is now a named flag (`-o/--output-dir`) rather than a positional argument, allowing it to be optional.

**Example migration:**

Old command:
```bash
wallpaper-core process effect image.jpg effect-name /home/outputs
```

New command:
```bash
wallpaper-core process effect image.jpg --effect effect-name -o /home/outputs
```

Or use default:
```bash
wallpaper-core process effect image.jpg --effect effect-name
```

## Examples

### Basic Workflow

```bash
# 1. Preview what will happen
wallpaper-core process effect wallpaper.jpg --effect blur --dry-run

# 2. Execute with default output
wallpaper-core process effect wallpaper.jpg --effect blur

# 3. Check results
ls /tmp/wallpaper-effects/wallpaper/effects/
```

### Batch Processing

```bash
# Generate all effects and presets for an image
wallpaper-core batch all photo.jpg -o ./my-wallpapers

# Generate only effects in flat structure
wallpaper-core batch effects photo.jpg -o ./my-wallpapers --flat

# Sequential processing with error handling
wallpaper-core batch all photo.jpg -o ./my-wallpapers --no-parallel
```

### Container-Based Processing

```bash
# First, install the container image
wallpaper-process install

# Process with container (reproducible environment)
wallpaper-process process composite photo.jpg --composite dark -o ./outputs

# Batch in container
wallpaper-process batch all photo.jpg -o ./outputs
```

### Configuration-Driven Defaults

With configuration set to default output to `~/my-wallpapers`:

```bash
# Uses configured default automatically
wallpaper-core batch all photo.jpg

# Still can override with -o flag
wallpaper-core batch all photo.jpg -o /tmp/quick-test
```

## Configuration Examples

### User-Level Configuration

```bash
mkdir -p ~/.config/wallpaper-effects-generator
```

```toml
# ~/.config/wallpaper-effects-generator/settings.toml

[core.output]
# Set your default wallpaper output directory
default_dir = "/home/user/Pictures/Wallpapers"
# Control verbosity (DEBUG, VERBOSE, NORMAL, QUIET)
verbosity = "VERBOSE"

[core.execution]
# Run batch operations sequentially on slower systems
parallel = false
# Or limit workers on high-end systems
max_workers = 4

[core.backend]
# Explicitly specify ImageMagick binary if needed
binary = "/usr/bin/magick"
```

### Project-Level Configuration

```toml
# ./settings.toml in your project directory

[core.output]
default_dir = "./wallpapers-generated"

[core.execution]
parallel = true
strict = true  # Abort on first failure
```

## System Requirements

- **Python**: 3.12 or later
- **ImageMagick**: `magick` or `convert` command-line tool
- **Docker/Podman**: Required only for containerized execution

### Installing Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install imagemagick
```

**macOS:**
```bash
brew install imagemagick
```

**Fedora/RHEL:**
```bash
sudo dnf install ImageMagick
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup, testing, and contribution guidelines.

## Architecture

This is a monorepo with 4 packages:

- **`wallpaper-settings`** (`packages/settings/`) - Layered configuration system
- **`wallpaper-core`** (`packages/core/`) - Core effects engine
- **`wallpaper-effects`** (`packages/effects/`) - Effect definitions and composites
- **`wallpaper-orchestrator`** (`packages/orchestrator/`) - Container orchestration

See architecture documentation in respective package READMEs.

## Troubleshooting

### "Output directory not created"

If the output directory doesn't exist, it will be created automatically. If it fails:

```bash
# Check permissions
ls -ld /path/to/output

# Or specify a different location
wallpaper-core process effect input.jpg --effect blur -o ./my-output
```

### "ImageMagick not found"

Make sure ImageMagick is installed and the binary is available:

```bash
which magick
# or
which convert

# If not found, install it (see System Requirements above)
```

### "Container image not found"

For orchestrator commands, build the image first:

```bash
wallpaper-process install
```

### Configuration Not Being Loaded

Check the configuration file location:

```bash
echo $XDG_CONFIG_HOME
# Should be ~/.config on Linux/macOS

# Verify file exists and is readable
cat ~/.config/wallpaper-effects-generator/settings.toml
```

## License

See [LICENSE](LICENSE) file in the repository.

## Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines.
