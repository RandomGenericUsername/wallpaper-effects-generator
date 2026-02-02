# Layered Settings

A generic layered configuration system for Python applications that supports multiple file formats and configuration layers.

## Features

- **Multiple File Formats**: Supports both TOML and YAML configuration files
- **Layered Configuration**: Merge configurations from multiple sources with clear precedence rules
- **Pydantic Validation**: Automatic validation using Pydantic models
- **Schema Registry**: Register multiple configuration schemas for different namespaces
- **Type Safe**: Full type hints and mypy support
- **Zero Domain Knowledge**: Completely generic and reusable across projects

## Layer Priority

Configurations are merged in the following order (later layers override earlier ones):

1. **Package defaults** - Default configuration files shipped with packages
2. **Project root** - Project-specific configuration in the repository root
3. **User config** - User-specific configuration in home directory
4. **CLI arguments** - Runtime overrides passed as arguments

## Quick Start

### Installation

```bash
# Install from local path
pip install -e packages/settings

# Or with development dependencies
pip install -e "packages/settings[dev]"
```

### Basic Usage

**Note:** The API shown below is the planned interface. Implementation is in progress (see Task 8).

```python
from pathlib import Path
from pydantic import BaseModel, Field
from layered_settings import SchemaRegistry, configure, get_config

# Define your configuration schema using Pydantic
class DatabaseSettings(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="myapp")

class AppSettings(BaseModel):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

# Register the schema with a namespace
SchemaRegistry.register(
    namespace="app",
    model=AppSettings,
    defaults_file=Path(__file__).parent / "config" / "defaults.toml"
)

# Configure the application (call once at startup)
class RootConfig(BaseModel):
    app: AppSettings

configure(RootConfig)

# Access configuration anywhere in your application
config = get_config()
print(f"Database: {config.app.database.host}:{config.app.database.port}")
```

### Configuration File Examples

**Package defaults (flat structure):**
```toml
# config/defaults.toml
[database]
host = "localhost"
port = 5432
name = "myapp"
```

**Project/User configuration (namespaced):**
```toml
# ./settings.toml or ~/.config/myapp/settings.toml
[app.database]
host = "production.example.com"
port = 5432
name = "myapp_prod"
```

## Architecture

The layered-settings package consists of several key components:

- **registry.py** - Schema registration and namespace management
- **loader.py** - File loading with automatic format detection (TOML/YAML)
- **merger.py** - Deep merge algorithm for combining configurations
- **layers.py** - Layer discovery and file resolution
- **builder.py** - Build validated Pydantic configuration from merged data
- **errors.py** - Comprehensive error hierarchy

## Development

### Setup Development Environment

```bash
cd packages/settings

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_registry.py

# Run with verbose output
pytest -v
```

### Type Checking

```bash
# Run mypy type checker
mypy src/layered_settings
```

## License

Part of the Wallpaper Effects Generator project.

## Contributing

This package is being developed as part of the wallpaper-effects-generator monorepo refactor.
See the main project documentation for contribution guidelines.
