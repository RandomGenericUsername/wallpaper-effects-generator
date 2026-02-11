"""Tests for ContainerManager."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager


@pytest.fixture
def config() -> UnifiedConfig:
    """Create test configuration."""
    return UnifiedConfig()


@pytest.fixture
def manager(config: UnifiedConfig) -> ContainerManager:
    """Create container manager."""
    return ContainerManager(config)


def test_manager_init(
    manager: ContainerManager, config: UnifiedConfig
) -> None:
    """Test ContainerManager initialization."""
    assert manager.config == config
    assert manager.engine == "docker"


def test_get_image_name_without_registry(manager: ContainerManager) -> None:
    """Test get_image_name without registry."""
    image = manager.get_image_name()
    assert image == "wallpaper-effects:latest"


def test_get_image_name_with_registry() -> None:
    """Test get_image_name with registry."""
    config = UnifiedConfig(
        orchestrator={"container": {"image_registry": "ghcr.io/user"}}
    )
    manager = ContainerManager(config)

    image = manager.get_image_name()
    assert image == "ghcr.io/user/wallpaper-effects:latest"


def test_build_volume_mounts(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test build_volume_mounts creates correct mount specs."""
    input_image = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"

    input_image.touch()
    output_dir.mkdir()

    mounts = manager.build_volume_mounts(input_image, output_dir)

    assert len(mounts) == 2
    assert f"{input_image}:/input/image.png:ro" in mounts
    assert f"{output_dir}:/output:rw" in mounts


def test_is_image_available_true(manager: ContainerManager) -> None:
    """Test is_image_available returns True when image exists."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        result = manager.is_image_available()

        assert result is True
        mock_run.assert_called_once()
        assert "docker" in mock_run.call_args[0][0]
        assert "inspect" in mock_run.call_args[0][0]


def test_is_image_available_false(manager: ContainerManager) -> None:
    """Test is_image_available returns False when image missing."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)

        result = manager.is_image_available()

        assert result is False
