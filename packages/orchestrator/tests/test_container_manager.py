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


def test_manager_init(manager: ContainerManager, config: UnifiedConfig) -> None:
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


def test_build_volume_mounts(manager: ContainerManager, tmp_path: Path) -> None:
    """Test build_volume_mounts creates correct mount specs."""
    input_image = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"

    input_image.touch()
    output_dir.mkdir()

    mounts = manager.build_volume_mounts(input_image, output_dir)

    assert len(mounts) == 2
    assert f"{input_image}:/input/input.jpg:ro" in mounts  # Uses actual filename
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


def test_is_image_available_subprocess_error(
    manager: ContainerManager,
) -> None:
    """Test is_image_available returns False on SubprocessError."""
    import subprocess

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.SubprocessError("Docker not found")

        result = manager.is_image_available()

        assert result is False


def test_is_image_available_file_not_found(manager: ContainerManager) -> None:
    """Test is_image_available returns False on FileNotFoundError."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("docker command not found")

        result = manager.is_image_available()

        assert result is False


def test_run_process_invalid_command_type(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process raises ValueError for invalid command_type."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    output_file = tmp_path / "output.jpg"

    with pytest.raises(ValueError, match="Invalid command_type"):
        manager.run_process(
            command_type="invalid",
            command_name="test",
            input_path=input_file,
            output_dir=output_file.parent,
        )


def test_run_process_empty_command_name(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process raises ValueError for empty command_name."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    output_file = tmp_path / "output.jpg"

    with pytest.raises(ValueError, match="command_name cannot be empty"):
        manager.run_process(
            command_type="effect",
            command_name="",
            input_path=input_file,
            output_dir=output_file.parent,
        )


def test_run_process_permission_error(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process raises PermissionError when output dir cannot be created."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    output_file = tmp_path / "forbidden" / "output.jpg"

    # Mock is_image_available and patch mkdir to fail
    with (
        patch.object(manager, "is_image_available", return_value=True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_mkdir.side_effect = PermissionError("Permission denied")

        with pytest.raises(PermissionError, match="Cannot create output directory"):
            manager.run_process(
                command_type="effect",
                command_name="blur",
                input_path=input_file,
                output_dir=output_file.parent,
            )
