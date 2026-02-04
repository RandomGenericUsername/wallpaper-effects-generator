# Phase 4 Implementation: Container Execution

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Transform orchestrator from CLI wrapper to container execution engine with proper package separation

**Architecture:** Rename core CLI to `wallpaper-core`, implement `ContainerManager.run_process()` for container execution, replace orchestrator's delegation with actual containerized commands

**Tech Stack:** Python 3.12, Docker/Podman, subprocess, Pydantic, typer, rich

**Reference:** Design document at `docs/plans/2026-02-04-phase4-container-execution.md`

---

## Current State Assessment

**Completed:**
- Phase 1: `layered_settings` package
- Phase 2: `wallpaper_core` package with local CLI
- Phase 3: `wallpaper_orchestrator` package structure

**Current Issue:**
- Both core and orchestrator use `wallpaper-process` as CLI entry point
- Orchestrator just delegates to core (no container execution)
- No separation between local and containerized execution

**Goal:**
- Core: `wallpaper-core` command (local execution)
- Orchestrator: `wallpaper-process` command (containerized execution)

---

## Implementation Tasks

Execute in order using TDD approach for each task.

### Task 1: Rename Core CLI Entry Point

**Goal:** Change core's CLI command from `wallpaper-process` to `wallpaper-core`

**Files:**
- Modify: `packages/core/pyproject.toml`
- Modify: `packages/core/README.md`
- Modify: `packages/core/src/wallpaper_core/cli/main.py`

**Step 1: Update pyproject.toml**

Modify `packages/core/pyproject.toml` line 30:

```toml
[project.scripts]
wallpaper-core = "wallpaper_core.cli.main:app"
```

**Step 2: Update CLI help text**

Modify `packages/core/src/wallpaper_core/cli/main.py` line 27:

```python
app = typer.Typer(
    name="wallpaper-core",
    help="Wallpaper effects processor with layered configuration",
    no_args_is_help=True,
)
```

**Step 3: Update README**

Modify `packages/core/README.md` - replace all instances of `wallpaper-process` with `wallpaper-core`:

```bash
cd packages/core
sed -i 's/wallpaper-process/wallpaper-core/g' README.md
```

**Step 4: Verify changes**

```bash
cd packages/core
grep -n "wallpaper-process" pyproject.toml README.md src/wallpaper_core/cli/main.py
```

Expected: No matches (all renamed to wallpaper-core)

**Step 5: Commit**

