# Container Management

Managing the wallpaper-effects container.

---

## Building the Container

### Using Docker

```bash
cd orchestrator
docker build -t wallpaper-effects -f docker/Dockerfile .
```

### Using Podman

```bash
cd orchestrator
podman build -t wallpaper-effects -f docker/Dockerfile .
```

---

## Container Contents

The container includes:

- Alpine Linux base
- ImageMagick 7.x
- Python 3.11+
- Core tool (`wallpaper-effects-process`)
- Effects configuration

---

## Updating the Container

After changes to the core tool or effects:

```bash
# Rebuild
docker build --no-cache -t wallpaper-effects -f docker/Dockerfile .
```

---

## Container Lifecycle

Each command:

1. Creates a new container
2. Mounts volumes
3. Executes the effect
4. Removes the container

Containers are ephemeral by default.

---

## Manual Container Execution

For debugging:

```bash
docker run --rm -it \
  -v /path/to/input:/input:ro \
  -v /path/to/output:/output:rw \
  wallpaper-effects \
  wallpaper-effects-process batch all /input/image.png /output
```

---

## Container Image Sizes

Typical sizes:

- Base image: ~50MB
- With ImageMagick: ~150MB
- Complete: ~200MB

---

## Multi-Architecture Builds

For cross-platform support:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t wallpaper-effects:latest \
  -f docker/Dockerfile .
```

---

## See Also

- [Usage Guide](usage.md)
- [Container Issues](../troubleshooting/container-issues.md)

