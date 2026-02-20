"""Tests for config builder functionality."""

from pathlib import Path

import pytest
from pydantic import BaseModel

from layered_settings.builder import ConfigBuilder
from layered_settings.errors import SettingsValidationError
from layered_settings.layers import LayerSource


class CoreSettings(BaseModel):
    """Test core settings schema."""

    parallel: bool = True
    workers: int = 4
    timeout: float = 30.0


class EffectsSettings(BaseModel):
    """Test effects settings schema."""

    blur: int = 5
    brightness: float = 1.0
    filters: list[str] = []


class AppConfig(BaseModel):
    """Test root configuration with nested namespaces."""

    core: CoreSettings = CoreSettings()
    effects: EffectsSettings = EffectsSettings()


class TestConfigBuilderBasics:
    """Test basic ConfigBuilder functionality."""

    def test_build_with_empty_layers(self) -> None:
        """build() should return instance with defaults when no layers provided."""
        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[],
            cli_overrides=None,
        )

        assert isinstance(result, AppConfig)
        assert result.core.parallel is True
        assert result.core.workers == 4
        assert result.effects.blur == 5

    def test_build_returns_validated_instance(self) -> None:
        """build() should return an instance of the root_model."""
        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[],
        )

        assert isinstance(result, AppConfig)
        assert isinstance(result.core, CoreSettings)
        assert isinstance(result.effects, EffectsSettings)


class TestFlatFormatLoading:
    """Test loading package defaults with flat format."""

    def test_build_with_flat_format_layer(self, tmp_path: Path) -> None:
        """build() should wrap flat format data in namespace key."""
        # Create flat format config file (package defaults)
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("""
parallel = false
workers = 8
timeout = 60.0
""")

        layer = LayerSource(
            name="package-defaults-core",
            filepath=core_defaults,
            namespace="core",
            is_namespaced=False,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        assert result.core.parallel is False
        assert result.core.workers == 8
        assert result.core.timeout == 60.0
        # Effects should still have defaults
        assert result.effects.blur == 5

    def test_build_with_multiple_flat_layers(self, tmp_path: Path) -> None:
        """build() should handle multiple flat format layers for different namespaces."""
        # Create flat core defaults
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("""
parallel = true
workers = 16
""")

        # Create flat effects defaults
        effects_defaults = tmp_path / "effects_defaults.toml"
        effects_defaults.write_text("""
blur = 10
brightness = 1.5
filters = ["sharpen", "contrast"]
""")

        layers = [
            LayerSource(
                name="package-defaults-core",
                filepath=core_defaults,
                namespace="core",
                is_namespaced=False,
            ),
            LayerSource(
                name="package-defaults-effects",
                filepath=effects_defaults,
                namespace="effects",
                is_namespaced=False,
            ),
        ]

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=layers,
        )

        assert result.core.workers == 16
        assert result.effects.blur == 10
        assert result.effects.filters == ["sharpen", "contrast"]


