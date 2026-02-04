# wallpaper_orchestrator

Container orchestrator for the wallpaper effects processor, providing isolated,
portable, and reproducible image processing.

## Features

- **Container Support**: Docker and Podman
- **Isolation**: Run effects in isolated containers
- **Portability**: Bundle ImageMagick with specific versions
- **Reproducibility**: Consistent behavior across systems
- **Simple Commands**: Easy install/uninstall

## Installation

```bash
# From workspace root
uv sync

# Install just orchestrator package
cd packages/orchestrator
uv pip install -e .
```

## Quick Start

```bash
# Build container image
wallpaper-process install

# Process with container (uses core functionality)
wallpaper-process process input.jpg output.jpg blur

# View configuration
wallpaper-process info

# Remove container image
wallpaper-process uninstall
```

## Configuration

### Layer Priority

1. **Package defaults** - Built-in settings
2. **Project settings** - `./settings.toml`
3. **User settings** - `~/.config/wallpaper-effects/settings.toml`
4. **CLI overrides** - Command-line flags

### Orchestrator Settings

**Container Settings:**
- `engine` (str, default="docker") - Container engine (docker or podman)
- `image_name` (str, default="wallpaper-effects:latest") - Image name
- `image_registry` (str, optional) - Registry prefix for images

**Example Configuration:**

```toml
# ~/.config/wallpaper-effects/settings.toml

[orchestrator.container]
engine = "podman"
image_registry = "ghcr.io/username"
```

## Architecture

The orchestrator package composes all configuration namespaces:

```python
from wallpaper_orchestrator.config.unified import UnifiedConfig

config = UnifiedConfig()
# Access: config.core.execution.parallel
#         config.effects.effects["blur"]
#         config.orchestrator.container.engine
```

### Package Structure

```
packages/orchestrator/
├── src/wallpaper_orchestrator/
│   ├── config/          # UnifiedConfig + OrchestratorSettings
│   ├── container/       # ContainerManager
│   ├── cli/             # CLI commands (wraps core)
│   └── docker/          # Dockerfile
├── tests/
└── pyproject.toml
```

## Commands

### Install

Build the container image:

```bash
wallpaper-process install
wallpaper-process install --engine podman
```

### Uninstall

Remove the container image:

```bash
wallpaper-process uninstall
wallpaper-process uninstall --yes  # Skip confirmation
```

### Core Commands

All core commands are available through the orchestrator:

```bash
wallpaper-process info
wallpaper-process process <input> <output> <effect>
wallpaper-process batch <input> --effects <list>
wallpaper-process show effects
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

## Container Details

The container image includes:

- Python 3.12 (Alpine Linux)
- ImageMagick (latest Alpine version)
- wallpaper-settings package
- wallpaper-core package
- All dependencies

**Security:**
- Runs as non-root user (UID 1000)
- Input mounts are read-only
- Output directory is the only writable mount

See `docker/README.md` for container build details.
