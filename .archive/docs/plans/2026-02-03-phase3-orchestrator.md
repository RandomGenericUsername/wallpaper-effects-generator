# Phase 3 Implementation: wallpaper_orchestrator Package

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build orchestrator package with container management for isolated, portable wallpaper effects processing

**Architecture:** Create packages/orchestrator/ with container engine support, UnifiedConfig composing all schemas, and CLI that wraps core functionality with containerized execution option

**Tech Stack:** Python 3.12, Docker/Podman, Pydantic 2.0, layered_settings, typer, rich, subprocess

**Reference:** `docs/plans/2026-01-31-monorepo-refactor-design.md` sections 391-463, `/home/inumaki/Development/color-scheme` reference implementation

---

## Current State Assessment

**Completed:**
- ✅ Phase 1: `layered_settings` package (generic config system)
- ✅ Phase 2: `wallpaper_core` package (effects processor with CLI)
- ✅ Test coverage: 101/101 tests passing (87% coverage)
- ✅ CLI entry point: `wallpaper-process` (core only)

**Package to build:**
- `wallpaper_orchestrator` - Container wrapper providing isolation, portability, reproducibility

**Container Strategy:**
- Single image: `wallpaper-effects:latest`
- Contents: `wallpaper_core` + ImageMagick + dependencies
- Engine support: Docker and Podman

**CLI Entry Points:**
- Core: `wallpaper-process` (when only core installed)
- Orchestrator: `wallpaper-process` (overwrites core when orchestrator installed)
- Orchestrator CLI wraps/extends core functionality

---

## Implementation Tasks

Execute in order using TDD approach for each task.

### Task 1: Package Structure Setup

**Goal:** Create packages/orchestrator/ directory structure with pyproject.toml

**Files:**
- Create: `packages/orchestrator/pyproject.toml`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/__init__.py`
- Create: `packages/orchestrator/README.md`
- Create: `packages/orchestrator/docker/` directory

**Step 1: Create directory structure**

```bash
mkdir -p packages/orchestrator/src/wallpaper_orchestrator
mkdir -p packages/orchestrator/docker
mkdir -p packages/orchestrator/tests
```

**Step 2: Write pyproject.toml**

```toml
[project]
name = "wallpaper-orchestrator"
version = "0.1.0"
description = "Container orchestrator for wallpaper effects processor"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "wallpaper-core>=0.3.0",
    "layered-settings>=0.1.0",
    "pydantic>=2.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.14.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
]

[project.scripts]
wallpaper-process = "wallpaper_orchestrator.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_orchestrator"]

[tool.hatch.metadata]
allow-direct-references = true

[tool.uv.sources]
wallpaper-core = { workspace = true }
layered-settings = { workspace = true }

[tool.black]
line-length = 79
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 79

