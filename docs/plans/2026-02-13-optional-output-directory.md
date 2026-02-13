# Optional Output Directory Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make output directory optional with configurable defaults from layered settings, standardizing behavior across all process and batch commands.

**Architecture:** Wire to existing layered settings architecture (no new patterns). Add `core.output.default_dir` setting, change CLI signatures from positional to optional `-o/--output-dir` flag, add `ItemType` enum for type-safe path resolution, standardize output structure across all commands.

**Tech Stack:** Python 3.12, Pydantic, Typer, pytest, layered-settings

**Breaking Change:** Yes - no backward compatibility. Old positional syntax will break.

**Design Document:** See `docs/plans/2026-02-13-optional-output-directory-design.md`

---

## Phase 1: Settings & Schema

### Task 1.1: Add ItemType Enum

**Files:**
- Modify: `packages/core/src/wallpaper_core/config/schema.py`
- Test: `packages/core/tests/test_config_schema.py`

**Step 1: Write failing tests for ItemType enum**

Add to `packages/core/tests/test_config_schema.py`:

```python
from wallpaper_core.config.schema import ItemType


def test_item_type_enum_values():
    """ItemType has correct enum values."""
    assert ItemType.EFFECT.value == "effect"
    assert ItemType.COMPOSITE.value == "composite"
    assert ItemType.PRESET.value == "preset"


def test_item_type_subdir_names():
    """ItemType.subdir_name returns plural form."""
    assert ItemType.EFFECT.subdir_name == "effects"
    assert ItemType.COMPOSITE.subdir_name == "composites"
    assert ItemType.PRESET.subdir_name == "presets"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_config_schema.py::test_item_type_enum_values -v
uv run pytest packages/core/tests/test_config_schema.py::test_item_type_subdir_names -v
```

Expected: FAIL with "cannot import name 'ItemType'"

**Step 3: Implement ItemType enum**

Add to `packages/core/src/wallpaper_core/config/schema.py` (after imports, before Verbosity):

```python
from enum import Enum


class ItemType(str, Enum):
    """Type of wallpaper item for output path resolution."""

    EFFECT = "effect"
    COMPOSITE = "composite"
    PRESET = "preset"

    @property
    def subdir_name(self) -> str:
        """Get the plural subdirectory name for this item type."""
        return {
            ItemType.EFFECT: "effects",
            ItemType.COMPOSITE: "composites",
            ItemType.PRESET: "presets",
        }[self]
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_config_schema.py::test_item_type_enum_values -v
uv run pytest packages/core/tests/test_config_schema.py::test_item_type_subdir_names -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/config/schema.py packages/core/tests/test_config_schema.py
git commit -m "feat(core): add ItemType enum for output path resolution

Add ItemType enum with EFFECT, COMPOSITE, PRESET values and subdir_name
property for type-safe output directory structure.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 1.2: Add default_dir to OutputSettings

**Files:**
- Modify: `packages/core/src/wallpaper_core/config/schema.py`
- Test: `packages/core/tests/test_config_schema.py`

**Step 1: Write failing tests for default_dir**

Add to `packages/core/tests/test_config_schema.py`:

```python
from pathlib import Path
from wallpaper_core.config.schema import OutputSettings


def test_output_settings_has_default_dir():
    """OutputSettings includes default_dir field."""
    settings = OutputSettings()
    assert settings.default_dir == Path("./wallpapers-output")


def test_output_settings_default_dir_is_path():
    """default_dir is a Path object."""
    settings = OutputSettings(default_dir="~/custom")
    assert isinstance(settings.default_dir, Path)
    assert settings.default_dir == Path("~/custom")


