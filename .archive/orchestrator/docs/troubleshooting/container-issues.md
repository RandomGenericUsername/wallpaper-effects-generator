# Container Issues

Container-specific problems and solutions.

---

## Docker Daemon Not Running

**Error:**

```
Cannot connect to the Docker daemon
```

**Solution:**

Start Docker:

```bash
sudo systemctl start docker
```

---

## Podman Socket Not Available

**Error:**

```
Cannot connect to Podman
```

**Solution:**

Start Podman socket:

```bash
systemctl --user start podman.socket
```

---

## Container Build Fails

**Error:**

```
Error building container image
```

**Solutions:**

1. Check Dockerfile syntax
2. Ensure network connectivity
3. Check disk space

```bash
# Check disk space
df -h

# Prune old images
docker system prune
```

---

## Volume Mount Permission Denied

**Error:**

```
Permission denied when accessing mounted volume
```

**Solutions:**

### Docker

```bash
# Run with user mapping
docker run --user $(id -u):$(id -g) ...
```

### Podman (SELinux)

```bash
# Add :Z suffix for SELinux
podman run -v /path:/container:Z ...
```

---

## Container Timeout

**Error:**

```
Container execution timed out
```

**Solution:**

Increase timeout or use smaller images:

```yaml
# settings.yaml
container:
  timeout: 300  # 5 minutes
```

---

## Out of Memory

**Error:**

```
Container killed: OOM
```

**Solution:**

Increase memory limit:

```yaml
# settings.yaml
container:
  limits:
    memory: "4g"
```

---

## Image Pull Fails

**Error:**

```
Error pulling image
```

**Solution:**

Build locally instead:

```bash
docker build -t wallpaper-effects -f docker/Dockerfile .
```

---

## Debugging Container Issues

Run container interactively:

```bash
docker run --rm -it \
  -v /path/to/input:/input:ro \
  -v /path/to/output:/output:rw \
  wallpaper-effects \
  /bin/sh
```

Inside container:

```bash
# Check ImageMagick
magick --version

# Test effect manually
magick /input/image.png -blur 0x8 /output/test.png
```

---

## See Also

- [Common Issues](common-issues.md)
- [Container Management](../guides/containers.md)