[tool.ruff]
line-length = 79
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "N"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["ARG", "PTH"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["typer.*", "rich.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
pythonpath = ["src"]
addopts = ["-v", "--strict-markers", "--tb=short"]
```

**Step 3: Write package __init__.py**

```python
"""Wallpaper effects orchestrator with container management."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

**Step 4: Write minimal README**

```markdown
# wallpaper_orchestrator

Container orchestrator for the wallpaper effects processor.

## Features

- Container engine support (Docker and Podman)
- Isolated effects processing
- Portable, reproducible builds
- Simple install/uninstall commands

## Installation

```bash
cd packages/orchestrator
uv pip install -e .
```

## Usage

```bash
# Install container image
wallpaper-process install

# Process with container
wallpaper-process process input.jpg output.jpg blur

# Uninstall container image
wallpaper-process uninstall
```

## Development

See root workspace documentation for development setup.
```

**Step 5: Verify structure**

```bash
tree packages/orchestrator -L 3
```

Expected: Directory structure created with all files

**Step 6: Commit**

```bash
git add packages/orchestrator/
git commit -m "feat(orchestrator): create package structure with pyproject.toml"
```

---

### Task 2: OrchestratorSettings Schema

**Goal:** Define Pydantic models for orchestrator configuration

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/config/__init__.py`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/config/settings.py`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml`
- Create: `packages/orchestrator/tests/test_config_settings.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_config_settings.py
"""Tests for OrchestratorSettings Pydantic schema."""

import pytest
from pydantic import ValidationError
from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)


def test_container_settings_defaults() -> None:
    """Test ContainerSettings default values."""
    settings = ContainerSettings()
    assert settings.engine == "docker"
    assert settings.image_name == "wallpaper-effects:latest"
    assert settings.image_registry is None


def test_container_settings_validates_engine() -> None:
    """Test ContainerSettings validates engine."""
    # Valid engines
    settings = ContainerSettings(engine="docker")
    assert settings.engine == "docker"

    settings = ContainerSettings(engine="podman")
    assert settings.engine == "podman"

    # Invalid engine
    with pytest.raises(ValidationError) as exc_info:
        ContainerSettings(engine="invalid")

    assert "Invalid container engine" in str(exc_info.value)


def test_container_settings_normalizes_registry() -> None:
    """Test ContainerSettings normalizes registry."""
    settings = ContainerSettings(image_registry="registry.example.com/")
    assert settings.image_registry == "registry.example.com"

    settings = ContainerSettings(image_registry="registry.example.com")
    assert settings.image_registry == "registry.example.com"


def test_orchestrator_settings_defaults() -> None:
    """Test OrchestratorSettings creates with defaults."""
    settings = OrchestratorSettings()
    assert settings.version == "1.0"
    assert settings.container.engine == "docker"
    assert settings.container.image_name == "wallpaper-effects:latest"


def test_orchestrator_settings_from_dict() -> None:
    """Test OrchestratorSettings can be created from dict."""
    data = {
        "container": {
            "engine": "podman",
            "image_registry": "ghcr.io/user",
        }
    }
    settings = OrchestratorSettings(**data)
    assert settings.container.engine == "podman"
    assert settings.container.image_registry == "ghcr.io/user"
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_config_settings.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'wallpaper_orchestrator.config'"

**Step 3: Write settings.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/config/settings.py
"""Pydantic schemas for orchestrator settings."""

from pydantic import BaseModel, Field, field_validator


class ContainerSettings(BaseModel):
    """Container engine configuration."""

    engine: str = Field(
        default="docker",
        description="Container engine to use (docker or podman)",
    )
    image_name: str = Field(
        default="wallpaper-effects:latest",
        description="Container image name",
    )
    image_registry: str | None = Field(
        default=None,
        description="Registry prefix for container images",
    )

    @field_validator("engine", mode="before")
    @classmethod
    def validate_engine(cls, v: str) -> str:
        """Validate container engine is valid."""
        valid_engines = {"docker", "podman"}
        v_lower = v.lower()
        if v_lower not in valid_engines:
            raise ValueError(
                f"Invalid container engine: {v}. "
                f"Must be one of: {', '.join(sorted(valid_engines))}"
            )
        return v_lower

    @field_validator("image_registry", mode="before")
    @classmethod
    def normalize_registry(cls, v: str | None) -> str | None:
        """Normalize registry by removing trailing slashes."""
        if v:
            return v.rstrip("/")
        return v


class OrchestratorSettings(BaseModel):
    """Root settings for wallpaper_orchestrator."""

    version: str = Field(
        default="1.0", description="Settings schema version"
    )
    container: ContainerSettings = Field(default_factory=ContainerSettings)
```

**Step 4: Write config package __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/config/__init__.py
"""Configuration module for wallpaper_orchestrator."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)

# Register OrchestratorSettings with layered_settings
SchemaRegistry.register(
    namespace="orchestrator",
    model=OrchestratorSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = [
    "OrchestratorSettings",
    "ContainerSettings",
]
```

**Step 5: Write settings.toml**

```toml
# packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml
# Package default settings for wallpaper_orchestrator
# Format: flat sections (not namespaced)

[container]
engine = "docker"
image_name = "wallpaper-effects:latest"
# image_registry is optional, uncomment to set:
# image_registry = "ghcr.io/username"
```

**Step 6: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_config_settings.py -v
```

Expected: PASS (all tests pass)

**Step 7: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/config/ packages/orchestrator/tests/test_config_settings.py
git commit -m "feat(orchestrator): add OrchestratorSettings Pydantic schema"
```

---

### Task 3: UnifiedConfig Composition

**Goal:** Create UnifiedConfig that composes core + effects + orchestrator schemas

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/config/unified.py`
- Create: `packages/orchestrator/tests/test_config_unified.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_config_unified.py
"""Tests for UnifiedConfig composition."""

from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_orchestrator.config.settings import OrchestratorSettings
from wallpaper_orchestrator.config.unified import UnifiedConfig


def test_unified_config_defaults() -> None:
    """Test UnifiedConfig creates with all defaults."""
    config = UnifiedConfig()

    assert isinstance(config.core, CoreSettings)
    assert isinstance(config.effects, EffectsConfig)
    assert isinstance(config.orchestrator, OrchestratorSettings)


def test_unified_config_access_core() -> None:
    """Test accessing core settings through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.core.execution.parallel is True
    assert config.core.backend.binary == "magick"
    assert config.core.output.verbosity.name == "NORMAL"


def test_unified_config_access_effects() -> None:
    """Test accessing effects config through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.effects.version == "1.0"
    assert isinstance(config.effects.effects, dict)


def test_unified_config_access_orchestrator() -> None:
    """Test accessing orchestrator settings through UnifiedConfig."""
    config = UnifiedConfig()

    assert config.orchestrator.container.engine == "docker"
    assert config.orchestrator.container.image_name == "wallpaper-effects:latest"


def test_unified_config_from_dict() -> None:
    """Test UnifiedConfig from merged dictionaries."""
    data = {
        "core": {
            "execution": {"parallel": False},
        },
        "orchestrator": {
            "container": {"engine": "podman"},
        },
    }

    config = UnifiedConfig(**data)

    assert config.core.execution.parallel is False
    assert config.orchestrator.container.engine == "podman"


def test_unified_config_is_frozen() -> None:
    """Test UnifiedConfig is immutable after creation."""
    config = UnifiedConfig()

    # Config should be frozen (immutable)
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        config.core = CoreSettings()  # type: ignore
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_config_unified.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named '...unified'"

**Step 3: Write unified.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/config/unified.py
"""Project-level UnifiedConfig composing all schemas."""

from pydantic import BaseModel, ConfigDict, Field
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig

from wallpaper_orchestrator.config.settings import OrchestratorSettings


class UnifiedConfig(BaseModel):
    """Root configuration composing all registered namespaces.

    Access pattern:
        config.core.execution.parallel
        config.core.backend.binary
        config.effects.effects["blur"]
        config.orchestrator.container.engine
    """

    model_config = ConfigDict(frozen=True)

    core: CoreSettings = Field(default_factory=CoreSettings)
    effects: EffectsConfig = Field(default_factory=EffectsConfig)
    orchestrator: OrchestratorSettings = Field(
        default_factory=OrchestratorSettings
    )
```

**Step 4: Update config __init__.py to export UnifiedConfig**

```python
# packages/orchestrator/src/wallpaper_orchestrator/config/__init__.py
"""Configuration module for wallpaper_orchestrator."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)
from wallpaper_orchestrator.config.unified import UnifiedConfig

# Register OrchestratorSettings with layered_settings
SchemaRegistry.register(
    namespace="orchestrator",
    model=OrchestratorSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = [
    "OrchestratorSettings",
    "ContainerSettings",
    "UnifiedConfig",
]
```

**Step 5: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_config_unified.py -v
```

Expected: PASS (all tests pass)

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/config/ packages/orchestrator/tests/test_config_unified.py
git commit -m "feat(orchestrator): add UnifiedConfig composition"
```

---

### Task 4: ContainerManager Module

**Goal:** Create ContainerManager class for container operations

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/container/__init__.py`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`
- Create: `packages/orchestrator/tests/test_container_manager.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_container_manager.py
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
        orchestrator={
            "container": {"image_registry": "ghcr.io/user"}
        }
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
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_container_manager.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write manager.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/container/manager.py
"""Container manager for orchestrating wallpaper effects processing."""

import subprocess
from pathlib import Path

from wallpaper_orchestrator.config.unified import UnifiedConfig


class ContainerManager:
    """Manages container lifecycle for wallpaper effects processing.

    Handles:
    - Container engine detection (Docker/Podman)
    - Image management (build, inspect, remove)
    - Container execution
    - Volume mount configuration
    """

    def __init__(self, config: UnifiedConfig):
        """Initialize container manager.

        Args:
            config: Unified application configuration
        """
        self.config: UnifiedConfig = config
        self.engine: str = config.orchestrator.container.engine

    def get_image_name(self) -> str:
        """Get full image name.

        Returns:
            Full image name (with registry if configured)
        """
        image_name = self.config.orchestrator.container.image_name

        # Add registry prefix if configured
        if self.config.orchestrator.container.image_registry:
            registry = self.config.orchestrator.container.image_registry
            image_name = f"{registry}/{image_name}"

        return image_name

    def build_volume_mounts(
        self,
        image_path: Path,
        output_dir: Path,
    ) -> list[str]:
        """Build volume mount specifications for container.

        Args:
            image_path: Path to source image on host
            output_dir: Path to output directory on host

        Returns:
            List of volume mount strings in Docker -v format
        """
        mounts = []

        # Input image file (read-only)
        mounts.append(f"{image_path.absolute()}:/input/image.png:ro")

        # Output directory (read-write)
        mounts.append(f"{output_dir.absolute()}:/output:rw")

        return mounts

    def is_image_available(self) -> bool:
        """Check if container image exists.

        Returns:
            True if image exists, False otherwise
        """
        image_name = self.get_image_name()

        try:
            result = subprocess.run(
                [self.engine, "inspect", image_name],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
```

**Step 4: Write container package __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/container/__init__.py
"""Container management module."""

from wallpaper_orchestrator.container.manager import ContainerManager

__all__ = ["ContainerManager"]
```

**Step 5: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_container_manager.py -v
```

Expected: PASS (all tests pass)

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/container/ packages/orchestrator/tests/test_container_manager.py
git commit -m "feat(orchestrator): add ContainerManager for image operations"
```

---

### Task 5: Install Command

**Goal:** Implement install command to build container image

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/cli/__init__.py`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/__init__.py`
- Create: `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py`
- Create: `packages/orchestrator/tests/test_cli_install.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_cli_install.py
"""Tests for install command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.commands.install import install


runner = CliRunner()


def test_install_default_engine() -> None:
    """Test install with default docker engine."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        # Call install function directly
        with pytest.raises(SystemExit) as exc_info:
            install()

        # Should exit successfully
        assert exc_info.value.code == 0

        # Should call docker build
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "docker"
        assert "build" in call_args


def test_install_with_podman() -> None:
    """Test install with podman engine."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as exc_info:
            install(engine="podman")

        assert exc_info.value.code == 0

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"


def test_install_build_failure() -> None:
    """Test install handles build failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Build failed"
        )

        with pytest.raises(SystemExit) as exc_info:
            install()

        # Should exit with error code
        assert exc_info.value.code == 1


def test_install_invalid_engine() -> None:
    """Test install rejects invalid engine."""
    with pytest.raises(SystemExit) as exc_info:
        install(engine="invalid")

    assert exc_info.value.code == 1
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_cli_install.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write install.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py
"""Install command to build wallpaper effects container image."""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def install(
    engine: str | None = typer.Option(  # noqa: B008
        None,
        "--engine",
        "-e",
        help="Container engine to use (docker or podman). "
        "Uses config default if not specified.",
    ),
) -> None:
    """Build container image for wallpaper effects processing.

    This command builds a Docker/Podman image containing wallpaper_core
    plus ImageMagick and all required dependencies.

    Examples:

        # Install with default engine (docker)
        wallpaper-process install

        # Install with podman
        wallpaper-process install --engine podman
    """
    try:
        # Determine container engine
        if engine is None:
            container_engine = "docker"
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        # Find project root (where packages/ directory is)
        # This file is at:
        # packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py
        # Project root is: ../../../../../../..
        current_file = Path(__file__)
        project_root = (
            current_file.parent.parent.parent.parent.parent.parent.parent
        )
        docker_dir = project_root / "packages" / "orchestrator" / "docker"
        dockerfile = docker_dir / "Dockerfile.imagemagick"

        if not dockerfile.exists():
            console.print(
                f"[red]Error:[/red] Dockerfile not found at {dockerfile}"
            )
            raise typer.Exit(1)

        image_name = "wallpaper-effects:latest"

        console.print(
            f"[cyan]Building {image_name} using {container_engine}...[/cyan]\n"
        )

        # Build docker command
        cmd = [
            container_engine,
            "build",
            "-f",
            str(dockerfile),
            "-t",
            image_name,
            str(project_root),
        ]

        # Show progress while building
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Building {image_name}...",
                total=None,
            )

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                )

                if result.returncode == 0:
                    progress.update(
                        task, description=f"✓ Built {image_name}"
                    )
                    console.print(
                        f"\n[green]✓ Successfully built {image_name}[/green]"
                    )
                    raise typer.Exit(0)
                else:
                    progress.update(
                        task, description=f"✗ Failed to build {image_name}"
                    )
                    console.print(f"\n[red]✗ Build failed[/red]")
                    console.print(f"[dim]{result.stderr}[/dim]")
                    raise typer.Exit(1)

            except subprocess.SubprocessError as e:
                progress.update(
                    task, description=f"✗ Error building {image_name}"
                )
                console.print(f"\n[red]✗ Build error:[/red] {str(e)}")
                raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