def test_output_settings_validates_default_dir():
    """default_dir accepts string or Path."""
    settings1 = OutputSettings(default_dir="/absolute/path")
    assert settings1.default_dir == Path("/absolute/path")

    settings2 = OutputSettings(default_dir=Path("./relative"))
    assert settings2.default_dir == Path("./relative")
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_has_default_dir -v
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_default_dir_is_path -v
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_validates_default_dir -v
```

Expected: FAIL with "OutputSettings has no attribute 'default_dir'"

**Step 3: Add default_dir field to OutputSettings**

Modify `packages/core/src/wallpaper_core/config/schema.py` OutputSettings class:

```python
class OutputSettings(BaseModel):
    """Output and display settings."""

    verbosity: Verbosity = Field(
        default=Verbosity.NORMAL, description="Output verbosity level"
    )

    default_dir: Path = Field(
        default=Path("./wallpapers-output"),
        description="Default output directory when -o/--output-dir not specified",
    )

    @field_validator("default_dir", mode="before")
    @classmethod
    def convert_str_to_path(cls, v: str | Path) -> Path:
        """Convert string to Path if needed."""
        if isinstance(v, Path):
            return v
        return Path(v)
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_has_default_dir -v
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_default_dir_is_path -v
uv run pytest packages/core/tests/test_config_schema.py::test_output_settings_validates_default_dir -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/config/schema.py packages/core/tests/test_config_schema.py
git commit -m "feat(core): add default_dir to OutputSettings

Add default_dir field with Path validation for configurable default
output directory. Defaults to './wallpapers-output'.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 1.3: Add default to package settings.toml

**Files:**
- Modify: `packages/core/src/wallpaper_core/config/settings.toml`

**Step 1: Add default_dir to package settings**

Add to `packages/core/src/wallpaper_core/config/settings.toml` in `[output]` section:

```toml
[output]
verbosity = 1
default_dir = "./wallpapers-output"
```

**Step 2: Verify settings load correctly**

```bash
uv run python -c "from layered_settings import configure, get_config; from wallpaper_core.config.schema import CoreSettings; from pydantic import BaseModel; class C(BaseModel): core: CoreSettings; configure(C, 'wallpaper-effects'); cfg = get_config(); print(f'default_dir: {cfg.core.output.default_dir}')"
```

Expected: Output shows `default_dir: wallpapers-output`

**Step 3: Commit**

```bash
git add packages/core/src/wallpaper_core/config/settings.toml
git commit -m "feat(core): add default_dir to package settings

Set default output directory to './wallpapers-output' in package
defaults.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Path Resolution

### Task 2.1: Create resolve_output_path helper

**Files:**
- Create: `packages/core/src/wallpaper_core/cli/path_utils.py`
- Test: `packages/core/tests/test_path_resolution.py`

**Step 1: Write failing tests for path resolution**

Create `packages/core/tests/test_path_resolution.py`:

```python
"""Tests for output path resolution."""

from pathlib import Path

import pytest

from wallpaper_core.cli.path_utils import resolve_output_path
from wallpaper_core.config.schema import ItemType


def test_resolve_output_path_effect_not_flat():
    """Resolve effect output path with subdirectory."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wallpaper.jpg"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/wallpaper/effects/blur.jpg")


def test_resolve_output_path_effect_flat():
    """Resolve effect output path without subdirectory."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wallpaper.jpg"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=True,
    )
    assert result == Path("/out/wallpaper/blur.jpg")


def test_resolve_output_path_composite():
    """Resolve composite output path."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("photo.png"),
        item_name="dark",
        item_type=ItemType.COMPOSITE,
        flat=False,
    )
    assert result == Path("/out/photo/composites/dark.png")


def test_resolve_output_path_preset():
    """Resolve preset output path."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("image.jpg"),
        item_name="dark_vibrant",
        item_type=ItemType.PRESET,
        flat=False,
    )
    assert result == Path("/out/image/presets/dark_vibrant.jpg")


def test_resolve_output_path_no_extension_defaults_png():
    """Input without extension defaults to .png."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wallpaper"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/wallpaper/effects/blur.png")


def test_resolve_output_path_preserves_extension():
    """Output preserves input extension."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("image.webp"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/image/effects/blur.webp")
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_path_resolution.py -v
```

Expected: FAIL with "cannot import name 'resolve_output_path'"

**Step 3: Implement resolve_output_path**

Create `packages/core/src/wallpaper_core/cli/path_utils.py`:

```python
"""Utility functions for CLI path resolution."""

