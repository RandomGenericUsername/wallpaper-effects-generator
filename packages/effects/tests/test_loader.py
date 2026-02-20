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
        from layered_effects.errors import EffectsLoadError
        from layered_effects.loader import EffectsLoader

        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("invalid: yaml: content:")

        loader = EffectsLoader(package_effects_file=bad_file)

        with pytest.raises(EffectsLoadError):
            loader._load_yaml_file(bad_file)


class TestEffectsLoaderMerge:
    """Tests for effects merging functionality."""

    def test_merges_effects_from_layers(
        self,
        tmp_path: Path,
    ):
        """Should deep merge effects from all layers."""
        from layered_effects.loader import EffectsLoader

        # Package layer: blur + brightness
        package_file = tmp_path / "package.yaml"
        package_file.write_text("""
version: "1.0"
effects:
  blur:
    description: "Package blur"
    command: "blur package"
  brightness:
    description: "Package brightness"
    command: "brightness package"
""")

        # User layer: blur (override) + neon (new)
        user_file = tmp_path / "user.yaml"
        user_file.write_text("""
version: "1.0"
effects:
  blur:
    description: "User blur"
    command: "blur user"
  neon:
    description: "User neon"
    command: "neon user"
""")

        loader = EffectsLoader(
            package_effects_file=package_file,
            user_effects_file=user_file,
        )
        merged = loader.load_and_merge()

        # Should have blur (user), brightness (package), neon (user)
        assert "blur" in merged["effects"]
        assert merged["effects"]["blur"]["command"] == "blur user"
        assert "brightness" in merged["effects"]
        assert merged["effects"]["brightness"]["command"] == "brightness package"
        assert "neon" in merged["effects"]
        assert merged["effects"]["neon"]["command"] == "neon user"

    def test_uses_package_version(self, tmp_path: Path):
        """Should use package version as canonical."""
        from layered_effects.loader import EffectsLoader

        package_file = tmp_path / "package.yaml"
        package_file.write_text('version: "1.0"\neffects: {}')

        user_file = tmp_path / "user.yaml"
        user_file.write_text('version: "2.0"\neffects: {}')

        loader = EffectsLoader(
            package_effects_file=package_file,
            user_effects_file=user_file,
        )
        merged = loader.load_and_merge()

        # First layer (package) version should be used
        assert merged["version"] == "1.0"

    def test_works_with_only_package_layer(self, package_effects_file: Path):
        """Should work when only package layer exists."""
        from layered_effects.loader import EffectsLoader

        loader = EffectsLoader(package_effects_file=package_effects_file)
        merged = loader.load_and_merge()

        assert "version" in merged
        assert "effects" in merged

    def test_raises_when_no_package_layer(self, tmp_path: Path):
        """Should raise when package layer doesn't exist."""
        from layered_effects.errors import EffectsLoadError
        from layered_effects.loader import EffectsLoader

        missing_file = tmp_path / "missing.yaml"

        loader = EffectsLoader(package_effects_file=missing_file)

        with pytest.raises(EffectsLoadError):
            loader.load_and_merge()
