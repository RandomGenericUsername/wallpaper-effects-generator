# Dry-Run Commands Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `--dry-run` flag to all 17 mutating CLI commands across wallpaper-core and wallpaper-orchestrator, showing resolved commands, structured summaries, and pre-flight validation without executing anything.

**Architecture:** Shared `DryRunBase` in layered-settings provides formatting utilities (tables, validation checklists, command blocks). `CoreDryRun` in wallpaper-core extends it for ImageMagick command resolution. `OrchestratorDryRun` in wallpaper-orchestrator extends it for container commands. Each command gets a `--dry-run` flag with early-return before any side effects.

**Tech Stack:** Python, Typer (CLI), Rich (tables/formatting), Pydantic (config models), pytest (testing)

---

### Task 1: DryRunBase — Write Failing Tests

**Files:**
- Create: `packages/settings/tests/test_dry_run.py`

**Step 1: Write the failing tests**

```python
"""Tests for DryRunBase formatting utilities."""

from io import StringIO

import pytest
from rich.console import Console

from layered_settings.dry_run import DryRunBase, ValidationCheck


@pytest.fixture
def console_output():
    """Capture console output."""
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    """Create DryRunBase with captured output."""
    console, _ = console_output
    return DryRunBase(console=console)


class TestValidationCheck:
    def test_passed_check(self):
        check = ValidationCheck(name="Input file exists", passed=True)
        assert check.passed is True
        assert check.name == "Input file exists"
        assert check.detail == ""

    def test_failed_check_with_detail(self):
        check = ValidationCheck(
            name="magick binary found",
            passed=False,
            detail="not found on PATH",
        )
        assert check.passed is False
        assert check.detail == "not found on PATH"


class TestDryRunBaseRendering:
    def test_render_header(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_header("process effect")
        output = string_io.getvalue()
        assert "Dry Run" in output
        assert "process effect" in output

    def test_render_field(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_field("Input", "/path/to/image.jpg")
        output = string_io.getvalue()
        assert "Input" in output
        assert "/path/to/image.jpg" in output

    def test_render_command(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_command("Command", 'magick "input.jpg" -blur 0x8 "output.jpg"')
        output = string_io.getvalue()
        assert "magick" in output
        assert "input.jpg" in output

    def test_render_validation_passed(self, dry_run, console_output):
        _, string_io = console_output
        checks = [
            ValidationCheck(name="Input file exists", passed=True),
            ValidationCheck(name="magick binary found", passed=True),
        ]
        dry_run.render_validation(checks)
        output = string_io.getvalue()
        assert "Input file exists" in output
        assert "magick binary found" in output

    def test_render_validation_failed(self, dry_run, console_output):
        _, string_io = console_output
        checks = [
            ValidationCheck(name="Input file exists", passed=False, detail="file not found"),
        ]
        dry_run.render_validation(checks)
        output = string_io.getvalue()
        assert "Input file exists" in output
        assert "file not found" in output

    def test_render_table(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_table(
            title="Effects (2)",
            columns=["Name", "Output Path", "Params"],
            rows=[
                ["blur", "/output/blur.jpg", "blur=0x8"],
                ["blackwhite", "/output/blackwhite.jpg", "—"],
            ],
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "blackwhite" in output

    def test_render_commands_list(self, dry_run, console_output):
        _, string_io = console_output
        commands = [
            'magick "input.jpg" -blur 0x8 "output.jpg"',
            'magick "input.jpg" -grayscale Average "output2.jpg"',
        ]
        dry_run.render_commands_list(commands)
        output = string_io.getvalue()
        assert "1." in output
        assert "2." in output
        assert "-blur" in output
        assert "-grayscale" in output
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/settings/tests/test_dry_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'layered_settings.dry_run'`

---

### Task 2: DryRunBase — Implement

**Files:**
- Create: `packages/settings/src/layered_settings/dry_run.py`
- Modify: `packages/settings/src/layered_settings/__init__.py:150-167`

**Step 1: Write the implementation**

```python
"""Dry-run base formatting utilities.

Provides shared rendering for dry-run output across packages.
Does not contain any domain-specific logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table


@dataclass
class ValidationCheck:
    """Result of a single pre-flight validation check."""

    name: str
    passed: bool
    detail: str = ""


class DryRunBase:
    """Base class for dry-run rendering.

    Provides generic formatting utilities used by CoreDryRun
    and OrchestratorDryRun.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_header(self, title: str) -> None:
        """Render the dry-run header banner."""
        self.console.print(f"\n[bold cyan]Dry Run:[/bold cyan] {title}\n")

    def render_field(self, label: str, value: str) -> None:
        """Render an aligned key-value field."""
        self.console.print(f"  [bold]{label}:[/bold]{' ' * max(1, 12 - len(label))}{value}")

    def render_command(self, label: str, command: str) -> None:
        """Render a labeled command block."""
        self.console.print(f"\n  [bold]{label}:[/bold]")
        self.console.print(f"    [dim]{command}[/dim]")

    def render_commands_list(self, commands: list[str]) -> None:
        """Render a numbered list of commands."""
        self.console.print(f"\n  [bold]Commands ({len(commands)}):[/bold]")
        for i, cmd in enumerate(commands, 1):
            self.console.print(f"    {i}. [dim]{cmd}[/dim]")

    def render_validation(self, checks: list[ValidationCheck]) -> None:
        """Render a validation checklist with pass/fail markers."""
        self.console.print(f"\n  [bold]Validation:[/bold]")
        for check in checks:
            if check.passed:
                detail = f" ({check.detail})" if check.detail else ""
                self.console.print(f"    [green]✓[/green] {check.name}{detail}")
            else:
                detail = f" ({check.detail})" if check.detail else ""
                self.console.print(f"    [red]✗[/red] {check.name}{detail}")

    def render_table(
        self,
        title: str,
        columns: list[str],
        rows: list[list[str]],
    ) -> None:
        """Render a Rich table with title."""
        self.console.print(f"\n  [bold]{title}[/bold]")
        table = Table(show_header=True, padding=(0, 1))
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)
```

**Step 2: Update `__init__.py` exports**

Add to `packages/settings/src/layered_settings/__init__.py` — append to `__all__` list and add imports:

After line 47, add:
```python
from layered_settings.dry_run import DryRunBase, ValidationCheck
```

In the `__all__` list, add:
```python
    "DryRunBase",
    "ValidationCheck",
```