from pathlib import Path

from wallpaper_core.config.schema import ItemType


def resolve_output_path(
    output_dir: Path,
    input_file: Path,
    item_name: str,
    item_type: ItemType,
    flat: bool = False,
) -> Path:
    """Resolve output file path using standardized structure.

    Args:
        output_dir: Base output directory
        input_file: Input image file
        item_name: Name of effect/composite/preset
        item_type: Type of item (ItemType enum)
        flat: If True, skip type subdirectory

    Returns:
        Path: output_dir/input_stem/[type_subdir/]item_name.ext

    Examples:
        >>> resolve_output_path(Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=False)
        Path('/out/wall/effects/blur.jpg')

        >>> resolve_output_path(Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=True)
        Path('/out/wall/blur.jpg')
    """
    suffix = input_file.suffix or ".png"
    base_dir = output_dir / input_file.stem

    if flat:
        return base_dir / f"{item_name}{suffix}"
    else:
        return base_dir / item_type.subdir_name / f"{item_name}{suffix}"
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_path_resolution.py -v
```

Expected: PASS (all 6 tests)

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/path_utils.py packages/core/tests/test_path_resolution.py
git commit -m "feat(core): add resolve_output_path helper function

Add standardized output path resolution with type-safe ItemType enum
support. Handles flat and hierarchical directory structures.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: CLI - Process Commands

### Task 3.1: Update process effect command

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/process.py`
- Modify: `packages/core/tests/test_cli.py`

**Step 1: Delete obsolete tests**

In `packages/core/tests/test_cli.py`, identify and DELETE all tests that use old positional `output_file` syntax. These tests will be incompatible:

```bash
# Find tests to delete (for reference):
grep -n "output_file.*Argument" packages/core/tests/test_cli.py
```

Delete those test functions entirely.

**Step 2: Write new failing tests**

Add to `packages/core/tests/test_cli.py`:

```python
def test_process_effect_with_output_dir_creates_subdirectory(tmp_path, mock_executor):
    """Process effect with -o flag creates subdirectory structure."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")
    output_dir = tmp_path / "out"

    result = runner.invoke(app, [
        "process", "effect",
        str(input_file),
        "-o", str(output_dir),
        "--effect", "blur"
    ])

    assert result.exit_code == 0
    expected = output_dir / "test" / "effects" / "blur.jpg"
    # Verify execute was called with correct path
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args
    assert call_args[0][2] == expected  # output_path argument


def test_process_effect_without_output_uses_default(tmp_path, monkeypatch, mock_executor):
    """Process effect without -o uses settings default."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")

    result = runner.invoke(app, [
        "process", "effect",
        str(input_file),
        "--effect", "blur"
    ])

    assert result.exit_code == 0
    expected = tmp_path / "wallpapers-output" / "test" / "effects" / "blur.jpg"
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args
    assert call_args[0][2] == expected


def test_process_effect_with_flat_flag(tmp_path, mock_executor):
    """Process effect with --flat skips subdirectory."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")
    output_dir = tmp_path / "out"

    result = runner.invoke(app, [
        "process", "effect",
        str(input_file),
        "-o", str(output_dir),
        "--effect", "blur",
        "--flat"
    ])

    assert result.exit_code == 0
    expected = output_dir / "test" / "blur.jpg"
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args
    assert call_args[0][2] == expected
```

**Step 3: Add mock_executor fixture to conftest**

Add to `packages/core/tests/conftest.py`:

```python
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_executor(monkeypatch):
    """Mock CommandExecutor for CLI tests."""
    from wallpaper_core.engine.executor import CommandExecutor, ExecutionResult

    mock = MagicMock(spec=CommandExecutor)
    mock.execute.return_value = ExecutionResult(
        success=True,
        command="magick ...",
        stdout="",
        stderr="",
        return_code=0,
    )

    monkeypatch.setattr(
        "wallpaper_core.cli.process.CommandExecutor",
        lambda output: mock
    )
    return mock
```

