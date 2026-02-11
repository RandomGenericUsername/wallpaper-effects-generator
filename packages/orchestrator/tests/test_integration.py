"""Integration tests for wallpaper_orchestrator."""

from layered_settings import configure, get_config
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager


def test_unified_config_loads_all_schemas() -> None:
    """Test UnifiedConfig loads core + effects + orchestrator."""
    configure(UnifiedConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have all three namespaces
    assert hasattr(config, "core")
    assert hasattr(config, "effects")
    assert hasattr(config, "orchestrator")

    # Core settings loaded
    assert config.core.execution.parallel is True
    assert config.core.backend.binary == "magick"

    # Effects loaded
    assert config.effects.version == "1.0"
    assert len(config.effects.effects) > 0

    # Orchestrator settings loaded
    assert config.orchestrator.container.engine == "docker"
    assert (
        config.orchestrator.container.image_name == "wallpaper-effects:latest"
    )


def test_config_merges_cli_overrides() -> None:
    """Test CLI overrides work across all namespaces."""
    configure(UnifiedConfig, app_name="wallpaper-effects-test")
    config = get_config(
        overrides={
            "core.execution.parallel": False,
            "orchestrator.container.engine": "podman",
        }
    )

    assert config.core.execution.parallel is False
    assert config.orchestrator.container.engine == "podman"


def test_container_manager_uses_config() -> None:
    """Test ContainerManager integrates with UnifiedConfig."""
    config = UnifiedConfig(orchestrator={"container": {"engine": "podman"}})
    manager = ContainerManager(config)

    assert manager.engine == "podman"
    assert manager.get_image_name() == "wallpaper-effects:latest"


def test_container_manager_with_registry() -> None:
    """Test ContainerManager handles image registry."""
    config = UnifiedConfig(
        orchestrator={"container": {"image_registry": "ghcr.io/user"}}
    )
    manager = ContainerManager(config)

    assert manager.get_image_name() == "ghcr.io/user/wallpaper-effects:latest"


def test_cli_commands_registered() -> None:
    """Test all CLI commands are registered."""
    from wallpaper_orchestrator.cli.main import app

    # Get all registered commands (some may have None name, check callback)
    command_names = {
        cmd.name or cmd.callback.__name__ for cmd in app.registered_commands
    }

    # Should have orchestrator commands
    assert "install" in command_names
    assert "uninstall" in command_names

    # Should have core command
    assert "info" in command_names
