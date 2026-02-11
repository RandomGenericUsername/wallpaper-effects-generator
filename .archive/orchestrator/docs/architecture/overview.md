# Architecture Overview

High-level design of the orchestrator.

---

## Design Principles

1. **Container isolation**: Effects run in containers
2. **Runtime agnostic**: Support Docker and Podman
3. **Transparent**: Same CLI as core tool
4. **No host dependencies**: ImageMagick not required on host

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator CLI                          │
│               (wallpaper-effects)                           │
│  ┌─────────┐  ┌─────────────┐  ┌─────────┐  ┌───────────┐  │
│  │  show   │  │   process   │  │  batch  │  │  version  │  │
│  └────┬────┘  └──────┬──────┘  └────┬────┘  └───────────┘  │
└───────┼──────────────┼──────────────┼──────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                 Container Manager                          │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  Docker Client  │  │  Podman Client  │                 │
│  └─────────────────┘  └─────────────────┘                 │
└───────────────────────────────────────────────────────────┘
        │              │
        ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                 Container Runtime                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 Container Image                      │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │          Core Tool                          │    │  │
│  │  │     (wallpaper-effects-process)             │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  │  ┌─────────────────────────────────────────────┐    │  │
│  │  │          ImageMagick                        │    │  │
│  │  └─────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
src/wallpaper_effects/
├── __init__.py
├── cli/                    # Command-line interface
│   ├── main.py             # App entry point
│   ├── show.py             # show command
│   ├── process.py          # process command
│   └── batch.py            # batch command
├── container/              # Container management
│   ├── manager.py          # Container lifecycle
│   ├── docker.py           # Docker client
│   └── podman.py           # Podman client
└── config/                 # Configuration
    └── settings.py         # Settings models
```

---

## Container Lifecycle

1. **Create**: Start container with volume mounts
2. **Execute**: Run core tool command
3. **Capture**: Collect stdout/stderr
4. **Cleanup**: Remove container

```
CLI Command → Container Create → Execute → Output → Container Remove
```

---

## Volume Mounting

```
Host                          Container
────────────────────────────────────────
/path/to/input.png     →     /input/input.png (ro)
/path/to/output/       →     /output/ (rw)
```

---

## See Also

- [Data Flow](data-flow.md)
- [Core Tool Architecture](../../../core/docs/architecture/overview.md)