**Step 4: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_effect_with_output_dir_creates_subdirectory -v
uv run pytest packages/core/tests/test_cli.py::test_process_effect_without_output_uses_default -v
uv run pytest packages/core/tests/test_cli.py::test_process_effect_with_flat_flag -v
```

Expected: FAIL (tests exist but command signature is wrong)

**Step 5: Update apply_effect signature and implementation**

In `packages/core/src/wallpaper_core/cli/process.py`, update the `apply_effect` function:

```python
from pathlib import Path
from typing import Annotated

import typer

from wallpaper_core.cli.path_utils import resolve_output_path
from wallpaper_core.config.schema import CoreSettings, ItemType, Verbosity
from wallpaper_core.dry_run import CoreDryRun
from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_core.engine.chain import ChainExecutor
from wallpaper_core.engine.executor import CommandExecutor


@app.command("effect")
def apply_effect(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    effect: Annotated[str, typer.Option("-e", "--effect", help="Effect to apply")],
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure (no type subdirectory)")
    ] = False,
    blur: Annotated[str | None, typer.Option("--blur", help="Blur geometry")] = None,
    brightness: Annotated[int | None, typer.Option("--brightness")] = None,
    contrast: Annotated[int | None, typer.Option("--contrast")] = None,
    saturation: Annotated[int | None, typer.Option("--saturation")] = None,
    strength: Annotated[int | None, typer.Option("--strength")] = None,
    color: Annotated[str | None, typer.Option("--color")] = None,
    opacity: Annotated[int | None, typer.Option("--opacity")] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Apply a single effect to an image.

    The output directory can be specified with -o/--output-dir or omitted
    to use the default from settings (./wallpapers-output by default).

    By default, creates: <output_dir>/<input_name>/effects/<effect_name>.ext
    With --flat: <output_dir>/<input_name>/<effect_name>.ext
    """
    output = ctx.obj["output"]
    config = ctx.obj["config"]
    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir from settings if not provided
    if output_dir is None:
        output_dir = settings.output.default_dir

    # Build output file path
    output_file = resolve_output_path(
        output_dir=output_dir,
        input_file=input_file,
        item_name=effect,
        item_type=ItemType.EFFECT,
        flat=flat,
    )

    # Build params from CLI options
    params: dict[str, str | int] = {}
    if blur is not None:
        params["blur"] = blur
    if brightness is not None:
        params["brightness"] = brightness
    if contrast is not None:
        params["contrast"] = contrast
    if saturation is not None:
        params["saturation"] = saturation
    if strength is not None:
        params["strength"] = strength
    if color is not None:
        params["color"] = color
    if opacity is not None:
        params["opacity"] = opacity

    if dry_run:
        dry = CoreDryRun(console=output.console)

        # Validation checks (non-fatal in dry-run mode)
        checks = dry.validate_core(
            input_path=input_file,
            output_path=output_file,
            item_name=effect,
            item_type="effect",
            config=config,
        )

        # Resolve command if effect exists
        effect_def = config.effects.get(effect)
        if effect_def is not None:
            chain_executor = ChainExecutor(config, None)
            final_params = chain_executor._get_params_with_defaults(effect, params)
            resolved = _resolve_command(
                effect_def.command, input_file, output_file, final_params
            )
        else:
            resolved = f"# Cannot resolve: unknown effect '{effect}'"

        if output.verbosity == Verbosity.QUIET:
            output.console.print(resolved)
        else:
            dry.render_process(
                item_name=effect,
                item_type="effect",
                input_path=input_file,
                output_path=output_file,
                params=params,
                resolved_command=resolved,
                command_template=effect_def.command if effect_def else None,
            )
            dry.render_validation(checks)

        raise typer.Exit(0)

    # Normal execution path
    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    effect_def = config.effects.get(effect)
    if effect_def is None:
        output.error(f"Unknown effect: {effect}")
        output.info("Use 'show effects' to list available effects")
        raise typer.Exit(1)

    # Execute
    executor = CommandExecutor(output)
    chain_executor = ChainExecutor(config, output)
    final_params = chain_executor._get_params_with_defaults(effect, params)

    output.verbose(f"Applying effect '{effect}' to {input_file}")
    result = executor.execute(effect_def.command, input_file, output_file, final_params)

    if result.success:
        output.success(f"Created {output_file}")
    else:
        output.error(f"Failed: {result.stderr}")
        raise typer.Exit(1)
```

**Step 6: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_effect_with_output_dir_creates_subdirectory -v
uv run pytest packages/core/tests/test_cli.py::test_process_effect_without_output_uses_default -v
uv run pytest packages/core/tests/test_cli.py::test_process_effect_with_flat_flag -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/process.py packages/core/tests/test_cli.py packages/core/tests/conftest.py
git commit -m "feat(core): update process effect to use optional output directory

BREAKING CHANGE: Replace positional output_file with optional -o/--output-dir.
Add --flat flag for output structure control. Uses settings default when
output not specified.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 3.2: Update process composite command

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/process.py`
- Modify: `packages/core/tests/test_cli.py`

**Step 1: Write failing tests**

Add to `packages/core/tests/test_cli.py`:

```python
def test_process_composite_with_output_dir(tmp_path, mock_executor):
    """Process composite with -o flag."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")
    output_dir = tmp_path / "out"

    result = runner.invoke(app, [
        "process", "composite",
        str(input_file),
        "-o", str(output_dir),
        "--composite", "dark"
    ])

    assert result.exit_code == 0
    expected = output_dir / "test" / "composites" / "dark.jpg"
    mock_executor.execute_chain.assert_called_once()


