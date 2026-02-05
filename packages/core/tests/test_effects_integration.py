"""Test layered-effects integration with wallpaper-core."""

from pathlib import Path


class TestPackageEffects:
    def test_get_package_effects_file_returns_valid_path(self):
        """Should return existing path to effects.yaml."""
        from wallpaper_core.effects import get_package_effects_file

        path = get_package_effects_file()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.name == "effects.yaml"
        assert "wallpaper_core" in str(path)

    def test_package_effects_file_is_valid_yaml(self):
        """Package effects.yaml should be valid and loadable."""
        import yaml

        from wallpaper_core.effects import get_package_effects_file

        path = get_package_effects_file()
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["version"] == "1.0"
        assert "effects" in data
        assert "parameter_types" in data