class TestNamespacedFormatLoading:
    """Test loading namespaced config files."""

    def test_build_with_namespaced_layer(self, tmp_path: Path) -> None:
        """build() should use namespaced data as-is."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
parallel = false
workers = 2

[effects]
blur = 20
brightness = 0.8
""")

        layer = LayerSource(
            name="project-root",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        assert result.core.parallel is False
        assert result.core.workers == 2
        assert result.effects.blur == 20
        assert result.effects.brightness == 0.8

    def test_build_with_partial_namespaced_layer(self, tmp_path: Path) -> None:
        """build() should handle namespaced files that only define some namespaces."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
workers = 12
""")

        layer = LayerSource(
            name="user-config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        # Core should be updated
        assert result.core.workers == 12
        # Other core fields should have defaults
        assert result.core.parallel is True
        # Effects should have all defaults
        assert result.effects.blur == 5


class TestLayerMerging:
    """Test merging multiple layers in priority order."""

    def test_build_merges_layers_in_order(self, tmp_path: Path) -> None:
        """build() should merge layers in order, with later layers overriding earlier ones."""
        # Layer 1: Package defaults (flat)
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("""
parallel = true
workers = 4
timeout = 30.0
""")

        # Layer 2: Project config (namespaced, overrides workers)
        project_config = tmp_path / "project.toml"
        project_config.write_text("""
[core]
workers = 8
""")

        # Layer 3: User config (namespaced, overrides parallel)
        user_config = tmp_path / "user.toml"
        user_config.write_text("""
[core]
parallel = false
""")

        layers = [
            LayerSource(
                name="package-defaults-core",
                filepath=core_defaults,
                namespace="core",
                is_namespaced=False,
            ),
            LayerSource(
                name="project-root",
                filepath=project_config,
                namespace="",
                is_namespaced=True,
            ),
            LayerSource(
                name="user-config",
                filepath=user_config,
                namespace="",
                is_namespaced=True,
            ),
        ]

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=layers,
        )

        # parallel overridden by user config (layer 3)
        assert result.core.parallel is False
        # workers overridden by project config (layer 2)
        assert result.core.workers == 8
        # timeout from package defaults (layer 1)
        assert result.core.timeout == 30.0

    def test_build_deep_merges_nested_values(self, tmp_path: Path) -> None:
        """build() should deep merge nested structures, not replace them."""
        # Layer 1: Set some core values
        layer1 = tmp_path / "layer1.toml"
        layer1.write_text("""
[core]
parallel = true
workers = 4
""")

        # Layer 2: Set different core values
        layer2 = tmp_path / "layer2.toml"
        layer2.write_text("""
[core]
timeout = 60.0

[effects]
blur = 15
""")

        layers = [
            LayerSource(
                name="layer1",
                filepath=layer1,
                namespace="",
                is_namespaced=True,
            ),
            LayerSource(
                name="layer2",
                filepath=layer2,
                namespace="",
                is_namespaced=True,
            ),
        ]

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=layers,
        )

        # All core values should be present (deep merge)
        assert result.core.parallel is True  # from layer1
        assert result.core.workers == 4  # from layer1
        assert result.core.timeout == 60.0  # from layer2
        # Effects from layer2
        assert result.effects.blur == 15

    def test_build_replaces_lists_atomically(self, tmp_path: Path) -> None:
        """build() should replace lists atomically, not merge element-wise."""
        # Layer 1: Set filters list
        layer1 = tmp_path / "layer1.toml"
        layer1.write_text("""
[effects]
filters = ["blur", "sharpen"]
""")

        # Layer 2: Override filters list
        layer2 = tmp_path / "layer2.toml"
        layer2.write_text("""
[effects]
filters = ["contrast"]
""")

        layers = [
            LayerSource(
                name="layer1",
                filepath=layer1,
                namespace="",
                is_namespaced=True,
            ),
            LayerSource(
                name="layer2",
                filepath=layer2,
                namespace="",
                is_namespaced=True,
            ),
        ]

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=layers,
        )

        # List should be replaced, not merged
        assert result.effects.filters == ["contrast"]


class TestCLIOverrides:
    """Test CLI overrides with dotted paths."""

    def test_build_applies_cli_overrides(self, tmp_path: Path) -> None:
        """build() should apply CLI overrides using dotted notation."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
parallel = true
workers = 4
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        cli_overrides = {
            "core.parallel": False,
            "core.workers": 16,
        }

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
            cli_overrides=cli_overrides,
        )

        # CLI overrides should take precedence
        assert result.core.parallel is False
        assert result.core.workers == 16

    def test_build_applies_deep_cli_overrides(self) -> None:
        """build() should handle multi-level dotted paths."""
        cli_overrides = {
            "core.timeout": 120.0,
            "effects.blur": 50,
            "effects.brightness": 2.0,
        }

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[],
            cli_overrides=cli_overrides,
        )

        assert result.core.timeout == 120.0
        assert result.effects.blur == 50
        assert result.effects.brightness == 2.0

    def test_build_cli_overrides_take_highest_priority(self, tmp_path: Path) -> None:
        """build() should ensure CLI overrides take precedence over all layers."""
        # Create config file
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
workers = 8
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        cli_overrides = {
            "core.workers": 32,
        }

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
            cli_overrides=cli_overrides,
        )

        # CLI should override config file
        assert result.core.workers == 32

    def test_build_creates_intermediate_dicts_for_cli_overrides(self) -> None:
        """build() should create intermediate dicts when applying CLI overrides."""
        cli_overrides = {
            "core.workers": 16,
        }

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[],
            cli_overrides=cli_overrides,
        )

        # Should create core dict and set workers
        assert result.core.workers == 16

    def test_build_with_none_cli_overrides(self, tmp_path: Path) -> None:
        """build() should handle None cli_overrides parameter."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
workers = 8
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
            cli_overrides=None,
        )

        assert result.core.workers == 8

    def test_build_with_empty_cli_overrides(self, tmp_path: Path) -> None:
        """build() should handle empty cli_overrides dict."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
workers = 8
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
            cli_overrides={},
        )

        assert result.core.workers == 8


class TestValidation:
    """Test Pydantic validation and error handling."""

    def test_build_validates_with_pydantic(self, tmp_path: Path) -> None:
        """build() should validate final config with Pydantic."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
parallel = true
workers = 4
timeout = 30.0

