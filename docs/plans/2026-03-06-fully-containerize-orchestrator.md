# Fully Containerize wallpaper-process batch — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every `wallpaper-process batch` command run inside the container instead of on the host, and fix all 13 findings identified in the audit (code, tests, docs, smoke tests).

**Architecture:** Add `ContainerManager.run_batch()` mirroring `run_process()` in structure; rewrite the `batch_app` Typer sub-app with four dedicated commands that call it; add `OrchestratorDryRun.render_container_batch()` for two-layer dry-run output; rewrite the broken integration tests; fix all five affected doc files; add orchestrator batch smoke tests.

**Tech Stack:** Python 3.12, Typer, Rich, pytest, unittest.mock, bash (smoke tests).

**Design doc:** `docs/plans/2026-03-06-fully-containerize-orchestrator-design.md`

---

## Task 1: `ContainerManager.run_batch()` — TDD

**Files:**
- Modify: `packages/orchestrator/tests/test_container_manager.py` (append tests)
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py` (add method)

**Context:** `run_process()` in `manager.py` is the reference implementation. `run_batch()` follows the exact same guard pattern but builds a `batch <type>` container command instead of `process <type>`. Read both files before starting.

---

**Step 1: Write the failing tests**

Append to `packages/orchestrator/tests/test_container_manager.py`:

```python
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
```

**Step 2: Run — expect failures**

```bash
cd packages/orchestrator
uv run pytest tests/test_container_manager.py -k "run_batch" -v
```

Expected: all `test_run_batch_*` tests fail with `AttributeError: 'ContainerManager' object has no attribute 'run_batch'`.

**Step 3: Implement `run_batch()` in `manager.py`**

In `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`, add after the `run_process()` method:

```python
def run_batch(
    self,
    batch_type: str,
    input_path: Path,
    output_dir: Path,
    flat: bool = False,
    parallel: bool = True,
    strict: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute wallpaper-core batch command inside container.

    Args:
        batch_type: One of "effects", "composites", "presets", "all"
        input_path: Path to input image on host
        output_dir: Output directory on host
        flat: Use flat output structure
        parallel: Run effects in parallel (True) or sequential (False)
        strict: Abort on first failure

    Returns:
        CompletedProcess with returncode, stdout, stderr

    Raises:
        ValueError: If batch_type is not one of the valid values
        RuntimeError: If container image not available
        FileNotFoundError: If input file doesn't exist
        PermissionError: If output directory cannot be created
    """
    valid_types = {"effects", "composites", "presets", "all"}
    if batch_type not in valid_types:
        raise ValueError(
            f"Invalid batch_type: {batch_type}. "
            f"Must be one of: {', '.join(sorted(valid_types))}"
        )

    if not self.is_image_available():
        raise RuntimeError(
            "Container image not found. "
            "Install the image first: wallpaper-process install"
        )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}\n"
            "Please check the file path is correct."
        )

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        abs_output_dir = output_dir.absolute()
        abs_output_dir.chmod(0o777)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot create output directory: {output_dir}\n"
            "Please check directory permissions."
        ) from e

    abs_input = input_path.absolute()
    input_mount = f"{abs_input}:/input/{input_path.name}:ro"
    output_mount = f"{abs_output_dir}:/output:rw"

    cmd = [self.engine, "run", "--rm"]

    if self.engine == "podman":
        cmd.append("--userns=keep-id")

    cmd.extend(
        [
            "-v",
            input_mount,
            "-v",
            output_mount,
            self.get_image_name(),
            "batch",
            batch_type,
            f"/input/{input_path.name}",
            "-o",
            "/output",
        ]
    )

    if flat:
        cmd.append("--flat")

    if parallel:
        cmd.append("--parallel")
    else:
        cmd.append("--sequential")

    if strict:
        cmd.append("--strict")
    else:
        cmd.append("--no-strict")

    return subprocess.run(  # nosec: B603
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
```

**Step 4: Run — expect all pass**

```bash
cd packages/orchestrator
uv run pytest tests/test_container_manager.py -k "run_batch" -v
```

Expected: all `test_run_batch_*` tests PASS.

**Step 5: Run full test suite — no regressions**

```bash
cd packages/orchestrator
uv run pytest tests/test_container_manager.py -v
```

Expected: all pass.

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/container/manager.py \
        packages/orchestrator/tests/test_container_manager.py
git commit -m "feat(orchestrator): add ContainerManager.run_batch() for containerized batch execution"
```

---

## Task 2: `OrchestratorDryRun.render_container_batch()` — TDD via CLI

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py` (add method)
- Modify: `packages/orchestrator/tests/test_cli_dry_run.py` (add TestBatchContainerDryRun class)

**Context:** `render_container_process()` in `dry_run.py` is the reference. The new method renders a header, input/output/type/engine/image fields, the full host command, and the inner commands table. The tests drive through the CLI runner (same pattern as `TestProcessEffectContainerDryRun`). The CLI side is not wired yet — that comes in Task 3. Add the renderer first so Task 3 can use it.

**Note:** The tests in this task will FAIL until Task 3 is complete. Write them now so they guide Task 3's implementation.

---

**Step 1: Add `render_container_batch()` to `dry_run.py`**

In `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py`, add after `render_container_process()`:

```python
def render_container_batch(
    self,
    batch_type: str,
    input_path: Path,
    output_dir: Path,
    engine: str,
    image_name: str,
    host_command: str,
    items: list[dict[str, str]],
) -> None:
    """Render container batch dry-run with both command layers."""
    self.render_header(f"batch {batch_type} (container)")
    self.render_field("Input", str(input_path))
    self.render_field("Output dir", str(output_dir))
    self.render_field("Batch type", batch_type)
    self.render_field("Engine", engine)
    self.render_field("Image", image_name)
    self.render_command("Host command", host_command)
    if items:
        inner = "\n".join(item.get("command", "") for item in items)
        self.render_command(
            f"Inner commands ({len(items)} items, run inside container)", inner
        )
```

**Step 2: Write the failing dry-run CLI tests**

Append to `packages/orchestrator/tests/test_cli_dry_run.py`:

```python
class TestBatchContainerDryRun:
    """Dry-run for containerized batch commands."""

    def _mock_manager(self, engine: str = "docker") -> MagicMock:
        mock = MagicMock()
        mock.engine = engine
        mock.get_image_name.return_value = "wallpaper-effects:latest"
        mock.is_image_available.return_value = True
        return mock

    def test_batch_effects_dry_run_shows_host_command(self, tmp_path):
        """batch effects --dry-run shows docker run command."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        assert "batch" in result.stdout.lower()
        assert "effects" in result.stdout.lower()

    def test_batch_effects_dry_run_shows_inner_commands(self, tmp_path):
        """batch effects --dry-run shows magick commands."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "magick" in result.stdout.lower()

    def test_batch_effects_dry_run_no_container_spawned(self, tmp_path):
        """batch effects --dry-run never calls run_batch."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = self._mock_manager()
            mock_mgr.return_value = mock_manager
            runner.invoke(app, ["batch", "effects", str(input_file), "--dry-run"])

        mock_manager.run_batch.assert_not_called()

    def test_batch_composites_dry_run_shows_host_command(self, tmp_path):
        """batch composites --dry-run shows docker run command."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "composites", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "composites" in result.stdout.lower()

    def test_batch_presets_dry_run_shows_host_command(self, tmp_path):
        """batch presets --dry-run shows docker run command."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "presets", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "presets" in result.stdout.lower()

    def test_batch_all_dry_run_shows_host_command(self, tmp_path):
        """batch all --dry-run shows docker run command."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "all", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "all" in result.stdout.lower() or "batch" in result.stdout.lower()

    def test_batch_dry_run_podman_shows_userns(self, tmp_path):
        """batch --dry-run with podman shows --userns flag."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager(engine="podman")
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "userns" in result.stdout or "podman" in result.stdout.lower()

    def test_batch_dry_run_uses_original_filename(self, tmp_path):
        """batch --dry-run shows original filename, not hardcoded image.jpg."""
        input_file = tmp_path / "my-wallpaper.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "--dry-run"],
            )

        assert result.exit_code == 0
        assert "my-wallpaper.jpg" in result.stdout
        assert "image.jpg" not in result.stdout