def test_process_composite_without_output_uses_default(tmp_path, monkeypatch, mock_executor):
    """Process composite without -o uses default."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")

    result = runner.invoke(app, [
        "process", "composite",
        str(input_file),
        "--composite", "dark"
    ])

    assert result.exit_code == 0


def test_process_composite_with_flat_flag(tmp_path, mock_executor):
    """Process composite with --flat."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")
    output_dir = tmp_path / "out"

    result = runner.invoke(app, [
        "process", "composite",
        str(input_file),
        "-o", str(output_dir),
        "--composite", "dark",
        "--flat"
    ])

    assert result.exit_code == 0
    expected = output_dir / "test" / "dark.jpg"
```

**Step 2: Update mock_executor fixture**

Update `packages/core/tests/conftest.py` to mock ChainExecutor too:

```python
@pytest.fixture
def mock_executor(monkeypatch):
    """Mock CommandExecutor and ChainExecutor for CLI tests."""
    from wallpaper_core.engine.executor import CommandExecutor, ExecutionResult

    mock_cmd = MagicMock(spec=CommandExecutor)
    mock_cmd.execute.return_value = ExecutionResult(
        success=True,
        command="magick ...",
        stdout="",
        stderr="",
        return_code=0,
    )

    mock_chain = MagicMock()
    mock_chain.execute_chain.return_value = ExecutionResult(
        success=True,
        command="chain: ...",
        stdout="",
        stderr="",
        return_code=0,
    )

    monkeypatch.setattr(
        "wallpaper_core.cli.process.CommandExecutor",
        lambda output: mock_cmd
    )
    monkeypatch.setattr(
        "wallpaper_core.cli.process.ChainExecutor",
        lambda config, output: mock_chain
    )

    mock_cmd.execute_chain = mock_chain.execute_chain
    return mock_cmd
```

**Step 3: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_composite_with_output_dir -v
```

Expected: FAIL

**Step 4: Update apply_composite function**

In `packages/core/src/wallpaper_core/cli/process.py`, update `apply_composite`:

```python
@app.command("composite")
def apply_composite(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    composite: Annotated[str, typer.Option("-c", "--composite", help="Composite")],
    flat: Annotated[
        bool, typer.Option("--flat", help="Flat output structure")
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Apply a composite effect (chain) to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]
    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    # Build output path
    output_file = resolve_output_path(
        output_dir=output_dir,
        input_file=input_file,
        item_name=composite,
        item_type=ItemType.COMPOSITE,
        flat=flat,
    )

    # [Rest of function similar to before, using output_file instead of positional arg]
    # ... (dry_run handling, validation, execution)
```

