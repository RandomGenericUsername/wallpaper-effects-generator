# Installation

Step-by-step installation guide for `wallpaper-effects`.

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd wallpaper-effects-generator
```

---

## Step 2: Build Container Image

```bash
cd orchestrator

# Using Docker
docker build -t wallpaper-effects -f docker/Dockerfile .

# Or using Podman
podman build -t wallpaper-effects -f docker/Dockerfile .
```

---

## Step 3: Install Orchestrator

```bash
cd orchestrator
uv sync
```

---

## Step 4: Verify Installation

```bash
# Check version
uv run wallpaper-effects version

# Check container image
docker images | grep wallpaper-effects
# or
podman images | grep wallpaper-effects
```

---

## Development Installation

For development with editable mode:

```bash
cd orchestrator
uv sync --dev
```

---

## Troubleshooting

### Container build fails

Ensure Docker/Podman daemon is running:

```bash
sudo systemctl start docker
# or
systemctl --user start podman
```

### Command not found

Use `uv run` prefix:

```bash
uv run wallpaper-effects version
```

---

## Next Steps

- [Quick Start](quick-start.md) - Run your first effect

