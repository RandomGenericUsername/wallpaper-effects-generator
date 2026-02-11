"""Tests for layer discovery in layered_settings."""

from pathlib import Path
from unittest.mock import patch

import pytest
from layered_settings.layers import LayerDiscovery, LayerSource
from layered_settings.registry import SchemaRegistry
from pydantic import BaseModel


class DummyConfig(BaseModel):
    """Dummy config for testing."""

    value: str = "test"


class AnotherConfig(BaseModel):
    """Another dummy config for testing."""

    number: int = 42


class TestLayerSource:
    """Test the LayerSource dataclass."""

    def test_creates_layer_source_with_all_fields(self):
        """LayerSource should be creatable with name, filepath, namespace, and is_namespaced."""
        source = LayerSource(
            name="package-defaults",
            filepath=Path("/path/to/defaults.toml"),
            namespace="core",
            is_namespaced=False,
        )
        assert source.name == "package-defaults"
        assert source.filepath == Path("/path/to/defaults.toml")
        assert source.namespace == "core"
        assert source.is_namespaced is False

    def test_creates_namespaced_layer_source(self):
        """LayerSource should handle namespaced format."""
        source = LayerSource(
            name="project-root",
            filepath=Path("./settings.toml"),
            namespace="core",
            is_namespaced=True,
        )
        assert source.name == "project-root"
        assert source.filepath == Path("./settings.toml")
        assert source.namespace == "core"
        assert source.is_namespaced is True

    def test_layer_source_is_immutable(self):
        """LayerSource should be immutable (frozen dataclass)."""
        source = LayerSource(
            name="test",
            filepath=Path("/test.toml"),
            namespace="core",
            is_namespaced=False,
        )
        with pytest.raises(AttributeError):
            source.name = "modified"  # type: ignore[misc]

    def test_stores_path_object(self):
        """LayerSource should store Path object, not string."""
        source = LayerSource(
            name="test",
            filepath=Path("/test.toml"),
            namespace="core",
            is_namespaced=False,
        )
        assert isinstance(source.filepath, Path)