**Step 5: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_composite_with_output_dir -v
uv run pytest packages/core/tests/test_cli.py::test_process_composite_without_output_uses_default -v
uv run pytest packages/core/tests/test_cli.py::test_process_composite_with_flat_flag -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/process.py packages/core/tests/test_cli.py packages/core/tests/conftest.py
git commit -m "feat(core): update process composite to use optional output directory

BREAKING CHANGE: Replace positional output_file with -o/--output-dir.
Uses settings default when not specified.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 3.3: Update process preset command

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/process.py`
- Modify: `packages/core/tests/test_cli.py`

**Step 1: Write failing tests**

Add to `packages/core/tests/test_cli.py`:

```python
def test_process_preset_with_output_dir(tmp_path, mock_executor):
    """Process preset with -o flag."""
    # Similar structure to composite tests

def test_process_preset_without_output_uses_default(tmp_path, monkeypatch, mock_executor):
    """Process preset without -o uses default."""
    # Similar structure

def test_process_preset_with_flat_flag(tmp_path, mock_executor):
    """Process preset with --flat."""
    # Similar structure
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_preset_with_output_dir -v
```

Expected: FAIL

**Step 3: Update apply_preset function**

In `packages/core/src/wallpaper_core/cli/process.py`, update `apply_preset` with same pattern as composite (using ItemType.PRESET).

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_cli.py::test_process_preset_with_output_dir -v
uv run pytest packages/core/tests/test_cli.py::test_process_preset_without_output_uses_default -v
uv run pytest packages/core/tests/test_cli.py::test_process_preset_with_flat_flag -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/process.py packages/core/tests/test_cli.py
git commit -m "feat(core): update process preset to use optional output directory

BREAKING CHANGE: Replace positional output_file with -o/--output-dir.
Completes process commands standardization.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: CLI - Batch Commands

### Task 4.1: Update batch effects command

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/batch.py`
- Modify: `packages/core/tests/test_cli.py`

**Step 1: Write failing test for default output**

Add to `packages/core/tests/test_cli.py`:

```python
def test_batch_effects_without_output_uses_default(tmp_path, monkeypatch):
    """Batch effects without -o uses settings default."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    monkeypatch.chdir(tmp_path)

    input_file = tmp_path / "test.jpg"
    input_file.write_text("fake image")

    # Mock BatchGenerator to avoid actual execution
    # ... (add mocking)

    result = runner.invoke(app, [
        "batch", "effects",
        str(input_file)
    ])

    assert result.exit_code == 0
    # Verify default path was used
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest packages/core/tests/test_cli.py::test_batch_effects_without_output_uses_default -v
```

Expected: FAIL (missing required positional)

**Step 3: Update batch_effects signature**

In `packages/core/src/wallpaper_core/cli/batch.py`:

```python
@app.command("effects")
def batch_effects(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Generate all effects for an image."""
    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    _run_batch(ctx, input_file, output_dir, "effects", parallel, strict, flat, dry_run)
```

**Step 4: Run test to verify it passes**

```bash
uv run pytest packages/core/tests/test_cli.py::test_batch_effects_without_output_uses_default -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/batch.py packages/core/tests/test_cli.py
git commit -m "feat(core): update batch effects to use optional output directory

BREAKING CHANGE: Replace positional output_dir with -o/--output-dir.
Uses settings default when not specified.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 4.2: Update remaining batch commands

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/batch.py`
- Modify: `packages/core/tests/test_cli.py`

**Step 1: Write failing tests for batch composites, presets, all**

Add tests similar to batch_effects for:
- `test_batch_composites_without_output_uses_default`
- `test_batch_presets_without_output_uses_default`
- `test_batch_all_without_output_uses_default`

**Step 2: Run tests to verify they fail**

```bash
uv run pytest packages/core/tests/test_cli.py -k "batch" -v
```

Expected: FAIL for new tests

**Step 3: Update batch_composites, batch_presets, batch_all**

