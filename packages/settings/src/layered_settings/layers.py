"""Layer discovery for layered_settings package.

This module provides functionality to discover configuration files from multiple
sources (package defaults, project root, user config) and return them in priority order.
"""

from dataclasses import dataclass
from pathlib import Path

from layered_settings.registry import SchemaRegistry


@dataclass(frozen=True)
class LayerSource:
    """Represents a configuration layer source.

    Attributes:
        name: Descriptive name for the layer (e.g., "package-defaults-core")
        filepath: Path to the configuration file
        namespace: The namespace this layer belongs to
        is_namespaced: Whether the file uses namespaced format ([namespace.section])
    """

    name: str
    filepath: Path
    namespace: str
    is_namespaced: bool


class LayerDiscovery:
    """Discovers configuration files from multiple locations.

    Discovers config files in priority order:
    1. Package defaults (from SchemaRegistry entries) - flat format
    2. Project root (./settings.toml) - namespaced format
    3. User config (~/.config/<app_name>/settings.toml) - namespaced format
    """

    @classmethod
    def discover_layers(cls, app_name: str | None = None) -> list[LayerSource]:
        """Discover configuration layer sources.

        Discovers config files from:
        - Package defaults: from SchemaRegistry entries (flat format)
        - Project root: ./settings.toml (namespaced format)
        - User config: ~/.config/<app_name>/settings.toml (namespaced format)

        Args:
            app_name: Application name for user config directory.
                     Defaults to "layered-settings" if None.

        Returns:
            List of LayerSource objects in priority order (lowest to highest):
            1. Package defaults (multiple, one per registered schema)
            2. Project root (if exists)
            3. User config (if exists)

            Non-existent files are skipped.
        """
        if app_name is None:
            app_name = "layered-settings"

        layers: list[LayerSource] = []

        # 1. Discover package defaults from registry
        for entry in SchemaRegistry.all_entries():
            if entry.defaults_file.exists():
                layer = LayerSource(
                    name=f"package-defaults-{entry.namespace}",
                    filepath=entry.defaults_file,
                    namespace=entry.namespace,
                    is_namespaced=False,
                )
                layers.append(layer)

        # 2. Discover project root settings.toml
        project_path = Path.cwd() / "settings.toml"
        if project_path.exists():
            layer = LayerSource(
                name="project-root",
                filepath=project_path,
                namespace="",
                is_namespaced=True,
            )
            layers.append(layer)

        # 3. Discover user config
        user_path = Path.home() / ".config" / app_name / "settings.toml"
        if user_path.exists():
            layer = LayerSource(
                name="user-config",
                filepath=user_path,
                namespace="",
                is_namespaced=True,
            )
            layers.append(layer)

        return layers