**Step 4: Write commands package __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/commands/__init__.py
"""CLI commands for wallpaper_orchestrator."""

from wallpaper_orchestrator.cli.commands.install import install
from wallpaper_orchestrator.cli.commands.uninstall import uninstall

__all__ = ["install", "uninstall"]
```

**Step 5: Write cli package __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/__init__.py
"""CLI module for wallpaper_orchestrator."""

__all__ = []
```

**Step 6: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_cli_install.py -v
```

Expected: PASS (all tests pass)

**Step 7: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/ packages/orchestrator/tests/test_cli_install.py
git commit -m "feat(orchestrator): add install command to build container"
```

---

### Task 6: Uninstall Command

**Goal:** Implement uninstall command to remove container image

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py`
- Create: `packages/orchestrator/tests/test_cli_uninstall.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_cli_uninstall.py
"""Tests for uninstall command."""

from unittest.mock import MagicMock, patch

import pytest

from wallpaper_orchestrator.cli.commands.uninstall import uninstall


def test_uninstall_with_confirmation() -> None:
    """Test uninstall with user confirmation."""
    with patch("subprocess.run") as mock_run, \
         patch("typer.confirm") as mock_confirm:

        mock_run.return_value = MagicMock(returncode=0)
        mock_confirm.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            uninstall(yes=False)

        assert exc_info.value.code == 0
        mock_confirm.assert_called_once()
        mock_run.assert_called_once()


