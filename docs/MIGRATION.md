# Migration Guide: v0.x to v1.0

## Overview

Version 1.0 introduces a **major breaking change** to the CLI syntax. The most significant change is the transition from **positional output directory arguments** to an **optional `-o/--output-dir` flag**.

### Why This Change?

The new design provides several benefits:

- **Sensible defaults**: Most users don't need to specify output directories every time
- **Configuration flexibility**: Set a default output directory once in settings, use it everywhere
- **Consistency**: All commands follow the same pattern
- **Clarity**: Command syntax is more readable and self-documenting
- **Flexibility**: Override defaults only when needed with the optional flag

## Breaking Changes Summary

All commands have been modified to make the output directory optional:

| Command Type | v0.x Syntax | v1.0 Syntax |
|---|---|---|
| **Process Effect** | `wallpaper-core process effect input.jpg output.jpg --effect blur` | `wallpaper-core process effect input.jpg --effect blur` |
| **Process Composite** | `wallpaper-core process composite input.jpg output.jpg --composite dark` | `wallpaper-core process composite input.jpg --composite dark` |
| **Process Preset** | `wallpaper-core process preset input.jpg output.jpg --preset dark_vibrant` | `wallpaper-core process preset input.jpg --preset dark_vibrant` |
| **Batch Effects** | `wallpaper-core batch effects input.jpg /output/dir` | `wallpaper-core batch effects input.jpg` |
| **Batch Composites** | `wallpaper-core batch composites input.jpg /output/dir` | `wallpaper-core batch composites input.jpg` |
| **Batch Presets** | `wallpaper-core batch presets input.jpg /output/dir` | `wallpaper-core batch presets input.jpg` |
| **Batch All** | `wallpaper-core batch all input.jpg /output/dir` | `wallpaper-core batch all input.jpg` |
| **Orchestrator Process** | `wallpaper-process process effect input.jpg output.jpg --effect blur` | `wallpaper-process process effect input.jpg --effect blur` |
| **Orchestrator Batch** | `wallpaper-process batch effects input.jpg /output/dir` | `wallpaper-process batch effects input.jpg` |

## Migration Steps

### Step 1: Update Your Scripts and Commands

Replace all positional output arguments with the optional `-o/--output-dir` flag.

#### Process Commands

Change from:
```bash
wallpaper-core process effect input.jpg output.jpg --effect blur
wallpaper-core process composite input.jpg output.jpg --composite dark
wallpaper-core process preset input.jpg output.jpg --preset dark_vibrant
```

To:
```bash
# Using default output directory (from settings)
wallpaper-core process effect input.jpg --effect blur
wallpaper-core process composite input.jpg --composite dark
wallpaper-core process preset input.jpg --preset dark_vibrant

# Or explicitly specify output directory
wallpaper-core process effect input.jpg --effect blur -o /custom/path
wallpaper-core process composite input.jpg --composite dark -o /custom/path
wallpaper-core process preset input.jpg --preset dark_vibrant -o /custom/path
```

#### Batch Commands

Change from:
```bash
wallpaper-core batch effects input.jpg /output/dir
wallpaper-core batch composites input.jpg /output/dir
wallpaper-core batch presets input.jpg /output/dir
wallpaper-core batch all input.jpg /output/dir
```

To:
```bash
# Using default output directory (from settings)
wallpaper-core batch effects input.jpg
wallpaper-core batch composites input.jpg
wallpaper-core batch presets input.jpg
wallpaper-core batch all input.jpg

# Or explicitly specify output directory
wallpaper-core batch effects input.jpg -o /custom/path
wallpaper-core batch composites input.jpg -o /custom/path
wallpaper-core batch presets input.jpg -o /custom/path
wallpaper-core batch all input.jpg -o /custom/path
```

#### Orchestrator Container Commands

Change from:
```bash
wallpaper-process process effect input.jpg output.jpg --effect blur
wallpaper-process process composite input.jpg output.jpg --composite dark
wallpaper-process process preset input.jpg output.jpg --preset dark_vibrant
```