```

**Step 3: Run — expect failures (CLI not wired yet)**

```bash
cd packages/orchestrator
uv run pytest tests/test_cli_dry_run.py::TestBatchContainerDryRun -v
```

Expected: FAIL — current CLI routes batch dry-run through core's `CoreDryRun.render_batch()`, not the new container path. These failures will be resolved in Task 3.

**Step 4: Commit the renderer (not the failing tests yet — those go with Task 3's commit)**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/dry_run.py
git commit -m "feat(orchestrator): add OrchestratorDryRun.render_container_batch()"
```

---

## Task 3: Rewrite `batch_app` in `cli/main.py` — TDD

**Files:**
- Create: `packages/orchestrator/tests/test_cli_batch.py`
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`

**Context:** Read `cli/main.py` in full before starting. The goal is to replace the `batch_callback` + re-registration loop with four dedicated command functions. The `show_app` pattern stays untouched. Reference `process_effect` for the command function shape.

---

**Step 1: Write the failing tests — create `test_cli_batch.py`**

Create `packages/orchestrator/tests/test_cli_batch.py`:

```python
"""Tests for containerized batch commands in wallpaper-process CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


# ── batch effects ──────────────────────────────────────────────────────────


def test_batch_effects_with_output_dir(tmp_path: Path) -> None:
    """batch effects -o calls run_batch with correct args."""
    input_file = tmp_path / "input.jpg"
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(output_dir)],
        )

        assert result.exit_code == 0
        mock_manager.run_batch.assert_called_once()
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "effects"
        assert kwargs["input_path"] == input_file
        assert kwargs["output_dir"] == output_dir
        assert kwargs["flat"] is False


def test_batch_effects_without_output_dir(tmp_path: Path) -> None:
    """batch effects without -o resolves default from config."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with (
        patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
        patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
    ):
        mock_settings = MagicMock()
        mock_settings.core.output.default_dir = tmp_path / "default"
        mock_config.return_value = mock_settings

        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(app, ["batch", "effects", str(input_file)])

        assert result.exit_code == 0
        mock_manager.run_batch.assert_called_once()


