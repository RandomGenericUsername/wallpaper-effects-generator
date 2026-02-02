"""Schema registry for layered_settings package.

This module provides a registry pattern for managing multiple configuration schemas.
Each schema is associated with a namespace, a Pydantic model, and a defaults file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel

from layered_settings.errors import SettingsRegistryError


@dataclass(frozen=True)
class SchemaEntry:
    """Metadata for a registered schema.

    Attributes:
        namespace: Unique identifier for the schema (e.g., "core", "effects")
        model: Pydantic model class that defines the schema
        defaults_file: Path to the file containing default values
    """

    namespace: str
    model: type[BaseModel]
    defaults_file: Path


class SchemaRegistry:
    """Registry for managing configuration schemas.

    This is a class-level registry that stores schema metadata for different
    configuration namespaces. It prevents duplicate registrations and provides
    methods to retrieve and list registered schemas.

    Example:
        >>> from pydantic import BaseModel
        >>> from pathlib import Path
        >>>
        >>> class MySettings(BaseModel):
        ...     value: str = "default"
        >>>
        >>> SchemaRegistry.register(
        ...     namespace="app.config",
        ...     model=MySettings,
        ...     defaults_file=Path("/path/to/defaults.toml")
        ... )
        >>>
        >>> entry = SchemaRegistry.get("app.config")
        >>> print(entry.namespace)
        app.config
    """

    _registry: ClassVar[dict[str, SchemaEntry]] = {}

    @classmethod
    def register(
        cls,
        namespace: str,
        model: type[BaseModel],
        defaults_file: Path,
    ) -> None:
        """Register a new schema.

        Args:
            namespace: Unique identifier for the schema
            model: Pydantic model class that defines the schema
            defaults_file: Path to the file containing default values

        Raises:
            SettingsRegistryError: If the namespace is already registered
        """
        if namespace in cls._registry:
            raise SettingsRegistryError(
                namespace=namespace,
                reason="Namespace already registered",
            )

        entry = SchemaEntry(
            namespace=namespace,
            model=model,
            defaults_file=defaults_file,
        )
        cls._registry[namespace] = entry

    @classmethod
    def get(cls, namespace: str) -> SchemaEntry | None:
        """Get a registered schema entry.

        Args:
            namespace: The namespace to look up

        Returns:
            The SchemaEntry if found, None otherwise
        """
        return cls._registry.get(namespace)

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """List all registered namespaces.

        Returns:
            List of all registered namespace strings
        """
        return list(cls._registry.keys())

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]:
        """List all registered schema entries.

        Returns:
            List of all SchemaEntry objects
        """
        return list(cls._registry.values())

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations.

        This method is primarily intended for testing purposes to ensure
        a clean state between tests.
        """
        cls._registry.clear()
