# Development Setup

Set up your development environment.

---

## Prerequisites

- Python 3.11+
- uv package manager
- ImageMagick 7.x
- Git

---

## Clone Repository

```bash
git clone <repository-url>
cd wallpaper-effects-generator/core
```

---

## Install Dependencies

```bash
# Install with dev dependencies
uv sync --dev
```

---

## Verify Installation

```bash
# Run the CLI
uv run wallpaper-effects-process version

# Run tests
uv run pytest
```

---

## Project Structure

```
core/
├── effects/              # Effect definitions
│   └── effects.yaml
├── src/wallpaper_processor/
│   ├── cli/              # CLI commands
│   ├── config/           # Configuration
│   ├── console/          # Output handling
│   └── engine/           # Processing engine
├── tests/                # Test suite
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

---

## IDE Setup

### VS Code

Recommended extensions:

- Python
- Pylance
- Ruff

Settings (`.vscode/settings.json`):

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.testing.pytestEnabled": true,
    "editor.formatOnSave": true
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WALLPAPER_EFFECTS_CONFIG_DIR` | Override config directory |

---

## See Also

- [Testing](testing.md)
- [Contributing](contributing.md)

