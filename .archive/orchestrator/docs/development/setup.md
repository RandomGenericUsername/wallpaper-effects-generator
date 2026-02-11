# Development Setup

Set up your development environment.

---

## Prerequisites

- Python 3.11+
- uv package manager
- Docker or Podman
- Git

---

## Clone Repository

```bash
git clone <repository-url>
cd wallpaper-effects-generator/orchestrator
```

---

## Install Dependencies

```bash
# Install with dev dependencies
uv sync --dev
```

---

## Build Container Image

```bash
docker build -t wallpaper-effects -f docker/Dockerfile .
```

---

## Verify Installation

```bash
# Run the CLI
uv run wallpaper-effects version

# Run tests
uv run pytest
```

---

## Project Structure

```
orchestrator/
├── docker/               # Container files
│   └── Dockerfile
├── src/wallpaper_effects/
│   ├── cli/              # CLI commands
│   ├── container/        # Container management
│   └── config/           # Configuration
├── tests/                # Test suite
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

---

## Working with Core Tool

The orchestrator depends on the core tool. When developing:

1. Make changes to core tool
2. Rebuild container image
3. Test with orchestrator

```bash
# After core changes
cd orchestrator
docker build --no-cache -t wallpaper-effects -f docker/Dockerfile .
```

---

## See Also

- [Testing](testing.md)
- [Contributing](contributing.md)
