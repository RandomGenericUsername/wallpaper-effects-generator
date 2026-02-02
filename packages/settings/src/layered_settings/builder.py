"""Configuration builder for merging and validating layered settings.

This module provides the ConfigBuilder class which orchestrates the loading,
merging, and validation of configuration from multiple sources.
"""

from typing import Any

from pydantic import BaseModel, ValidationError

from layered_settings.errors import SettingsValidationError
from layered_settings.layers import LayerSource
from layered_settings.loader import FileLoader
from layered_settings.merger import ConfigMerger


class ConfigBuilder:
    """Builder for constructing validated configuration from multiple layers.

    The ConfigBuilder orchestrates the complete configuration loading process:
    1. Loads configuration files from multiple layers
    2. Merges them in priority order (later layers override earlier ones)
    3. Applies CLI overrides with highest priority
    4. Validates the final configuration with Pydantic
    """

    @classmethod
    def build(
        cls,
        root_model: type[BaseModel],
        layers: list[LayerSource],
        cli_overrides: dict[str, Any] | None = None,
    ) -> BaseModel:
        """Build and validate configuration from multiple layers.

        This method orchestrates the complete configuration loading process:

        1. Start with an empty merged data dictionary
        2. For each layer in order:
           - Load the file using FileLoader.load()
           - If flat format (is_namespaced=False): wrap data in {namespace: data}
           - If namespaced format (is_namespaced=True): use data as-is
           - Merge with ConfigMerger.merge()
        3. Apply CLI overrides with dotted path notation
        4. Validate with Pydantic root_model
        5. Return validated instance

        Args:
            root_model: Pydantic model class to validate the final configuration
            layers: List of LayerSource objects in priority order (lowest to highest)
            cli_overrides: Optional dictionary of CLI overrides with dotted paths
                          (e.g., {"core.workers": 16, "effects.blur": 10})

        Returns:
            Validated instance of root_model

        Raises:
            SettingsValidationError: If Pydantic validation fails
            SettingsFileError: If any file cannot be loaded (propagated from FileLoader)

        Examples:
            >>> layers = [
            ...     LayerSource("defaults", Path("defaults.toml"), "core", False),
            ...     LayerSource("project", Path("settings.toml"), "", True),
            ... ]
            >>> config = ConfigBuilder.build(AppConfig, layers, {"core.workers": 16})
        """
        # Start with empty merged data
        merged_data: dict[str, Any] = {}

        # Process each layer in order
        for layer in layers:
            # Load the file
            layer_data = FileLoader.load(layer.filepath)

            # Handle format differences
            if layer.is_namespaced:
                # Namespaced format: use data as-is
                data_to_merge = layer_data
            else:
                # Flat format: wrap in namespace key
                data_to_merge = {layer.namespace: layer_data}

            # Merge with accumulated data
            merged_data = ConfigMerger.merge(merged_data, data_to_merge)

        # Apply CLI overrides
        if cli_overrides:
            merged_data = cls._apply_overrides(merged_data, cli_overrides)

        # Validate with Pydantic
        try:
            return root_model.model_validate(merged_data)
        except ValidationError as e:
            raise SettingsValidationError(
                config_name=root_model.__name__,
                reason=str(e),
            ) from e

    @classmethod
    def _apply_overrides(
        cls,
        data: dict[str, Any],
        overrides: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply CLI overrides using dotted path notation.

        This method walks dotted paths and sets values in nested dictionaries,
        creating intermediate dictionaries as needed.

        Args:
            data: The base data dictionary to apply overrides to
            overrides: Dictionary with dotted path keys (e.g., "core.workers")

        Returns:
            New dictionary with overrides applied

        Examples:
            >>> data = {"core": {"workers": 4}}
            >>> overrides = {"core.workers": 16, "core.timeout": 30.0}
            >>> result = ConfigBuilder._apply_overrides(data, overrides)
            >>> result["core"]["workers"]
            16
            >>> result["core"]["timeout"]
            30.0
        """
        # Create a deep copy to avoid mutating input
        from copy import deepcopy

        result = deepcopy(data)

        # Apply each override
        for path, value in overrides.items():
            # Split dotted path
            parts = path.split(".")

            # Walk to the parent dict, creating intermediate dicts as needed
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # If intermediate value is not a dict, replace it
                    current[part] = {}
                current = current[part]

            # Set the final value
            current[parts[-1]] = value

        return result
