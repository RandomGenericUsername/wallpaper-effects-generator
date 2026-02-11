# Quick Start

Your first containerized wallpaper effect.

---

## Prerequisites

- Orchestrator installed (see [Installation](installation.md))
- Container image built
- A wallpaper image

---

## Step 1: List Available Effects

```bash
wallpaper-effects show all
```

---

## Step 2: Apply a Single Effect

```bash
wallpaper-effects process effect wallpaper.png blurred.png -e blur
```

The orchestrator:
1. Starts a container
2. Mounts the input/output paths
3. Runs the effect inside the container
4. Copies the result out

---

## Step 3: Batch Generate All Effects

```bash
wallpaper-effects batch all wallpaper.png /output/dir
```

Output structure:

```
/output/dir/
└── wallpaper/
    ├── effects/
    │   ├── blur.png
    │   └── ...
    ├── composites/
    │   └── ...
    └── presets/
        └── ...
```

---

## Step 4: Specify Container Runtime

```bash
# Force Docker
wallpaper-effects --runtime docker batch all wallpaper.png /output

# Force Podman
wallpaper-effects --runtime podman batch all wallpaper.png /output
```

---

## Verbosity Options

```bash
# Quiet mode
wallpaper-effects -q batch all wallpaper.png /output

# Verbose mode (show container commands)
wallpaper-effects -v batch all wallpaper.png /output

# Debug mode
wallpaper-effects -vv batch all wallpaper.png /output
```

---

## Next Steps

- [Usage Guide](../guides/usage.md)
- [Configuration](../configuration/settings.md)