class TestLayerDiscovery:
    """Test the LayerDiscovery class."""

    def setup_method(self):
        """Clear registry before each test."""
        SchemaRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        SchemaRegistry.clear()

    def test_discover_layers_with_no_registry_and_no_files(self):
        """discover_layers() should return empty list when no schemas registered and no files exist."""
        with patch("pathlib.Path.exists", return_value=False):
            layers = LayerDiscovery.discover_layers()
            assert layers == []

    def test_discover_layers_returns_package_defaults_from_registry(self):
        """discover_layers() should return package defaults from SchemaRegistry."""
        # Register two schemas
        core_path = Path("/pkg/core/defaults.toml")
        effects_path = Path("/pkg/effects/defaults.yaml")

        SchemaRegistry.register("core", DummyConfig, core_path)
        SchemaRegistry.register("effects", AnotherConfig, effects_path)

        with patch("pathlib.Path.exists", return_value=True):
            layers = LayerDiscovery.discover_layers()

        # Should have 2 package default layers
        package_layers = [layer for layer in layers if "package-defaults" in layer.name]
        assert len(package_layers) == 2

        # Check core layer
        core_layer = next(
            (layer for layer in package_layers if layer.namespace == "core"), None
        )
        assert core_layer is not None
        assert core_layer.filepath == core_path
        assert core_layer.is_namespaced is False

        # Check effects layer
        effects_layer = next(
            (layer for layer in package_layers if layer.namespace == "effects"), None
        )
        assert effects_layer is not None
        assert effects_layer.filepath == effects_path
        assert effects_layer.is_namespaced is False

    def test_discover_layers_skips_nonexistent_package_defaults(self):
        """discover_layers() should skip package default files that don't exist."""
        existing_path = Path("/pkg/core/defaults.toml")
        missing_path = Path("/pkg/missing/defaults.toml")

        SchemaRegistry.register("core", DummyConfig, existing_path)
        SchemaRegistry.register("missing", AnotherConfig, missing_path)

        def mock_exists(self):
            return str(self) == str(existing_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers()

        package_layers = [layer for layer in layers if "package-defaults" in layer.name]
        assert len(package_layers) == 1
        assert package_layers[0].namespace == "core"

    def test_discover_layers_includes_project_root_when_exists(self):
        """discover_layers() should include project root settings.toml when it exists."""
        project_path = Path.cwd() / "settings.toml"

        def mock_exists(self):
            return str(self) == str(project_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers()

        project_layers = [layer for layer in layers if layer.name == "project-root"]
        assert len(project_layers) == 1
        assert project_layers[0].filepath == project_path
        assert project_layers[0].is_namespaced is True
        # Project root doesn't have single namespace (it's namespaced format)
        assert project_layers[0].namespace == ""

    def test_discover_layers_skips_project_root_when_missing(self):
        """discover_layers() should skip project root when settings.toml doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            layers = LayerDiscovery.discover_layers()

        project_layers = [layer for layer in layers if layer.name == "project-root"]
        assert len(project_layers) == 0

    def test_discover_layers_includes_user_config_when_exists(self):
        """discover_layers() should include user config when it exists."""
        app_name = "test-app"
        user_path = Path.home() / ".config" / app_name / "settings.toml"

        def mock_exists(self):
            return str(self) == str(user_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers(app_name=app_name)

        user_layers = [layer for layer in layers if layer.name == "user-config"]
        assert len(user_layers) == 1
        assert user_layers[0].filepath == user_path
        assert user_layers[0].is_namespaced is True
        assert user_layers[0].namespace == ""

    def test_discover_layers_skips_user_config_when_missing(self):
        """discover_layers() should skip user config when it doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            layers = LayerDiscovery.discover_layers(app_name="test-app")

        user_layers = [layer for layer in layers if layer.name == "user-config"]
        assert len(user_layers) == 0

    def test_discover_layers_uses_default_app_name(self):
        """discover_layers() should use 'layered-settings' as default app_name."""
        default_user_path = (
            Path.home() / ".config" / "layered-settings" / "settings.toml"
        )

        def mock_exists(self):
            return str(self) == str(default_user_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers()

        user_layers = [layer for layer in layers if layer.name == "user-config"]
        assert len(user_layers) == 1
        assert user_layers[0].filepath == default_user_path

    def test_discover_layers_respects_explicit_app_name(self):
        """discover_layers() should use explicit app_name when provided."""
        app_name = "my-custom-app"
        user_path = Path.home() / ".config" / app_name / "settings.toml"

        def mock_exists(self):
            return str(self) == str(user_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers(app_name=app_name)

        user_layers = [layer for layer in layers if layer.name == "user-config"]
        assert len(user_layers) == 1
        assert user_layers[0].filepath == user_path

    def test_discover_layers_returns_correct_priority_order(self):
        """discover_layers() should return layers in priority order: package defaults, project, user."""
        # Register schemas
        core_path = Path("/pkg/core/defaults.toml")
        effects_path = Path("/pkg/effects/defaults.yaml")
        SchemaRegistry.register("core", DummyConfig, core_path)
        SchemaRegistry.register("effects", AnotherConfig, effects_path)

        Path.cwd() / "settings.toml"
        Path.home() / ".config" / "test-app" / "settings.toml"

        # All files exist
        with patch("pathlib.Path.exists", return_value=True):
            layers = LayerDiscovery.discover_layers(app_name="test-app")

        # Extract layer names
        layer_names = [layer.name for layer in layers]

        # Package defaults should come first (both of them)
        package_indices = [
            i for i, name in enumerate(layer_names) if "package-defaults" in name
        ]
        project_index = layer_names.index("project-root")
        user_index = layer_names.index("user-config")

        # All package defaults should come before project root
        assert all(idx < project_index for idx in package_indices)
        # Project root should come before user config
        assert project_index < user_index

    def test_discover_layers_with_mixed_existence(self):
        """discover_layers() should handle mix of existing and non-existing files."""
        # Register schemas
        core_path = Path("/pkg/core/defaults.toml")
        missing_path = Path("/pkg/missing/defaults.yaml")
        SchemaRegistry.register("core", DummyConfig, core_path)
        SchemaRegistry.register("missing", AnotherConfig, missing_path)

        Path.cwd() / "settings.toml"
        user_path = Path.home() / ".config" / "test-app" / "settings.toml"

        # Only core defaults and user config exist
        def mock_exists(self):
            return str(self) in [str(core_path), str(user_path)]

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers(app_name="test-app")

        # Should have exactly 2 layers: core defaults and user config
        assert len(layers) == 2

        layer_names = [layer.name for layer in layers]
        assert "package-defaults-core" in layer_names
        assert "user-config" in layer_names
        assert "project-root" not in layer_names


class TestLayerDiscoveryIntegration:
    """Test realistic layer discovery scenarios."""

    def setup_method(self):
        """Clear registry before each test."""
        SchemaRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        SchemaRegistry.clear()

    def test_discover_full_application_layers(self):
        """Simulate discovering all layers for a real application."""

        class CoreSettings(BaseModel):
            parallel: bool = True

        class EffectsConfig(BaseModel):
            blur: int = 5

        class OrchestratorSettings(BaseModel):
            engine: str = "docker"

        # Register all schemas
        core_path = Path("/app/core/config/settings.toml")
        effects_path = Path("/app/effects/config/effects.yaml")
        orch_path = Path("/app/orchestrator/config/settings.toml")

        SchemaRegistry.register("core", CoreSettings, core_path)
        SchemaRegistry.register("effects", EffectsConfig, effects_path)
        SchemaRegistry.register("orchestrator", OrchestratorSettings, orch_path)

        project_path = Path.cwd() / "settings.toml"
        user_path = Path.home() / ".config" / "wallpaper-gen" / "settings.toml"

        # All files exist
        with patch("pathlib.Path.exists", return_value=True):
            layers = LayerDiscovery.discover_layers(app_name="wallpaper-gen")

        # Should have 5 layers total
        assert len(layers) == 5

        # Verify package defaults (first 3)
        package_layers = [layer for layer in layers if "package-defaults" in layer.name]
        assert len(package_layers) == 3
        assert all(not layer.is_namespaced for layer in package_layers)

        # Verify project root (4th)
        project_layers = [layer for layer in layers if layer.name == "project-root"]
        assert len(project_layers) == 1
        assert project_layers[0].filepath == project_path
        assert project_layers[0].is_namespaced is True

        # Verify user config (5th, last)
        user_layers = [layer for layer in layers if layer.name == "user-config"]
        assert len(user_layers) == 1
        assert user_layers[0].filepath == user_path
        assert user_layers[0].is_namespaced is True

    def test_discover_minimal_application_layers(self):
        """Simulate discovering layers when only package defaults exist."""

        class MinimalConfig(BaseModel):
            setting: str = "default"

        # Register single schema
        defaults_path = Path("/minimal/config/settings.toml")
        SchemaRegistry.register("minimal", MinimalConfig, defaults_path)

        # Only package defaults exist
        def mock_exists(self):
            return str(self) == str(defaults_path)

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers(app_name="minimal-app")

        # Should have only 1 layer
        assert len(layers) == 1
        assert layers[0].name == "package-defaults-minimal"
        assert layers[0].namespace == "minimal"
        assert not layers[0].is_namespaced

    def test_discover_user_only_override(self):
        """Simulate discovering layers when only user config exists (no project root)."""

        class AppConfig(BaseModel):
            value: str = "default"

        # Register schema
        defaults_path = Path("/app/config/settings.toml")
        SchemaRegistry.register("app", AppConfig, defaults_path)

        user_path = Path.home() / ".config" / "my-app" / "settings.toml"

        # Package defaults and user config exist, but not project root
        def mock_exists(self):
            return str(self) in [str(defaults_path), str(user_path)]

        with patch.object(Path, "exists", mock_exists):
            layers = LayerDiscovery.discover_layers(app_name="my-app")

        # Should have 2 layers
        assert len(layers) == 2

        # First should be package defaults
        assert "package-defaults" in layers[0].name
        # Second should be user config
        assert layers[1].name == "user-config"