def test_batch_effects_flat_flag(tmp_path: Path) -> None:
    """--flat forwarded to run_batch."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--flat"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["flat"] is True


def test_batch_effects_sequential_flag(tmp_path: Path) -> None:
    """--sequential forwarded as parallel=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--sequential"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["parallel"] is False


def test_batch_effects_no_strict_flag(tmp_path: Path) -> None:
    """--no-strict forwarded as strict=False."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path), "--no-strict"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["strict"] is False


def test_batch_effects_image_not_available(tmp_path: Path) -> None:
    """Missing container image exits 1 with install hint."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
        assert "wallpaper-process install" in result.output
        mock_manager.run_batch.assert_not_called()


def test_batch_effects_container_failure(tmp_path: Path) -> None:
    """Non-zero returncode from container exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(
            returncode=1, stdout="", stderr="magick: error"
        )
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "failed" in result.output.lower()


def test_batch_effects_runtime_error(tmp_path: Path) -> None:
    """RuntimeError from run_batch exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.side_effect = RuntimeError("container exploded")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "effects", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch composites ───────────────────────────────────────────────────────


def test_batch_composites_with_output_dir(tmp_path: Path) -> None:
    """batch composites -o calls run_batch with batch_type=composites."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "composites"


def test_batch_composites_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output


def test_batch_composites_container_failure(tmp_path: Path) -> None:
    """Non-zero returncode exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=1, stdout="", stderr="err")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "composites", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch presets ──────────────────────────────────────────────────────────


def test_batch_presets_with_output_dir(tmp_path: Path) -> None:
    """batch presets -o calls run_batch with batch_type=presets."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "presets", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "presets"


def test_batch_presets_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "presets", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1


# ── batch all ──────────────────────────────────────────────────────────────


def test_batch_all_with_output_dir(tmp_path: Path) -> None:
    """batch all -o calls run_batch with batch_type=all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["batch_type"] == "all"


