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


# ── run_batch() tests ──────────────────────────────────────────────────────


def test_run_batch_invalid_type(manager: ContainerManager, tmp_path: Path) -> None:
    """Invalid batch_type raises ValueError."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with pytest.raises(ValueError, match="Invalid batch_type"):
        manager.run_batch(batch_type="invalid", input_path=input_file, output_dir=tmp_path)


def test_run_batch_image_not_available(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Image not available raises RuntimeError."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch.object(manager, "is_image_available", return_value=False),
        pytest.raises(RuntimeError, match="Container image not found"),
    ):
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)


def test_run_batch_input_not_found(manager: ContainerManager, tmp_path: Path) -> None:
    """Missing input file raises FileNotFoundError."""
    input_file = tmp_path / "missing.jpg"
    with (
        patch.object(manager, "is_image_available", return_value=True),
        pytest.raises(FileNotFoundError, match="Input file not found"),
    ):
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)


def test_run_batch_permission_error(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """PermissionError on output dir is wrapped and re-raised."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch.object(manager, "is_image_available", return_value=True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        pytest.raises(PermissionError, match="Cannot create output directory"),
    ):
        mock_mkdir.side_effect = PermissionError("denied")
        manager.run_batch(
            batch_type="effects",
            input_path=input_file,
            output_dir=tmp_path / "forbidden",
        )


def test_run_batch_effects_command_structure(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Correct docker run command built for batch effects."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert "run" in call_args
        assert "--rm" in call_args
        assert "wallpaper-effects:latest" in call_args
        assert "batch" in call_args
        assert "effects" in call_args
        assert "/input/input.jpg" in call_args
        assert "-o" in call_args
        assert "/output" in call_args


def test_run_batch_composites_command_structure(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Correct batch type forwarded for composites."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="composites", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        assert "composites" in call_args


def test_run_batch_presets_command_structure(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Correct batch type forwarded for presets."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="presets", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        assert "presets" in call_args


def test_run_batch_all_command_structure(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Correct batch type forwarded for all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="all", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        assert "all" in call_args


def test_run_batch_flat_flag_forwarded(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """--flat flag forwarded to container command."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path, flat=True
        )
        assert "--flat" in mock_run.call_args[0][0]


def test_run_batch_sequential_flag_forwarded(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """--sequential flag forwarded when parallel=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path, parallel=False
        )
        call_args = mock_run.call_args[0][0]
        assert "--sequential" in call_args
        assert "--parallel" not in call_args


def test_run_batch_parallel_flag_forwarded(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """--parallel flag forwarded when parallel=True (default)."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path, parallel=True
        )
        assert "--parallel" in mock_run.call_args[0][0]


def test_run_batch_no_strict_flag_forwarded(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """--no-strict flag forwarded when strict=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path, strict=False
        )
        call_args = mock_run.call_args[0][0]
        assert "--no-strict" in call_args
        assert "--strict" not in call_args


def test_run_batch_strict_flag_forwarded(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """--strict flag forwarded when strict=True (default)."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path, strict=True
        )
        assert "--strict" in mock_run.call_args[0][0]


def test_run_batch_podman_adds_userns(tmp_path: Path) -> None:
    """Podman engine adds --userns=keep-id."""
    config = UnifiedConfig(orchestrator={"container": {"engine": "podman"}})
    podman_manager = ContainerManager(config)
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(podman_manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        podman_manager.run_batch(
            batch_type="effects", input_path=input_file, output_dir=tmp_path
        )
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"
        assert "--userns=keep-id" in call_args


def test_run_batch_docker_no_userns(manager: ContainerManager, tmp_path: Path) -> None:
    """Docker engine does NOT add --userns=keep-id."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)
        assert "--userns=keep-id" not in mock_run.call_args[0][0]


def test_run_batch_returns_process_result(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """CompletedProcess returncode and stderr are passed through."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=42, stdout="", stderr="batch error")
        result = manager.run_batch(
            batch_type="all", input_path=input_file, output_dir=tmp_path
        )
        assert result.returncode == 42
        assert result.stderr == "batch error"


def test_run_batch_uses_absolute_input_path(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Volume mount for input uses absolute path."""
    input_file = tmp_path / "wallpaper.jpg"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        mounts = [
            call_args[i + 1]
            for i, arg in enumerate(call_args)
            if arg == "-v" and i + 1 < len(call_args)
        ]
        input_mounts = [m for m in mounts if "/input" in m and ":ro" in m]
        assert len(input_mounts) == 1
        host_path = input_mounts[0].split(":")[0]
        assert Path(host_path).is_absolute()


def test_run_batch_preserves_original_filename(
    manager: ContainerManager, tmp_path: Path
) -> None:
    """Container receives /input/<original-name>, not /input/image.jpg."""
    input_file = tmp_path / "my-wallpaper.png"
    input_file.touch()
    with (
        patch("subprocess.run") as mock_run,
        patch.object(manager, "is_image_available", return_value=True),
    ):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        manager.run_batch(batch_type="effects", input_path=input_file, output_dir=tmp_path)
        call_args = mock_run.call_args[0][0]
        assert "/input/my-wallpaper.png" in call_args
        assert "/input/image.jpg" not in call_args
