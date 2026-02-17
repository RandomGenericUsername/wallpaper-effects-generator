#!/usr/bin/env python3
"""Basic usage example for layered-settings package.

This example demonstrates:
1. Defining configuration schemas with Pydantic
2. Registering schemas with the SchemaRegistry
3. Configuring the system with configure()
4. Getting configuration with get_config()
5. Applying CLI overrides
"""

from pathlib import Path

from pydantic import BaseModel, Field

from layered_settings import SchemaRegistry, configure, get_config

# Step 1: Define your configuration schemas using Pydantic
# =========================================================


class DatabaseSettings(BaseModel):
    """Database connection settings."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="myapp", description="Database name")
    pool_size: int = Field(default=10, description="Connection pool size")
    timeout: float = Field(default=30.0, description="Connection timeout in seconds")


class ServerSettings(BaseModel):
    """Web server settings."""

    host: str = Field(
        default="0.0.0.0", description="Server bind address"  # nosec B104
    )
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")
    debug: bool = Field(default=False, description="Enable debug mode")


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format (json or text)")
    output: str = Field(default="stdout", description="Log output destination")


# Step 2: Define the root configuration model
# ============================================
# This model combines all namespaces into a single configuration


class AppConfig(BaseModel):
    """Root configuration for the entire application."""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


# Step 3: Register schemas with the SchemaRegistry
# =================================================
# Each schema is registered with a namespace and a defaults file


def register_schemas() -> None:
    """Register all configuration schemas."""
    # Get the path to the defaults file
    defaults_file = Path(__file__).parent / "app_defaults.toml"

    # Register each namespace with its model
    # Note: We register with the root model's field names as namespaces
    SchemaRegistry.register(
        namespace="database",
        model=DatabaseSettings,
        defaults_file=defaults_file,
    )

    SchemaRegistry.register(
        namespace="server",
        model=ServerSettings,
        defaults_file=defaults_file,
    )

    SchemaRegistry.register(
        namespace="logging",
        model=LoggingSettings,
        defaults_file=defaults_file,
    )


# Step 4: Initialize the configuration system
# ============================================


def main() -> None:
    """Main function demonstrating configuration usage."""

    # Register all schemas first
    register_schemas()

    # Configure the system (call once at startup)
    configure(root_model=AppConfig, app_name="myapp")

    # Get configuration (without overrides)
    print("=" * 60)
    print("Configuration without overrides:")
    print("=" * 60)
    config = get_config()

    print(
        f"Database: {config.database.host}:{config.database.port}/{config.database.db_name}"
    )
    print(
        f"Server: {config.server.host}:{config.server.port} (workers={config.server.workers})"
    )
    print(f"Logging: {config.logging.level} ({config.logging.format})")
    print()

    # Get configuration with CLI overrides
    print("=" * 60)
    print("Configuration with CLI overrides:")
    print("=" * 60)
    overrides = {
        "database.host": "production.example.com",
        "database.port": 5433,
        "server.workers": 16,
        "server.debug": True,
        "logging.level": "DEBUG",
    }

    config_with_overrides = get_config(overrides=overrides)

    print(
        f"Database: {config_with_overrides.database.host}:{config_with_overrides.database.port}/{config_with_overrides.database.db_name}"
    )
    print(
        f"Server: {config_with_overrides.server.host}:{config_with_overrides.server.port} (workers={config_with_overrides.server.workers}, debug={config_with_overrides.server.debug})"
    )
    print(
        f"Logging: {config_with_overrides.logging.level} ({config_with_overrides.logging.format})"
    )
    print()

    # Demonstrate caching behavior
    print("=" * 60)
    print("Caching behavior:")
    print("=" * 60)
    config_cached = get_config()
    print(f"config is config_cached: {config is config_cached}")
    print("(Configurations without overrides are cached and reused)")
    print()

    config_new = get_config(overrides={"server.port": 9000})
    print(f"config is config_new: {config is config_new}")
    print("(Configurations with overrides are always freshly built)")


if __name__ == "__main__":
    main()