Apply same pattern as batch_effects to:
- `batch_composites()`
- `batch_presets()`
- `batch_all()`

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/core/tests/test_cli.py -k "batch" -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/batch.py packages/core/tests/test_cli.py
git commit -m "feat(core): update all batch commands to use optional output directory

BREAKING CHANGE: Make output_dir optional for batch composites, presets, all.
All batch commands now use -o/--output-dir with settings defaults.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 4.3: Update BatchGenerator to use ItemType enum

**Files:**
- Modify: `packages/core/src/wallpaper_core/engine/batch.py`
- Modify: `packages/core/tests/test_engine_batch.py`

**Step 1: Write failing test for enum usage**

Add to `packages/core/tests/test_engine_batch.py`:

```python
from wallpaper_core.config.schema import ItemType

def test_batch_generator_get_output_path_uses_enum():
    """_get_output_path uses ItemType enum."""
    from wallpaper_core.engine.batch import BatchGenerator

    generator = BatchGenerator(config=mock_config, output=None)

    path = generator._get_output_path(
        base_dir=Path("/out/wallpaper"),
        name="blur",
        item_type=ItemType.EFFECT,  # Use enum not string
        input_path=Path("test.jpg"),
        flat=False,
    )

    assert path == Path("/out/wallpaper/effects/blur.jpg")
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest packages/core/tests/test_engine_batch.py::test_batch_generator_get_output_path_uses_enum -v
```

Expected: FAIL (signature mismatch)

**Step 3: Update BatchGenerator._get_output_path**

In `packages/core/src/wallpaper_core/engine/batch.py`:

```python
from wallpaper_core.config.schema import ItemType

def _get_output_path(
    self,
    base_dir: Path,
    name: str,
    item_type: ItemType,  # Changed from str
    input_path: Path,
    flat: bool,
) -> Path:
    """Get output path for an item."""
    suffix = input_path.suffix or ".png"
    if flat:
        return base_dir / f"{name}{suffix}"
    else:
        return base_dir / item_type.subdir_name / f"{name}{suffix}"
```

**Step 4: Update all callers to use ItemType**

Update calls to `_get_output_path` in batch methods to use ItemType enum values.

**Step 5: Run test to verify it passes**

```bash
uv run pytest packages/core/tests/test_engine_batch.py::test_batch_generator_get_output_path_uses_enum -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/engine/batch.py packages/core/tests/test_engine_batch.py
git commit -m "refactor(core): update BatchGenerator to use ItemType enum

Replace string item_type with type-safe ItemType enum for consistency
with process commands.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 5: Orchestrator Commands

### Task 5.1: Update orchestrator process commands

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`
- Modify: `packages/orchestrator/tests/test_cli_process.py`

**Step 1: Delete obsolete orchestrator tests**

In `packages/orchestrator/tests/test_cli_process.py`, delete tests using old positional syntax.

**Step 2: Write new failing tests**

Add tests for orchestrator process commands with new syntax (similar pattern to core tests).

**Step 3: Update process_effect, process_composite, process_preset in orchestrator**

Apply same pattern as core (optional -o/--output-dir, --flat flag, resolve from settings).

**Step 4: Run tests to verify they pass**

```bash
uv run pytest packages/orchestrator/tests/test_cli_process.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py packages/orchestrator/tests/test_cli_process.py
git commit -m "feat(orchestrator): update process commands to use optional output directory

BREAKING CHANGE: Orchestrator process commands now use -o/--output-dir
with settings defaults, matching core behavior.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 5.2: Update orchestrator batch commands

**Files:**
- Modify: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`
- Modify: `packages/orchestrator/tests/test_cli_integration.py`

**Step 1: Write failing tests for batch commands**

**Step 2: Update batch command callbacks in orchestrator**

Update `batch_callback()` to get settings and pass to core commands.

**Step 3: Run tests to verify they pass**

**Step 4: Commit**

