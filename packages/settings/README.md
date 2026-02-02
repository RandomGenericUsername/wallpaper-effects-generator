# Layered Settings

A generic layered configuration system for Python applications that supports multiple file formats and configuration layers.

## Features

- **Multiple File Formats**: Supports both TOML and YAML configuration files
- **Layered Configuration**: Merge configurations from multiple sources with clear precedence rules
- **Pydantic Validation**: Automatic validation using Pydantic models
- **Schema Registry**: Register multiple configuration schemas for different namespaces
- **Type Safe**: Full type hints and mypy support
- **Zero Domain Knowledge**: Completely generic and reusable across projects
- **Caching**: Intelligent configuration caching for optimal performance

## Installation

```bash
# Install from local path
pip install -e packages/settings

# Or with development dependencies
pip install -e "packages/settings[dev]"
```

## Quick Start

```python
from pathlib import Path
from pydantic import BaseModel, Field
from layered_settings import SchemaRegistry, configure, get_config

# 1. Define your configuration schema using Pydantic
class DatabaseSettings(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=5432)

class AppSettings(BaseModel):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

# 2. Register the schema with a namespace
SchemaRegistry.register(
    namespace="database",
    model=DatabaseSettings,
    defaults_file=Path(__file__).parent / "defaults.toml"
)

# 3. Configure the application (call once at startup)
configure(root_model=AppSettings, app_name="myapp")

# 4. Access configuration anywhere in your application
config = get_config()
print(f"Database: {config.database.host}:{config.database.port}")
```

## Layer Priority

Configurations are merged in the following order (later layers override earlier ones):

1. **Package defaults** - Default configuration files shipped with packages (flat format)
2. **Project root** - Project-specific configuration in `./settings.toml` (namespaced format)
3. **User config** - User-specific configuration in `~/.config/<app_name>/settings.toml` (namespaced format)
4. **CLI arguments** - Runtime overrides passed as arguments (highest priority)

### Configuration File Formats

**Package defaults (flat structure):**
```toml
# config/defaults.toml
[database]
host = "localhost"
port = 5432
```

**Project/User configuration (namespaced):**
```toml
# ./settings.toml or ~/.config/myapp/settings.toml
[database]
host = "production.example.com"
port = 5432
```

## Usage Examples

### Basic Usage

See [examples/basic_usage.py](examples/basic_usage.py) for a complete working example that demonstrates:
- Defining configuration schemas with Pydantic
- Registering schemas with the SchemaRegistry
- Using configure() and get_config()
- Applying CLI overrides
- Configuration caching behavior

Run it:
```bash
cd packages/settings
python examples/basic_usage.py
```

### Layer Priority

See [examples/layer_priority.py](examples/layer_priority.py) for a demonstration of how configuration layers override each other in priority order.

Run it:
```bash
cd packages/settings
python examples/layer_priority.py
```

### CLI Overrides

You can override any configuration value at runtime using dotted path notation:

```python
# Override specific values
config = get_config(overrides={
    "database.host": "production.example.com",
    "database.port": 5433,
    "server.workers": 16,
})
```

Overrides are applied with the highest priority and create a fresh configuration instance (bypassing the cache).

## Architecture

The layered-settings package consists of several key components that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                        Application                          │
│                                                              │
│  configure(root_model, app_name)  →  get_config(overrides) │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      ConfigBuilder                          │
│                                                              │
│  Orchestrates the entire configuration loading process      │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ LayerDiscovery│  │  ConfigMerger │  │  FileLoader   │
│               │  │               │  │               │
│ Find config   │  │ Deep merge    │  │ Load TOML/    │
│ files in all  │  │ dictionaries  │  │ YAML files    │
│ layers        │  │               │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
        ↓