```bash
git add packages/core/pyproject.toml packages/core/README.md packages/core/src/wallpaper_core/cli/main.py
git commit -m "refactor(core): rename CLI from wallpaper-process to wallpaper-core

- Update entry point in pyproject.toml
- Update CLI app name
- Update README with new command name

BREAKING CHANGE: CLI command renamed from wallpaper-process to wallpaper-core

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Implement ContainerManager.run_process() - Part 1 (Tests)

**Goal:** Write tests for container execution method

**Files:**
- Create: `packages/orchestrator/tests/test_container_execution.py`

**Step 1: Write failing test for successful execution**

Create `packages/orchestrator/tests/test_container_execution.py`:

```python
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

    with patch("subprocess.run") as mock_run, \
         patch.object(manager, "is_image_available", return_value=True):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )

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

        # Verify mounts
        assert any("/input/image.jpg:ro" in arg for arg in call_args)
        assert any("/output:rw" in arg for arg in call_args)

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

    with patch("subprocess.run") as mock_run, \
         patch.object(manager, "is_image_available", return_value=True):
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

    with patch("subprocess.run") as mock_run, \
         patch.object(manager, "is_image_available", return_value=True):
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

    with patch("subprocess.run") as mock_run, \
         patch.object(manager, "is_image_available", return_value=True):
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
    config = UnifiedConfig(
        orchestrator={"container": {"engine": "podman"}}
    )
    manager = ContainerManager(config)

    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch("subprocess.run") as mock_run, \
         patch.object(manager, "is_image_available", return_value=True):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager.run_process(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "podman"
```

**Step 2: Run tests to verify they fail**

```bash
cd packages/orchestrator
pytest tests/test_container_execution.py -v
```

Expected: FAIL with "ContainerManager object has no attribute 'run_process'"

**Step 3: Commit tests**

```bash
git add packages/orchestrator/tests/test_container_execution.py
git commit -m "test(orchestrator): add tests for ContainerManager.run_process

- Test command construction for docker/podman
- Test validation (image exists, input exists)
- Test output directory creation
- Test absolute path handling
- Test exit code propagation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Implement ContainerManager.run_process() - Part 2 (Implementation)

**Goal:** Implement container execution method

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`

**Step 1: Import required modules**

Add imports to `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py` (after existing imports):

```python
import os
```

**Step 2: Implement run_process method**

Add method to `ContainerManager` class in `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`:

```python
def run_process(
    self,
    command_type: str,
    command_name: str,
    input_path: Path,
    output_path: Path,
    additional_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Execute wallpaper-core command inside container.

    Args:
        command_type: Type of command (effect/composite/preset)
        command_name: Name of effect/composite/preset
        input_path: Path to input image on host
        output_path: Path for output image on host
        additional_args: Additional CLI arguments to pass

    Returns:
        CompletedProcess with returncode, stdout, stderr

    Raises:
        RuntimeError: If container image not available
        FileNotFoundError: If input file doesn't exist
    """
    # Validate container image exists
    if not self.is_image_available():
        raise RuntimeError(
            "Container image not found. "
            "Install the image first:\n  wallpaper-process install"
        )

    # Validate input file exists
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}\n"
            "Please check the file path is correct."
        )

    # Ensure output directory exists
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert paths to absolute
    abs_input = input_path.absolute()
    abs_output_dir = output_dir.absolute()

    # Build volume mounts
    input_mount = f"{abs_input}:/input/image.jpg:ro"
    output_mount = f"{abs_output_dir}:/output:rw"

    # Build container command
    cmd = [
        self.engine,
        "run",
        "--rm",
        "-v",
        input_mount,
        "-v",
        output_mount,
        self.get_image_name(),
        "process",
        command_type,
        "/input/image.jpg",
        f"/output/{output_path.name}",
        command_name,
    ]

    # Add additional arguments if provided
    if additional_args:
        cmd.extend(additional_args)

    # Execute container
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    return result
```

**Step 3: Run tests to verify they pass**

```bash
cd packages/orchestrator
pytest tests/test_container_execution.py -v
```

Expected: PASS (all 8 tests pass)

**Step 4: Run full orchestrator test suite**

```bash
cd packages/orchestrator
pytest -v
```

Expected: All tests pass (including new tests)

**Step 5: Commit implementation**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/container/manager.py
git commit -m "feat(orchestrator): implement ContainerManager.run_process for container execution

- Execute wallpaper-core commands inside containers
- Validate image availability and input file
- Handle volume mounts for input (ro) and output (rw)
- Support docker and podman engines
- Return CompletedProcess with exit code

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 4: Implement Orchestrator Process Commands - Part 1 (Tests)

**Goal:** Write tests for orchestrator's process commands

**Files:**
- Create: `packages/orchestrator/tests/test_cli_process.py`

**Step 1: Write failing tests**

Create `packages/orchestrator/tests/test_cli_process.py`:

```python
"""Tests for orchestrator process commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


def test_process_effect_calls_container_manager(tmp_path: Path) -> None:
    """Test process effect command calls ContainerManager.run_process."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch(
        "wallpaper_orchestrator.cli.main.ContainerManager"
    ) as MockManager:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        MockManager.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="effect",
            command_name="blur",
            input_path=input_file,
            output_path=output_file,
        )


def test_process_effect_checks_image_available(tmp_path: Path) -> None:
    """Test process effect checks if container image is available."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch(
        "wallpaper_orchestrator.cli.main.ContainerManager"
    ) as MockManager:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        MockManager.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
        assert "wallpaper-process install" in result.output


def test_process_effect_handles_container_failure(
    tmp_path: Path,
) -> None:
    """Test process effect handles container execution failure."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch(
        "wallpaper_orchestrator.cli.main.ContainerManager"
    ) as MockManager:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=1, stdout="", stderr="magick: invalid parameter"
        )
        MockManager.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "effect",
                str(input_file),
                str(output_file),
                "blur",
            ],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_process_composite_calls_container_manager(
    tmp_path: Path,
) -> None:
    """Test process composite command calls ContainerManager."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch(
        "wallpaper_orchestrator.cli.main.ContainerManager"
    ) as MockManager:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        MockManager.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "composite",
                str(input_file),
                str(output_file),
                "dark",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="composite",
            command_name="dark",
            input_path=input_file,
            output_path=output_file,
        )


