# wallpaper_orchestrator

Container orchestrator for the wallpaper effects processor.

## Features

- Container engine support (Docker and Podman)
- Isolated effects processing
- Portable, reproducible builds
- Simple install/uninstall commands

## Installation

```bash
cd packages/orchestrator
uv pip install -e .
```

## Usage

```bash
# Install container image
wallpaper-process install

# Process with container
wallpaper-process process input.jpg output.jpg blur

# Uninstall container image
wallpaper-process uninstall
```

## Development

See root workspace documentation for development setup.
