# Phase 2: Layered Effects Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate layered-effects package into wallpaper-core CLI to enable 3-layer configuration (package/project/user) for effects.

**Architecture:** Remove effects from CoreOnlyConfig, initialize layered-effects at module level in main.py, add comprehensive error handling for configuration loading.

**Tech Stack:** Python 3.12, layered-effects, layered-settings, Pydantic, Typer, pytest

---

## Task 1: Add Package Effects Path Helper

**Files:**
- Modify: `packages/core/src/wallpaper_core/effects/__init__.py:1-35`
- Test: `packages/core/tests/test_effects_integration.py` (create)

**Step 1: Write failing test for helper function**

Create `packages/core/tests/test_effects_integration.py`:

```python
"""Test layered-effects integration with wallpaper-core."""
from pathlib import Path


class TestPackageEffects:
    def test_get_package_effects_file_returns_valid_path(self):
        """Should return existing path to effects.yaml."""
        from wallpaper_core.effects import get_package_effects_file

        path = get_package_effects_file()
        assert isinstance(path, Path)
        assert path.exists()
        assert path.name == "effects.yaml"
        assert "wallpaper_core" in str(path)

    def test_package_effects_file_is_valid_yaml(self):
        """Package effects.yaml should be valid and loadable."""
        import yaml
        from wallpaper_core.effects import get_package_effects_file

        path = get_package_effects_file()
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data["version"] == "1.0"
        assert "effects" in data
        assert "parameter_types" in data
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest packages/core/tests/test_effects_integration.py::TestPackageEffects::test_get_package_effects_file_returns_valid_path -v`

Expected: FAIL with "ImportError: cannot import name 'get_package_effects_file'"

**Step 3: Implement helper function**

In `packages/core/src/wallpaper_core/effects/__init__.py`, add after imports and before SchemaRegistry.register():

```python
def get_package_effects_file() -> Path:
    """Get the path to the package's default effects.yaml file.

    Returns:
        Path to effects.yaml in the wallpaper_core.effects package.
    """
    from importlib import resources
    return Path(resources.files("wallpaper_core.effects") / "effects.yaml")
```

Update `__all__` at the end:

```python
__all__ = [
    "ChainStep",
    "CompositeEffect",
    "Effect",
    "EffectsConfig",
    "get_package_effects_file",  # NEW
    "ParameterDefinition",
    "ParameterType",
    "Preset",
]
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_effects_integration.py::TestPackageEffects -v`

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/effects/__init__.py packages/core/tests/test_effects_integration.py
git commit -m "feat(core): add get_package_effects_file helper

Add helper function to get package effects.yaml path using
importlib.resources for robust package data access.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Update CoreOnlyConfig to Remove Effects

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/main.py:15-20`
- Test: Manual verification (no behavioral change yet)

**Step 1: Remove effects field from CoreOnlyConfig**

In `packages/core/src/wallpaper_core/cli/main.py`, modify class at line 15:

```python
class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    # effects: EffectsConfig  # REMOVED - now handled by layered-effects
```

**Step 2: Verify no immediate breakage**

Run: `uv run pytest packages/core/tests/ -k "not test_effects" -x`

Expected: Tests may fail on config.effects access, which is expected. We'll fix in next tasks.

**Step 3: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/main.py
git commit -m "refactor(core): remove effects from CoreOnlyConfig

Effects now loaded via layered-effects instead of
layered-settings SchemaRegistry.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Initialize Layered Effects in Main

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/main.py:1-24`
- Test: Manual verification with CLI

**Step 1: Add imports**

At top of `packages/core/src/wallpaper_core/cli/main.py`, add to imports:

```python
from pathlib import Path
from layered_effects import configure as configure_effects, load_effects
from layered_effects.errors import EffectsError, EffectsLoadError, EffectsValidationError
from wallpaper_core.effects import get_package_effects_file
```

**Step 2: Add layered-effects initialization**

After line 23 (`configure(CoreOnlyConfig, app_name="wallpaper-effects")`), add:

```python
# Configure layered_effects for effects configuration
configure_effects(
    package_effects_file=get_package_effects_file(),
    project_root=Path.cwd()
)
```

**Step 3: Verify initialization doesn't crash**

Run: `uv run wallpaper-core version`

Expected: Should print version without errors

**Step 4: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/main.py
git commit -m "feat(core): initialize layered-effects at module level