def test_batch_all_flat_flag(tmp_path: Path) -> None:
    """--flat forwarded to run_batch for all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = True
        mock_manager.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        mock_mgr.return_value = mock_manager

        runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path), "--flat"],
        )

        kwargs = mock_manager.run_batch.call_args[1]
        assert kwargs["flat"] is True


def test_batch_all_image_not_available(tmp_path: Path) -> None:
    """Missing image exits 1 for all."""
    input_file = tmp_path / "input.jpg"
    input_file.touch()

    with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
        mock_manager = MagicMock()
        mock_manager.is_image_available.return_value = False
        mock_mgr.return_value = mock_manager

        result = runner.invoke(
            app,
            ["batch", "all", str(input_file), "-o", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "Container image not found" in result.output
```

**Step 2: Run — expect failures**

```bash
cd packages/orchestrator
uv run pytest tests/test_cli_batch.py -v
```

Expected: all tests FAIL. The current `batch_app` runs core callbacks directly; `run_batch` is never called.

**Step 3: Rewrite the `batch_app` section in `cli/main.py`**

In `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`, make these changes:

**3a. Remove the import:**
```python
# DELETE this line:
from wallpaper_core.cli import batch as core_batch_module
```

**3b. Add the new import (keep it with the other `wallpaper_core.cli` imports):**
```python
from wallpaper_core.cli.batch import _resolve_batch_items
```

**3c. Replace the entire `batch_app` block** (from the `batch_app = typer.Typer(...)` line through the `app.add_typer(batch_app, ...)` line) with:

```python
# Create batch sub-app — all commands run inside the container
batch_app = typer.Typer(
    name="batch",
    help="Batch generate effects (runs in container)",
    no_args_is_help=True,
)


def _build_batch_host_command(
    manager: ContainerManager,
    batch_type: str,
    input_file: Path,
    output_dir: Path,
    flat: bool,
    parallel: bool,
    strict: bool,
) -> str:
    """Build the docker/podman run command string for batch dry-run display."""
    image_name = manager.get_image_name()
    abs_input = input_file.absolute()
    abs_output_dir = output_dir.absolute()

    cmd_parts = [manager.engine, "run", "--rm"]
    if manager.engine == "podman":
        cmd_parts.append("--userns=keep-id")
    cmd_parts.extend(
        [
            "-v",
            f"{abs_input}:/input/{input_file.name}:ro",
            "-v",
            f"{abs_output_dir}:/output:rw",
            image_name,
            "batch",
            batch_type,
            f"/input/{input_file.name}",
            "-o",
            "/output",
        ]
    )
    if flat:
        cmd_parts.append("--flat")
    if not parallel:
        cmd_parts.append("--sequential")
    if not strict:
        cmd_parts.append("--no-strict")
    return " ".join(cmd_parts)


def _run_containerized_batch(
    batch_type: str,
    input_file: Path,
    output_dir: Path | None,
    flat: bool,
    parallel: bool,
    strict: bool,
    dry_run: bool,
) -> None:
    """Shared implementation for all four batch subcommands."""
    try:
        config = get_config()
        manager = ContainerManager(config)  # type: ignore[arg-type]

        if output_dir is None:
            output_dir = config.core.output.default_dir  # type: ignore[attr-defined]

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            image_name = manager.get_image_name()
            host_command = _build_batch_host_command(
                manager, batch_type, input_file, output_dir, flat, parallel, strict
            )
            effects_config = load_effects()
            items = _resolve_batch_items(
                effects_config, batch_type, input_file, output_dir, flat
            )
            renderer.render_container_batch(
                batch_type=batch_type,
                input_path=input_file,
                output_dir=output_dir,
                engine=manager.engine,
                image_name=image_name,
                host_command=host_command,
                items=items,
            )
            container_checks = renderer.validate_container(
                engine=manager.engine,
                image_name=image_name,
            )
            renderer.render_validation(container_checks)
            raise typer.Exit(0)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(f"[cyan]Generating {batch_type} in container...[/cyan]")
        result = manager.run_batch(
            batch_type=batch_type,
            input_path=input_file,
            output_dir=output_dir,
            flat=flat,
            parallel=parallel,
            strict=strict,
        )

        if result.returncode != 0:
            console.print(f"[red]Batch failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(f"[green]✓ Output written to:[/green] {output_dir}")

    except typer.Exit:
        raise
    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@batch_app.command("effects")
def batch_effects(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure")
    ] = False,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview without executing")
    ] = False,
) -> None:
    """Generate all effects for an image (runs in container).

    Examples:
        wallpaper-process batch effects input.jpg
        wallpaper-process batch effects input.jpg -o /out --flat
    """
    _run_containerized_batch(
        "effects", input_file, output_dir, flat, parallel, strict, dry_run
    )


@batch_app.command("composites")
def batch_composites(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure")
    ] = False,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview without executing")
    ] = False,
) -> None:
    """Generate all composites for an image (runs in container).

    Examples:
        wallpaper-process batch composites input.jpg
        wallpaper-process batch composites input.jpg -o /out --flat
    """
    _run_containerized_batch(
        "composites", input_file, output_dir, flat, parallel, strict, dry_run
    )


@batch_app.command("presets")
def batch_presets(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure")
    ] = False,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview without executing")
    ] = False,
) -> None:
    """Generate all presets for an image (runs in container).

    Examples:
        wallpaper-process batch presets input.jpg
        wallpaper-process batch presets input.jpg -o /out --flat
    """
    _run_containerized_batch(
        "presets", input_file, output_dir, flat, parallel, strict, dry_run
    )


@batch_app.command("all")
def batch_all(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure")
    ] = False,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview without executing")
    ] = False,
) -> None:
    """Generate all effects, composites, and presets for an image (runs in container).

    Examples:
        wallpaper-process batch all input.jpg
        wallpaper-process batch all input.jpg -o /out --flat
    """
    _run_containerized_batch(
        "all", input_file, output_dir, flat, parallel, strict, dry_run
    )


# Add the sub-apps to main app
app.add_typer(batch_app, name="batch")
```

Also **remove the batch re-registration loop** (the block that reads `for cmd_info in core_batch_module.app.registered_commands`).

**3d. Remove `batch_callback` function** — it is no longer needed.

**Step 4: Run test_cli_batch.py — expect all pass**

```bash
cd packages/orchestrator
uv run pytest tests/test_cli_batch.py -v
```

Expected: all PASS.

**Step 5: Run dry-run tests from Task 2 — expect all pass**

```bash
cd packages/orchestrator
uv run pytest tests/test_cli_dry_run.py::TestBatchContainerDryRun -v
```

Expected: all PASS.

**Step 6: Run full suite**

```bash
cd packages/orchestrator
uv run pytest --tb=short -q
```

Expected: only the intentionally-broken `TestBatchCommands` tests in `test_cli_integration.py` fail (they will be fixed in Task 5). Everything else passes.

**Step 7: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py \
        packages/orchestrator/tests/test_cli_batch.py \
        packages/orchestrator/tests/test_cli_dry_run.py
git commit -m "feat(orchestrator): containerize batch commands via ContainerManager.run_batch()"
```

---

## Task 4: Fix `test_cli_integration.py` — rewrite `TestBatchCommands`

**Files:**
- Modify: `packages/orchestrator/tests/test_cli_integration.py`

**Context:** The 13 tests in `TestBatchCommands` verify host filesystem file creation by mocking `wallpaper_core.engine.executor.subprocess.run`. That code path is no longer exercised by the orchestrator's batch commands. The tests must be rewritten to mock `ContainerManager.run_batch()` and assert the correct arguments are passed. Read the class in full before editing.

---

**Step 1: Replace `TestBatchCommands` entirely**

In `packages/orchestrator/tests/test_cli_integration.py`, replace the entire `TestBatchCommands` class and its associated fixtures (`test_image_file`, `use_tmp_default_output` at the bottom — those fixtures are now unused, remove them too) with:

```python
class TestBatchCommands:
    """Tests for containerized batch commands."""

    def _mock_manager(self) -> MagicMock:
        mock = MagicMock()
        mock.is_image_available.return_value = True
        mock.run_batch.return_value = MagicMock(returncode=0, stdout="", stderr="")
        return mock

    def test_batch_effects_calls_run_batch(self, tmp_path: Path) -> None:
        """batch effects calls run_batch(batch_type='effects')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()
        output_dir = tmp_path / "output"

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "effects", str(input_file), "-o", str(output_dir)],
            )

        assert result.exit_code == 0
        call_kwargs = mock_mgr.return_value.run_batch.call_args[1]
        assert call_kwargs["batch_type"] == "effects"

    def test_batch_effects_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch effects without -o passes config default_dir to run_batch."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()
        default_dir = tmp_path / "wallpapers-output"

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = default_dir
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()

            result = runner.invoke(app, ["batch", "effects", str(input_file)])

        assert result.exit_code == 0
        call_kwargs = mock_mgr.return_value.run_batch.call_args[1]
        assert call_kwargs["output_dir"] == default_dir

    def test_batch_effects_flat(self, tmp_path: Path) -> None:
        """--flat forwarded correctly."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                ["batch", "effects", str(input_file), "-o", str(tmp_path), "--flat"],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["flat"] is True

    def test_batch_effects_sequential(self, tmp_path: Path) -> None:
        """--sequential forwarded as parallel=False."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                ["batch", "effects", str(input_file), "-o", str(tmp_path), "--sequential"],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["parallel"] is False

    def test_batch_composites_calls_run_batch(self, tmp_path: Path) -> None:
        """batch composites calls run_batch(batch_type='composites')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "composites", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "composites"

    def test_batch_composites_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch composites without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "composites", str(input_file)])

        assert result.exit_code == 0

    def test_batch_presets_calls_run_batch(self, tmp_path: Path) -> None:
        """batch presets calls run_batch(batch_type='presets')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "presets", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "presets"

    def test_batch_presets_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch presets without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "presets", str(input_file)])

        assert result.exit_code == 0

    def test_batch_all_calls_run_batch(self, tmp_path: Path) -> None:
        """batch all calls run_batch(batch_type='all')."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(
                app,
                ["batch", "all", str(input_file), "-o", str(tmp_path)],
            )

        assert result.exit_code == 0
        assert mock_mgr.return_value.run_batch.call_args[1]["batch_type"] == "all"

    def test_batch_all_without_output_uses_config_default(
        self, tmp_path: Path
    ) -> None:
        """batch all without -o passes config default_dir."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with (
            patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr,
            patch("wallpaper_orchestrator.cli.main.get_config") as mock_config,
        ):
            mock_settings = MagicMock()
            mock_settings.core.output.default_dir = tmp_path / "default"
            mock_config.return_value = mock_settings
            mock_mgr.return_value = self._mock_manager()
            result = runner.invoke(app, ["batch", "all", str(input_file)])

        assert result.exit_code == 0

    def test_batch_all_flat(self, tmp_path: Path) -> None:
        """--flat forwarded for batch all."""
        input_file = tmp_path / "test_image.png"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_mgr.return_value = self._mock_manager()
            runner.invoke(
                app,
                ["batch", "all", str(input_file), "-o", str(tmp_path), "--flat"],
            )

        assert mock_mgr.return_value.run_batch.call_args[1]["flat"] is True
