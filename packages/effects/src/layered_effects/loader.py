"""Effects discovery and loading from layered configuration files."""

from pathlib import Path
from typing import Any

import yaml
from layered_settings.paths import USER_EFFECTS_FILE, get_project_effects_file

from layered_effects.errors import EffectsLoadError


class EffectsLoader:
    """Discovers and loads effects.yaml files from all layers.

    Layers (lowest to highest priority):
    1. Package defaults - specified via package_effects_file
    2. Project root - {project_root}/effects.yaml
    3. User config - ~/.config/wallpaper-effects-generator/effects.yaml

    Args:
        package_effects_file: Path to package default effects.yaml
        project_root: Optional project root directory
        user_effects_file: Optional user effects file (defaults to standard location)
    """

    def __init__(
        self,
        package_effects_file: Path,
        project_root: Path | None = None,
        user_effects_file: Path | None = None,
    ) -> None:
        self.package_effects_file = package_effects_file
        self.project_root = project_root
        self.user_effects_file = (
            user_effects_file if user_effects_file is not None else USER_EFFECTS_FILE
        )

    def discover_layers(self) -> list[Path]:
        """Discover all effects.yaml files across layers.

        Returns:
            List of paths in priority order (lowest to highest).
            Only includes files that exist.
        """
        layers = []

        # Layer 1: Package defaults (required)
        if self.package_effects_file.exists():
            layers.append(self.package_effects_file)

        # Layer 2: Project (optional)
        if self.project_root is not None:
            project_effects = get_project_effects_file(self.project_root)
            if project_effects.exists():
                layers.append(project_effects)

        # Layer 3: User (optional)
        if self.user_effects_file.exists():
            layers.append(self.user_effects_file)

        return layers

    def _load_yaml_file(self, file_path: Path) -> dict[str, Any]:
        """Load and parse a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML as dictionary

        Raises:
            EffectsLoadError: If file cannot be read or parsed
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            return data if data is not None else {}
        except yaml.YAMLError as e:
            raise EffectsLoadError(
                file_path=file_path,
                reason=f"Invalid YAML: {e}",
            ) from e
        except OSError as e:
            raise EffectsLoadError(
                file_path=file_path,
                reason=f"Cannot read file: {e}",
            ) from e

    def load_and_merge(self) -> dict[str, Any]:
        """Load all layers and deep merge into single configuration.

        Returns:
            Merged configuration dictionary

        Raises:
            EffectsLoadError: If package layer doesn't exist or loading fails
        """
        from layered_settings.merger import ConfigMerger

        layers = self.discover_layers()

        if not layers:
            raise EffectsLoadError(
                file_path=self.package_effects_file,
                reason="Package effects.yaml not found",
            )

        # Load first layer as base
        merged = self._load_yaml_file(layers[0])

        # Store package version to preserve it
        package_version = merged.get("version")

        # Merge subsequent layers
        for layer_path in layers[1:]:
            layer_data = self._load_yaml_file(layer_path)
            merged = ConfigMerger.merge(merged, layer_data)

        # Restore package version as canonical
        if package_version is not None:
            merged["version"] = package_version

        return merged
