"""Integration tests for the layered_settings public API.

These tests verify the complete workflow from schema registration through
configuration building, including caching and override behavior.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from layered_settings import SchemaRegistry, configure, get_config
from layered_settings.errors import SettingsError
from pydantic import BaseModel


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


class TestConfigureFunction:
    """Test the configure() function."""

    def test_configure_stores_root_model_and_app_name(self, tmp_path: Path) -> None:
        """configure() should store the root model and app name."""
        # Setup: clear registry
        SchemaRegistry.clear()

        # Create dummy defaults file
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = true\nworkers = 4\n")

        # Register a schema
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        # Act: configure the system
        configure(root_model=AppConfig, app_name="test-app")

        # Assert: should not raise, state stored internally
        # (we'll verify by calling get_config() in next test)

    def test_configure_clears_cache(self, tmp_path: Path) -> None:
        """configure() should clear any existing cached configuration."""
        # Setup: configure once and build config to populate cache
        SchemaRegistry.clear()
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        configure(root_model=AppConfig, app_name="test-app")
        first_config = get_config()

        # Act: configure again (simulating reconfiguration)
        configure(root_model=AppConfig, app_name="test-app-2")

        # Assert: cache should be cleared, next get_config() rebuilds
        second_config = get_config()

        # Both should be valid but independently created
        assert isinstance(first_config, AppConfig)
        assert isinstance(second_config, AppConfig)


class TestGetConfigFunction:
    """Test the get_config() function."""

    def test_get_config_raises_if_not_configured(self) -> None:
        """get_config() should raise RuntimeError if configure() not called."""
        # Setup: clear any previous configuration
        SchemaRegistry.clear()

        # Clear global state by accessing the module's private variables
        import layered_settings

        layered_settings._configured_model = None
        layered_settings._app_name = None
        layered_settings._config_cache = None

        with pytest.raises(RuntimeError) as exc_info:
            get_config()

        assert "configure() must be called" in str(exc_info.value)

    def test_get_config_returns_validated_instance(self, tmp_path: Path) -> None:
        """get_config() should return a validated instance of the root model."""
        # Setup: register schema and configure
        SchemaRegistry.clear()
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = false\nworkers = 8\n")
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        configure(root_model=AppConfig, app_name="test-app")

        # Act: get config
        config = get_config()

        # Assert: should return AppConfig instance with loaded values
        assert isinstance(config, AppConfig)
        assert config.core.parallel is False
        assert config.core.workers == 8

    def test_get_config_caches_result(self, tmp_path: Path) -> None:
        """get_config() should cache the result and return same instance."""
        # Setup
        SchemaRegistry.clear()
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        configure(root_model=AppConfig, app_name="test-app")

        # Act: call get_config() twice
        first_call = get_config()
        second_call = get_config()

        # Assert: should return the same cached instance
        assert first_call is second_call

    def test_get_config_with_overrides_does_not_cache(self, tmp_path: Path) -> None:
        """get_config() with overrides should not cache (returns fresh instance)."""
        # Setup
        SchemaRegistry.clear()
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        configure(root_model=AppConfig, app_name="test-app")

        # Act: call get_config() with different overrides
        first_call = get_config(overrides={"core.workers": 8})
        second_call = get_config(overrides={"core.workers": 16})

        # Assert: should return different instances with different values
        assert first_call is not second_call
        assert first_call.core.workers == 8
        assert second_call.core.workers == 16

    def test_get_config_overrides_do_not_affect_cache(self, tmp_path: Path) -> None:
        """get_config() with overrides should not affect the cached base config."""
        # Setup
        SchemaRegistry.clear()
        defaults_file = tmp_path / "defaults.toml"
        defaults_file.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, defaults_file)

        configure(root_model=AppConfig, app_name="test-app")

        # Act: get base config, then get with overrides, then get base again
        base_config = get_config()
        override_config = get_config(overrides={"core.workers": 99})
        base_config_again = get_config()

        # Assert: base config should be cached and unaffected
        assert base_config is base_config_again
        assert base_config.core.workers == 4
        assert override_config.core.workers == 99


class TestFullWorkflow:
    """Test complete end-to-end workflow."""

    def test_full_workflow_with_package_defaults(self, tmp_path: Path) -> None:
        """Test complete workflow: register -> configure -> get_config."""
        # Setup: clear registry
        SchemaRegistry.clear()

        # Step 1: Register schemas with package defaults
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text(
            """
parallel = false
workers = 8
timeout = 60.0
"""
        )

        effects_defaults = tmp_path / "effects_defaults.toml"
        effects_defaults.write_text(
            """