```

Also remove the now-unused fixtures at the bottom of the file:
- `test_image_file` fixture (was only used by old batch tests)
- `use_tmp_default_output` fixture (same)

**Step 2: Run — expect all pass**

```bash
cd packages/orchestrator
uv run pytest tests/test_cli_integration.py::TestBatchCommands -v
```

Expected: all PASS.

**Step 3: Run full suite — expect clean**

```bash
cd packages/orchestrator
uv run pytest --tb=short -q
```

Expected: all tests PASS.

**Step 4: Commit**

```bash
git add packages/orchestrator/tests/test_cli_integration.py
git commit -m "test(orchestrator): rewrite TestBatchCommands to mock ContainerManager.run_batch()"
```

---

## Task 5: Fix `test_integration.py` — extend `test_cli_commands_registered`

**Files:**
- Modify: `packages/orchestrator/tests/test_integration.py`

**Context:** The current test only checks for `install`, `uninstall`, `info`. After the CLI rewrite, `batch`, `show`, and `process` are registered as Typer sub-apps (not individual commands). Sub-apps appear in `app.registered_groups`, not `app.registered_commands`.

---

**Step 1: Add the assertion**

In `test_cli_commands_registered`, extend the test:

```python
def test_cli_commands_registered() -> None:
    """Test all CLI commands are registered."""
    from wallpaper_orchestrator.cli.main import app

    command_names = {
        cmd.name or cmd.callback.__name__ for cmd in app.registered_commands
    }
    group_names = {grp.name for grp in app.registered_groups}

    # Scalar commands
    assert "install" in command_names
    assert "uninstall" in command_names
    assert "info" in command_names
    assert "version" in command_names

    # Sub-app groups
    assert "batch" in group_names
    assert "show" in group_names
    assert "process" in group_names
