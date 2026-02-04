"""Layered Settings - Generic layered configuration system for Python.

This package provides a flexible configuration system that supports:
- Multiple file formats (TOML, YAML)
- Layered configuration merging (package -> project -> user -> CLI)
- Pydantic validation
- Schema registration for multiple namespaces

Basic usage:
    >>> from pydantic import BaseModel
    >>> from layered_settings import SchemaRegistry, configure, get_config
    >>>
    >>> # Define your settings schema
    >>> class AppSettings(BaseModel):
    ...     debug: bool = False
    >>>
    >>> # Register package defaults
    >>> SchemaRegistry.register("app", AppSettings, Path("defaults.toml"))
    >>>
    >>> # Configure the system
    >>> configure(root_model=AppSettings, app_name="myapp")
    >>>
    >>> # Get configuration (discovers and merges all layers)
    >>> config = get_config()
    >>> print(config.debug)
"""

from typing import Any

from pydantic import BaseModel

from layered_settings.builder import ConfigBuilder
from layered_settings.constants import (
    APP_NAME,
    EFFECTS_FILENAME,
    SETTINGS_FILENAME,
)
from layered_settings.layers import LayerDiscovery
from layered_settings.registry import SchemaRegistry

__version__ = "0.1.0"

# Global state for the configuration system
_configured_model: type[BaseModel] | None = None
_app_name: str | None = None
_config_cache: BaseModel | None = None


def configure(root_model: type[BaseModel], app_name: str) -> None:
    """Configure the layered settings system.

    This function must be called before get_config(). It stores the root model
    and app name, and clears any cached configuration.

    Args:
        root_model: Pydantic model class that defines the complete configuration schema.
                   This should typically have nested models for different namespaces.
        app_name: Application name used for user config directory
                 (e.g., ~/.config/<app_name>/settings.toml)

    Example:
        >>> from pydantic import BaseModel
        >>> class CoreSettings(BaseModel):
        ...     workers: int = 4
        >>> class AppConfig(BaseModel):
        ...     core: CoreSettings = CoreSettings()
        >>> configure(root_model=AppConfig, app_name="myapp")
    """
    global _configured_model, _app_name, _config_cache

    _configured_model = root_model
    _app_name = app_name
    _config_cache = None  # Clear cache on reconfiguration


def get_config(overrides: dict[str, Any] | None = None) -> BaseModel:
    """Get the application configuration.

    This function discovers configuration layers, merges them in priority order,
    applies CLI overrides, and returns a validated configuration instance.

    The configuration is cached when called without overrides. Subsequent calls
    without overrides return the same cached instance. Calls with overrides
    always return a new instance and do not affect the cache.

    Priority order (lowest to highest):
    1. Package defaults (from SchemaRegistry)
    2. Project root settings.toml
    3. User config (~/.config/<app_name>/settings.toml)
    4. CLI overrides (provided as overrides parameter)

    Args:
        overrides: Optional dictionary of CLI overrides using dotted path notation.
                  Example: {"core.workers": 16, "effects.blur": 10}
                  Overrides are applied last and have highest priority.

    Returns:
        Validated configuration instance of the root model type.

    Raises:
        RuntimeError: If configure() has not been called first.
        SettingsValidationError: If configuration validation fails.
        SettingsFileError: If a configuration file cannot be loaded.

    Example:
        >>> config = get_config()  # Uses cached config if available
        >>> config_with_overrides = get_config(overrides={"core.workers": 16})
    """
    global _config_cache

    # Check if configure() was called
    if _configured_model is None or _app_name is None:
        raise RuntimeError(
            "configure() must be called before get_config(). "
            "Call configure(root_model=YourModel, app_name='yourapp') first."
        )

    # If overrides provided, always build fresh (don't use or update cache)
    if overrides is not None:
        layers = LayerDiscovery.discover_layers(app_name=_app_name)
        return ConfigBuilder.build(
            root_model=_configured_model,
            layers=layers,
            cli_overrides=overrides,
        )

    # Without overrides: use cache if available
    if _config_cache is not None:
        return _config_cache

    # Build and cache the configuration
    layers = LayerDiscovery.discover_layers(app_name=_app_name)
    config = ConfigBuilder.build(
        root_model=_configured_model,
        layers=layers,
        cli_overrides=None,
    )
    _config_cache = config
    return config


# Public API
__all__ = [
    "__version__",
    "SchemaRegistry",
    "configure",
    "get_config",
    # Constants
    "APP_NAME",
    "SETTINGS_FILENAME",
    "EFFECTS_FILENAME",
]