def test_process_preset_calls_container_manager(tmp_path: Path) -> None:
    """Test process preset command calls ContainerManager."""
    input_file = tmp_path / "input.jpg"
    output_file = tmp_path / "output.jpg"
    input_file.touch()

    with patch(
        "wallpaper_orchestrator.cli.main.ContainerManager"
    ) as MockManager:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_process.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        MockManager.return_value = mock_manager

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                str(output_file),
                "dark_vibrant",
            ],
        )

        assert result.exit_code == 0
        mock_manager.run_process.assert_called_once_with(
            command_type="preset",
            command_name="dark_vibrant",
            input_path=input_file,
            output_path=output_file,
        )
```

**Step 2: Run tests to verify they fail**

```bash
cd packages/orchestrator
pytest tests/test_cli_process.py -v
```

Expected: FAIL (commands not implemented yet)

**Step 3: Commit tests**

```bash
git add packages/orchestrator/tests/test_cli_process.py
git commit -m "test(orchestrator): add tests for process commands

- Test process effect/composite/preset commands
- Test image availability check
- Test container failure handling
- Mock ContainerManager.run_process

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 5: Implement Orchestrator Process Commands - Part 2 (Implementation)

**Goal:** Replace orchestrator CLI delegation with container execution

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`

**Step 1: Add required imports**

Add to imports in `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`:

```python
from pathlib import Path

from layered_settings import configure, get_config
from rich.console import Console