```

**Step 2: Run**

```bash
cd packages/orchestrator
uv run pytest tests/test_integration.py::test_cli_commands_registered -v
```

Expected: PASS.

**Step 3: Commit**

```bash
git add packages/orchestrator/tests/test_integration.py
git commit -m "test(orchestrator): verify batch/show/process sub-apps are registered in CLI"
```

---

## Task 6: Update `conftest.py` — clarify autouse fixture scope

**Files:**
- Modify: `packages/orchestrator/tests/conftest.py`

**Context:** The `mock_subprocess_for_integration_tests` fixture mocks `wallpaper_core.engine.executor.subprocess.run`. After containerization, batch commands no longer touch that code path — they go through `ContainerManager.run_batch()`. The fixture is still valid for show/info/other tests that internally use core machinery. Add a comment to prevent confusion.

---

**Step 1: Add the comment**

In `packages/orchestrator/tests/conftest.py`, update the docstring of `mock_subprocess_for_integration_tests`:

```python
@pytest.fixture(autouse=True)
def mock_subprocess_for_integration_tests():
    """
    Auto-use fixture that mocks subprocess.run and shutil.which for all tests.

    This mocks wallpaper_core.engine.executor.subprocess.run (the ImageMagick
    execution path used by core's BatchGenerator and CommandExecutor). It applies
    to show, info, and any test that exercises core machinery directly.

    NOTE: Batch commands in the orchestrator (wallpaper-process batch) no longer
    go through this code path — they call ContainerManager.run_batch(), which
    uses a separate subprocess call. Those tests mock ContainerManager directly.
    """
```

**Step 2: Run full suite — verify no change in pass/fail**

```bash
cd packages/orchestrator
uv run pytest --tb=short -q
```

Expected: same results as before (all pass).

**Step 3: Commit**

```bash
git add packages/orchestrator/tests/conftest.py
git commit -m "docs(tests): clarify autouse mock fixture scope after batch containerization"
```

---

## Task 7: Fix documentation — 5 files

**Files:**
- Modify: `docs/reference/cli-orchestrator.md`
- Modify: `docs/explanation/host-vs-container.md`
- Modify: `docs/how-to/run-in-container.md`
- Modify: `docs/how-to/batch-process.md`
- Modify: `CHANGELOG.md`

Do these one file at a time, commit after each.

---

### 7a: `docs/reference/cli-orchestrator.md`

**Changes:**
1. **Line 3** — Change: `"Batch, show, info, and version commands run on the host."` → `"Batch commands run inside the container. Show, info, and version commands run on the host."`
2. **Commands overview table** — Change `batch` row from `Host` to `Container`.
3. **`## batch` section** — Rewrite entirely:

```markdown
## batch

Runs batch generation **inside the container**. Each subcommand spawns one container run that executes `wallpaper-core batch <type>` internally. (BHV-0081)

```bash
wallpaper-process batch effects <input-file> [options]
wallpaper-process batch composites <input-file> [options]
wallpaper-process batch presets <input-file> [options]
wallpaper-process batch all <input-file> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--output-dir` | `-o` | Output directory on host. | `core.output.default_dir` |
| `--flat` | | Flat output structure. | false |
| `--parallel` / `--sequential` | | Run effects in parallel or sequentially inside the container. | `--parallel` |
| `--strict` / `--no-strict` | | Abort on first failure or continue. | `--strict` |
| `--dry-run` | | Preview host and inner commands. | false |

**Container invocation (example for `effects`):**
```
docker run --rm \
  -v <abs-input>:/input/<filename>:ro \
  -v <abs-output-dir>:/output:rw \
  wallpaper-effects:latest \
  batch effects /input/<filename> -o /output [--flat] [--parallel] [--strict]
```

With Podman, `--userns=keep-id` is added.

**`--dry-run` behavior:** Prints both the host `docker run ...` command and the table of inner `magick ...` commands that will execute inside the container. No container is spawned.
```

Commit:
```bash
git add docs/reference/cli-orchestrator.md
git commit -m "docs: update cli-orchestrator reference to reflect batch runs in container"
```

### 7b: `docs/explanation/host-vs-container.md`

**Changes:**
1. **"What runs where" table** — Change `batch` row: `wallpaper-process` column from `On host (delegates to core batch engine)` to `In container`.
2. **Line 88** — The sentence *"Switching from host to container mode is as simple as replacing `wallpaper-core` with `wallpaper-process`"* is now accurate — no change needed.
3. **Update the practical guidance examples** to show `wallpaper-process batch` as a valid container-mode command.

Commit:
```bash
git add docs/explanation/host-vs-container.md
git commit -m "docs: update host-vs-container explanation — batch now runs in container for orchestrator"
```

### 7c: `docs/how-to/run-in-container.md`

**Change:** Rewrite the "Run batch in the container environment" section (lines 70-78):