Configure layered-effects system alongside layered-settings
for 3-layer effects configuration (package/project/user).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Add Comprehensive Error Handling

**Files:**
- Modify: `packages/core/src/wallpaper_core/cli/main.py:49-77`
- Test: `packages/core/tests/test_cli_effects_loading.py` (create)

**Step 1: Write tests for error handling**

Create `packages/core/tests/test_cli_effects_loading.py`:

```python
"""Test CLI properly loads and uses layered effects."""
from pathlib import Path
from typer.testing import CliRunner
from wallpaper_core.cli.main import app

runner = CliRunner()


def test_cli_shows_package_effects():
    """CLI should show package default effects."""
    result = runner.invoke(app, ["show", "effects"])
    assert result.exit_code == 0
    assert "blur" in result.stdout
    assert "brightness" in result.stdout


def test_cli_shows_composites():
    """CLI should show composites from effects config."""
    result = runner.invoke(app, ["show", "composites"])
    assert result.exit_code == 0
    assert "blackwhite-blur" in result.stdout


def test_cli_shows_presets():
    """CLI should show presets from effects config."""
    result = runner.invoke(app, ["show", "presets"])
    assert result.exit_code == 0
    assert "dark_blur" in result.stdout


def test_cli_error_on_invalid_user_effects(tmp_path, monkeypatch):
    """CLI should show helpful error for invalid user config."""
    user_config = tmp_path / "wallpaper-effects-generator"
    user_config.mkdir()
    (user_config / "effects.yaml").write_text("invalid: yaml: content:")

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["show", "effects"])
    assert result.exit_code == 1
    assert ("Failed to load" in result.stdout or
            "Failed to load" in str(result.exception) if result.exception else False)
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest packages/core/tests/test_cli_effects_loading.py -v`

Expected: Tests fail because effects not loaded in main() callback yet

**Step 3: Update main() callback with error handling**

In `packages/core/src/wallpaper_core/cli/main.py`, replace the main() callback (starting at line 49):

```python
@app.callback()
def main(
    ctx: typer.Context,
    quiet: Annotated[
        bool,
        typer.Option("-q", "--quiet", help="Quiet mode (errors only)"),
    ] = False,
    verbose: Annotated[
        int,
        typer.Option(
            "-v", "--verbose", count=True, help="Verbose mode (-v or -vv for debug)"
        ),
    ] = 0,
) -> None:
    """Wallpaper Effects Processor - Apply ImageMagick effects to images."""
    # Get core settings from layered_settings
    config_obj = get_config()

    # Get verbosity early for error output
    verbosity = _get_verbosity(quiet, verbose)
    output = RichOutput(verbosity)

    # Load effects configuration with comprehensive error handling
    try:
        effects_config = load_effects()
    except EffectsLoadError as e:
        output.error(f"[bold red]Failed to load effects configuration[/bold red]")
        output.error(f"Layer: {getattr(e, 'layer', 'unknown')}")
        output.error(f"File: {e.file_path}")
        output.error(f"Reason: {e.reason}")
        raise typer.Exit(1)
    except EffectsValidationError as e:
        output.error(f"[bold red]Effects configuration validation failed[/bold red]")
        output.error(f"Layer: {e.layer or 'merged'}")
        output.error(f"Problem: {e.message}")
        output.newline()
        output.error("[dim]Check your effects.yaml for:[/dim]")
        output.error("  • Undefined parameter types referenced in effects")
        output.error("  • Missing required fields (description, command)")
        output.error("  • Invalid YAML syntax")
        raise typer.Exit(1)
    except EffectsError as e:
        output.error(f"[bold red]Effects error:[/bold red] {e}")
        raise typer.Exit(1)

    # Store context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbosity
    ctx.obj["output"] = output
    ctx.obj["config"] = effects_config  # Changed from config_obj.effects
    ctx.obj["settings"] = config_obj.core
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_cli_effects_loading.py -v`

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/main.py packages/core/tests/test_cli_effects_loading.py
git commit -m "feat(core): add comprehensive effects loading error handling

Load effects via layered-effects with detailed error messages:
- Show which layer failed (package/project/user)
- Display file path and specific error reason
- Provide actionable suggestions for fixing issues

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Remove SchemaRegistry for Effects

**Files:**
- Modify: `packages/core/src/wallpaper_core/effects/__init__.py:17-24`

**Step 1: Remove SchemaRegistry.register() call**

In `packages/core/src/wallpaper_core/effects/__init__.py`, delete lines 17-24:

```python
# DELETE THESE LINES:
# Register EffectsConfig with layered_settings
# effects.yaml is in the same directory as this file
_effects_dir = Path(__file__).parent
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_effects_dir / "effects.yaml",
)
```

Also remove unused imports if present:
- Remove `from layered_settings import SchemaRegistry` if only used for effects
- Remove `_effects_dir = Path(__file__).parent` line

**Step 2: Verify tests still pass**

Run: `uv run pytest packages/core/tests/test_effects_integration.py packages/core/tests/test_cli_effects_loading.py -v`

Expected: PASS (6 tests total)

**Step 3: Commit**

```bash
git add packages/core/src/wallpaper_core/effects/__init__.py
git commit -m "refactor(core): remove SchemaRegistry for effects

Effects now loaded exclusively via layered-effects package.
SchemaRegistry still used for core settings via layered-settings.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Add Layered Configuration Unit Tests

**Files:**
- Modify: `packages/core/tests/test_effects_integration.py:1-end`

**Step 1: Add comprehensive configuration tests**

In `packages/core/tests/test_effects_integration.py`, add after TestPackageEffects class:

```python
import pytest
from layered_effects import configure, load_effects, _reset


class TestLayeredEffectsConfiguration:
    def setup_method(self):
        """Reset layered_effects state before each test."""
        _reset()

    def test_loads_package_defaults_only(self, tmp_path):
        """Should work with only package layer."""
        from wallpaper_core.effects import get_package_effects_file

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path  # Empty directory
        )
        config = load_effects()

        # Should have all package defaults
        assert "blur" in config.effects
        assert "brightness" in config.effects
        assert "blackwhite-blur" in config.composites

    def test_project_effects_extend_package(self, tmp_path):
        """Project effects should add to package defaults."""
        from wallpaper_core.effects import get_package_effects_file

        # Create project effects.yaml
        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
effects:
  custom_project:
    description: "Project custom effect"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )
        config = load_effects()

        # Should have both package and project effects
        assert "blur" in config.effects  # Package
        assert "custom_project" in config.effects  # Project

    def test_user_effects_override_package(self, tmp_path, monkeypatch):
        """User effects should override package defaults."""
        from wallpaper_core.effects import get_package_effects_file

        # Create user effects.yaml
        user_config = tmp_path / "wallpaper-effects-generator"
        user_config.mkdir()
        user_effects = user_config / "effects.yaml"
        user_effects.write_text("""
version: "1.0"
effects:
  blur:
    description: "My custom blur"
    command: "convert $INPUT -blur 0x50 $OUTPUT"
    parameters: {}
""")

        # Point to test user config
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )
        config = load_effects()

        # Blur should be overridden
        assert config.effects["blur"].description == "My custom blur"
        assert "0x50" in config.effects["blur"].command

    def test_parameter_types_merge_across_layers(self, tmp_path):
        """Parameter types from all layers should be available."""
        from wallpaper_core.effects import get_package_effects_file

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
parameter_types:
  custom_range:
    type: integer
    min: 0
    max: 100
    default: 50
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )
        config = load_effects()

        # Should have both package and project parameter types
        assert "blur_geometry" in config.parameter_types  # Package
        assert "custom_range" in config.parameter_types  # Project


class TestErrorHandling:
    def setup_method(self):
        _reset()

    def test_invalid_yaml_raises_load_error(self, tmp_path):
        """Invalid YAML should raise EffectsLoadError."""
        from layered_effects.errors import EffectsLoadError
        from wallpaper_core.effects import get_package_effects_file

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("invalid: yaml: content:")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )

        with pytest.raises(EffectsLoadError):
            load_effects()

    def test_validation_error_shows_helpful_message(self, tmp_path):
        """Validation errors should have helpful context."""
        from layered_effects.errors import EffectsValidationError
        from wallpaper_core.effects import get_package_effects_file

        project_effects = tmp_path / "effects.yaml"
        project_effects.write_text("""
version: "1.0"
effects:
  bad_effect:
    description: "Missing command field"
    parameters: {}
""")

        configure(
            package_effects_file=get_package_effects_file(),
            project_root=tmp_path
        )

        with pytest.raises(EffectsValidationError) as exc_info:
            load_effects()

        # Should mention what's wrong
        assert "command" in str(exc_info.value).lower()

    def test_missing_package_effects_fails(self, tmp_path):
        """Should fail if package effects.yaml doesn't exist."""
        from layered_effects.errors import EffectsLoadError

        fake_package = tmp_path / "nonexistent.yaml"

        configure(
            package_effects_file=fake_package,
            project_root=tmp_path
        )

        with pytest.raises(EffectsLoadError):
            load_effects()
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest packages/core/tests/test_effects_integration.py -v`

Expected: PASS (11 tests total: 2 package + 4 configuration + 3 error handling + 2 CLI)

**Step 3: Commit**

```bash
git add packages/core/tests/test_effects_integration.py
git commit -m "test(core): add comprehensive layered effects tests

