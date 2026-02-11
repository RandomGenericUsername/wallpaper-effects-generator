"""Tests for ContainerManager.run_process() container execution."""

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


def test_run_process_effect_builds_correct_command(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process constructs proper docker run command for effect."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        # Verify subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args[0][0]

        # Verify command structure
        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "wallpaper-effects:latest" in call_args

        # Verify mounts - extract volume mount arguments
        volume_mounts = [arg for arg in call_args if arg.startswith("-v")]
        assert (
            len(volume_mounts) >= 2
        ), "Should have at least input and output mounts"

        # Find the actual mount specifications (they follow -v flags)
        mount_specs = []
        for i, arg in enumerate(call_args):
            if arg == "-v" and i + 1 < len(call_args):
                mount_specs.append(call_args[i + 1])

        # Verify input mount (read-only)
        input_mounts = [m for m in mount_specs if "/input" in m and ":ro" in m]
        assert len(input_mounts) == 1, "Should have one read-only input mount"

        # Verify output mount (read-write)
        output_mounts = [
            m for m in mount_specs if "/output" in m and ":rw" in m
        ]
        assert (
            len(output_mounts) == 1
        ), "Should have one read-write output mount"

        # Verify core command
        assert "process" in call_args
        assert "effect" in call_args
        assert "/input/image.jpg" in call_args
        assert "blur" in call_args

        # Verify result
        assert result.returncode == 0


def test_run_process_validates_image_exists(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process raises error if container image doesn't exist."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch.object(manager, "is_image_available", return_value=False):
        with pytest.raises(
            RuntimeError,
            match="Container image not found.*wallpaper-process install",
        ):
            manager.run_process(
                command_type="effect",
                command_name="blur",
                input_path=input_file,
                output_path=output_file,
            )


def test_run_process_validates_input_exists(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process raises error if input file doesn't exist."""
    input_file = tmp_path / "missing.jpg"  # Don't create
    output_file = tmp_path / "output.jpg"

    with patch.object(manager, "is_image_available", return_value=True):
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            manager.run_process(
                command_type="effect",
                command_name="blur",
                input_path=input_file,
                output_path=output_file,
            )


def test_run_process_creates_output_directory(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process creates output directory if needed."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "nested" / "output"
    output_file = output_dir / "result.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        # Verify output directory was created
        assert output_dir.exists()
        assert output_dir.is_dir()


def test_run_process_uses_absolute_paths(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process converts paths to absolute."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        call_args = mock_run.call_args[0][0]
        # Find volume mount arguments
        mounts = [arg for arg in call_args if ":" in arg and "/" in arg]

        # Verify all paths are absolute
        for mount in mounts:
            host_path = mount.split(":")[0]
            assert Path(host_path).is_absolute()


def test_run_process_returns_container_exit_code(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process returns container's exit code."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(
            returncode=42, stdout="", stderr="error"
        )

        result = manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        assert result.returncode == 42
        assert result.stderr == "error"


def test_run_process_with_podman_engine(tmp_path: Path) -> None:
    """Test run_process works with podman engine."""
    config = UnifiedConfig(orchestrator={"container": {"engine": "podman"}})
    manager = ContainerManager(config)

    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"


def test_run_process_with_additional_args(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Test run_process passes additional arguments to container."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
            additional_args=["--intensity", "5"],
        )

        call_args = mock_run.call_args[0][0]
        # Verify additional args are included
        assert "--intensity" in call_args
        assert "5" in call_args