**Step 3: Run tests to verify they pass**

Run: `uv run pytest packages/settings/tests/test_dry_run.py -v`
Expected: All 8 tests PASS

**Step 4: Commit**

```bash
git add packages/settings/src/layered_settings/dry_run.py packages/settings/tests/test_dry_run.py packages/settings/src/layered_settings/__init__.py
git commit -m "feat(settings): add DryRunBase formatting utilities"
```

---

### Task 3: CoreDryRun — Write Failing Tests

**Files:**
- Create: `packages/core/tests/test_dry_run.py`

**Step 1: Write the failing tests**

```python
"""Tests for CoreDryRun rendering and validation."""

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from wallpaper_core.dry_run import CoreDryRun


@pytest.fixture
def console_output():
    """Capture console output."""
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    """Create CoreDryRun with captured output."""
    console, _ = console_output
    return CoreDryRun(console=console)


class TestCoreValidation:
    def test_validate_input_exists(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(input_path=input_file)
        input_check = next(c for c in checks if "Input file" in c.name)
        assert input_check.passed is True

    def test_validate_input_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "nonexistent.jpg"
        checks = dry_run.validate_core(input_path=input_file)
        input_check = next(c for c in checks if "Input file" in c.name)
        assert input_check.passed is False

    def test_validate_magick_found(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        with patch("shutil.which", return_value="/usr/bin/magick"):
            checks = dry_run.validate_core(input_path=input_file)
        magick_check = next(c for c in checks if "magick" in c.name.lower())
        assert magick_check.passed is True

    def test_validate_magick_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        with patch("shutil.which", return_value=None):
            checks = dry_run.validate_core(input_path=input_file)
        magick_check = next(c for c in checks if "magick" in c.name.lower())
        assert magick_check.passed is False

    def test_validate_effect_found(self, dry_run, tmp_path, sample_effects_config):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(
            input_path=input_file,
            item_name="blur",
            item_type="effect",
            config=sample_effects_config,
        )
        effect_check = next(c for c in checks if "blur" in c.name.lower() or "found" in c.name.lower())
        assert effect_check.passed is True

    def test_validate_effect_not_found(self, dry_run, tmp_path, sample_effects_config):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        checks = dry_run.validate_core(
            input_path=input_file,
            item_name="nonexistent",
            item_type="effect",
            config=sample_effects_config,
        )
        effect_check = next(c for c in checks if "not found" in c.detail.lower() or not c.passed)
        assert effect_check.passed is False

    def test_validate_output_dir_exists(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output" / "result.jpg"
        (tmp_path / "output").mkdir()
        checks = dry_run.validate_core(input_path=input_file, output_path=output_file)
        dir_check = next(c for c in checks if "Output" in c.name or "directory" in c.name.lower())
        assert dir_check.passed is True

    def test_validate_output_dir_missing(self, dry_run, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "nonexistent_dir" / "result.jpg"
        checks = dry_run.validate_core(input_path=input_file, output_path=output_file)
        dir_check = next(c for c in checks if "Output" in c.name or "directory" in c.name.lower())
        assert dir_check.passed is False
        assert "would be created" in dir_check.detail.lower()


class TestCoreRenderProcess:
    def test_render_process_shows_effect(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/home/user/wallpaper.jpg"),
            output_path=Path("/home/user/output/blur.jpg"),
            params={"blur": "0x8"},
            resolved_command='magick "/home/user/wallpaper.jpg" -blur 0x8 "/home/user/output/blur.jpg"',
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "/home/user/wallpaper.jpg" in output
        assert "/home/user/output/blur.jpg" in output
        assert "0x8" in output

    def test_render_process_shows_command(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/input.jpg"),
            output_path=Path("/output.jpg"),
            params={"blur": "0x8"},
            resolved_command='magick "/input.jpg" -blur 0x8 "/output.jpg"',
        )
        output = string_io.getvalue()
        assert "magick" in output

    def test_render_process_composite_shows_chain(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_process(
            item_name="blur-brightness80",
            item_type="composite",
            input_path=Path("/input.jpg"),
            output_path=Path("/output.jpg"),
            params={},
            resolved_command="chain: blur -> brightness",
            chain_commands=[
                'magick "/input.jpg" -blur 0x8 "/tmp/step_0.jpg"',
                'magick "/tmp/step_0.jpg" -brightness-contrast -20% "/output.jpg"',
            ],
        )
        output = string_io.getvalue()
        assert "blur-brightness80" in output
        assert "step" in output.lower() or "1." in output


class TestCoreRenderBatch:
    def test_render_batch_shows_table(self, dry_run, console_output):
        _, string_io = console_output
        items = [
            {"name": "blur", "type": "effect", "output_path": "/output/blur.jpg", "params": "blur=0x8", "command": 'magick "in.jpg" -blur 0x8 "/output/blur.jpg"'},
            {"name": "blackwhite", "type": "effect", "output_path": "/output/blackwhite.jpg", "params": "—", "command": 'magick "in.jpg" -grayscale Average "/output/blackwhite.jpg"'},
        ]
        dry_run.render_batch(
            input_path=Path("/home/user/wallpaper.jpg"),
            output_dir=Path("/output/"),
            items=items,
            parallel=True,
            max_workers=4,
            strict=True,
        )
        output = string_io.getvalue()
        assert "blur" in output
        assert "blackwhite" in output
        assert "2" in output  # item count
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/core/tests/test_dry_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wallpaper_core.dry_run'`

---

### Task 4: CoreDryRun — Implement

**Files:**
- Create: `packages/core/src/wallpaper_core/dry_run.py`

**Step 1: Write the implementation**

