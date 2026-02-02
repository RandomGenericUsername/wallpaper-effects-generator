"""Configuration merging utilities for layered settings.

This module provides deep merge functionality for configuration dictionaries,
supporting recursive merging of nested structures while maintaining immutability.
"""

from copy import deepcopy
from typing import Any


class ConfigMerger:
    """Utility class for merging configuration dictionaries.

    The ConfigMerger provides a static merge method that performs deep merging
    of configuration dictionaries according to specific rules:

    - Dictionaries: Recursively merged, combining keys from both
    - Lists: Replaced atomically (not merged element-wise)
    - Scalars: Replaced with override value
    - New keys: Added to the result

    The merge operation does not mutate the input dictionaries.
    """

    @staticmethod
    def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configuration dictionaries.

        This method recursively merges two configuration dictionaries, with the
        override dictionary taking precedence over the base. The merge follows
        these rules:

        1. When both values are dicts: Recursively merge their contents
        2. When either value is not a dict: Replace base with override
        3. Lists are replaced atomically, not merged element-wise
        4. New keys from override are added to the result

        Neither input dictionary is mutated. A new dictionary is returned.

        Args:
            base: The base configuration dictionary
            override: The override configuration dictionary

        Returns:
            A new dictionary containing the merged configuration

        Examples:
            >>> ConfigMerger.merge({"a": 1}, {"b": 2})
            {"a": 1, "b": 2}

            >>> ConfigMerger.merge({"a": {"x": 1}}, {"a": {"y": 2}})
            {"a": {"x": 1, "y": 2}}

            >>> ConfigMerger.merge({"items": [1, 2]}, {"items": [3]})
            {"items": [3]}
        """
        # Create a deep copy of base to avoid mutation
        result = deepcopy(base)

        # Iterate through override keys
        for key, override_value in override.items():
            if key in result:
                base_value = result[key]

                # If both values are dictionaries, recursively merge them
                if isinstance(base_value, dict) and isinstance(override_value, dict):
                    result[key] = ConfigMerger.merge(base_value, override_value)
                else:
                    # For all other cases (including lists), replace atomically
                    result[key] = deepcopy(override_value)
            else:
                # New key from override, add it to result
                result[key] = deepcopy(override_value)

        return result
