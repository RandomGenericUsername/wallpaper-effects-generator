# Container Settings

Container-specific configuration.

---

## Runtime Selection

### Auto-Detection (Default)

```yaml
container:
  runtime: auto
```

Checks in order:
1. Docker
2. Podman

### Force Docker

```yaml
container:
  runtime: docker
```

Or via CLI:

```bash
wallpaper-effects --runtime docker batch all input.png /output
```

### Force Podman

```yaml
container:
  runtime: podman
```

---

## Container Image

### Default Image

```yaml
container:
  image: wallpaper-effects
```

### Custom Image/Tag

```yaml
container:
  image: myregistry/wallpaper-effects:v1.0
```

---

## Volume Mounting

Automatic mounts:

| Host Path | Container Path | Mode |
|-----------|----------------|------|
| Input directory | `/input` | Read-only |
| Output directory | `/output` | Read-write |

---

## Environment Variables

Pass environment variables to container:

```yaml
container:
  environment:
    MAGICK_MEMORY_LIMIT: "512MB"
    MAGICK_THREAD_LIMIT: "4"
```

---

## Resource Limits

Limit container resources:

```yaml
container:
  limits:
    memory: "2g"
    cpus: "2"
```

---

## See Also

- [Container Management](../guides/containers.md)
- [Container Issues](../troubleshooting/container-issues.md)

