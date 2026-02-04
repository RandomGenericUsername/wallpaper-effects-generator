# Common Issues

Frequently encountered problems and solutions.

---

## Command Not Found

**Error:**

```
wallpaper-effects: command not found
```

**Solution:**

Use `uv run`:

```bash
cd orchestrator
uv run wallpaper-effects version
```

Or add to PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Container Image Not Found

**Error:**

```
Error: Image 'wallpaper-effects' not found
```

**Solution:**

Build the container image:

```bash
cd orchestrator
docker build -t wallpaper-effects -f docker/Dockerfile .
```

---

## No Container Runtime Found

**Error:**

```
Error: No container runtime found (docker or podman)
```

**Solution:**

Install Docker or Podman:

```bash
# Docker
sudo apt-get install docker.io
sudo systemctl enable --now docker

# Or Podman
sudo apt-get install podman
```

---

## Permission Denied

**Error:**

```
Permission denied: '/output/path'
```

**Solution:**

Ensure output directory exists and is writable:

```bash
mkdir -p /output/path
chmod 755 /output/path
```

---

## Effect Not Found

**Error:**

```
Effect 'effect_name' not found
```

**Solution:**

1. Check available effects:
   ```bash
   wallpaper-effects show effects
   ```

2. Verify spelling

---

## Slow Processing

**Problem:** Batch processing is slow.

**Solutions:**

1. Ensure parallel mode is enabled (default)
2. Use smaller images for testing
3. Check container resource limits

---

## See Also

- [Container Issues](container-issues.md)
- [Core Troubleshooting](../../../core/docs/troubleshooting/)

