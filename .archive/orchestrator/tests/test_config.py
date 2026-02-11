"""Tests for the config module."""

from pathlib import Path

import pytest
from wallpaper_effects.config import (
    BACKEND_VERSIONS,
    BASE_IMAGES,
    CONTAINER_CONFIG_DIR,
    CONTAINER_INPUT_DIR,
    CONTAINER_OUTPUT_DIR,
    DEFAULT_BACKEND,
    OrchestratorConfig,
)


class TestConstants:
    """Tests for configuration constants."""

    def test_base_images_defined(self) -> None:
        """Verify base images are defined."""
        # BASE_IMAGES only has 'python' key for the Python base image
        assert "python" in BASE_IMAGES
        assert all(isinstance(img, str) for img in BASE_IMAGES.values())

    def test_backend_versions_defined(self) -> None:
        """Verify backend versions are defined."""
        assert "imagemagick" in BACKEND_VERSIONS
        assert "pil" in BACKEND_VERSIONS
        for backend, info in BACKEND_VERSIONS.items():
            assert "version" in info

    def test_default_backend(self) -> None:
        """Verify default backend is valid."""
        assert DEFAULT_BACKEND in BACKEND_VERSIONS
        assert DEFAULT_BACKEND == "imagemagick"

    def test_container_paths(self) -> None:
        """Verify container mount paths are set."""
        assert CONTAINER_INPUT_DIR == "/input"
        assert CONTAINER_OUTPUT_DIR == "/output"
        assert CONTAINER_CONFIG_DIR == "/config"


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig dataclass."""

    def test_default_config(self) -> None:
        """Test creating config with defaults."""
        config = OrchestratorConfig.default()

        # runtime is None by default (auto-detected)
        assert config.runtime is None
        assert config.backend == "imagemagick"
        assert config.container_timeout == 300
        assert config.container_memory_limit == "1g"
        assert config.verbose is False
        assert isinstance(config.config_dir, Path)
        assert isinstance(config.output_dir, Path)

    def test_config_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test creating config from environment variables."""
        monkeypatch.setenv("WALLPAPER_EFFECTS_RUNTIME", "docker")
        monkeypatch.setenv("WALLPAPER_EFFECTS_BACKEND", "pil")
        monkeypatch.setenv("WALLPAPER_EFFECTS_VERBOSE", "true")

        config = OrchestratorConfig.from_env()

        assert config.runtime == "docker"
        assert config.backend == "pil"
        assert config.verbose is True

    def test_config_paths_expanduser(self) -> None:
        """Test that config paths expand user home directory."""
        config = OrchestratorConfig.default()

        # Paths should not contain ~
        assert "~" not in str(config.config_dir)
        assert "~" not in str(config.output_dir)

    def test_config_custom_values(self, tmp_path: Path) -> None:
        """Test config with custom values."""
        config = OrchestratorConfig(
            runtime="podman",
            backend="pil",
            config_dir=tmp_path / "config",
            output_dir=tmp_path / "output",
            container_timeout=600,
            container_memory_limit="2g",
            verbose=True,
        )

        assert config.runtime == "podman"
        assert config.backend == "pil"
        assert config.config_dir == tmp_path / "config"
        assert config.output_dir == tmp_path / "output"
        assert config.container_timeout == 600
        assert config.container_memory_limit == "2g"
        assert config.verbose is True