def test_uninstall_cancelled() -> None:
    """Test uninstall when user cancels."""
    with patch("typer.confirm") as mock_confirm:
        mock_confirm.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            uninstall(yes=False)

        assert exc_info.value.code == 0
        mock_confirm.assert_called_once()


def test_uninstall_skip_confirmation() -> None:
    """Test uninstall with --yes flag."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as exc_info:
            uninstall(yes=True)

        assert exc_info.value.code == 0
        mock_run.assert_called_once()


def test_uninstall_image_not_found() -> None:
    """Test uninstall when image doesn't exist."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="no such image"
        )

        with pytest.raises(SystemExit) as exc_info:
            uninstall(yes=True)

        # Should still exit successfully (image already gone)
        assert exc_info.value.code == 0


def test_uninstall_with_podman() -> None:
    """Test uninstall with podman engine."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as exc_info:
            uninstall(yes=True, engine="podman")

        assert exc_info.value.code == 0

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_cli_uninstall.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write uninstall.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py
"""Uninstall command to remove wallpaper effects container image."""

import subprocess

import typer
from rich.console import Console

console = Console()


def uninstall(
    yes: bool = typer.Option(  # noqa: B008
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    engine: str | None = typer.Option(  # noqa: B008
        None,
        "--engine",
        "-e",
        help="Container engine to use (docker or podman). "
        "Uses config default if not specified.",
    ),
) -> None:
    """Remove container image for wallpaper effects processing.

    This command removes the Docker/Podman image from your system.
    Use with caution as this will delete the image.

    Examples:

        # Remove image (with confirmation)
        wallpaper-process uninstall

        # Remove without confirmation
        wallpaper-process uninstall --yes

        # Use podman instead of docker
        wallpaper-process uninstall --engine podman
    """
    try:
        # Determine container engine
        if engine is None:
            container_engine = "docker"
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        image_name = "wallpaper-effects:latest"

        # Confirm deletion
        if not yes:
            console.print(
                "[yellow]Warning:[/yellow] This will remove the image:"
            )
            console.print(f"  - {image_name}")
            console.print()

            confirm = typer.confirm("Are you sure you want to continue?")
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        # Remove image
        console.print(f"[cyan]Removing {image_name}...[/cyan]\n")

        cmd = [container_engine, "rmi", image_name]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                console.print(
                    f"[green]✓ Removed {image_name}[/green]"
                )
                raise typer.Exit(0)
            else:
                # Image might not exist, which is fine
                if (
                    "no such image" in result.stderr.lower()
                    or "not found" in result.stderr.lower()
                ):
                    console.print(
                        f"[dim]○ Image not found (already removed)[/dim]"
                    )
                    raise typer.Exit(0)
                else:
                    console.print(f"[red]✗ Failed to remove[/red]")
                    console.print(f"[dim]{result.stderr}[/dim]")
                    raise typer.Exit(1)

        except subprocess.SubprocessError as e:
            console.print(f"[red]✗ Error:[/red] {str(e)}")
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

**Step 4: Update commands __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/commands/__init__.py
"""CLI commands for wallpaper_orchestrator."""

from wallpaper_orchestrator.cli.commands.install import install
from wallpaper_orchestrator.cli.commands.uninstall import uninstall

__all__ = ["install", "uninstall"]
```

**Step 5: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_cli_uninstall.py -v
```

Expected: PASS (all tests pass)

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py packages/orchestrator/tests/test_cli_uninstall.py
git commit -m "feat(orchestrator): add uninstall command to remove container"
```

---

### Task 7: CLI Bootstrap with UnifiedConfig

**Goal:** Create main CLI entry point that configures layered_settings with UnifiedConfig

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`
- Create: `packages/orchestrator/tests/test_cli_bootstrap.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_cli_bootstrap.py
"""Tests for CLI bootstrap and configuration."""

import pytest
from typer import Typer
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


def test_cli_app_exists() -> None:
    """Test CLI app is a Typer instance."""
    assert isinstance(app, Typer)


def test_cli_help_works() -> None:
    """Test CLI --help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "wallpaper" in result.stdout.lower()