```python
"""Dry-run rendering for wallpaper-core commands."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from layered_settings.dry_run import DryRunBase, ValidationCheck
from rich.console import Console

if TYPE_CHECKING:
    from wallpaper_core.effects.schema import EffectsConfig


class CoreDryRun(DryRunBase):
    """Dry-run renderer for wallpaper-core commands.

    Extends DryRunBase with ImageMagick and effects domain logic.
    """

    def validate_core(
        self,
        input_path: Path,
        output_path: Path | None = None,
        item_name: str | None = None,
        item_type: str | None = None,
        config: "EffectsConfig | None" = None,
    ) -> list[ValidationCheck]:
        """Run pre-flight validation checks.

        Args:
            input_path: Input image file path
            output_path: Output image file path (optional)
            item_name: Effect/composite/preset name (optional)
            item_type: "effect", "composite", or "preset" (optional)
            config: Effects configuration (optional, needed for name lookup)

        Returns:
            List of validation check results
        """
        checks = []

        # Check input file exists
        checks.append(ValidationCheck(
            name="Input file exists",
            passed=input_path.exists(),
            detail=str(input_path) if input_path.exists() else f"not found: {input_path}",
        ))

        # Check magick binary
        magick_path = shutil.which("magick")
        checks.append(ValidationCheck(
            name="magick binary found",
            passed=magick_path is not None,
            detail=magick_path or "not found on PATH",
        ))

        # Check item name in config
        if item_name and item_type and config:
            collection = {
                "effect": config.effects,
                "composite": config.composites,
                "preset": config.presets,
            }.get(item_type, {})
            found = item_name in collection
            checks.append(ValidationCheck(
                name=f"{item_type.title()} '{item_name}' found in config",
                passed=found,
                detail="" if found else f"not found in {item_type}s",
            ))

        # Check output directory
        if output_path:
            output_dir = output_path.parent
            dir_exists = output_dir.exists()
            checks.append(ValidationCheck(
                name="Output directory exists",
                passed=dir_exists,
                detail=str(output_dir) if dir_exists else f"would be created: {output_dir}",
            ))

        return checks

    def render_process(
        self,
        item_name: str,
        item_type: str,
        input_path: Path,
        output_path: Path,
        params: dict,
        resolved_command: str,
        chain_commands: list[str] | None = None,
        command_template: str | None = None,
    ) -> None:
        """Render single process dry-run output.

        Args:
            item_name: Effect/composite/preset name
            item_type: "effect", "composite", or "preset"
            input_path: Input image path
            output_path: Output image path
            params: Resolved parameters
            resolved_command: Fully resolved command string
            chain_commands: List of commands for composite chains
            command_template: Original command template (verbose mode)
        """
        self.render_header(f"process {item_type}")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_path))
        self.render_field(item_type.title(), item_name)

        if params:
            param_str = "  ".join(f"{k}={v}" for k, v in params.items())
            self.render_field("Params", param_str)

        if command_template:
            self.render_command("Command template", command_template)

        if chain_commands:
            self.render_commands_list(chain_commands)
        else:
            self.render_command("Command", resolved_command)

    def render_batch(
        self,
        input_path: Path,
        output_dir: Path,
        items: list[dict],
        parallel: bool,
        max_workers: int | None,
        strict: bool,
    ) -> None:
        """Render batch dry-run output with table and commands.

        Args:
            input_path: Input image path
            output_dir: Output directory path
            items: List of dicts with keys: name, type, output_path, params, command
            parallel: Whether parallel mode is enabled
            max_workers: Number of parallel workers
            strict: Whether strict mode is enabled
        """
        # Group items by type
        effects = [i for i in items if i["type"] == "effect"]
        composites = [i for i in items if i["type"] == "composite"]
        presets = [i for i in items if i["type"] == "preset"]

        self.render_header(f"batch ({len(items)} items)")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_dir))
        mode = f"parallel ({max_workers or 'auto'} workers)" if parallel else "sequential"
        self.render_field("Mode", mode)
        self.render_field("Strict", "yes" if strict else "no")

        # Render tables per type
        if effects:
            self.render_table(
                title=f"Effects ({len(effects)})",
                columns=["Name", "Output Path", "Params"],
                rows=[[e["name"], e["output_path"], e["params"]] for e in effects],
            )
        if composites:
            self.render_table(
                title=f"Composites ({len(composites)})",
                columns=["Name", "Output Path", "Chain"],
                rows=[[c["name"], c["output_path"], c.get("params", "—")] for c in composites],
            )
        if presets:
            self.render_table(
                title=f"Presets ({len(presets)})",
                columns=["Name", "Output Path", "Type", "Target"],
                rows=[[p["name"], p["output_path"], p.get("preset_type", "—"), p.get("target", "—")] for p in presets],
            )

        # Render all commands
        commands = [i["command"] for i in items]
        self.render_commands_list(commands)
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_dry_run.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add packages/core/src/wallpaper_core/dry_run.py packages/core/tests/test_dry_run.py
git commit -m "feat(core): add CoreDryRun rendering and validation"
```

---

### Task 5: Core Process Commands — Write Failing CLI Tests

**Files:**
- Create: `packages/core/tests/test_cli_dry_run.py`

**Step 1: Write the failing tests**

```python
"""Tests for --dry-run flag on core CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from wallpaper_core.cli.main import app

runner = CliRunner()


class TestProcessEffectDryRun:
    def test_dry_run_shows_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "magick" in result.stdout
        assert "blur" in result.stdout

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert not output_file.exists()

    def test_dry_run_shows_validation(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        # Should show validation section
        assert "Validation" in result.stdout or "✓" in result.stdout

    def test_dry_run_missing_input_shows_warning(self, tmp_path):
        result = runner.invoke(app, [
            "process", "effect",
            str(tmp_path / "nonexistent.jpg"), str(tmp_path / "output.jpg"),
            "--effect", "blur", "--dry-run",
        ])
        # Should still show dry-run output (not exit with error)
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "✗" in result.stdout

    def test_dry_run_unknown_effect_shows_warning(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "process", "effect",
            str(test_image_file), str(tmp_path / "output.jpg"),
            "--effect", "nonexistent_effect", "--dry-run",
        ])
        assert "Dry Run" in result.stdout
        assert "not found" in result.stdout.lower() or "✗" in result.stdout

    def test_dry_run_quiet_shows_only_command(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "-q", "process", "effect",
            str(test_image_file), str(output_file),
            "--effect", "blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "magick" in result.stdout
        # Quiet mode should NOT have the verbose fields
        assert "Validation" not in result.stdout


class TestProcessCompositeDryRun:
    def test_dry_run_shows_chain(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "composite",
            str(test_image_file), str(output_file),
            "--composite", "blur-brightness80", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "blur" in result.stdout.lower()
        assert "brightness" in result.stdout.lower()

    def test_dry_run_no_file_created(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        runner.invoke(app, [
            "process", "composite",
            str(test_image_file), str(output_file),
            "--composite", "blur-brightness80", "--dry-run",
        ])
        assert not output_file.exists()


class TestProcessPresetDryRun:
    def test_dry_run_composite_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "preset",
            str(test_image_file), str(output_file),
            "--preset", "dark_blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "dark_blur" in result.stdout

    def test_dry_run_effect_preset(self, test_image_file, tmp_path):
        output_file = tmp_path / "output.jpg"
        result = runner.invoke(app, [
            "process", "preset",
            str(test_image_file), str(output_file),
            "--preset", "subtle_blur", "--dry-run",
        ])
        assert result.exit_code == 0
        assert "subtle_blur" in result.stdout
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/core/tests/test_cli_dry_run.py -v`
Expected: FAIL — `--dry-run` flag not recognized by Typer

