"""Tests for effects loader module."""

from pathlib import Path

import pytest


class TestEffectsLoader:
    """Tests for EffectsLoader class."""

    def test_discovers_package_layer(self, package_effects_file: Path):
        """Should discover package effects file."""
        from layered_effects.loader import EffectsLoader

        loader = EffectsLoader(package_effects_file=package_effects_file)
        layers = loader.discover_layers()

        assert len(layers) >= 1
        assert layers[0] == package_effects_file

    def test_discovers_project_layer(
        self,
        package_effects_file: Path,
        tmp_path: Path,
    ):
        """Should discover project effects file when it exists."""
        from layered_effects.loader import EffectsLoader

        project_root = tmp_path / "project"
        project_root.mkdir()
        project_effects = project_root / "effects.yaml"
        project_effects.write_text("version: '1.0'\neffects: {}")

        loader = EffectsLoader(
            package_effects_file=package_effects_file,
            project_root=project_root,
        )
        layers = loader.discover_layers()

        assert project_effects in layers

    def test_discovers_user_layer(
        self,
        package_effects_file: Path,
        user_effects_file: Path,
    ):
        """Should discover user effects file when it exists."""
        from layered_effects.loader import EffectsLoader

        loader = EffectsLoader(
            package_effects_file=package_effects_file,
            user_effects_file=user_effects_file,
        )
        layers = loader.discover_layers()

        assert user_effects_file in layers

    def test_layer_priority_order(
        self,
        package_effects_file: Path,
        project_effects_file: Path,
        user_effects_file: Path,
        tmp_path: Path,
    ):
        """Layers should be in priority order: package, project, user."""
        from layered_effects.loader import EffectsLoader

        project_root = tmp_path / "project"
        project_root.mkdir()
        project_effects = project_root / "effects.yaml"
        project_effects.write_text("version: '1.0'\neffects: {}")

        loader = EffectsLoader(
            package_effects_file=package_effects_file,
            project_root=project_root,
            user_effects_file=user_effects_file,
        )
        layers = loader.discover_layers()

        # Should be: package, project, user
        assert layers[0] == package_effects_file
        assert layers[1] == project_effects
        assert layers[2] == user_effects_file

    def test_loads_single_file(self, package_effects_file: Path):
        """Should load a single effects file."""
        from layered_effects.loader import EffectsLoader

        loader = EffectsLoader(package_effects_file=package_effects_file)
        data = loader._load_yaml_file(package_effects_file)

        assert "version" in data
        assert "effects" in data
        assert "test_effect" in data["effects"]

    def test_raises_on_invalid_yaml(self, tmp_path: Path):
        """Should raise EffectsLoadError for invalid YAML."""
        from layered_effects.loader import EffectsLoader
        from layered_effects.errors import EffectsLoadError

        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("invalid: yaml: content:")

        loader = EffectsLoader(package_effects_file=bad_file)

        with pytest.raises(EffectsLoadError):
            loader._load_yaml_file(bad_file)
