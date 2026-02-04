# Docker Build for Wallpaper Effects

This directory contains the Dockerfile for building the wallpaper effects
processor container image.

## Image Contents

- Python 3.12 (Alpine Linux base)
- ImageMagick (latest Alpine version)
- wallpaper-settings package
- wallpaper-core package
- All Python dependencies

## Building

From the project root:

```bash
docker build -f packages/orchestrator/docker/Dockerfile.imagemagick \
  -t wallpaper-effects:latest .
```

Or use the install command:

```bash
wallpaper-process install
```

## Usage

Process an image with blur effect:

```bash
docker run --rm \
  -v $(pwd)/input.jpg:/input/image.png:ro \
  -v $(pwd)/output:/output:rw \
  wallpaper-effects:latest \
  process /input/image.png /output/blurred.jpg blur
```

## Security

- Runs as non-root user (UID 1000)
- Input mounts are read-only
- Output directory is the only writable mount