---

### Task 6: Core Process Commands — Add --dry-run Flag

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/process.py:1-157`

**Step 1: Add --dry-run to process effect command**

Add import at top of `process.py` (after line 12):
```python
from wallpaper_core.dry_run import CoreDryRun
```

Modify `apply_effect` function signature (line 18-30) to add `dry_run` parameter after `opacity`:
```python
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
```

Add dry-run logic after params are built and before execution (after line 67, before line 69):
```python
    if dry_run:
        renderer = CoreDryRun(console=output.console)
        checks = renderer.validate_core(
            input_path=input_file,
            output_path=output_file,
            item_name=effect,
            item_type="effect",
            config=config,
        )
        if output.verbosity == 0:  # QUIET
            command = effect_def.command
            substitutions = {"INPUT": str(input_file), "OUTPUT": str(output_file)}
            for k, v in final_params.items():
                substitutions[k.upper()] = str(v)
            for k, v in substitutions.items():
                command = command.replace(f'"${k}"', f'"{v}"')
                command = command.replace(f"${k}", v)
            output.console.print(command)
        else:
            command = effect_def.command
            substitutions = {"INPUT": str(input_file), "OUTPUT": str(output_file)}
            for k, v in final_params.items():
                substitutions[k.upper()] = str(v)
            for k, v in substitutions.items():
                command = command.replace(f'"${k}"', f'"{v}"')
                command = command.replace(f"${k}", v)
            renderer.render_process(
                item_name=effect,
                item_type="effect",
                input_path=input_file,
                output_path=output_file,
                params=final_params,
                resolved_command=command,
                command_template=effect_def.command if output.verbosity >= 2 else None,
            )
            renderer.render_validation(checks)
        raise typer.Exit(0)
```

**Step 2: Refactor command resolution into a helper**

The command substitution logic is duplicated from `executor.py`. Extract it to a module-level helper in `process.py`:

```python
def _resolve_command(command_template: str, input_path: Path, output_path: Path, params: dict) -> str:
    """Resolve command template by substituting variables."""
    substitutions = {"INPUT": str(input_path), "OUTPUT": str(output_path)}
    for k, v in params.items():
        substitutions[k.upper()] = str(v)
    command = command_template
    for k, v in substitutions.items():
        command = command.replace(f'"${k}"', f'"{v}"')
        command = command.replace(f"${k}", v)
    return command
```

Then use it in the dry-run block:
```python
    if dry_run:
        renderer = CoreDryRun(console=output.console)
        checks = renderer.validate_core(
            input_path=input_file, output_path=output_file,
            item_name=effect, item_type="effect", config=config,
        )
        resolved = _resolve_command(effect_def.command, input_file, output_file, final_params)
        if output.verbosity == 0:  # QUIET
            output.console.print(resolved)
        else:
            renderer.render_process(
                item_name=effect, item_type="effect",
                input_path=input_file, output_path=output_file,
                params=final_params, resolved_command=resolved,
                command_template=effect_def.command if output.verbosity >= 2 else None,
            )
            renderer.render_validation(checks)
        raise typer.Exit(0)
```

**Step 3: Add --dry-run to apply_composite (line 79-107)**

Add `dry_run` parameter to signature:
```python
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
```

Add dry-run block after composite_def lookup (after line 97, before line 99):
```python
    if dry_run:
        renderer = CoreDryRun(console=output.console)
        checks = renderer.validate_core(
            input_path=input_file, output_path=output_file,
            item_name=composite, item_type="composite", config=config,
        )
        chain_commands = []
        for i, step in enumerate(composite_def.chain):
            step_effect = config.effects.get(step.effect)
            if step_effect:
                step_params = chain_executor._get_params_with_defaults(step.effect, step.params)
                step_in = input_file if i == 0 else Path(f"<temp/step_{i - 1}{output_file.suffix}>")
                is_last = i == len(composite_def.chain) - 1
                step_out = output_file if is_last else Path(f"<temp/step_{i}{output_file.suffix}>")
                chain_commands.append(_resolve_command(step_effect.command, step_in, step_out, step_params))
        if output.verbosity == 0:
            for cmd in chain_commands:
                output.console.print(cmd)
        else:
            renderer.render_process(
                item_name=composite, item_type="composite",
                input_path=input_file, output_path=output_file,
                params={}, resolved_command=f"chain: {' -> '.join(s.effect for s in composite_def.chain)}",
                chain_commands=chain_commands,
            )
            renderer.render_validation(checks)
        raise typer.Exit(0)
```

**Step 4: Add --dry-run to apply_preset (line 110-156)**

Add `dry_run` parameter to signature:
```python
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
```

Add dry-run block after preset_def lookup (after line 128, before line 130):
```python
    if dry_run:
        renderer = CoreDryRun(console=output.console)
        checks = renderer.validate_core(
            input_path=input_file, output_path=output_file,
            item_name=preset, item_type="preset", config=config,
        )
        if preset_def.composite:
            composite_def = config.composites.get(preset_def.composite)
            if composite_def:
                chain_commands = []
                for i, step in enumerate(composite_def.chain):
                    step_effect = config.effects.get(step.effect)
                    if step_effect:
                        step_params = chain_executor._get_params_with_defaults(step.effect, step.params)
                        step_in = input_file if i == 0 else Path(f"<temp/step_{i - 1}{output_file.suffix}>")
                        is_last = i == len(composite_def.chain) - 1
                        step_out = output_file if is_last else Path(f"<temp/step_{i}{output_file.suffix}>")
                        chain_commands.append(_resolve_command(step_effect.command, step_in, step_out, step_params))
                resolved = f"chain: {' -> '.join(s.effect for s in composite_def.chain)}"
            else:
                chain_commands = []
                resolved = f"composite '{preset_def.composite}' not found"
        elif preset_def.effect:
            effect_def = config.effects.get(preset_def.effect)
            if effect_def:
                params = chain_executor._get_params_with_defaults(preset_def.effect, preset_def.params)
                resolved = _resolve_command(effect_def.command, input_file, output_file, params)
                chain_commands = None
            else:
                resolved = f"effect '{preset_def.effect}' not found"
                chain_commands = None
                params = {}
        else:
            resolved = "no effect or composite defined"
            chain_commands = None
            params = {}

        if output.verbosity == 0:
            if chain_commands:
                for cmd in chain_commands:
                    output.console.print(cmd)
            else:
                output.console.print(resolved)
        else:
            renderer.render_process(
                item_name=preset, item_type="preset",
                input_path=input_file, output_path=output_file,
                params=params if preset_def.effect else {},
                resolved_command=resolved,
                chain_commands=chain_commands,
            )
            renderer.render_validation(checks)
        raise typer.Exit(0)