```markdown
### Run batch in the container

`wallpaper-process batch` generates multiple effects, composites, or presets inside the container. No host ImageMagick required.

```bash
wallpaper-process batch effects wallpaper.jpg
wallpaper-process batch composites wallpaper.jpg
wallpaper-process batch presets wallpaper.jpg
wallpaper-process batch all wallpaper.jpg
```

Each command spawns one container run. Parallelism (`--parallel`) runs inside the container. Flags are identical to `wallpaper-core batch`. (BHV-0081)
```

Commit:
```bash
git add docs/how-to/run-in-container.md
git commit -m "docs: fix run-in-container — batch now actually runs in container"
```

### 7d: `docs/how-to/batch-process.md`

**Add** a new section after the existing `wallpaper-core batch` content:

```markdown
---

## Using the container (wallpaper-process batch)

If you do not have ImageMagick installed on your host, use `wallpaper-process batch` instead. It runs the same batch processing inside the container.

**Prerequisites:** Container image installed (`wallpaper-process install`). Docker or Podman on host.

### Generate all effects (in container)

```bash
wallpaper-process batch effects wallpaper.jpg
```

### Generate all composites (in container)

```bash
wallpaper-process batch composites wallpaper.jpg
```

### Generate all presets (in container)

```bash
wallpaper-process batch presets wallpaper.jpg
```

### Generate everything at once (in container)

```bash
wallpaper-process batch all wallpaper.jpg
```

### All flags are supported

`-o`, `--flat`, `--parallel`/`--sequential`, `--strict`/`--no-strict`, `--dry-run` work identically to `wallpaper-core batch`.
```

**Also update the Prerequisites section** at the top to distinguish the two paths:

```markdown
## Prerequisites

**For `wallpaper-core batch` (host mode):**
- `wallpaper-core` is installed.
- ImageMagick is installed on the host.

**For `wallpaper-process batch` (container mode):**
- `wallpaper-process` is installed.
- Container image is built: `wallpaper-process install`
- Docker or Podman is installed and running.
```

Commit:
```bash
git add docs/how-to/batch-process.md
git commit -m "docs: add wallpaper-process batch section to batch-process how-to"
```

### 7e: `CHANGELOG.md`

Add under an `Unreleased` or next-version section at the top:

```markdown
### Fixed

- `wallpaper-process batch` now runs inside the container instead of on the host.
  Previously, all four batch subcommands (`effects`, `composites`, `presets`, `all`)
  called ImageMagick directly on the host via the core batch engine, requiring
  ImageMagick to be installed locally — defeating the purpose of the containerized CLI.
  They now dispatch a single `docker run` / `podman run` per batch invocation.
  Flags (`--flat`, `--parallel/--sequential`, `--strict/--no-strict`, `--dry-run`)
  are forwarded to the container unchanged.
```

Commit:
```bash
git add CHANGELOG.md
git commit -m "docs: add changelog entry for batch containerization fix"
```

---

## Task 8: Add smoke tests for `wallpaper-process batch`

**Files:**
- Modify: `tests/smoke/run-smoke-tests.sh`

**Context:** Read the existing "Testing Orchestrator Process Commands" section in the smoke script to understand the section header format, `print_header`, `print_test`, `run_cmd`, `test_passed`, `test_failed`, `add_detail` helper functions. The new section goes after the existing orchestrator process tests.

---

**Step 1: Locate the insertion point**

Search for the end of the orchestrator process section. It will be near the orchestrator install/uninstall tests. The new section goes immediately after.

**Step 2: Add the new section**

Insert into `tests/smoke/run-smoke-tests.sh`:

```bash
# ============================================================================
# Testing Orchestrator Batch Commands (containerized)
# ============================================================================

print_header "Testing Orchestrator Batch Commands (containerized)"

# Ensure container image is available before running batch tests
if ! wallpaper-process install --dry-run > /dev/null 2>&1; then
    echo "Skipping orchestrator batch tests: container image not available"
fi

print_test "wallpaper-process batch effects runs in container and generates outputs"
orch_batch_effect="$TEST_OUTPUT_DIR/orch-batch-effect"
mkdir -p "$orch_batch_effect"
if run_cmd "wallpaper-process batch effects \"$TEST_IMAGE\" -o \"$orch_batch_effect\""; then
    output_count=$(find "$orch_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        add_detail "• Command: wallpaper-process batch effects <image> -o <output-dir>"
        add_detail "• Effects generated: $output_count (ran inside container)"
        test_passed
    else
        test_failed "insufficient effects generated (expected ≥9, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$orch_batch_effect" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "wallpaper-process batch effects failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch composites runs in container and generates outputs"
orch_batch_composite="$TEST_OUTPUT_DIR/orch-batch-composite"
mkdir -p "$orch_batch_composite"
if run_cmd "wallpaper-process batch composites \"$TEST_IMAGE\" -o \"$orch_batch_composite\""; then
    output_count=$(find "$orch_batch_composite" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 4 ]; then
        add_detail "• Command: wallpaper-process batch composites <image> -o <output-dir>"
        add_detail "• Composites generated: $output_count (ran inside container)"
        test_passed
    else
        test_failed "insufficient composites generated (expected ≥4, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$orch_batch_composite" 2>/dev/null | tr '\n' ' ')"
    fi
else
    test_failed "wallpaper-process batch composites failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch presets runs in container and generates outputs"
orch_batch_preset="$TEST_OUTPUT_DIR/orch-batch-preset"
mkdir -p "$orch_batch_preset"
if run_cmd "wallpaper-process batch presets \"$TEST_IMAGE\" -o \"$orch_batch_preset\""; then
    output_count=$(find "$orch_batch_preset" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 7 ]; then
        add_detail "• Command: wallpaper-process batch presets <image> -o <output-dir>"
        add_detail "• Presets generated: $output_count (ran inside container)"
        test_passed
    else
        test_failed "insufficient presets generated (expected ≥7, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$orch_batch_preset" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "wallpaper-process batch presets failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch all runs in container and generates all outputs"
orch_batch_all="$TEST_OUTPUT_DIR/orch-batch-all"
mkdir -p "$orch_batch_all"
if run_cmd "wallpaper-process batch all \"$TEST_IMAGE\" -o \"$orch_batch_all\""; then
    output_count=$(find "$orch_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then
        add_detail "• Command: wallpaper-process batch all <image> -o <output-dir>"
        add_detail "• Total files generated: $output_count (effects + composites + presets, in container)"
        test_passed
    else
        test_failed "insufficient outputs generated (expected >15, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$orch_batch_all" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "wallpaper-process batch all failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch effects --dry-run shows container command, no files created"
orch_dry_dir="$TEST_OUTPUT_DIR/orch-batch-dry"
mkdir -p "$orch_dry_dir"
dry_output=$(wallpaper-process batch effects "$TEST_IMAGE" -o "$orch_dry_dir" --dry-run 2>&1)
dry_exit=$?
if [ $dry_exit -eq 0 ]; then
    if echo "$dry_output" | grep -qi "docker\|podman\|run"; then
        file_count=$(find "$orch_dry_dir" -type f 2>/dev/null | wc -l)
        if [ "$file_count" -eq 0 ]; then
            add_detail "• Container command visible in dry-run output"
            add_detail "• No files created (correct)"
            test_passed
        else
            test_failed "dry-run created files (should not)" \
                "wallpaper-process batch effects --dry-run" \
                "Files found: $(ls -1 "$orch_dry_dir" | head -5)"
        fi
    else
        test_failed "dry-run output missing container command" \
            "wallpaper-process batch effects --dry-run" \
            "Output: $dry_output"
    fi
else
    test_failed "dry-run exited non-zero ($dry_exit)" \
        "wallpaper-process batch effects --dry-run" \
        "Output: $dry_output"
fi

print_test "wallpaper-process batch all --flat generates flat output structure"
orch_flat_dir="$TEST_OUTPUT_DIR/orch-batch-flat"
mkdir -p "$orch_flat_dir"
if run_cmd "wallpaper-process batch all \"$TEST_IMAGE\" -o \"$orch_flat_dir\" --flat"; then
    # Flat: no type subdirectories — all files should be under image-stem dir directly
    subdir_count=$(find "$orch_flat_dir" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l)
    file_count=$(find "$orch_flat_dir" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$file_count" -gt 0 ] && [ "$subdir_count" -eq 0 ]; then
        add_detail "• Files generated: $file_count"
        add_detail "• No type subdirectories (correct flat structure)"
        test_passed
    else
        test_failed "unexpected directory structure for --flat" \
            "$LAST_CMD" \
            "Files: $file_count, Type subdirs: $subdir_count"
    fi
else
    test_failed "wallpaper-process batch all --flat failed" "$LAST_CMD" "$LAST_OUTPUT"
fi
```

**Step 3: Verify the script is valid bash**

```bash
bash -n tests/smoke/run-smoke-tests.sh
```

Expected: no output (syntax valid).

**Step 4: Commit**

```bash
git add tests/smoke/run-smoke-tests.sh
git commit -m "test(smoke): add wallpaper-process batch container smoke tests"
```

---

## Final Verification

**Step 1: Run the full orchestrator test suite**

```bash
cd packages/orchestrator
uv run pytest -v --tb=short
```

Expected: all tests PASS. Coverage should remain ≥ 95%.

**Step 2: Check coverage threshold**

```bash
cd packages/orchestrator
uv run pytest --cov=src --cov-report=term-missing
uv run coverage report --fail-under=95
```

Expected: passes threshold.

**Step 3: Run linting**

```bash
cd packages/orchestrator
uv run ruff check --line-length 88 .
uv run black --check --line-length=88 .
uv run mypy src/
```

Expected: all pass. Fix any issues and commit with `fix:` prefix.

**Step 4: Verify help string**

```bash
uv run wallpaper-process --help
```

Expected output includes: `batch    Batch generate effects (runs in container)`

**Step 5: Final summary commit (if needed)**

If any lint fixes were made:
```bash
git add -p   # stage only the lint fixes
git commit -m "fix(orchestrator): lint and type fixes after batch containerization"
```
