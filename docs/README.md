# Wallpaper Effects Generator Documentation

**YAML-driven wallpaper effects processor using ImageMagick**

## Project Overview

This monorepo contains three packages for wallpaper image effects processing:

| Package | Command | Purpose | Documentation |
|---------|---------|---------|---------------|
| **layered-settings** | - | Configuration system | [packages/settings/](../packages/settings/) |
| **wallpaper-core** | `wallpaper-core` | Local execution | [packages/core/](../packages/core/) |
| **wallpaper-orchestrator** | `wallpaper-process` | Containerized execution | [packages/orchestrator/](../packages/orchestrator/) |

## Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd wallpaper-effects-generator
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Local Execution (wallpaper-core)

Requires ImageMagick installed on your system.

```bash
# Process single effect
wallpaper-core process effect input.jpg output.jpg --effect blur

# Generate all variations
wallpaper-core batch all input.jpg /output/directory
```

📖 **Full Documentation**: [packages/core/README.md](../packages/core/README.md)

### Containerized Execution (wallpaper-orchestrator)

No ImageMagick installation required - runs in Docker/Podman containers.

```bash
# One-time setup: build container image
wallpaper-process install

# Process with effects
wallpaper-process process effect input.jpg output.jpg blur

# Generate all variations (runs on host, not containerized)
wallpaper-process batch all input.jpg /output/directory
```

📖 **Full Documentation**: [packages/orchestrator/README.md](../packages/orchestrator/README.md)

## Architecture

```
wallpaper-effects-generator/
├── packages/
│   ├── settings/           # layered-settings package
│   ├── core/              # wallpaper-core package
│   └── orchestrator/      # wallpaper-orchestrator package
├── docs/
│   ├── README.md          # This file
│   ├── STATUS.md          # Project status and next steps
│   └── plans/             # Design documents
└── settings.toml          # Project configuration
```

## Package Choice

**Use wallpaper-core when:**
- You have ImageMagick installed locally
- You want direct control and minimal overhead
- You're developing or debugging effects

**Use wallpaper-orchestrator when:**
- You want isolated, reproducible execution
- You don't want to install ImageMagick
- You need portability across systems

## Configuration

Settings are managed via layered configuration:

1. Package defaults (built-in)
2. Project settings (`./settings.toml`)
3. User settings (`~/.config/wallpaper-effects/settings.toml`)
4. CLI overrides

Example `settings.toml`:
```toml
[core.execution]
parallel = true
max_workers = 4

[orchestrator.container]
engine = "docker"
image_name = "wallpaper-effects:latest"
```

## Development Status

✅ **Phase 4 Complete** - All packages functional and production-ready

- 153 tests passing (52 orchestrator + 101 core)
- Container execution validated
- Real-world testing complete

See [STATUS.md](STATUS.md) for detailed project status and next steps.

## Documentation

- **Project Status**: [STATUS.md](STATUS.md)
- **Architecture Design**: [plans/2026-01-31-monorepo-refactor-design.md](plans/2026-01-31-monorepo-refactor-design.md)
- **Package READMEs**: See individual package directories

---

**Last Updated**: 2026-02-04