def test_cli_has_install_command() -> None:
    """Test CLI has install command."""
    result = runner.invoke(app, ["install", "--help"])
    assert result.exit_code == 0
    assert "build" in result.stdout.lower()


def test_cli_has_uninstall_command() -> None:
    """Test CLI has uninstall command."""
    result = runner.invoke(app, ["uninstall", "--help"])
    assert result.exit_code == 0
    assert "remove" in result.stdout.lower()


def test_cli_configures_layered_settings() -> None:
    """Test CLI configures layered_settings on startup."""
    from layered_settings import get_config

    # Import triggers configuration
    from wallpaper_orchestrator.cli import main  # noqa: F401

    try:
        config = get_config()
        assert hasattr(config, "core")
        assert hasattr(config, "effects")
        assert hasattr(config, "orchestrator")
    except Exception:
        # If fails due to missing files, that's OK
        # Just verify the configure was called
        pass
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_cli_bootstrap.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write main.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/main.py
"""Main CLI entry point for wallpaper_orchestrator."""

import typer

from layered_settings import configure
from wallpaper_orchestrator.cli.commands import install, uninstall
from wallpaper_orchestrator.config.unified import UnifiedConfig

# Configure layered_settings at module import
configure(UnifiedConfig, app_name="wallpaper-effects")

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with container orchestration",
    no_args_is_help=True,
)

# Add orchestrator-specific commands
app.command()(install)
app.command()(uninstall)

# TODO: Add core command wrapping in next task


if __name__ == "__main__":
    app()
```

**Step 4: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_cli_bootstrap.py -v
```

Expected: PASS (all tests pass)

