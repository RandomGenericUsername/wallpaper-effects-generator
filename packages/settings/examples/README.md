# Layered Settings Examples

This directory contains working examples demonstrating the layered-settings package.

## Running the Examples

All examples are standalone Python scripts that can be run directly:

```bash
# From the packages/settings directory
python examples/basic_usage.py
python examples/layer_priority.py
```

Or if you have a virtual environment:

```bash
# From the packages/settings directory
.venv/bin/python examples/basic_usage.py
.venv/bin/python examples/layer_priority.py
```

## Available Examples

### basic_usage.py

A complete working example that demonstrates:
- Defining configuration schemas with Pydantic
- Registering multiple schemas with the SchemaRegistry
- Using configure() and get_config()
- Applying CLI overrides with dotted path notation
- Configuration caching behavior

This is the best starting point for new users.

**Example Output:**
```
============================================================
Configuration without overrides:
============================================================
Database: localhost:5432/myapp
Server: 0.0.0.0:8000 (workers=4)
Logging: INFO (json)

============================================================
Configuration with CLI overrides:
============================================================
Database: production.example.com:5433/myapp
Server: 0.0.0.0:8000 (workers=16, debug=True)
Logging: DEBUG (json)
```

### layer_priority.py

Demonstrates how configuration layers work together and override each other:
- Package defaults (flat format)
- Project root settings (namespaced format)
- User config directory settings (namespaced format)
- CLI overrides (highest priority)

This example creates a temporary directory structure to simulate all four layers
and shows which value wins at each level.

**Example Output:**
```
============================================================
Layer Priority Demonstration
============================================================

Final configuration values:
  workers: 8
  timeout: 30.0
  debug: True

Value sources:
  workers: 8 (from PROJECT settings.toml)
  timeout: 30.0 (from PACKAGE defaults.toml)
  debug: True (from USER ~/.config/layer-demo/settings.toml)
```

### app_defaults.toml

Example package defaults file in flat format. This demonstrates the structure
used for package-level default configurations.

Shows configuration for:
- Database settings
- Server settings
- Logging settings

## Using These Examples as Templates

Feel free to copy and modify these examples for your own applications:

1. Copy `basic_usage.py` as a starting template
2. Replace the schema definitions with your own
3. Update the namespace names to match your application
4. Create your own defaults TOML file based on `app_defaults.toml`
5. Register all your schemas in a single function
6. Call configure() once at application startup

## Need More Help?

See the main [README.md](../README.md) for:
- Complete API reference
- Architecture overview
- Best practices
- Troubleshooting guide
