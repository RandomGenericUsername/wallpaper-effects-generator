# Orchestrator Documentation

Documentation for `wallpaper-effects` - the containerized wallpaper effects orchestrator.

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Getting Started](getting-started/) | Installation and first steps |
| [Guides](guides/) | Usage guides and workflows |
| [Configuration](configuration/) | Settings and customization |
| [Architecture](architecture/) | Technical design |
| [API Reference](api/) | CLI reference |
| [Examples](examples/) | Usage examples |
| [Development](development/) | Contributing and development |
| [Troubleshooting](troubleshooting/) | Common issues and solutions |
| [Errors](errors/) | Error log and incident history |

---

## What is wallpaper-effects?

`wallpaper-effects` is a container orchestrator that runs ImageMagick effects processing in Docker/Podman containers. It provides isolation, consistency, and easy deployment without requiring ImageMagick installed locally.

### Key Features

- **Container isolation**: Effects run in containers
- **Multiple runtimes**: Docker or Podman
- **Consistent environment**: Same results everywhere
- **No local dependencies**: Just container runtime needed
- **Simple deployment**: Build container and run

### Quick Example

```bash
cd orchestrator
uv run wallpaper-effects batch all /path/to/wallpaper.png /output/dir
```

Output is organized into `effects/`, `composites/`, and `presets/` subdirectories.

---

## Relationship to Core Tool

The orchestrator wraps the [core tool](../../core/docs/) (`wallpaper-effects-process`). The core tool is packaged inside the containers and executed by the orchestrator.

```
┌─────────────────────────────────────────┐
│           Orchestrator CLI              │
│        (wallpaper-effects)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Docker/Podman Container         │
│  ┌───────────────────────────────────┐  │
│  │       Core Tool (inside)          │  │
│  │    (wallpaper-effects-process)    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Getting Help

- [Troubleshooting Guide](troubleshooting/common-issues.md)
- [Container Issues](troubleshooting/container-issues.md)

