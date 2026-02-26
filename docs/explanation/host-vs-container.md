# Host Mode vs Container Mode

An explanation of when to use `wallpaper-core` directly versus `wallpaper-process` with a container, and what the tradeoffs are.

<!-- BHV IDs: BHV-0074, BHV-0075 -->

---

## Two execution modes

`wallpaper-effects-generator` provides two CLIs for running effects:

| CLI | Mode | Requires on host |
|---|---|---|
| `wallpaper-core` | Host mode — runs `magick` directly | ImageMagick |
| `wallpaper-process` | Container mode — runs inside Docker/Podman | Docker or Podman |

---

## Host mode (wallpaper-core)

`wallpaper-core` calls `magick` (or `convert`) directly as a subprocess. The binary must be installed and on your PATH.

**When to use:**
- You already have ImageMagick installed.
- You are developing or testing effects.
- You want maximum performance without container startup overhead.
- You do not have Docker or Podman available.

**Configuration:** The `core.backend.binary` setting specifies which binary to use. Default is `"magick"`.

---

## Container mode (wallpaper-process)

`wallpaper-process` builds a `docker run` (or `podman run`) command that:

1. Mounts the input file read-only at `/input/image.jpg`.
2. Mounts the output directory read-write at `/output`.
3. Runs `wallpaper-core` inside the container (which has ImageMagick bundled).
4. Removes the container after each run (`--rm`).

(BHV-0074)

**When to use:**
- You do not have ImageMagick installed on your host and do not want to install it.
- You want a reproducible, hermetically isolated processing environment.
- You are deploying to a system that only has Docker or Podman.

**One-time setup:** The container image must be built before any `process` commands will work:

```bash
wallpaper-process install
```

(BHV-0075)

---

## What runs where

| Command | wallpaper-core | wallpaper-process |
|---|---|---|
| `process effect/composite/preset` | On host (runs `magick`) | In container |
| `batch effects/composites/presets/all` | On host | On host (delegates to core batch engine) |
| `show effects/composites/presets/all` | On host | On host |
| `info` | On host | On host |
| `version` | On host | On host |
| `install` / `uninstall` | N/A | On host (manages the container image) |

---

## Practical guidance

Use **host mode** (`wallpaper-core`) for day-to-day development:

```bash
wallpaper-core process effect input.jpg --effect blur
```

Use **container mode** (`wallpaper-process`) when you want isolation or lack ImageMagick:

```bash
wallpaper-process install           # once
wallpaper-process process effect input.jpg --effect blur
```

The command syntax for `process`, `batch`, and `show` is identical between the two CLIs. Switching from host to container mode is as simple as replacing `wallpaper-core` with `wallpaper-process`.

---

## Container image details

- Image name: `wallpaper-effects:latest`
- Default engine: Docker (configurable to Podman via `[orchestrator.container] engine = "podman"`)
- Built from `packages/orchestrator/docker/Dockerfile.imagemagick`
- The image bundles ImageMagick; no host ImageMagick installation is required for container mode.
- The container is always removed after each run (`--rm`), so no state persists between invocations.
