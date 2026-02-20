"""Tests for schema registry in layered_settings."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from layered_settings.errors import SettingsRegistryError
from layered_settings.registry import SchemaEntry, SchemaRegistry


class DummyConfig(BaseModel):
    """Dummy config for testing."""

    value: str = Field(default="test")


class AnotherConfig(BaseModel):
    """Another dummy config for testing."""

    number: int = Field(default=42)


class TestSchemaEntry:
    """Test the SchemaEntry dataclass."""

    def test_creates_entry_with_all_fields(self):
        """SchemaEntry should be creatable with namespace, model, and defaults_file."""
        entry = SchemaEntry(
            namespace="test.config",
            model=DummyConfig,
            defaults_file=Path("/path/to/defaults.toml"),
        )
        assert entry.namespace == "test.config"
        assert entry.model == DummyConfig
        assert entry.defaults_file == Path("/path/to/defaults.toml")

    def test_entry_is_immutable(self):
        """SchemaEntry should be immutable (frozen dataclass)."""
        entry = SchemaEntry(
            namespace="test",
            model=DummyConfig,
            defaults_file=Path("/test.toml"),
        )
        with pytest.raises(AttributeError):
            entry.namespace = "modified"  # type: ignore

    def test_stores_model_type_not_instance(self):
        """SchemaEntry should store model type, not instance."""
        entry = SchemaEntry(
            namespace="test",
            model=DummyConfig,
            defaults_file=Path("/test.toml"),
        )
        # Should be the class itself, not an instance
        assert entry.model is DummyConfig
        assert not isinstance(entry.model, DummyConfig)


class TestSchemaRegistry:
    """Test the SchemaRegistry class."""

    def setup_method(self):
        """Clear registry before each test."""
        SchemaRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        SchemaRegistry.clear()

    def test_register_creates_new_entry(self):
        """register() should create a new schema entry."""
        defaults_path = Path("/path/to/defaults.toml")
        SchemaRegistry.register(
            namespace="core.config",
            model=DummyConfig,
            defaults_file=defaults_path,
        )

        entry = SchemaRegistry.get("core.config")
        assert entry is not None
        assert entry.namespace == "core.config"
        assert entry.model == DummyConfig
        assert entry.defaults_file == defaults_path

    def test_register_with_different_namespaces(self):
        """register() should allow multiple different namespaces."""
        SchemaRegistry.register(
            namespace="core",
            model=DummyConfig,
            defaults_file=Path("/core.toml"),
        )
        SchemaRegistry.register(
            namespace="effects",
            model=AnotherConfig,
            defaults_file=Path("/effects.yaml"),
        )

        core_entry = SchemaRegistry.get("core")
        effects_entry = SchemaRegistry.get("effects")

        assert core_entry is not None
        assert effects_entry is not None
        assert core_entry.model == DummyConfig
        assert effects_entry.model == AnotherConfig

    def test_register_duplicate_namespace_raises_error(self):
        """register() should raise SettingsRegistryError for duplicate namespace."""
        SchemaRegistry.register(
            namespace="duplicate",
            model=DummyConfig,
            defaults_file=Path("/test1.toml"),
        )

        with pytest.raises(SettingsRegistryError) as exc_info:
            SchemaRegistry.register(
                namespace="duplicate",
                model=AnotherConfig,
                defaults_file=Path("/test2.toml"),
            )

        error = exc_info.value
        assert error.namespace == "duplicate"
        assert "already registered" in error.reason.lower()
        assert "duplicate" in str(error)

    def test_get_returns_none_for_unregistered_namespace(self):
        """get() should return None for unregistered namespace."""
        result = SchemaRegistry.get("nonexistent.namespace")
        assert result is None

    def test_get_returns_correct_entry(self):
        """get() should return the correct entry for registered namespace."""
        path1 = Path("/path1.toml")
        path2 = Path("/path2.yaml")

        SchemaRegistry.register("ns1", DummyConfig, path1)
        SchemaRegistry.register("ns2", AnotherConfig, path2)

        entry1 = SchemaRegistry.get("ns1")
        entry2 = SchemaRegistry.get("ns2")

        assert entry1 is not None
        assert entry1.namespace == "ns1"
        assert entry1.model == DummyConfig
        assert entry1.defaults_file == path1

        assert entry2 is not None
        assert entry2.namespace == "ns2"
        assert entry2.model == AnotherConfig
        assert entry2.defaults_file == path2

    def test_all_namespaces_returns_empty_list_when_empty(self):
        """all_namespaces() should return empty list when no schemas registered."""
        namespaces = SchemaRegistry.all_namespaces()
        assert namespaces == []

    def test_all_namespaces_returns_all_registered_namespaces(self):
        """all_namespaces() should return list of all registered namespaces."""
        SchemaRegistry.register("core", DummyConfig, Path("/core.toml"))
        SchemaRegistry.register("effects", AnotherConfig, Path("/effects.yaml"))
        SchemaRegistry.register("orchestrator", DummyConfig, Path("/orch.toml"))

        namespaces = SchemaRegistry.all_namespaces()
        assert set(namespaces) == {"core", "effects", "orchestrator"}
        assert len(namespaces) == 3

    def test_all_entries_returns_empty_list_when_empty(self):
        """all_entries() should return empty list when no schemas registered."""
        entries = SchemaRegistry.all_entries()
        assert entries == []

    def test_all_entries_returns_all_schema_entries(self):
        """all_entries() should return list of all SchemaEntry objects."""
        path1 = Path("/core.toml")
        path2 = Path("/effects.yaml")

        SchemaRegistry.register("core", DummyConfig, path1)
        SchemaRegistry.register("effects", AnotherConfig, path2)

        entries = SchemaRegistry.all_entries()
        assert len(entries) == 2

        # Convert to dict for easier testing
        entries_dict = {e.namespace: e for e in entries}
        assert "core" in entries_dict
        assert "effects" in entries_dict
        assert entries_dict["core"].model == DummyConfig
        assert entries_dict["core"].defaults_file == path1
        assert entries_dict["effects"].model == AnotherConfig
        assert entries_dict["effects"].defaults_file == path2

    def test_clear_removes_all_registrations(self):
        """clear() should remove all registered schemas."""
        SchemaRegistry.register("ns1", DummyConfig, Path("/test1.toml"))
        SchemaRegistry.register("ns2", AnotherConfig, Path("/test2.yaml"))

        # Verify they're registered
        assert SchemaRegistry.get("ns1") is not None
        assert SchemaRegistry.get("ns2") is not None
        assert len(SchemaRegistry.all_namespaces()) == 2

        # Clear and verify
        SchemaRegistry.clear()
        assert SchemaRegistry.get("ns1") is None
        assert SchemaRegistry.get("ns2") is None
        assert SchemaRegistry.all_namespaces() == []
        assert SchemaRegistry.all_entries() == []

    def test_clear_allows_re_registration(self):
        """clear() should allow re-registering same namespace."""
        SchemaRegistry.register("test", DummyConfig, Path("/test1.toml"))
        SchemaRegistry.clear()

        # Should not raise error
        SchemaRegistry.register("test", AnotherConfig, Path("/test2.toml"))
        entry = SchemaRegistry.get("test")
        assert entry is not None
        assert entry.model == AnotherConfig

    def test_registry_uses_class_level_storage(self):
        """Registry should use class-level storage (not instance-level)."""
        # Register on the class
        SchemaRegistry.register("test", DummyConfig, Path("/test.toml"))

        # Access should work without creating instances
        entry = SchemaRegistry.get("test")
        assert entry is not None

        # All methods should work as class methods
        assert "test" in SchemaRegistry.all_namespaces()
        assert len(SchemaRegistry.all_entries()) == 1


class TestRegistryIntegration:
    """Test realistic registry usage scenarios."""

    def setup_method(self):
        """Clear registry before each test."""
        SchemaRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        SchemaRegistry.clear()

    def test_register_multiple_schemas_for_application(self):
        """Simulate registering schemas for a real application."""

        class CoreSettings(BaseModel):
            parallel: bool = True
            max_workers: int = 4

        class EffectsConfig(BaseModel):
            default_blur: int = 5

        class OrchestratorSettings(BaseModel):
            engine: str = "docker"

        # Register all schemas
        SchemaRegistry.register(
            "core",
            CoreSettings,
            Path("/app/core/config/settings.toml"),
        )
        SchemaRegistry.register(
            "effects",
            EffectsConfig,
            Path("/app/core/effects/effects.yaml"),
        )
        SchemaRegistry.register(
            "orchestrator",
            OrchestratorSettings,
            Path("/app/orchestrator/config/settings.toml"),
        )

        # Verify all registered correctly
        namespaces = SchemaRegistry.all_namespaces()
        assert len(namespaces) == 3
        assert set(namespaces) == {"core", "effects", "orchestrator"}

        # Verify each entry
        core = SchemaRegistry.get("core")
        assert core is not None
        assert core.model == CoreSettings

        effects = SchemaRegistry.get("effects")
        assert effects is not None
        assert effects.model == EffectsConfig

        orchestrator = SchemaRegistry.get("orchestrator")
        assert orchestrator is not None
        assert orchestrator.model == OrchestratorSettings

    def test_prevents_accidental_duplicate_registration(self):
        """Registry should prevent accidentally registering same namespace twice."""

        class SettingsV1(BaseModel):
            version: int = 1

        class SettingsV2(BaseModel):
            version: int = 2

        # Register v1
        SchemaRegistry.register("app.settings", SettingsV1, Path("/v1.toml"))

        # Attempt to register v2 with same namespace should fail
        with pytest.raises(SettingsRegistryError) as exc_info:
            SchemaRegistry.register("app.settings", SettingsV2, Path("/v2.toml"))

        assert "already registered" in str(exc_info.value).lower()

        # Original registration should still be active
        entry = SchemaRegistry.get("app.settings")
        assert entry is not None
        assert entry.model == SettingsV1