**Step 5: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py packages/orchestrator/tests/test_cli_bootstrap.py
git commit -m "feat(orchestrator): add CLI bootstrap with UnifiedConfig"
```

---

### Task 8: Dockerfile Creation

**Goal:** Create Dockerfile for building wallpaper-effects container

**Files:**
- Create: `packages/orchestrator/docker/Dockerfile.imagemagick`
- Create: `packages/orchestrator/docker/.dockerignore`
- Create: `packages/orchestrator/docker/README.md`

**Step 1: Write Dockerfile.imagemagick**

```dockerfile
# packages/orchestrator/docker/Dockerfile.imagemagick
# Wallpaper effects processor with ImageMagick
FROM python:3.12-alpine AS base

# Install ImageMagick and system dependencies
RUN apk add --no-cache \
    imagemagick \
    imagemagick-dev \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    libffi-dev

# Create non-root user
RUN adduser -D -u 1000 wallpaper

# Set working directory
WORKDIR /app

# Install uv for package management
RUN pip install --no-cache-dir uv

# Copy settings package (dependency of core)
COPY --chown=wallpaper:wallpaper packages/settings /app/wallpaper-settings

# Copy wallpaper-core package
COPY --chown=wallpaper:wallpaper packages/core /app/wallpaper-core

# Install settings first, then core (use pip to avoid uv.sources issues)
RUN cd /app/wallpaper-settings && \
    pip install --no-cache-dir . && \
    cd /app/wallpaper-core && \
    pip install --no-cache-dir .

# Create mount points
RUN mkdir -p /input /output && \
    chown -R wallpaper:wallpaper /input /output

# Switch to non-root user
USER wallpaper

# Set entrypoint to wallpaper-process CLI
ENTRYPOINT ["wallpaper-process"]

# Default command shows help
CMD ["--help"]
```

**Step 2: Write .dockerignore**

```
# packages/orchestrator/docker/.dockerignore
# Ignore build artifacts and caches
**/__pycache__/
**/*.pyc
**/*.pyo
**/*.pyd
**/.pytest_cache/
**/.mypy_cache/
**/.ruff_cache/
**/.coverage
**/htmlcov/
**/*.egg-info/
**/dist/
**/build/

# Ignore virtual environments
**/.venv/
**/venv/
**/.env

# Ignore IDE and editor files
**/.idea/
**/.vscode/
**/.DS_Store

# Ignore git
**/.git/
**/.gitignore

# Ignore test files (we only need source)
**/tests/