┌───────────────┐
│SchemaRegistry │
│               │
│ Package       │
│ defaults      │
└───────────────┘
```

### Component Overview

- **`registry.py`** - Schema registration and namespace management
  - `SchemaRegistry`: Class-level registry for configuration schemas
  - `SchemaEntry`: Metadata for registered schemas

- **`loader.py`** - File loading with automatic format detection
  - Supports TOML and YAML files
  - Automatic format detection based on file extension
  - Clear error messages for invalid files

- **`merger.py`** - Deep merge algorithm for combining configurations
  - Recursively merges nested dictionaries
  - Later values override earlier values
  - Preserves all non-conflicting values

- **`layers.py`** - Layer discovery and file resolution
  - Discovers configuration files in all layers
  - Handles both flat and namespaced formats
  - Skips missing files gracefully

- **`builder.py`** - Build validated Pydantic configuration
  - Orchestrates loading, merging, and validation
  - Applies CLI overrides with dotted path notation
  - Returns validated Pydantic model instances

- **`errors.py`** - Comprehensive error hierarchy
  - `SettingsError`: Base exception for all errors
  - `SettingsFileError`: File loading/parsing errors
  - `SettingsRegistryError`: Registration conflicts
  - `SettingsValidationError`: Pydantic validation failures

## API Reference

### Main API Functions

#### `configure(root_model: type[BaseModel], app_name: str) -> None`

Configure the layered settings system. Must be called before `get_config()`.

**Parameters:**
- `root_model`: Pydantic model class that defines the complete configuration schema
- `app_name`: Application name used for user config directory

**Example:**
```python
class AppConfig(BaseModel):
    database: DatabaseSettings
    server: ServerSettings

configure(root_model=AppConfig, app_name="myapp")
```

#### `get_config(overrides: dict[str, Any] | None = None) -> BaseModel`

Get the application configuration with automatic layer discovery, merging, and validation.

**Parameters:**
- `overrides`: Optional dictionary of CLI overrides using dotted path notation

**Returns:**
- Validated configuration instance of the root model type

**Raises:**
- `RuntimeError`: If `configure()` has not been called first
- `SettingsValidationError`: If configuration validation fails
- `SettingsFileError`: If a configuration file cannot be loaded

**Caching Behavior:**
- Without overrides: Configuration is cached and reused
- With overrides: Fresh instance is created (does not affect cache)

**Example:**
```python
# Get cached configuration
config = get_config()

# Get configuration with overrides (not cached)
config = get_config(overrides={"database.host": "prod.example.com"})
```

### SchemaRegistry

#### `SchemaRegistry.register(namespace: str, model: type[BaseModel], defaults_file: Path) -> None`

Register a configuration schema with a namespace.

**Parameters:**
- `namespace`: Unique identifier for the schema (e.g., "database", "server")
- `model`: Pydantic model class that defines the schema
- `defaults_file`: Path to the file containing default values

**Raises:**
- `SettingsRegistryError`: If the namespace is already registered

**Example:**
```python
SchemaRegistry.register(
    namespace="database",
    model=DatabaseSettings,
    defaults_file=Path(__file__).parent / "defaults.toml"
)
```

#### `SchemaRegistry.get(namespace: str) -> SchemaEntry | None`

Get a registered schema entry by namespace.

**Returns:**
- `SchemaEntry` if found, `None` otherwise

#### `SchemaRegistry.all_namespaces() -> list[str]`

List all registered namespace strings.

#### `SchemaRegistry.all_entries() -> list[SchemaEntry]`

List all registered schema entries.

#### `SchemaRegistry.clear() -> None`

Clear all registrations (primarily for testing).

### Error Classes

#### `SettingsError`

Base exception for all settings-related errors.

#### `SettingsFileError`

Exception raised when there are file loading or parsing errors.

**Attributes:**
- `filepath`: Path to the file that caused the error
- `reason`: Description of why the error occurred

#### `SettingsRegistryError`

Exception raised when there are registration conflicts.

**Attributes:**
- `namespace`: The namespace that caused the error
- `reason`: Description of why the error occurred

#### `SettingsValidationError`

Exception raised when Pydantic validation fails.

**Attributes:**
- `config_name`: Name of the configuration that failed validation
- `reason`: Description of why validation failed

## Best Practices

### 1. Schema Design

- Use descriptive field names and add docstrings
- Provide sensible defaults for all fields
- Use Pydantic's `Field` for descriptions and constraints
- Group related settings into nested models

```python
class DatabaseSettings(BaseModel):
    """Database connection settings."""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    pool_size: int = Field(default=10, ge=1, description="Connection pool size")