Test coverage for:
- Package-only configuration
- Project effects extending package
- User effects overriding defaults
- Parameter type merging
- Error handling for invalid YAML and validation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Run Integration Test Suite

**Files:**
- None (verification only)

**Step 1: Run full test suite**

Run: `uv run pytest packages/core/tests/ -v`

Expected: All core tests pass

**Step 2: Run integration script**

From project root:

Run: `./tools/dev/test-all-commands.sh ~/Downloads/wallpaper.jpg`

Expected: All 29 tests pass (including the 5 layered effects tests that were previously failing)

**Step 3: Verify specific layered effects tests**

Check output for:
- ✓ User config custom effect loaded
- ✓ User config effect override applied
- ✓ Project-level effects loaded
- ✓ User custom effect can be processed
- ✓ Project effect can be processed

**Step 4: Document results**

If any tests fail, investigate and fix before proceeding. If all pass, ready for final commit.

---

## Task 8: Update Design Document Status

**Files:**
- Modify: `docs/plans/2026-02-05-phase2-layered-effects-integration.md:4`

**Step 1: Update status in design document**

Change line 4 from:
```markdown
**Status:** Approved
```

To:
```markdown
**Status:** Implemented
```

**Step 2: Commit**

```bash
git add docs/plans/2026-02-05-phase2-layered-effects-integration.md
git commit -m "docs: mark Phase 2 integration as implemented

All tests passing:
- 11 unit tests for layered effects integration
- 4 CLI loading tests
- 29/29 integration tests (5 layered effects tests now passing)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Final Verification and Completion

**Files:**
- Create: `phase2-complete.txt`

**Step 1: Create completion marker**

Create `phase2-complete.txt` at project root:

```
Phase 2: Layered Effects Integration - Complete
================================================

Date: 2026-02-05
Branch: feature/phase2-integration

Summary
-------
Successfully integrated layered-effects package into wallpaper-core CLI,
enabling 3-layer configuration (package/project/user) for effects.

Test Results
------------
Core Unit Tests: 11/11 passing
CLI Loading Tests: 4/4 passing
Integration Tests: 29/29 passing (including 5 layered effects tests)

Changes Made
------------
1. Added get_package_effects_file() helper to effects module
2. Removed effects field from CoreOnlyConfig
3. Initialized layered-effects at module level in main.py
4. Added comprehensive error handling for effects loading
5. Removed SchemaRegistry registration for effects
6. Added 11 new unit tests for integration
7. Verified all integration tests pass

Key Features
------------
- Users can define custom effects in ~/.config/wallpaper-effects-generator/effects.yaml
- Projects can have local effects.yaml that extend package defaults
- User effects can override package defaults
- Clear, actionable error messages for configuration issues
- Deep merge across all three layers (package/project/user)

Breaking Changes
----------------
For developers importing wallpaper-core:
- CoreOnlyConfig no longer has effects field
- Must use layered_effects.load_effects() directly

For CLI users: None (transparent change)

Next Steps
----------
Ready for code review and merge to master.
```

**Step 2: Commit completion marker**

```bash
git add phase2-complete.txt
git commit -m "docs: mark Phase 2 integration complete

Integration verified with all tests passing.
Layered effects system fully operational.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

**Step 3: Show summary**

Display final status:
- Total commits: 8
- Tests added: 15 (11 unit + 4 CLI)
- Tests passing: 29/29 integration tests
- Ready for merge

---

## Success Criteria

✓ All 11 new unit tests pass
✓ All 4 CLI loading tests pass
✓ All 29 integration tests pass (especially 5 layered effects tests)
✓ `wallpaper-core show effects` displays effects
✓ User can create `~/.config/wallpaper-effects-generator/effects.yaml`
✓ Projects can have local `effects.yaml`
✓ Error messages are clear and actionable
✓ No breaking changes for CLI users