To:
```bash
# Using default output directory
wallpaper-process process effect input.jpg --effect blur
wallpaper-process process composite input.jpg --composite dark
wallpaper-process process preset input.jpg --preset dark_vibrant

# Or with custom output directory
wallpaper-process process effect input.jpg --effect blur -o /custom/path
wallpaper-process process composite input.jpg --composite dark -o /custom/path
wallpaper-process process preset input.jpg --preset dark_vibrant -o /custom/path
```

### Step 2: Configure Default Output Directory

The easiest way to upgrade is to set your preferred default output directory in your configuration file once, then use commands without specifying output directories.

#### User-Level Configuration (Recommended)

Create or edit `~/.config/wallpaper-effects-generator/settings.toml`:

```toml
[core.output]
default_dir = "/home/user/my-wallpapers"
```

This applies to all commands globally on your system.

#### Project-Level Configuration

Create or edit `./settings.toml` in your project directory:

```toml
[core.output]
default_dir = "./wallpapers"
```

This applies to commands run from this directory.

#### Finding Your Configuration Directory

**Linux/macOS:**
```bash
# User config directory
~/.config/wallpaper-effects-generator/settings.toml

# Project config (current directory)
./settings.toml
```

**Windows:**
```
%APPDATA%\wallpaper-effects-generator\settings.toml
```

### Step 3: Update Scripts and Automation

If you have scripts or automation that run these commands, update them to remove positional output path arguments:

#### Before (v0.x):
```bash
#!/bin/bash

INPUT="wallpaper.jpg"
OUTPUT="/output/results"

# Process single effect
wallpaper-core process effect "$INPUT" "$OUTPUT/effect.jpg" --effect blur

# Batch generate all
wallpaper-core batch all "$INPUT" "$OUTPUT"
```

#### After (v1.0):
```bash
#!/bin/bash

INPUT="wallpaper.jpg"

# Process single effect (uses default from settings)
wallpaper-core process effect "$INPUT" --effect blur

# Batch generate all (uses default from settings)
wallpaper-core batch all "$INPUT"

# Or with explicit output directory
wallpaper-core process effect "$INPUT" --effect blur -o /output
wallpaper-core batch all "$INPUT" -o /output
```

## Command-by-Command Examples

### Process Effect

#### v0.x Syntax (Old)
```bash
# Required both input and output
wallpaper-core process effect input.jpg output/effect.jpg --effect blur
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default output directory (from settings)
wallpaper-core process effect input.jpg --effect blur

# Option 2: Specify custom output directory
wallpaper-core process effect input.jpg --effect blur -o /custom/output

# Option 3: With additional flags
wallpaper-core process effect input.jpg --effect blur --flat --dry-run
wallpaper-core process effect input.jpg --effect blur -o /custom/output --flat
```

#### What Happens
- **v1.0 with no `-o` flag**: Output goes to `core.output.default_dir` (configured in settings)
- **v1.0 with `-o` flag**: Output goes to the specified directory
- **Default value**: If not configured, defaults to `./wallpapers-output`

### Process Composite

#### v0.x Syntax (Old)
```bash
wallpaper-core process composite input.jpg output/composite.jpg --composite dark
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core process composite input.jpg --composite dark

# Option 2: Custom output directory
wallpaper-core process composite input.jpg --composite dark -o /output

# Option 3: With flat structure
wallpaper-core process composite input.jpg --composite dark --flat
```

### Process Preset

#### v0.x Syntax (Old)
```bash
wallpaper-core process preset input.jpg output/preset.jpg --preset dark_vibrant
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core process preset input.jpg --preset dark_vibrant

# Option 2: Custom directory with flat output
wallpaper-core process preset input.jpg --preset dark_vibrant -o /output --flat

# Option 3: With dry-run to preview
wallpaper-core process preset input.jpg --preset dark_vibrant --dry-run
```

### Batch Effects

#### v0.x Syntax (Old)
```bash
# Required to specify output directory as second positional argument
wallpaper-core batch effects input.jpg /output/effects
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core batch effects input.jpg

# Option 2: Custom output directory
wallpaper-core batch effects input.jpg -o /output/effects

# Option 3: With flags
wallpaper-core batch effects input.jpg -o /output --flat --parallel
wallpaper-core batch effects input.jpg -o /output --sequential --dry-run
```

### Batch Composites