```bash
git add packages/orchestrator/src/wallpaper_orchestrator/cli/main.py packages/orchestrator/tests/test_cli_integration.py
git commit -m "feat(orchestrator): update batch commands to use optional output directory

BREAKING CHANGE: Orchestrator batch commands now use -o/--output-dir.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 6: Smoke Tests

### Task 6.1: Update smoke test commands

**Files:**
- Modify: `tests/smoke/run-smoke-tests.sh`

**Step 1: Update all process command invocations**

Search and replace in smoke test file:

```bash
# Find all process commands (for reference):
grep -n "wallpaper-core process" tests/smoke/run-smoke-tests.sh | head -20

# Update pattern (manual edits required):
# OLD: wallpaper-core process effect "$IMAGE" "$OUTPUT_FILE" --effect blur
# NEW: wallpaper-core process effect "$IMAGE" -o "$OUTPUT_DIR" --effect blur
```

Update approximately 50+ command invocations.

**Step 2: Update output validation checks**

Update checks to verify correct output structure:

```bash
# OLD: [ -f "$OUTPUT_FILE" ]
# NEW: [ -f "$OUTPUT_DIR/$(basename "$IMAGE" .jpg)/effects/blur.jpg" ]
```

**Step 3: Add new smoke tests for defaults and --flat**

Add new test sections:
- Process commands without -o (uses default)
- Process commands with --flat
- Batch commands without -o

**Step 4: Run smoke tests**

```bash
./tests/smoke/run-smoke-tests.sh /path/to/test-image.jpg
```

Expected: ALL PASS

**Step 5: Commit**

```bash
git add tests/smoke/run-smoke-tests.sh
git commit -m "test: update smoke tests for optional output directory

Update ~50+ command invocations to new -o/--output-dir syntax.
Update output validation for new directory structure.
Add tests for default output and --flat flag.

BREAKING CHANGE: Old positional syntax no longer works.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 7: Documentation

### Task 7.1: Update README

**Files:**
- Modify: `README.md`

**Step 1: Update all example commands**

Replace all process/batch examples with new syntax.

**Step 2: Add configuration section**

Add documentation for `core.output.default_dir` setting.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README for optional output directory

Update all examples to use -o/--output-dir syntax.
Document core.output.default_dir configuration.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 7.2: Create migration guide

**Files:**
- Create: `docs/MIGRATION.md`

**Step 1: Write migration guide**

Create comprehensive migration guide showing old vs new syntax.

**Step 2: Commit**

```bash
git add docs/MIGRATION.md
git commit -m "docs: add migration guide for optional output directory

Document breaking changes and migration path from old positional
syntax to new -o/--output-dir flag.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

### Task 7.3: Update CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Add breaking changes entry**

Document all breaking changes in unreleased section.

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for optional output directory release

Document breaking changes, new features, and migration requirements.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 8: Final Validation

### Task 8.1: Run full test suite

**Step 1: Run all unit tests**

```bash
uv run pytest packages/core/tests/ -v
uv run pytest packages/orchestrator/tests/ -v
uv run pytest packages/settings/tests/ -v
uv run pytest packages/effects/tests/ -v
```

Expected: ALL PASS

**Step 2: Run smoke tests**

```bash
./tests/smoke/run-smoke-tests.sh /path/to/test-image.jpg
```

Expected: ALL PASS

**Step 3: Manual testing**

Test key scenarios:
- Process effect without -o (uses default)
- Process effect with -o (uses specified)
- Process effect with --flat
- Batch effects without -o
- Settings overrides (project, user)

---

### Task 8.2: Create final commit

**Step 1: Review all changes**

```bash
git log --oneline dev..HEAD
git diff dev..HEAD --stat
```

**Step 2: Create summary commit (optional)**

If needed, create a summary commit tying everything together.

---

## Execution Complete

**Total Tasks:** 8 phases, ~25 tasks
**Estimated Time:** 4-6 hours (TDD adds time but ensures correctness)
**Breaking Changes:** Yes - document thoroughly

**Next Steps:**
1. Choose execution approach (subagent-driven or parallel session)
2. Execute plan task-by-task
3. Code review after major phases
4. Final validation before merge