from wallpaper_orchestrator.container.manager import ContainerManager
```

**Step 2: Remove old delegation code**

Delete lines 24-46 in `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py` (the code that delegates to core CLI).

**Step 3: Add console instance**

Add after imports:

```python
console = Console()
```

**Step 4: Implement process effect command**

Add to `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`:

```python
@app.command()
def process_effect(
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    effect: str = typer.Argument(..., help="Effect name to apply"),  # noqa: B008
) -> None:
    """Apply single effect to image (runs in container).

    Examples:
        wallpaper-process process effect input.jpg output.jpg blur
        wallpaper-process process effect photo.png blurred.png gaussian_blur
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        # Validate container image
        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        # Execute in container
        console.print(f"[cyan]Processing with effect:[/cyan] {effect}")
        result = manager.run_process(
            command_type="effect",
            command_name=effect,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(f"[red]Effect failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@app.command()
def process_composite(
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    composite: str = typer.Argument(  # noqa: B008
        ..., help="Composite name to apply"
    ),
) -> None:
    """Apply composite effect to image (runs in container).

    Examples:
        wallpaper-process process composite input.jpg output.jpg dark
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(
            f"[cyan]Processing with composite:[/cyan] {composite}"
        )
        result = manager.run_process(
            command_type="composite",
            command_name=composite,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(
                f"[red]Composite failed:[/red]\n{result.stderr}"
            )
            raise typer.Exit(result.returncode)

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@app.command()
def process_preset(
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    preset: str = typer.Argument(..., help="Preset name to apply"),  # noqa: B008
) -> None:
    """Apply preset to image (runs in container).

    Examples:
        wallpaper-process process preset input.jpg output.jpg dark_vibrant
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(f"[cyan]Processing with preset:[/cyan] {preset}")
        result = manager.run_process(
            command_type="preset",
            command_name=preset,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(f"[red]Preset failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

**Step 5: Keep info and version commands (delegate to core)**

Add these commands:

```python
@app.command()
def info() -> None:
    """Show current configuration (runs on host)."""
    from wallpaper_core.cli.main import info as core_info

    core_info()


@app.command()
def version() -> None:
    """Show version information (runs on host)."""
    from wallpaper_orchestrator import __version__

    console.print(f"wallpaper-orchestrator v{__version__}")
```

**Step 6: Run tests to verify they pass**

```bash
cd packages/orchestrator
pytest tests/test_cli_process.py -v
```

Expected: PASS (all 6 tests pass)

**Step 7: Run full test suite**

```bash
cd packages/orchestrator
pytest -v
```

Expected: All tests pass

**Step 8: Commit implementation**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py
git commit -m "feat(orchestrator): implement process commands with container execution

- Replace core CLI delegation with container execution
- Add process effect/composite/preset commands
- Each calls ContainerManager.run_process()
- Keep info/version as host commands (no container)
- Rich console output for user feedback

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Update Orchestrator Documentation

**Goal:** Update README to reflect new architecture

**Files:**
- Modify: `packages/orchestrator/README.md`

**Step 1: Update README with new command examples**

Replace content in `packages/orchestrator/README.md`:

```markdown
# wallpaper_orchestrator

Container orchestrator for wallpaper effects processing with Docker/Podman support.

## Overview

The orchestrator package provides containerized execution of wallpaper effects, offering isolation, reproducibility, and portability. All image processing happens inside containers - no need to install ImageMagick on your host system.

## Features

- **Container Execution**: Run effects inside Docker/Podman containers
- **Isolation**: Isolated execution environment, reproducible results
- **Portability**: Works anywhere Docker/Podman runs
- **No Dependencies**: ImageMagick bundled in container image
- **Simple Commands**: Install image, run effects, uninstall

## Installation

```bash
# From workspace root
uv sync

# Install orchestrator package
cd packages/orchestrator
uv pip install -e .
```

## Quick Start

```bash
# 1. Build container image (one-time setup)
wallpaper-process install

# 2. Process images (runs in container)
wallpaper-process process effect input.jpg output.jpg blur

# 3. When done, remove image
wallpaper-process uninstall
```

## Commands

### Container Management

**Install container image:**
```bash
wallpaper-process install                # Use default engine (docker)
wallpaper-process install --engine podman  # Use podman
```

**Uninstall container image:**
```bash
wallpaper-process uninstall             # With confirmation
wallpaper-process uninstall --yes       # Skip confirmation
```

### Process Commands (Container Execution)

**Apply single effect:**
```bash
wallpaper-process process effect input.jpg output.jpg blur
wallpaper-process process effect photo.png result.png darken
```

**Apply composite:**
```bash
wallpaper-process process composite input.jpg output.jpg dark
```

**Apply preset:**
```bash
wallpaper-process process preset input.jpg output.jpg dark_vibrant
```

### Info Commands (Host Execution)

These commands run on the host (no container):

```bash
wallpaper-process info       # Show configuration
wallpaper-process version    # Show version
```

## Architecture

### Container Execution Model

When you run a process command, the orchestrator:

1. Validates container image exists
2. Mounts input file (read-only) and output directory (read-write)
3. Executes `wallpaper-core` inside container
4. Returns results to your output location

**Volume Mounts:**
- Input: `{your-input}:/input/image.jpg:ro` (read-only)
- Output: `{your-output-dir}:/output:rw` (read-write)

**Example:**
```bash
$ wallpaper-process process effect ~/photo.jpg ~/output/blurred.jpg blur

# Internally runs:
# docker run --rm \
#   -v ~/photo.jpg:/input/image.jpg:ro \
#   -v ~/output:/output:rw \
#   wallpaper-effects:latest \
#   process effect /input/image.jpg /output/blurred.jpg blur
```

### Package Structure

```
wallpaper_orchestrator/
├── cli/
│   ├── main.py              # CLI entry point (wallpaper-process)
│   └── commands/
│       ├── install.py       # Build container image
│       └── uninstall.py     # Remove container image
├── config/
│   ├── settings.py          # OrchestratorSettings
│   └── unified.py           # UnifiedConfig (core + orchestrator)
└── container/
    └── manager.py           # ContainerManager (execution)
```

## Configuration

Settings are managed via `layered_settings` with multiple layers:

1. Package defaults (built-in)
2. Project settings (`./settings.toml`)
3. User settings (`~/.config/wallpaper-effects/settings.toml`)
4. CLI overrides

### Orchestrator Settings

**Container engine:**
```toml
# ~/.config/wallpaper-effects/settings.toml
[orchestrator.container]
engine = "podman"  # or "docker" (default)
```

**Custom registry:**
```toml
[orchestrator.container]
image_registry = "ghcr.io/username"
image_name = "wallpaper-effects:latest"
```

## vs. wallpaper-core

**Use orchestrator when:**
- You want isolated, reproducible execution
- You don't want to install ImageMagick
- You need portability across systems
- You're okay with Docker/Podman requirement

**Use core when:**
- You want direct control over ImageMagick
- You have ImageMagick installed already
- You want minimal overhead
- You don't need containers

**Installation:**
```bash
# Core only (local execution)
pip install wallpaper-core
# Command: wallpaper-core

# Orchestrator (containerized execution)
pip install wallpaper-orchestrator
# Command: wallpaper-process
```

## Troubleshooting

**"Container image not found"**
```bash
# Solution: Install the image
wallpaper-process install
```

**"docker: command not found"**
```bash
# Solution: Install Docker or switch to Podman
# Install Docker: https://docs.docker.com/get-docker/
# Or use Podman:
wallpaper-process install --engine podman
```

**"permission denied" on output**
```bash
# Solution: Ensure output directory is writable
mkdir -p output
chmod 755 output
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

## Security

The container image:
- Runs as non-root user (UID 1000)
- Input mounts are read-only (`:ro`)
- Output directory is the only writable mount (`:rw`)
- Container is removed after execution (`--rm`)

## License

MIT
```

**Step 2: Commit updated README**

```bash
git add packages/orchestrator/README.md
git commit -m "docs(orchestrator): update README for container execution architecture

- Document new command structure
- Explain container execution model
- Add troubleshooting section
- Compare with wallpaper-core package
- Show volume mounting strategy

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Update Core Documentation

**Goal:** Update core README to reflect CLI rename

**Files:**
- Modify: `packages/core/README.md`

**Step 1: Add note about orchestrator at top**

Add to `packages/core/README.md` after the title:

```markdown
# wallpaper_core

Core wallpaper effects processor with local ImageMagick execution.

> **Note:** For containerized execution, see `wallpaper-orchestrator` package.
> This package runs effects locally using your system's ImageMagick installation.

## CLI Command

This package provides the `wallpaper-core` command for local execution.

For containerized execution, install `wallpaper-orchestrator` which provides the `wallpaper-process` command.
```

**Step 2: Verify all examples use wallpaper-core**

```bash
cd packages/core
grep -c "wallpaper-core" README.md
```

Expected: Multiple matches (should be updated from Task 1)

**Step 3: Commit**

```bash
git add packages/core/README.md
git commit -m "docs(core): add note about orchestrator package

- Clarify core provides wallpaper-core command
- Point users to orchestrator for containerized execution
- Note that core requires local ImageMagick

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Completion Checklist

After completing all tasks, verify:

- [ ] Core CLI renamed to `wallpaper-core`
- [ ] Orchestrator CLI is `wallpaper-process`
- [ ] `ContainerManager.run_process()` implemented and tested
- [ ] Process commands execute in containers
- [ ] Info/version commands run on host
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Both packages have clear README files

## Testing

Run full test suite:

```bash
# Test core package
cd packages/core
pytest -v

# Test orchestrator package
cd packages/orchestrator
pytest -v
```

Expected: All tests pass

## Manual Verification

```bash
# 1. Install orchestrator
cd packages/orchestrator
uv pip install -e .

# 2. Build container (optional - will fail without Docker, that's OK)
wallpaper-process install

# 3. Check help
wallpaper-process --help

# 4. Check commands registered
wallpaper-process process --help
```

---

## Notes

- All container execution tests use mocked subprocess calls
- No Docker/Podman required to run tests
- Container image must be built before running actual effects
- Volume mounting uses absolute paths to avoid issues
- Both Docker and Podman supported equally
