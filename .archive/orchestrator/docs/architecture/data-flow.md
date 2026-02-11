# Data Flow

Processing pipeline through containers.

---

## Single Effect Flow

```
┌──────────┐     ┌────────────────┐     ┌─────────────────┐
│  Host    │     │   Container    │     │     Host        │
│  Input   │────▶│   Processing   │────▶│    Output       │
└──────────┘     └────────────────┘     └─────────────────┘
     │                   │                      │
     │                   ▼                      │
     │           ┌───────────────┐              │
     │           │ Core Tool     │              │
     │           │ (inside)      │              │
     │           └───────────────┘              │
     │                   │                      │
     │                   ▼                      │
     │           ┌───────────────┐              │
     │           │ ImageMagick   │              │
     │           └───────────────┘              │
     │                                          │
     └──────────────────────────────────────────┘
                  Volume Mounts
```

### Steps:

1. Orchestrator receives command
2. Creates container with volume mounts
3. Executes core tool inside container
4. Core tool runs ImageMagick command
5. Output written to mounted volume
6. Container removed

---

## Batch Flow

```
┌──────────┐
│  Input   │
│  Image   │
└────┬─────┘
     │
     ▼
┌────────────────────────────────────────────┐
│              Orchestrator                   │
│                                             │
│  Effect 1  Effect 2  Effect 3  ...         │
│     │         │         │                   │
│     ▼         ▼         ▼                   │
│  Container Container Container             │ (parallel)
│     │         │         │                   │
└─────┼─────────┼─────────┼──────────────────┘
      │         │         │
      ▼         ▼         ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ out1.png │ │ out2.png │ │ out3.png │
└──────────┘ └──────────┘ └──────────┘
```

### Steps:

1. Collect all effects/composites/presets
2. For each (parallel or sequential):
   - Start container
   - Execute effect
   - Capture output
   - Remove container
3. Return results

---

## Container Runtime Abstraction

```
┌─────────────────────────────────────────┐
│            Container Manager            │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│ Docker Client │ │ Podman Client │
└───────────────┘ └───────────────┘
        │                 │
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│    Docker     │ │    Podman     │
│    Daemon     │ │    Service    │
└───────────────┘ └───────────────┘
```

---

## See Also

- [Architecture Overview](overview.md)
- [Container Management](../guides/containers.md)
