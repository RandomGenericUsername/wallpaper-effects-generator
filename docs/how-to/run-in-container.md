# How-to: Run Effects in a Container

Use `wallpaper-process` to execute effects inside a Docker or Podman container. This does not require ImageMagick to be installed on your host machine.

<!-- BHV IDs: BHV-0067, BHV-0074, BHV-0078, BHV-0079, BHV-0081 -->

---

## Prerequisites

- The container image is installed. If not, run:
  ```bash
  wallpaper-process install
  ```
  See [Install the Container Image](install-container.md) for details.
- Docker or Podman is installed and running on your host.

---

## Steps

### Process a single effect in the container

```bash
wallpaper-process process effect wallpaper.jpg --effect blur
```

`wallpaper-process` builds a `docker run` (or `podman run`) command, mounts the input file read-only and the output directory read-write, and invokes `wallpaper-core` inside the container. The container is removed after each run (`--rm`). (BHV-0074, BHV-0078)

The container mounts are:
- Input: `{abs-input-path}:/input/{filename}:ro` — the original filename is preserved, not renamed to `image.jpg`.
- Output: `{abs-output-dir}:/output:rw`

(BHV-0074)

### Process a composite in the container

```bash
wallpaper-process process composite wallpaper.jpg --composite blur-brightness80
```

### Process a preset in the container

```bash
wallpaper-process process preset wallpaper.jpg --preset dark_blur
```

### Specify an output directory

All process subcommands accept `-o` / `--output-dir`:

```bash
wallpaper-process process effect wallpaper.jpg --effect blur -o ~/wallpapers-out
```

### Use a flat output structure

```bash
wallpaper-process process effect wallpaper.jpg --effect blur --flat
```

### Preview the container command without executing

```bash
wallpaper-process process effect wallpaper.jpg --effect blur --dry-run
```

The `--dry-run` flag prints both the host `docker run ...` command (with all mount arguments) and the inner `magick ...` command that will execute inside the container. No container is spawned. (BHV-0079)

### Run batch in the container environment

`wallpaper-process batch` delegates to the core batch engine and runs **on the host** (not in the container):

```bash
wallpaper-process batch all wallpaper.jpg
```

Batch supports the same flags as `wallpaper-core batch`: `--sequential`, `--no-strict`, `--flat`, `--dry-run`. (BHV-0081)

### List available effects, composites, and presets

```bash
wallpaper-process show effects
wallpaper-process show composites
wallpaper-process show presets
wallpaper-process show all
```

Show commands run on the host. (BHV-0067)

---

## See also

- [Install/Uninstall the Container Image](install-container.md)
- [Preview Commands Without Executing](dry-run.md)
- [wallpaper-process CLI Reference](../reference/cli-orchestrator.md)
- [Host Mode vs Container Mode](../explanation/host-vs-container.md)
