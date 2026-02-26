# How-to: Install and Uninstall the Container Image

Build (install) or remove (uninstall) the `wallpaper-effects:latest` container image using `wallpaper-process install` / `wallpaper-process uninstall`.

<!-- BHV IDs: BHV-0075, BHV-0076, BHV-0077 -->

---

## Prerequisites

- `wallpaper-process` is installed:
  ```bash
  uv pip install -e packages/orchestrator
  ```
- Docker or Podman is installed and its daemon is running.

---

## Install

### Build with the default engine (Docker)

```bash
wallpaper-process install
```

This runs `docker build` against the project's `Dockerfile.imagemagick`, tagging the result as `wallpaper-effects:latest`. The image bundles `wallpaper-core` and ImageMagick, so no host ImageMagick installation is needed for container-mode execution. (BHV-0075)

### Build with Podman

```bash
wallpaper-process install --engine podman
```

(BHV-0075)

### Preview the build command without executing

```bash
wallpaper-process install --dry-run
```

Prints the full `docker build ...` command (including the Dockerfile path and build context) without running it. Also displays validation checks (Dockerfile exists, engine binary found). No image is built. (BHV-0077)

---

## Uninstall

### Remove the image (with confirmation prompt)

```bash
wallpaper-process uninstall
```

Displays the image name and asks for confirmation before removing. (BHV-0076)

### Remove without a confirmation prompt

```bash
wallpaper-process uninstall --yes
```

Skips the prompt and removes immediately. (BHV-0076)

### Remove using Podman

```bash
wallpaper-process uninstall --engine podman
```

### Preview the removal command without executing

```bash
wallpaper-process uninstall --dry-run
```

Prints the `docker rmi wallpaper-effects:latest` command without executing it. No image is removed. (BHV-0077)

---

## See also

- [Run Effects in a Container](run-in-container.md)
- [wallpaper-process CLI Reference](../reference/cli-orchestrator.md)
- [Host Mode vs Container Mode](../explanation/host-vs-container.md)