```

**Step 5: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_cli_dry_run.py -v`
Expected: All tests PASS

**Step 6: Run all existing core tests to verify no regressions**

Run: `uv run pytest packages/core/tests/ -v`
Expected: All existing tests still PASS

**Step 7: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/process.py packages/core/tests/test_cli_dry_run.py
git commit -m "feat(core): add --dry-run to process effect/composite/preset commands"
```

---

### Task 7: Core Batch Commands — Write Failing Tests

**Files:**
- Modify: `packages/core/tests/test_cli_dry_run.py` (append)

**Step 1: Append batch dry-run tests**

```python
class TestBatchEffectsDryRun:
    def test_dry_run_shows_table(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "batch", "effects",
            str(test_image_file), str(tmp_path / "output"),
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "blur" in result.stdout
        assert "blackwhite" in result.stdout

    def test_dry_run_no_files_created(self, test_image_file, tmp_path):
        output_dir = tmp_path / "output"
        runner.invoke(app, [
            "batch", "effects",
            str(test_image_file), str(output_dir),
            "--dry-run",
        ])
        assert not output_dir.exists()

    def test_dry_run_shows_commands(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "batch", "effects",
            str(test_image_file), str(tmp_path / "output"),
            "--dry-run",
        ])
        assert "magick" in result.stdout

    def test_dry_run_shows_item_count(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "batch", "effects",
            str(test_image_file), str(tmp_path / "output"),
            "--dry-run",
        ])
        assert "items" in result.stdout.lower() or "9" in result.stdout


