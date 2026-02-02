"""File loading functionality for configuration files.

This module provides utilities for loading and parsing configuration files
in various formats (TOML, YAML).
"""

import tomllib
from pathlib import Path
from typing import Any, cast

import yaml

from layered_settings.errors import SettingsFileError


class FileLoader:
    """Loader for configuration files with format auto-detection.

    Supports TOML and YAML formats with comprehensive error handling.
    """

    @staticmethod
    def detect_format(filepath: Path) -> str:
        """Detect file format from extension.

        Args:
            filepath: Path to the configuration file

        Returns:
            Format identifier ("toml" or "yaml")

        Raises:
            SettingsFileError: If file extension is not supported
        """
        suffix = filepath.suffix.lower()

        if suffix == ".toml":
            return "toml"
        elif suffix in {".yaml", ".yml"}:
            return "yaml"
        else:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Unsupported file format: {suffix or '(no extension)'}",
            )

    @staticmethod
    def load(filepath: Path) -> dict[str, Any]:
        """Load and parse a configuration file.

        Automatically detects the file format from its extension and parses
        accordingly. Returns the parsed configuration as a nested dictionary.

        Args:
            filepath: Path to the configuration file

        Returns:
            Parsed configuration as nested dictionary

        Raises:
            SettingsFileError: If file cannot be read or parsed
        """
        # Validate file exists
        if not filepath.exists():
            raise SettingsFileError(
                filepath=str(filepath),
                reason="File not found",
            )

        # Validate it's a file, not a directory
        if not filepath.is_file():
            raise SettingsFileError(
                filepath=str(filepath),
                reason="Path is not a file",
            )

        # Detect format
        format_type = FileLoader.detect_format(filepath)

        # Load based on format
        try:
            if format_type == "toml":
                return FileLoader._load_toml(filepath)
            elif format_type == "yaml":
                return FileLoader._load_yaml(filepath)
            else:
                # Should never reach here due to detect_format validation
                raise SettingsFileError(
                    filepath=str(filepath),
                    reason=f"Unknown format type: {format_type}",
                )
        except SettingsFileError:
            # Re-raise our own errors
            raise
        except PermissionError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason="Failed to read file (permission denied)",
            ) from e
        except OSError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Failed to read file: {e}",
            ) from e

    @staticmethod
    def _load_toml(filepath: Path) -> dict[str, Any]:
        """Load and parse a TOML file.

        Args:
            filepath: Path to the TOML file

        Returns:
            Parsed TOML data as dictionary

        Raises:
            SettingsFileError: If parsing fails
        """
        try:
            with open(filepath, "rb") as f:
                return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Failed to parse TOML file: {e}",
            ) from e
        except UnicodeDecodeError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Failed to decode TOML file (encoding issue): {e}",
            ) from e

    @staticmethod
    def _load_yaml(filepath: Path) -> dict[str, Any]:
        """Load and parse a YAML file.

        Args:
            filepath: Path to the YAML file

        Returns:
            Parsed YAML data as dictionary (or empty dict if file is empty)

        Raises:
            SettingsFileError: If parsing fails
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                # Handle empty files (yaml.safe_load returns None)
                if content is None:
                    return {}
                return cast(dict[str, Any], content)
        except yaml.YAMLError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Failed to parse YAML file: {e}",
            ) from e
        except UnicodeDecodeError as e:
            raise SettingsFileError(
                filepath=str(filepath),
                reason=f"Failed to decode YAML file (encoding issue): {e}",
            ) from e