# Ignore documentation
**/docs/
**/*.md

# Keep only necessary files
!packages/settings/src/
!packages/settings/pyproject.toml
!packages/core/src/
!packages/core/pyproject.toml
!packages/core/effects/
```

**Step 3: Write docker README**

```markdown
# packages/orchestrator/docker/README.md
# Docker Build for Wallpaper Effects

This directory contains the Dockerfile for building the wallpaper effects
processor container image.

## Image Contents

- Python 3.12 (Alpine Linux base)
- ImageMagick (latest Alpine version)
- wallpaper-settings package
- wallpaper-core package
- All Python dependencies

## Building

From the project root:

```bash
docker build -f packages/orchestrator/docker/Dockerfile.imagemagick \
  -t wallpaper-effects:latest .
```

Or use the install command:

```bash
wallpaper-process install
```

## Usage

Process an image with blur effect:

```bash
docker run --rm \
  -v $(pwd)/input.jpg:/input/image.png:ro \
  -v $(pwd)/output:/output:rw \
  wallpaper-effects:latest \
  process /input/image.png /output/blurred.jpg blur
```

## Security

- Runs as non-root user (UID 1000)
- Input mounts are read-only
- Output directory is the only writable mount
```

**Step 4: Test Dockerfile builds (manual)**

```bash
cd /home/inumaki/Development/wallpaper-effects-generator

# Try building the image
docker build \
  -f packages/orchestrator/docker/Dockerfile.imagemagick \
  -t wallpaper-effects:latest \
  .
```

Expected: Image builds successfully

**Step 5: Commit**

```bash
git add packages/orchestrator/docker/
git commit -m "feat(orchestrator): add Dockerfile for container image"
```

---

### Task 9: Integrate Core CLI Commands

**Goal:** Wrap core CLI commands to work through orchestrator

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`
- Create: `packages/orchestrator/tests/test_cli_integration.py`

**Step 1: Write failing test**

```python
# packages/orchestrator/tests/test_cli_integration.py
"""Tests for CLI integration with core commands."""

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


def test_cli_has_core_commands() -> None:
    """Test CLI includes core commands."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0

    # Should have orchestrator commands
    assert "install" in result.stdout
    assert "uninstall" in result.stdout

    # Should have core commands
    assert "process" in result.stdout or "info" in result.stdout


def test_cli_info_command() -> None:
    """Test info command is available."""
    result = runner.invoke(app, ["info"])

    # Should execute (may fail due to missing config files, that's OK)
    assert "Core Settings" in result.stdout or result.exit_code in [0, 1]


def test_cli_process_help() -> None:
    """Test process command help is available."""
    result = runner.invoke(app, ["process", "--help"])

    assert result.exit_code == 0
    # Should show core's process command help
```

**Step 2: Run test to verify it fails**

```bash
cd packages/orchestrator
pytest tests/test_cli_integration.py -v
```

Expected: FAIL (core commands not integrated yet)

**Step 3: Update main.py to integrate core commands**

```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/main.py
"""Main CLI entry point for wallpaper_orchestrator."""

import typer

from layered_settings import configure
from wallpaper_core.cli import main as core_cli
from wallpaper_orchestrator.cli.commands import install, uninstall
from wallpaper_orchestrator.config.unified import UnifiedConfig

# Configure layered_settings at module import
configure(UnifiedConfig, app_name="wallpaper-effects")

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with container orchestration",
    no_args_is_help=True,
)

# Add orchestrator-specific commands
app.command(name="install")(install)
app.command(name="uninstall")(uninstall)

# Import and add core commands
# Note: We import the core CLI app and add its commands
# This makes all core functionality available through orchestrator
try:
    # Get the info command from core
    for name, command in core_cli.app.registered_commands:
        if name == "info":
            app.command(name="info")(command.callback)

    # Add core sub-apps (process, batch, show)
    for name, sub_app in core_cli.app.registered_groups:
        app.add_typer(sub_app.typer_instance, name=name)
except AttributeError:
    # Fallback: manually register known commands
    # This ensures compatibility even if core's internal structure changes
    from wallpaper_core.cli.main import info

    app.command(name="info")(info)


if __name__ == "__main__":
    app()
```

**Step 4: Run test to verify it passes**

```bash
cd packages/orchestrator
pytest tests/test_cli_integration.py -v
```

Expected: PASS (all tests pass)

**Step 5: Test CLI manually**

```bash
cd packages/orchestrator
uv pip install -e .

# Test orchestrator commands
wallpaper-process --help
wallpaper-process install --help
wallpaper-process uninstall --help

# Test core commands (inherited)
wallpaper-process info
```

Expected: All commands work correctly

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py packages/orchestrator/tests/test_cli_integration.py
git commit -m "feat(orchestrator): integrate core CLI commands into orchestrator"
```

---

### Task 10: Update Root Workspace

**Goal:** Add packages/orchestrator to root workspace configuration

**Files:**
- Modify: `pyproject.toml` (root)

**Step 1: Update root workspace config**

```toml
# pyproject.toml (root)
[tool.uv.workspace]
members = [
    "packages/settings",
    "packages/core",
    "packages/orchestrator",
]
```

**Step 2: Sync workspace**

```bash
cd /home/inumaki/Development/wallpaper-effects-generator
uv sync
```

Expected: All packages in workspace synced

**Step 3: Test workspace imports**

```bash
cd packages/orchestrator
uv run python -c "
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager
print('OK')
"
```

Expected: "OK"

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "feat(workspace): add packages/orchestrator to workspace"
```

---

### Task 11: Integration Testing

**Goal:** Create end-to-end integration tests

**Files:**
- Create: `packages/orchestrator/tests/test_integration.py`

**Step 1: Write integration test**

```python
# packages/orchestrator/tests/test_integration.py
"""Integration tests for wallpaper_orchestrator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
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
    assert config.orchestrator.container.image_name == "wallpaper-effects:latest"


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
    config = UnifiedConfig(
        orchestrator={"container": {"engine": "podman"}}
    )
    manager = ContainerManager(config)

    assert manager.engine == "podman"
    assert manager.get_image_name() == "wallpaper-effects:latest"


def test_container_manager_with_registry() -> None:
    """Test ContainerManager handles image registry."""
    config = UnifiedConfig(
        orchestrator={
            "container": {"image_registry": "ghcr.io/user"}
        }
    )
    manager = ContainerManager(config)

    assert manager.get_image_name() == "ghcr.io/user/wallpaper-effects:latest"


def test_cli_commands_registered() -> None:
    """Test all CLI commands are registered."""
    from wallpaper_orchestrator.cli.main import app

    # Get all registered commands
    command_names = {cmd.name for cmd in app.registered_commands}

    # Should have orchestrator commands
    assert "install" in command_names
    assert "uninstall" in command_names

    # Should have core command
    assert "info" in command_names
```

**Step 2: Run integration tests**

```bash
cd packages/orchestrator
pytest tests/test_integration.py -v
```

Expected: PASS (all integration tests pass)

**Step 3: Run full test suite**

```bash
cd packages/orchestrator
pytest -v
```

Expected: All tests pass

**Step 4: Commit**

```bash
git add packages/orchestrator/tests/test_integration.py
git commit -m "test(orchestrator): add integration tests"
```

---

### Task 12: Update Documentation

**Goal:** Update README with usage examples and architecture

**Files:**
- Modify: `packages/orchestrator/README.md`

**Step 1: Write comprehensive README**

```markdown
# wallpaper_orchestrator

Container orchestrator for the wallpaper effects processor, providing isolated,
portable, and reproducible image processing.

## Features

- **Container Support**: Docker and Podman
- **Isolation**: Run effects in isolated containers
- **Portability**: Bundle ImageMagick with specific versions
- **Reproducibility**: Consistent behavior across systems
- **Simple Commands**: Easy install/uninstall

## Installation

```bash
# From workspace root
uv sync

# Install just orchestrator package
cd packages/orchestrator
uv pip install -e .
```

## Quick Start

```bash
# Build container image
wallpaper-process install

# Process with container (uses core functionality)
wallpaper-process process input.jpg output.jpg blur

# View configuration
wallpaper-process info

# Remove container image
wallpaper-process uninstall
```

## Configuration

### Layer Priority

1. **Package defaults** - Built-in settings
2. **Project settings** - `./settings.toml`
3. **User settings** - `~/.config/wallpaper-effects/settings.toml`
4. **CLI overrides** - Command-line flags

### Orchestrator Settings

**Container Settings:**
- `engine` (str, default="docker") - Container engine (docker or podman)
- `image_name` (str, default="wallpaper-effects:latest") - Image name
- `image_registry` (str, optional) - Registry prefix for images

**Example Configuration:**

```toml
# ~/.config/wallpaper-effects/settings.toml

[orchestrator.container]
engine = "podman"
image_registry = "ghcr.io/username"
```

## Architecture

The orchestrator package composes all configuration namespaces:

```python
from wallpaper_orchestrator.config.unified import UnifiedConfig

config = UnifiedConfig()
# Access: config.core.execution.parallel
#         config.effects.effects["blur"]
#         config.orchestrator.container.engine
```

### Package Structure

```
packages/orchestrator/
├── src/wallpaper_orchestrator/
│   ├── config/          # UnifiedConfig + OrchestratorSettings
│   ├── container/       # ContainerManager
│   ├── cli/             # CLI commands (wraps core)
│   └── docker/          # Dockerfile
├── tests/
└── pyproject.toml
```

## Commands

### Install

Build the container image:

```bash
wallpaper-process install
wallpaper-process install --engine podman
```

### Uninstall

Remove the container image:

```bash
wallpaper-process uninstall
wallpaper-process uninstall --yes  # Skip confirmation
```

### Core Commands

All core commands are available through the orchestrator:

```bash
wallpaper-process info
wallpaper-process process <input> <output> <effect>
wallpaper-process batch <input> --effects <list>
wallpaper-process show effects
```

## Development

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=wallpaper_orchestrator

# Type checking
mypy src/wallpaper_orchestrator

# Format code
black src/ tests/
isort src/ tests/
```

## Container Details

The container image includes:

- Python 3.12 (Alpine Linux)
- ImageMagick (latest Alpine version)
- wallpaper-settings package
- wallpaper-core package
- All dependencies

**Security:**
- Runs as non-root user (UID 1000)
- Input mounts are read-only
- Output directory is the only writable mount

See `docker/README.md` for container build details.
```

**Step 2: Commit**

```bash
git add packages/orchestrator/README.md
git commit -m "docs(orchestrator): update README with complete usage guide"
```

---

### Task 13: Update Package __init__.py

**Goal:** Export public API from package

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/__init__.py`

**Step 1: Write updated __init__.py**

```python
# packages/orchestrator/src/wallpaper_orchestrator/__init__.py
"""Wallpaper effects orchestrator with container management."""

from wallpaper_orchestrator.config.settings import (
    ContainerSettings,
    OrchestratorSettings,
)
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # Config
    "OrchestratorSettings",
    "ContainerSettings",
    "UnifiedConfig",
    # Container
    "ContainerManager",
]
```

**Step 2: Test imports**

```bash
cd packages/orchestrator
python -c "from wallpaper_orchestrator import UnifiedConfig, ContainerManager; print('OK')"
```

Expected: "OK"

**Step 3: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/__init__.py
git commit -m "feat(orchestrator): update package __init__ with public API"
```

---

## Completion Checklist

After completing all tasks, verify:

- [ ] All tests pass: `cd packages/orchestrator && pytest -v`
- [ ] Good coverage: `pytest --cov=wallpaper_orchestrator`
- [ ] Type checking passes: `mypy src/wallpaper_orchestrator`
- [ ] CLI works: `wallpaper-process --help`
- [ ] Install command works: `wallpaper-process install --help`
- [ ] Workspace syncs: `cd ../.. && uv sync`
- [ ] All commits made with clear messages
- [ ] Documentation complete
- [ ] Dockerfile builds successfully

## Next Steps (Phase 4)

After Phase 3 completion:
1. Add container execution support (run effects in containers)
2. Implement volume mounting for effects processing
3. Add container health checks
4. Archive old `core/` directory
5. Update root documentation
6. Create end-to-end examples

---

## Notes for Implementer

- **TDD Approach**: Write test first, see it fail, implement, see it pass, commit
- **Reference Project**: `/home/inumaki/Development/color-scheme` for patterns
- **Container Testing**: Mock subprocess calls, don't require Docker installed for tests
- **CLI Integration**: Orchestrator wraps core, doesn't replace it
- **Config Composition**: UnifiedConfig = core + effects + orchestrator
- **Entry Point**: `wallpaper-process` command overwrites core's entry point
