# wallpaper_orchestrator

Container orchestrator for wallpaper effects processing with Docker/Podman support.

## Overview

The orchestrator package provides containerized execution of wallpaper effects, offering isolation, reproducibility, and portability. All image processing happens inside containers - no need to install ImageMagick on your host system.

## Features

- **Container Execution**: Run effects inside Docker/Podman containers
- **Isolation**: Isolated execution environment, reproducible results
- **Portability**: Works anywhere Docker/Podman runs
- **No Dependencies**: ImageMagick bundled in container image
- **Simple Commands**: Install image, run effects, uninstall

## Installation

```bash
# From workspace root
uv sync

# Install orchestrator package
cd packages/orchestrator
uv pip install -e .
```

## Quick Start

```bash
# 1. Build container image (one-time setup)
wallpaper-process install

# 2. Process images (runs in container)
wallpaper-process process effect input.jpg output.jpg blur

# 3. When done, remove image
wallpaper-process uninstall
```

## Commands

### Container Management

**Install container image:**
```bash
wallpaper-process install                # Use default engine (docker)
wallpaper-process install --engine podman  # Use podman
```

**Uninstall container image:**
```bash
wallpaper-process uninstall             # With confirmation
wallpaper-process uninstall --yes       # Skip confirmation
```

### Process Commands (Container Execution)

**Apply single effect:**
```bash
wallpaper-process process effect input.jpg output.jpg blur
wallpaper-process process effect photo.png result.png darken
```

**Apply composite:**
```bash
wallpaper-process process composite input.jpg output.jpg dark
```

**Apply preset:**
```bash
wallpaper-process process preset input.jpg output.jpg dark_vibrant
```

### Info Commands (Host Execution)

These commands run on the host (no container):

```bash
wallpaper-process info       # Show configuration
wallpaper-process version    # Show version
```

## Architecture

### Container Execution Model

When you run a process command, the orchestrator:

1. Validates container image exists
2. Mounts input file (read-only) and output directory (read-write)
3. Executes `wallpaper-core` inside container
4. Returns results to your output location

**Volume Mounts:**
- Input: `{your-input}:/input/image.jpg:ro` (read-only)
- Output: `{your-output-dir}:/output:rw` (read-write)

**Example:**
```bash
$ wallpaper-process process effect ~/photo.jpg ~/output/blurred.jpg blur

# Internally runs:
# docker run --rm \
#   -v ~/photo.jpg:/input/image.jpg:ro \
#   -v ~/output:/output:rw \
#   wallpaper-effects:latest \
#   process effect /input/image.jpg /output/blurred.jpg blur
```

### Package Structure

```
wallpaper_orchestrator/
├── cli/
│   ├── main.py              # CLI entry point (wallpaper-process)
│   └── commands/
│       ├── install.py       # Build container image
│       └── uninstall.py     # Remove container image
├── config/
│   ├── settings.py          # OrchestratorSettings
│   └── unified.py           # UnifiedConfig (core + orchestrator)
└── container/
    └── manager.py           # ContainerManager (execution)
```

## Configuration

Settings are managed via `layered_settings` with multiple layers:

1. Package defaults (built-in)
2. Project settings (`./settings.toml`)
3. User settings (`~/.config/wallpaper-effects/settings.toml`)
4. CLI overrides

### Orchestrator Settings

**Container engine:**
```toml
# ~/.config/wallpaper-effects/settings.toml
[orchestrator.container]
engine = "podman"  # or "docker" (default)
```

**Custom registry:**
```toml
[orchestrator.container]
image_registry = "ghcr.io/username"
image_name = "wallpaper-effects:latest"
```

## vs. wallpaper-core

**Use orchestrator when:**
- You want isolated, reproducible execution
- You don't want to install ImageMagick
- You need portability across systems
- You're okay with Docker/Podman requirement

**Use core when:**
- You want direct control over ImageMagick
- You have ImageMagick installed already
- You want minimal overhead
- You don't need containers

**Installation:**
```bash
# Core only (local execution)
pip install wallpaper-core
# Command: wallpaper-core

# Orchestrator (containerized execution)
pip install wallpaper-orchestrator
# Command: wallpaper-process
```

## Troubleshooting

**"Container image not found"**
```bash
# Solution: Install the image
wallpaper-process install
```

**"docker: command not found"**
```bash
# Solution: Install Docker or switch to Podman
# Install Docker: https://docs.docker.com/get-docker/
# Or use Podman:
wallpaper-process install --engine podman
```

**"permission denied" on output**
```bash
# Solution: Ensure output directory is writable
mkdir -p output
chmod 755 output
```

## Development

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=wallpaper_orchestrator

# Type checking
mypy src/wallpaper_orchestrator

# Format code
black src/ tests/
isort src/ tests/
```

## Security

The container image:
- Runs as non-root user (UID 1000)
- Input mounts are read-only (`:ro`)
- Output directory is the only writable mount (`:rw`)
- Container is removed after execution (`--rm`)

## License

MIT