#### v0.x Syntax (Old)
```bash
wallpaper-core batch composites input.jpg /output/composites
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core batch composites input.jpg

# Option 2: Custom output directory
wallpaper-core batch composites input.jpg -o /output/composites

# Option 3: Sequential processing
wallpaper-core batch composites input.jpg -o /output --sequential
```

### Batch Presets

#### v0.x Syntax (Old)
```bash
wallpaper-core batch presets input.jpg /output/presets
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core batch presets input.jpg

# Option 2: Custom output directory
wallpaper-core batch presets input.jpg -o /output/presets

# Option 3: Flat structure
wallpaper-core batch presets input.jpg -o /output --flat
```

### Batch All

#### v0.x Syntax (Old)
```bash
# Generate all effects, composites, and presets
wallpaper-core batch all input.jpg /output/all
```

#### v1.0 Syntax (New)
```bash
# Option 1: Use default
wallpaper-core batch all input.jpg

# Option 2: Custom output directory
wallpaper-core batch all input.jpg -o /output/all

# Option 3: Flat structure (no type subdirectories)
wallpaper-core batch all input.jpg -o /output --flat

# Option 4: Sequential processing with preview
wallpaper-core batch all input.jpg -o /output --sequential --dry-run
```

## Configuration Changes

### Setting Default Output Directory

In v1.0, configure `core.output.default_dir` in your settings file instead of hardcoding paths in commands.

#### Configuration Hierarchy

Settings are resolved in order (later overrides earlier):

1. **Package Defaults** - Built-in defaults
2. **Project-Level** - `./settings.toml` in your working directory
3. **User-Level** - `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml` (usually `~/.config/`)

#### Example: User-Level Configuration

Create `~/.config/wallpaper-effects-generator/settings.toml`:

```toml
# Set your preferred default output directory
[core.output]
default_dir = "/home/user/my-wallpapers"

# Optional: Configure other settings
[core.execution]
# Disable parallel processing if you prefer sequential
parallel = false
max_workers = 1

# Set verbosity level
[core.output]
verbosity = "VERBOSE"  # or "NORMAL", "QUIET", "DEBUG"
```

#### Example: Project-Level Configuration

Create `./settings.toml` in your project directory:

```toml
# Project-specific settings override user settings
[core.output]
default_dir = "./wallpapers-output"
```

### Verifying Your Configuration

Check what output directory will be used:

```bash
# Show current configuration (runs on host)
wallpaper-core info

# For orchestrator (container-based)
wallpaper-process info
```

Look for the `core.output.default_dir` setting in the output.

## New Features in v1.0

### Flat Output Structure

The `--flat` flag (available in both v0.x and v1.0) organizes output differently:

#### Without `--flat` (Default)
```
input/
├── effects/
│   ├── blur.png
│   ├── sharpen.png
│   └── ...
├── composites/
│   ├── dark.png
│   ├── vibrant.png
│   └── ...
└── presets/
    ├── dark_vibrant.png
    ├── light_soft.png
    └── ...
```

#### With `--flat`
```
input/
├── blur.png
├── sharpen.png
├── dark.png
├── vibrant.png
├── dark_vibrant.png
└── light_soft.png
```

### Example: Batch All with Flat Structure

```bash
# Old (v0.x) - with flat output
wallpaper-core batch all input.jpg /output --flat

# New (v1.0) - same result
wallpaper-core batch all input.jpg --flat
# Or with custom directory
wallpaper-core batch all input.jpg -o /output --flat
```

## Common Scenarios

### Scenario 1: Daily Processing with Default Output

**Goal**: Process images daily without specifying output directory each time.

#### Setup (One-Time)
```bash
# Configure default output directory
mkdir -p ~/.config/wallpaper-effects-generator
cat > ~/.config/wallpaper-effects-generator/settings.toml << 'EOF'
[core.output]
default_dir = "/home/user/my-wallpapers"
EOF
```

#### Daily Usage
```bash
# Just run commands - output goes to configured directory
wallpaper-core process effect my-wallpaper.jpg --effect blur
wallpaper-core batch all my-wallpaper.jpg
```

### Scenario 2: Different Output for Different Batches

**Goal**: Process the same image for different purposes with different output directories.