[effects]
blur = 5
brightness = 1.0
filters = []
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        # Should not raise
        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        assert isinstance(result, AppConfig)

    def test_build_raises_settings_validation_error_on_invalid_data(
        self, tmp_path: Path
    ) -> None:
        """build() should raise SettingsValidationError when validation fails."""
        config_file = tmp_path / "settings.toml"
        # workers should be int, not string
        config_file.write_text("""
[core]
workers = "invalid"
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        with pytest.raises(SettingsValidationError) as exc_info:
            ConfigBuilder.build(
                root_model=AppConfig,
                layers=[layer],
            )

        assert "AppConfig" in str(exc_info.value)
        assert exc_info.value.config_name == "AppConfig"

    def test_build_validation_error_includes_details(self, tmp_path: Path) -> None:
        """build() should include validation error details in SettingsValidationError."""
        config_file = tmp_path / "settings.toml"
        # Multiple validation errors
        config_file.write_text("""
[core]
workers = "not_a_number"
timeout = "not_a_float"
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        with pytest.raises(SettingsValidationError) as exc_info:
            ConfigBuilder.build(
                root_model=AppConfig,
                layers=[layer],
            )

        # Error message should contain validation details
        error_msg = str(exc_info.value)
        assert "AppConfig" in error_msg

    def test_build_handles_missing_required_fields(self) -> None:
        """build() should raise SettingsValidationError for missing required fields."""

        class StrictConfig(BaseModel):
            required_field: str
            optional_field: str = "default"

        # Should raise error for missing required field
        with pytest.raises(SettingsValidationError) as exc_info:
            ConfigBuilder.build(
                root_model=StrictConfig,
                layers=[],
            )

        assert "required_field" in str(exc_info.value)


class TestIntegration:
    """Integration tests for complete build workflows."""

    def test_build_realistic_multi_layer_scenario(self, tmp_path: Path) -> None:
        """build() should handle realistic scenario with multiple layers and CLI overrides."""
        # Package defaults (flat)
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("""
parallel = true
workers = 4
timeout = 30.0
""")

        effects_defaults = tmp_path / "effects_defaults.toml"
        effects_defaults.write_text("""
blur = 5
brightness = 1.0
filters = []
""")

        # Project config (namespaced)
        project_config = tmp_path / "project.toml"
        project_config.write_text("""
[core]
workers = 8

[effects]
blur = 10
filters = ["sharpen"]
""")

        # User config (namespaced)
        user_config = tmp_path / "user.toml"
        user_config.write_text("""
[core]
parallel = false
""")

        layers = [
            LayerSource(
                name="package-defaults-core",
                filepath=core_defaults,
                namespace="core",
                is_namespaced=False,
            ),
            LayerSource(
                name="package-defaults-effects",
                filepath=effects_defaults,
                namespace="effects",
                is_namespaced=False,
            ),
            LayerSource(
                name="project-root",
                filepath=project_config,
                namespace="",
                is_namespaced=True,
            ),
            LayerSource(
                name="user-config",
                filepath=user_config,
                namespace="",
                is_namespaced=True,
            ),
        ]

        cli_overrides = {
            "core.workers": 16,
            "effects.brightness": 1.5,
        }

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=layers,
            cli_overrides=cli_overrides,
        )

        # Verify merging order:
        # - parallel: False (user config)
        # - workers: 16 (CLI override)
        # - timeout: 30.0 (package defaults)
        # - blur: 10 (project config)
        # - brightness: 1.5 (CLI override)
        # - filters: ["sharpen"] (project config)
        assert result.core.parallel is False
        assert result.core.workers == 16
        assert result.core.timeout == 30.0
        assert result.effects.blur == 10
        assert result.effects.brightness == 1.5
        assert result.effects.filters == ["sharpen"]

    def test_build_with_yaml_files(self, tmp_path: Path) -> None:
        """build() should work with YAML files."""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("""
core:
  parallel: false
  workers: 12
effects:
  blur: 8
  brightness: 0.9
""")

        layer = LayerSource(
            name="yaml-config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        assert result.core.parallel is False
        assert result.core.workers == 12
        assert result.effects.blur == 8
        assert result.effects.brightness == 0.9

    def test_build_preserves_data_types(self, tmp_path: Path) -> None:
        """build() should preserve data types through loading and merging."""
        config_file = tmp_path / "settings.toml"
        config_file.write_text("""
[core]
parallel = true
workers = 4
timeout = 30.5

[effects]
blur = 5
brightness = 1.0
filters = ["a", "b", "c"]
""")

        layer = LayerSource(
            name="config",
            filepath=config_file,
            namespace="",
            is_namespaced=True,
        )

        result = ConfigBuilder.build(
            root_model=AppConfig,
            layers=[layer],
        )

        assert isinstance(result.core.parallel, bool)
        assert isinstance(result.core.workers, int)
        assert isinstance(result.core.timeout, float)
        assert isinstance(result.effects.blur, int)
        assert isinstance(result.effects.brightness, float)
        assert isinstance(result.effects.filters, list)
        assert all(isinstance(f, str) for f in result.effects.filters)