```

### 2. Schema Registration

- Register all schemas at application startup
- Use consistent namespace naming (e.g., lowercase, dotted notation)
- Keep package defaults files alongside your code

```python
def register_all_schemas() -> None:
    """Register all application schemas."""
    base_path = Path(__file__).parent

    SchemaRegistry.register("database", DatabaseSettings, base_path / "defaults.toml")
    SchemaRegistry.register("server", ServerSettings, base_path / "defaults.toml")
    SchemaRegistry.register("logging", LoggingSettings, base_path / "defaults.toml")
```

### 3. Configuration Access

- Call `configure()` once at application startup
- Use `get_config()` without arguments for normal use (utilizes cache)
- Use `get_config(overrides={...})` only for runtime overrides (e.g., CLI arguments)
- Consider storing the config in your application state if needed frequently

```python
# In main.py
def main():
    register_all_schemas()
    configure(root_model=AppConfig, app_name="myapp")

    # Get configuration once
    config = get_config()

    # Use throughout application
    start_server(config.server)
    connect_database(config.database)
```

### 4. Testing

- Use `SchemaRegistry.clear()` in test fixtures to ensure clean state
- Create temporary config files in tests using `tempfile` module
- Test with different layer combinations
- Test validation error handling

```python
import pytest
from layered_settings import SchemaRegistry

@pytest.fixture(autouse=True)
def clean_registry():
    """Clear registry before each test."""
    SchemaRegistry.clear()
    yield
    SchemaRegistry.clear()
```

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

The test suite includes 143 tests covering:
- Unit tests for each component
- Integration tests for end-to-end workflows
- Edge cases and error handling
- Type safety and validation

### Type Checking

```bash
# Run mypy type checker
mypy src/layered_settings
```

The package is fully type-annotated and passes strict mypy checks.

### Code Coverage

Run tests with coverage report:

```bash
pytest --cov=layered_settings --cov-report=html
```

Then open `htmlcov/index.html` to view the detailed coverage report.

## Troubleshooting

### Common Issues

**1. RuntimeError: configure() must be called before get_config()**

Solution: Call `configure(root_model=YourModel, app_name="yourapp")` before calling `get_config()`.

**2. SettingsValidationError: Validation error**

Solution: Check that your configuration files match your Pydantic schema. The error message includes details about which field failed validation.

**3. SettingsFileError: Error loading file**

Solution: Verify that your configuration files exist and contain valid TOML or YAML. Check file permissions and paths.

**4. SettingsRegistryError: Namespace already registered**

Solution: Each namespace can only be registered once. Either use a different namespace name or call `SchemaRegistry.clear()` if you need to re-register (typically only needed in tests).

## Contributing

This package is being developed as part of the wallpaper-effects-generator monorepo refactor.

To contribute:

1. Follow the development setup instructions above
2. Write tests for any new features
3. Ensure all tests pass and type checking succeeds
4. Follow the existing code style and documentation patterns

## License

Part of the Wallpaper Effects Generator project.

## Version History

### 0.1.0 (Current)

- Initial implementation with complete feature set
- Support for TOML and YAML configuration files
- Four-layer configuration system (package, project, user, CLI)
- Pydantic validation with full type safety
- Comprehensive test suite (143 tests)
- Complete documentation and working examples