class TestBatchAllDryRun:
    def test_dry_run_shows_all_types(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "batch", "all",
            str(test_image_file), str(tmp_path / "output"),
            "--dry-run",
        ])
        assert result.exit_code == 0
        # Should show effects, composites, and presets
        assert "blur" in result.stdout
        assert "dark_blur" in result.stdout or "preset" in result.stdout.lower()

    def test_dry_run_no_files_created(self, test_image_file, tmp_path):
        output_dir = tmp_path / "output"
        runner.invoke(app, [
            "batch", "all",
            str(test_image_file), str(output_dir),
            "--dry-run",
        ])
        assert not output_dir.exists()

    def test_dry_run_quiet_shows_only_commands(self, test_image_file, tmp_path):
        result = runner.invoke(app, [
            "-q", "batch", "effects",
            str(test_image_file), str(tmp_path / "output"),
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "magick" in result.stdout
        assert "Validation" not in result.stdout
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/core/tests/test_cli_dry_run.py::TestBatchEffectsDryRun -v`
Expected: FAIL — `--dry-run` flag not recognized

---

### Task 8: Core Batch Commands — Add --dry-run Flag

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/batch.py:1-131`

**Step 1: Add import and dry-run to _run_batch**

Add imports at top (after line 8):
```python
from wallpaper_core.dry_run import CoreDryRun
from wallpaper_core.engine.chain import ChainExecutor
```

Add `dry_run` parameter to `_run_batch` (modify line 33-41):
```python
def _run_batch(
    ctx: typer.Context,
    input_file: Path,
    output_dir: Path,
    batch_type: str,
    parallel: bool,
    strict: bool,
    flat: bool,
    dry_run: bool = False,
) -> None:
```

Add dry-run logic after the generator is created and count is determined (after line 64, before line 66). This is the core of batch dry-run — resolve all items without executing:

```python
    if dry_run:
        from wallpaper_core.cli.process import _resolve_command

        renderer = CoreDryRun(console=output.console)
        chain_executor = ChainExecutor(config)
        image_name = input_file.stem
        base_dir = output_dir / image_name

        items = []
        # Collect all items with resolved commands
        if batch_type in ("effects", "all"):
            subdir = None if flat else "effects"
            for name in config.effects:
                effect_def = config.effects[name]
                params = chain_executor._get_params_with_defaults(name, {})
                suffix = input_file.suffix or ".png"
                if flat or batch_type != "all":
                    out = base_dir / (f"{name}{suffix}" if subdir is None else f"{name}{suffix}")
                    if subdir and batch_type != "all":
                        out = base_dir / subdir / f"{name}{suffix}"
                else:
                    out = base_dir / "effects" / f"{name}{suffix}"
                resolved = _resolve_command(effect_def.command, input_file, out, params)
                param_str = "  ".join(f"{k}={v}" for k, v in params.items()) if params else "—"
                items.append({"name": name, "type": "effect", "output_path": str(out), "params": param_str, "command": resolved})

        if batch_type in ("composites", "all"):
            subdir = None if flat else "composites"
            for name in config.composites:
                comp = config.composites[name]
                suffix = input_file.suffix or ".png"
                if flat or batch_type != "all":
                    out = base_dir / f"{name}{suffix}"
                    if subdir and batch_type != "all":
                        out = base_dir / subdir / f"{name}{suffix}"
                else:
                    out = base_dir / "composites" / f"{name}{suffix}"
                chain_str = " -> ".join(s.effect for s in comp.chain)
                # Resolve chain commands
                chain_cmds = []
                for i, step in enumerate(comp.chain):
                    step_effect = config.effects.get(step.effect)
                    if step_effect:
                        step_params = chain_executor._get_params_with_defaults(step.effect, step.params)
                        step_in = input_file if i == 0 else Path(f"<temp/step_{i-1}{suffix}>")
                        is_last = i == len(comp.chain) - 1
                        step_out = out if is_last else Path(f"<temp/step_{i}{suffix}>")
                        chain_cmds.append(_resolve_command(step_effect.command, step_in, step_out, step_params))
                # For batch table, use the first command; for commands list, join all
                items.append({
                    "name": name, "type": "composite", "output_path": str(out),
                    "params": chain_str, "command": " && ".join(chain_cmds),
                })

        if batch_type in ("presets", "all"):
            subdir = None if flat else "presets"
            for name in config.presets:
                preset_def = config.presets[name]
                suffix = input_file.suffix or ".png"
                if flat or batch_type != "all":
                    out = base_dir / f"{name}{suffix}"
                    if subdir and batch_type != "all":
                        out = base_dir / subdir / f"{name}{suffix}"
                else:
                    out = base_dir / "presets" / f"{name}{suffix}"
                if preset_def.composite:
                    target = preset_def.composite
                    preset_type = "composite"
                    comp = config.composites.get(preset_def.composite)
                    if comp:
                        chain_cmds = []
                        for i, step in enumerate(comp.chain):
                            step_effect = config.effects.get(step.effect)
                            if step_effect:
                                step_params = chain_executor._get_params_with_defaults(step.effect, step.params)
                                step_in = input_file if i == 0 else Path(f"<temp/step_{i-1}{suffix}>")
                                is_last = i == len(comp.chain) - 1
                                step_out = out if is_last else Path(f"<temp/step_{i}{suffix}>")
                                chain_cmds.append(_resolve_command(step_effect.command, step_in, step_out, step_params))
                        cmd = " && ".join(chain_cmds)
                    else:
                        cmd = f"composite '{target}' not found"
                elif preset_def.effect:
                    target = preset_def.effect
                    preset_type = "effect"
                    effect_def = config.effects.get(preset_def.effect)
                    if effect_def:
                        params = chain_executor._get_params_with_defaults(preset_def.effect, preset_def.params)
                        cmd = _resolve_command(effect_def.command, input_file, out, params)
                    else:
                        cmd = f"effect '{target}' not found"
                else:
                    target = "—"
                    preset_type = "—"
                    cmd = "no effect or composite"
                items.append({
                    "name": name, "type": "preset", "output_path": str(out),
                    "params": chain_str if preset_def.composite else "—",
                    "preset_type": preset_type, "target": target, "command": cmd,
                })

        if output.verbosity == 0:  # QUIET
            for item in items:
                output.console.print(item["command"])
        else:
            checks = renderer.validate_core(input_path=input_file, output_path=output_dir / image_name / "dummy")
            renderer.render_batch(
                input_path=input_file, output_dir=output_dir,
                items=items, parallel=use_parallel if 'use_parallel' in dir() else parallel,
                max_workers=max_workers if 'max_workers' in dir() else None,
                strict=use_strict if 'use_strict' in dir() else strict,
            )
            renderer.render_validation(checks)
        raise typer.Exit(0)
```

Note: The dry-run block needs access to `use_parallel`, `use_strict`, and `max_workers` — these are determined by `_get_batch_generator`. Move their resolution before the dry-run block. Refactor `_run_batch` to resolve settings first:

```python
    settings = ctx.obj["settings"]
    use_parallel = parallel if parallel is not None else settings.execution.parallel
    use_strict = strict if strict is not None else settings.execution.strict
    max_workers = settings.execution.max_workers
```

**Step 2: Add --dry-run to each batch command**

Update all four batch commands to pass `dry_run` through. Example for `batch_effects` (line 81-91):

```python
@app.command("effects")
def batch_effects(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
) -> None:
    """Generate all effects for an image."""
    _run_batch(ctx, input_file, output_dir, "effects", parallel, strict, flat, dry_run)
```

Repeat for `batch_composites`, `batch_presets`, `batch_all`.

**Step 3: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_cli_dry_run.py -v`
Expected: All tests PASS

**Step 4: Run all existing core tests**

Run: `uv run pytest packages/core/tests/ -v`
Expected: All existing tests still PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/batch.py packages/core/tests/test_cli_dry_run.py
git commit -m "feat(core): add --dry-run to batch effects/composites/presets/all commands"
```

---

### Task 9: OrchestratorDryRun — Write Failing Tests

**Files:**
- Create: `packages/orchestrator/tests/test_dry_run.py`

**Step 1: Write the failing tests**

```python
"""Tests for OrchestratorDryRun rendering and validation."""

from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from wallpaper_orchestrator.dry_run import OrchestratorDryRun


@pytest.fixture
def console_output():
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=True, width=120)
    return console, string_io


@pytest.fixture
def dry_run(console_output):
    console, _ = console_output
    return OrchestratorDryRun(console=console)


class TestContainerValidation:
    def test_validate_engine_found(self, dry_run):
        with patch("shutil.which", return_value="/usr/bin/podman"):
            checks = dry_run.validate_container(engine="podman")
        engine_check = next(c for c in checks if "podman" in c.name.lower() or "engine" in c.name.lower())
        assert engine_check.passed is True

    def test_validate_engine_missing(self, dry_run):
        with patch("shutil.which", return_value=None):
            checks = dry_run.validate_container(engine="podman")
        engine_check = next(c for c in checks if "podman" in c.name.lower() or "engine" in c.name.lower())
        assert engine_check.passed is False

    def test_validate_image_available(self, dry_run):
        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                checks = dry_run.validate_container(
                    engine="docker", image_name="wallpaper-effects:latest"
                )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is True

    def test_validate_image_missing(self, dry_run):
        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1)
                checks = dry_run.validate_container(
                    engine="docker", image_name="wallpaper-effects:latest"
                )
        image_check = next(c for c in checks if "image" in c.name.lower())
        assert image_check.passed is False


class TestContainerRenderProcess:
    def test_render_container_process_shows_both_commands(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_container_process(
            item_name="blur",
            item_type="effect",
            input_path=Path("/home/user/wallpaper.jpg"),
            output_path=Path("/home/user/output/blur.jpg"),
            engine="podman",
            image_name="wallpaper-effects:latest",
            host_command="podman run --rm ...",
            inner_command='magick "/input/image.jpg" -blur 0x8 "/output/blur.jpg"',
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "magick" in output
        assert "Host" in output or "host" in output
        assert "Inner" in output or "inner" in output or "Inside" in output.lower()

    def test_render_install(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_install(
            engine="podman",
            image_name="wallpaper-effects:latest",
            dockerfile=Path("/path/to/Dockerfile.imagemagick"),
            build_command="podman build -f ... -t wallpaper-effects:latest .",
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "wallpaper-effects" in output
        assert "Dockerfile" in output

    def test_render_uninstall(self, dry_run, console_output):
        _, string_io = console_output
        dry_run.render_uninstall(
            engine="podman",
            image_name="wallpaper-effects:latest",
            command="podman rmi wallpaper-effects:latest",
        )
        output = string_io.getvalue()
        assert "podman" in output
        assert "rmi" in output
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/orchestrator/tests/test_dry_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wallpaper_orchestrator.dry_run'`

---

### Task 10: OrchestratorDryRun — Implement

**Files:**
- Create: `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py`

**Step 1: Write the implementation**

```python
"""Dry-run rendering for wallpaper-orchestrator commands."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from layered_settings.dry_run import DryRunBase, ValidationCheck
from rich.console import Console


class OrchestratorDryRun(DryRunBase):
    """Dry-run renderer for wallpaper-orchestrator commands.

    Extends DryRunBase with container domain logic.
    """

    def validate_container(
        self,
        engine: str,
        image_name: str | None = None,
    ) -> list[ValidationCheck]:
        """Run container pre-flight validation checks."""
        checks = []

        # Check engine binary
        engine_path = shutil.which(engine)
        checks.append(ValidationCheck(
            name=f"{engine} binary found",
            passed=engine_path is not None,
            detail=engine_path or "not found on PATH",
        ))

        # Check image availability
        if image_name and engine_path:
            try:
                result = subprocess.run(
                    [engine, "inspect", image_name],
                    capture_output=True, text=True, check=False,
                )
                available = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                available = False
            checks.append(ValidationCheck(
                name=f"Container image '{image_name}' available",
                passed=available,
                detail="" if available else "not found — run: wallpaper-process install",
            ))

        return checks

    def render_container_process(
        self,
        item_name: str,
        item_type: str,
        input_path: Path,
        output_path: Path,
        engine: str,
        image_name: str,
        host_command: str,
        inner_command: str,
    ) -> None:
        """Render container process dry-run with both command layers."""
        self.render_header(f"process {item_type} (container)")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_path))
        self.render_field(item_type.title(), item_name)
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_command("Host command", host_command)
        self.render_command("Inner command (runs inside container)", inner_command)

    def render_install(
        self,
        engine: str,
        image_name: str,
        dockerfile: Path,
        build_command: str,
    ) -> None:
        """Render install dry-run output."""
        self.render_header("install")
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_field("Dockerfile", str(dockerfile))
        self.render_command("Command", build_command)

    def render_uninstall(
        self,
        engine: str,
        image_name: str,
        command: str,
    ) -> None:
        """Render uninstall dry-run output."""
        self.render_header("uninstall")
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_command("Command", command)
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest packages/orchestrator/tests/test_dry_run.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/dry_run.py packages/orchestrator/tests/test_dry_run.py
git commit -m "feat(orchestrator): add OrchestratorDryRun rendering and validation"
```

---

### Task 11: Orchestrator CLI — Write Failing Tests for --dry-run

**Files:**
- Create: `packages/orchestrator/tests/test_cli_dry_run.py`

**Step 1: Write the failing tests**

```python
"""Tests for --dry-run flag on orchestrator CLI commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


class TestInstallDryRun:
    def test_dry_run_shows_build_command(self):
        result = runner.invoke(app, ["install", "--dry-run"])
        assert result.exit_code == 0
        assert "build" in result.stdout.lower()
        assert "Dockerfile" in result.stdout or "dockerfile" in result.stdout.lower()

    def test_dry_run_no_image_built(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["install", "--dry-run"])
            # subprocess.run should NOT be called for building
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert "build" not in args, "Should not run build during dry-run"


class TestUninstallDryRun:
    def test_dry_run_shows_rmi_command(self):
        result = runner.invoke(app, ["uninstall", "--dry-run"])
        assert result.exit_code == 0
        assert "rmi" in result.stdout

    def test_dry_run_no_image_removed(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["uninstall", "--dry-run"])
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert "rmi" not in args, "Should not run rmi during dry-run"


class TestProcessEffectContainerDryRun:
    def test_dry_run_shows_both_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as MockManager:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            MockManager.return_value = mock_manager

            result = runner.invoke(app, [
                "process", "effect",
                str(input_file), str(output_file), "blur",
                "--dry-run",
            ])

        assert result.exit_code == 0
        # Should show host command (docker run...)
        assert "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        # Should show inner command (magick...)
        assert "magick" in result.stdout

    def test_dry_run_no_container_spawned(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as MockManager:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            MockManager.return_value = mock_manager

            runner.invoke(app, [
                "process", "effect",
                str(input_file), str(output_file), "blur",
                "--dry-run",
            ])

            mock_manager.run_process.assert_not_called()
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/orchestrator/tests/test_cli_dry_run.py -v`
Expected: FAIL — `--dry-run` flag not recognized

---

### Task 12: Orchestrator Process Commands — Add --dry-run

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:48-207`

**Step 1: Add imports**

After line 15, add:
```python
from layered_effects import load_effects
from wallpaper_orchestrator.dry_run import OrchestratorDryRun
from wallpaper_core.dry_run import CoreDryRun
```

**Step 2: Add --dry-run to process_effect (line 48-99)**

Add parameter:
```python
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),  # noqa: B008
```

Add dry-run block after `manager = ContainerManager(config)` but before image availability check:
```python
    if dry_run:
        renderer = OrchestratorDryRun(console=console)
        image_name = manager.get_image_name()

        # Build host command string
        abs_input = input_file.absolute()
        abs_output_dir = output_file.parent.absolute()
        cmd_parts = [manager.engine, "run", "--rm"]
        if manager.engine == "podman":
            cmd_parts.append("--userns=keep-id")
        cmd_parts.extend([
            "-v", f"{abs_input}:/input/image.jpg:ro",
            "-v", f"{abs_output_dir}:/output:rw",
            image_name, "process", "effect",
            "/input/image.jpg", f"/output/{output_file.name}",
            "--effect", effect,
        ])
        host_command = " ".join(cmd_parts)

        # Resolve inner ImageMagick command
        effects_config = load_effects()
        effect_def = effects_config.effects.get(effect)
        if effect_def:
            from wallpaper_core.cli.process import _resolve_command
            from wallpaper_core.engine.chain import ChainExecutor
            chain_exec = ChainExecutor(effects_config)
            params = chain_exec._get_params_with_defaults(effect, {})
            inner_command = _resolve_command(
                effect_def.command,
                Path("/input/image.jpg"),
                Path(f"/output/{output_file.name}"),
                params,
            )
        else:
            inner_command = f"<effect '{effect}' not found in config>"

        renderer.render_container_process(
            item_name=effect, item_type="effect",
            input_path=input_file, output_path=output_file,
            engine=manager.engine, image_name=image_name,
            host_command=host_command, inner_command=inner_command,
        )

        # Validation
        core_checks = CoreDryRun(console=console).validate_core(
            input_path=input_file, output_path=output_file,
            item_name=effect, item_type="effect", config=effects_config,
        )
        container_checks = renderer.validate_container(
            engine=manager.engine, image_name=image_name,
        )
        renderer.render_validation(core_checks + container_checks)
        raise typer.Exit(0)
```

**Step 3: Apply same pattern to process_composite and process_preset**

Same structure as process_effect, changing:
- `command_type` to "composite" / "preset"
- `command_name` variable to `composite` / `preset`
- Inner command resolution for composites resolves the chain; for presets resolves via composite or effect

**Step 4: Run tests to verify they pass**

Run: `uv run pytest packages/orchestrator/tests/test_cli_dry_run.py -v`
Expected: All tests PASS

**Step 5: Run all orchestrator tests**

Run: `uv run pytest packages/orchestrator/tests/ -v`
Expected: All existing tests still PASS

**Step 6: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py packages/orchestrator/tests/test_cli_dry_run.py
git commit -m "feat(orchestrator): add --dry-run to process effect/composite/preset commands"
```

---

### Task 13: Orchestrator Install/Uninstall — Add --dry-run

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py:13-129`
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py:11-111`

**Step 1: Add --dry-run to install**

Add import after line 8:
```python
from wallpaper_orchestrator.dry_run import OrchestratorDryRun
```

Add parameter to install function signature (line 13):
```python
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),  # noqa: B008
```

Add dry-run block after the build command is constructed (after line 80, before line 82):
```python
        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            renderer.render_install(
                engine=container_engine,
                image_name=image_name,
                dockerfile=dockerfile,
                build_command=" ".join(cmd),
            )
            # Validation
            checks = renderer.validate_container(engine=container_engine, image_name=image_name)
            # Check Dockerfile exists
            from layered_settings.dry_run import ValidationCheck
            checks.insert(0, ValidationCheck(
                name="Dockerfile exists",
                passed=dockerfile.exists(),
                detail=str(dockerfile),
            ))
            renderer.render_validation(checks)
            raise typer.Exit(0)
```

**Step 2: Add --dry-run to uninstall**

Add import after line 6:
```python
from wallpaper_orchestrator.dry_run import OrchestratorDryRun
```

Add parameter to uninstall function signature (line 11):
```python
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),  # noqa: B008
```

Add dry-run block after the engine is determined and image_name is set (after line 55, before line 57):
```python
        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            cmd_str = f"{container_engine} rmi {image_name}"
            renderer.render_uninstall(
                engine=container_engine,
                image_name=image_name,
                command=cmd_str,
            )
            checks = renderer.validate_container(engine=container_engine, image_name=image_name)
            renderer.render_validation(checks)
            raise typer.Exit(0)
```

**Step 3: Run install/uninstall dry-run tests**

Run: `uv run pytest packages/orchestrator/tests/test_cli_dry_run.py::TestInstallDryRun packages/orchestrator/tests/test_cli_dry_run.py::TestUninstallDryRun -v`
Expected: All tests PASS

**Step 4: Run all orchestrator tests**

Run: `uv run pytest packages/orchestrator/tests/ -v`
Expected: All existing tests still PASS

**Step 5: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py
git commit -m "feat(orchestrator): add --dry-run to install and uninstall commands"
```

---

### Task 14: Run All Tests Across All Packages

**Files:** None (verification only)

**Step 1: Run settings tests**

Run: `uv run pytest packages/settings/tests/ -v`
Expected: All PASS

**Step 2: Run core tests**

Run: `uv run pytest packages/core/tests/ -v`
Expected: All PASS

**Step 3: Run orchestrator tests**

Run: `uv run pytest packages/orchestrator/tests/ -v`
Expected: All PASS

**Step 4: Run effects tests**

Run: `uv run pytest packages/effects/tests/ -v`
Expected: All PASS (no changes to this package, regression check)

**Step 5: If any failures, fix and re-run before proceeding**

---

### Task 15: Final Commit and Summary

**Step 1: Verify git status is clean**

Run: `git status`
Expected: All dry-run changes committed in previous tasks

**Step 2: If any uncommitted changes remain, commit them**

```bash
git add -A
git commit -m "feat: complete dry-run implementation across all packages"
```

---

## File Summary

### New Files (7)
| File | Package | Purpose |
|------|---------|---------|
| `packages/settings/src/layered_settings/dry_run.py` | settings | DryRunBase + ValidationCheck |
| `packages/settings/tests/test_dry_run.py` | settings | DryRunBase tests |
| `packages/core/src/wallpaper_core/dry_run.py` | core | CoreDryRun |
| `packages/core/tests/test_dry_run.py` | core | CoreDryRun tests |
| `packages/core/tests/test_cli_dry_run.py` | core | CLI --dry-run tests |
| `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py` | orchestrator | OrchestratorDryRun |
| `packages/orchestrator/tests/test_dry_run.py` | orchestrator | OrchestratorDryRun tests |
| `packages/orchestrator/tests/test_cli_dry_run.py` | orchestrator | CLI --dry-run tests |

### Modified Files (5)
| File | Change |
|------|--------|
| `packages/settings/src/layered_settings/__init__.py` | Export DryRunBase, ValidationCheck |
| `packages/core/src/wallpaper_core/cli/process.py` | Add --dry-run + _resolve_command helper |
| `packages/core/src/wallpaper_core/cli/batch.py` | Add --dry-run to _run_batch and all 4 commands |
| `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py` | Add --dry-run to process commands |
| `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py` | Add --dry-run |
| `packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py` | Add --dry-run |
