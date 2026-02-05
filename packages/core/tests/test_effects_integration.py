"""Test layered-effects integration with wallpaper-core."""

import pytest
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


class TestLayeredEffectsConfiguration:
    def setup_method(self):
        """Reset layered_effects state before each test."""
        from layered_effects import _reset
        _reset()

    def test_loads_package_defaults_only(self, tmp_path):
        """Should work with only package layer."""
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path  # Empty directory
        )
        config = load_effects()

        # Should have all package defaults
        assert "blur" in config.effects
        assert "brightness" in config.effects
        assert "blackwhite-blur" in config.composites

    def test_project_effects_extend_package(self, tmp_path):
        """Project effects should add to package defaults."""
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        # Create project effects.yaml
        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
effects:
  custom_project:
    description: "Project custom effect"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )
        config = load_effects()

        # Should have both package and project effects
        assert "blur" in config.effects  # Package
        assert "custom_project" in config.effects  # Project

    def test_user_effects_override_package(self, tmp_path):
        """User effects should override package defaults."""
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        # Create user effects.yaml
        user_effects = tmp_path / "user_effects.yaml"
        user_effects.write_text("""
version: "1.0"
effects:
  blur:
    description: "My custom blur"
    command: "convert $INPUT -blur 0x50 $OUTPUT"
    parameters: {}
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path,
            user_effects_file=user_effects
        )
        config = load_effects()

        # Blur should be overridden
        assert config.effects["blur"].description == "My custom blur"
        assert "0x50" in config.effects["blur"].command

    def test_parameter_types_merge_across_layers(self, tmp_path):
        """Parameter types from all layers should be available."""
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
parameter_types:
  custom_range:
    type: integer
    min: 0
    max: 100
    default: 50
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )
        config = load_effects()

        # Should have both package and project parameter types
        assert "blur_geometry" in config.parameter_types  # Package
        assert "custom_range" in config.parameter_types  # Project


class TestErrorHandling:
    def setup_method(self):
        from layered_effects import _reset
        _reset()

    def test_invalid_yaml_raises_load_error(self, tmp_path):
        """Invalid YAML should raise EffectsLoadError."""
        from layered_effects.errors import EffectsLoadError
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("invalid: yaml: content:")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )

        with pytest.raises(EffectsLoadError):
            load_effects()

    def test_validation_error_shows_helpful_message(self, tmp_path):
        """Validation errors should have helpful context."""
        from layered_effects.errors import EffectsValidationError
        from wallpaper_core.effects import get_package_effects_file
        from layered_effects import configure, load_effects

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
effects:
  bad_effect:
    description: "Missing command field"
    parameters: {}
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )

        with pytest.raises(EffectsValidationError) as exc_info:
            load_effects()

        # Should mention what's wrong
        assert "command" in str(exc_info.value).lower()

    def test_missing_package_effects_fails(self, tmp_path):
        """Should fail if package effects.yaml doesn't exist."""
        from layered_effects.errors import EffectsLoadError
        from layered_effects import configure, load_effects

        fake_package = tmp_path / "nonexistent.yaml"

        configure(
            package_effects_file=fake_package,
            project_root=tmp_path
        )

        with pytest.raises(EffectsLoadError):
            load_effects()