blur = 10
brightness = 0.8
filters = ["sharpen", "contrast"]
"""
        )

        SchemaRegistry.register("core", CoreSettings, core_defaults)
        SchemaRegistry.register("effects", EffectsSettings, effects_defaults)

        # Step 2: Configure the system
        configure(root_model=AppConfig, app_name="test-app")

        # Step 3: Get configuration
        config = get_config()

        # Assert: configuration loaded from package defaults
        assert isinstance(config, AppConfig)
        assert config.core.parallel is False
        assert config.core.workers == 8
        assert config.core.timeout == 60.0
        assert config.effects.blur == 10
        assert config.effects.brightness == 0.8
        assert config.effects.filters == ["sharpen", "contrast"]

    def test_full_workflow_with_project_settings(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test workflow with project root settings.toml."""
        # Setup: clear registry and change to tmp directory
        SchemaRegistry.clear()
        monkeypatch.chdir(tmp_path)

        # Step 1: Register package defaults
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, core_defaults)

        # Step 2: Create project settings.toml (namespaced format)
        project_settings = tmp_path / "settings.toml"
        project_settings.write_text(
            """
[core]
workers = 16
timeout = 120.0

[effects]
blur = 20
"""
        )

        # Step 3: Configure and get config
        configure(root_model=AppConfig, app_name="test-app")
        config = get_config()

        # Assert: project settings should override package defaults
        assert config.core.parallel is True  # from defaults
        assert config.core.workers == 16  # overridden by project
        assert config.core.timeout == 120.0  # from project
        assert config.effects.blur == 20  # from project

    def test_full_workflow_with_user_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test workflow with user config directory."""
        # Setup: clear registry
        SchemaRegistry.clear()
        monkeypatch.chdir(tmp_path)

        # Step 1: Register package defaults
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, core_defaults)

        # Step 2: Mock user config directory
        user_config_dir = tmp_path / ".config" / "test-app"
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / "settings.toml"
        user_config.write_text(
            """
[core]
workers = 32
"""
        )

        # Mock Path.home() to return tmp_path
        with patch("layered_settings.layers.Path.home", return_value=tmp_path):
            # Step 3: Configure and get config
            configure(root_model=AppConfig, app_name="test-app")
            config = get_config()

            # Assert: user config should override package defaults
            assert config.core.workers == 32

    def test_full_workflow_with_cli_overrides(self, tmp_path: Path) -> None:
        """Test workflow with CLI overrides (highest priority)."""
        # Setup
        SchemaRegistry.clear()

        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("parallel = true\nworkers = 4\n")
        SchemaRegistry.register("core", CoreSettings, core_defaults)

        configure(root_model=AppConfig, app_name="test-app")

        # Act: get config with CLI overrides
        config = get_config(overrides={"core.workers": 64, "effects.blur": 30})

        # Assert: CLI overrides should have highest priority
        assert config.core.workers == 64
        assert config.effects.blur == 30

    def test_layer_priority_order(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that layers are applied in correct priority order."""
        # Setup: create all layer types
        SchemaRegistry.clear()
        monkeypatch.chdir(tmp_path)

        # Package defaults (lowest priority)
        core_defaults = tmp_path / "core_defaults.toml"
        core_defaults.write_text("parallel = true\nworkers = 4\ntimeout = 30.0\n")
        SchemaRegistry.register("core", CoreSettings, core_defaults)

        # Project settings (medium priority)
        project_settings = tmp_path / "settings.toml"
        project_settings.write_text("[core]\nworkers = 16\n")

        # User config (high priority)
        user_config_dir = tmp_path / ".config" / "test-app"
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / "settings.toml"
        user_config.write_text("[core]\ntimeout = 120.0\n")

        # Mock Path.home()
        with patch("layered_settings.layers.Path.home", return_value=tmp_path):
            configure(root_model=AppConfig, app_name="test-app")

            # Act: get config with CLI overrides (highest priority)
            config = get_config(overrides={"core.parallel": False})

            # Assert: each layer should override the previous
            # parallel: CLI override (False)
            # workers: project settings (16)
            # timeout: user config (120.0)
            assert config.core.parallel is False  # CLI
            assert config.core.workers == 16  # project
            assert config.core.timeout == 120.0  # user


class TestErrorHandling:
    """Test error handling in public API."""

    def test_configure_without_registration_works(self) -> None:
        """configure() should work even if no schemas registered."""
        SchemaRegistry.clear()

        # Should not raise
        configure(root_model=AppConfig, app_name="test-app")

    def test_get_config_with_validation_error(self, tmp_path: Path) -> None:
        """get_config() should raise SettingsValidationError on invalid data."""
        # Setup: create defaults with invalid type
        SchemaRegistry.clear()

        core_defaults = tmp_path / "core_defaults.toml"
        # workers should be int, but we'll provide string
        core_defaults.write_text('parallel = true\nworkers = "invalid"\n')
        SchemaRegistry.register("core", CoreSettings, core_defaults)

        configure(root_model=AppConfig, app_name="test-app")

        # Act & Assert
        with pytest.raises(SettingsError):  # Should raise validation error
            get_config()


class TestPublicAPIExports:
    """Test that public API exports the correct symbols."""

    def test_configure_is_exported(self) -> None:
        """configure function should be exported."""
        from layered_settings import configure as imported_configure

        assert callable(imported_configure)

    def test_get_config_is_exported(self) -> None:
        """get_config function should be exported."""
        from layered_settings import get_config as imported_get_config

        assert callable(imported_get_config)

    def test_schema_registry_is_exported(self) -> None:
        """SchemaRegistry class should be exported."""
        from layered_settings import SchemaRegistry as imported_registry

        assert hasattr(imported_registry, "register")
        assert hasattr(imported_registry, "get")
