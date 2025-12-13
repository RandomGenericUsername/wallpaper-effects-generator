# Wallpaper Effects Generator Documentation

**A YAML-driven wallpaper effects processor using ImageMagick**

---

## Component Documentation

This project consists of two components, each with its own documentation:

| Component | Command | Documentation |
|-----------|---------|---------------|
| **Core Tool** | `wallpaper-effects-process` | [core/docs/](../core/docs/) |
| **Orchestrator** | `wallpaper-effects` | [orchestrator/docs/](../orchestrator/docs/) |

---

## Which Tool Should I Use?

| Tool | Use Case |
|------|----------|
| **Core Tool** (`wallpaper-effects-process`) | Local execution, no containers, development |
| **Orchestrator** (`wallpaper-effects`) | Containerized execution, isolation, production |

### Core Tool

Runs ImageMagick directly on your system. Requires ImageMagick installed locally.

```bash
cd core
uv run wallpaper-effects-process batch all /path/to/image.png /output/dir
```

📖 **Documentation:** [core/docs/](../core/docs/)

### Orchestrator

Runs ImageMagick inside Docker/Podman containers. No local ImageMagick needed.

```bash
cd orchestrator
uv run wallpaper-effects batch all /path/to/image.png /output/dir
```

📖 **Documentation:** [orchestrator/docs/](../orchestrator/docs/)

---

## Quick Start

```bash
# Clone and install
git clone <repository-url>
cd wallpaper-effects-generator

# Install core tool
cd core
uv sync

# Generate all effects
uv run wallpaper-effects-process batch all /path/to/wallpaper.png /output/dir

# Output: /output/dir/{image_name}/effects/, composites/, presets/
```

---

## Project Structure

```
wallpaper-effects-generator/
├── core/                    # Standalone tool
│   ├── docs/                # Core documentation
│   ├── effects/             # Effect definitions (YAML)
│   └── src/
├── orchestrator/            # Container orchestrator
│   ├── docs/                # Orchestrator documentation
│   ├── docker/              # Dockerfiles
│   └── src/
└── docs/                    # This index
    └── README.md            # You are here
```

---

## Key Features

- **YAML-driven effects**: All effects defined in `effects/effects.yaml`
- **ImageMagick only**: No PIL/Pillow, pure shell commands
- **Composites**: Chain multiple effects together
- **Presets**: Named configurations for common use cases
- **Batch generation**: Generate all effects, composites, or presets at once
- **Parallel execution**: Concurrent batch processing (configurable)
- **Rich CLI output**: Verbosity levels, progress bars, colored output

---

## Documentation Guidelines

See [DOCUMENTATION_GUIDELINES.md](../../DOCUMENTATION_GUIDELINES.md) for information on how documentation is structured.