```bash
# Archive batch
wallpaper-core batch all input.jpg -o ./archive

# Temporary testing
wallpaper-core batch all input.jpg -o /tmp/test --dry-run

# Production batch
wallpaper-core batch all input.jpg -o ./production --flat
```

### Scenario 3: Processing Pipeline

**Goal**: Process an image through multiple steps.

```bash
#!/bin/bash

INPUT="source.jpg"
OUTPUT_DIR="/output"

# Step 1: Apply single effect
wallpaper-core process effect "$INPUT" --effect blur -o "$OUTPUT_DIR"

# Step 2: Apply composite
wallpaper-core process composite "$INPUT" --composite dark -o "$OUTPUT_DIR"

# Step 3: Generate all variations
wallpaper-core batch all "$INPUT" -o "$OUTPUT_DIR"
```

### Scenario 4: Container-Based Processing

**Goal**: Use Docker/Podman for consistent results.

```bash
# First time: Install container image
wallpaper-process install

# Process via container
wallpaper-process process effect input.jpg --effect blur

# With custom output directory
wallpaper-process process effect input.jpg --effect blur -o /output

# Batch processing
wallpaper-process batch all input.jpg -o /output
```

## Troubleshooting

### Issue: "output_dir is a required argument"

**Cause**: You're using v0.x syntax with v1.0 code.

**Solution**: Remove the positional output argument.

```bash
# Old v0.x (fails in v1.0)
wallpaper-core process effect input.jpg output.jpg --effect blur

# New v1.0 (works)
wallpaper-core process effect input.jpg --effect blur
```

### Issue: Output goes to wrong directory

**Cause**: `core.output.default_dir` isn't configured as expected.

**Solution**: Check your configuration and set it explicitly.

```bash
# Check current configuration
wallpaper-core info

# Set default in settings
mkdir -p ~/.config/wallpaper-effects-generator
cat > ~/.config/wallpaper-effects-generator/settings.toml << 'EOF'
[core.output]
default_dir = "/home/user/my-wallpapers"
EOF
```

### Issue: Scripts fail after update

**Cause**: Scripts are still using old positional syntax.

**Solution**: Update scripts to use new flag-based syntax.

```bash
# Before (v0.x)
wallpaper-core batch all input.jpg /output

# After (v1.0)
wallpaper-core batch all input.jpg -o /output
```

### Issue: Processes fail with "permission denied" errors

**Cause**: Output directory doesn't exist or isn't writable.

**Solution**: Create the directory or use an existing writable directory.

```bash
# Create output directory if it doesn't exist
mkdir -p /your/output/directory

# Or use a home directory subdirectory
wallpaper-core batch all input.jpg -o ~/wallpapers-output
```

### Issue: Can't find effects/composites/presets

**Cause**: Effects configuration may need to be refreshed.

**Solution**: Verify effects are available.

```bash
# List available effects
wallpaper-core show effects

# List available composites
wallpaper-core show composites

# List available presets
wallpaper-core show presets
```

## Migration Checklist

Use this checklist to ensure your migration is complete:

- [ ] Read the overview and breaking changes summary
- [ ] Updated all CLI commands to remove positional output arguments
- [ ] Added `-o/--output-dir` flags where needed for custom paths
- [ ] Configured `core.output.default_dir` in settings file
- [ ] Updated shell scripts and automation to use new syntax
- [ ] Tested commands with `--dry-run` to preview changes
- [ ] Verified output is going to expected directories
- [ ] Removed any v0.x command wrappers or aliases
- [ ] Updated documentation for your projects
- [ ] Tested batch processing with both `--flat` and default structures

## Getting Help

If you encounter issues during migration:

1. **Check the Help Output**: `wallpaper-core --help` or specific command help
2. **Run with Dry-Run**: Use `--dry-run` flag to see what will happen
3. **Check Configuration**: Use `wallpaper-core info` to see current settings
4. **Review Examples**: Look at examples in the main README.md

## Summary

The migration from v0.x to v1.0 is straightforward:

1. **Remove positional output arguments** from all commands
2. **Use `-o/--output-dir`** when you need to specify custom directories
3. **Configure `core.output.default_dir`** in settings for your default location
4. **Test with `--dry-run`** to verify before running

Once you configure the default output directory, most commands become simpler and faster to type. The flexibility to override with `-o` when needed gives you the best of both worlds.
