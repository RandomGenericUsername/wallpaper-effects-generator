# Phase 4: Container Execution Implementation

**Date**: 2026-02-04
**Status**: Design Complete, Ready for Implementation
**Previous Phase**: Phase 3 - Orchestrator Package Structure

---

## Overview & Goals

Phase 4 transforms the orchestrator from a CLI wrapper into a true container execution engine. Users choose their execution environment by which package they install:

- Install `wallpaper-core` → Get `wallpaper-core` command (local execution, user manages ImageMagick)
- Install `wallpaper-orchestrator` → Get `wallpaper-process` command (containerized execution, isolated environment)

### Key Changes

1. Rename core's CLI entry point from `wallpaper-process` to `wallpaper-core`
2. Implement `ContainerManager.run_process()` to execute commands inside containers
3. Replace orchestrator's CLI delegation with actual container execution calls
4. Handle volume mounting for input images and output directories
5. Support both Docker and Podman equally

### User Experience

```bash
# Using core (local execution)
$ wallpaper-core process effect input.jpg output.jpg blur
# Runs ImageMagick directly on host

# Using orchestrator (containerized execution)
$ wallpaper-process process effect input.jpg output.jpg blur
# Runs ImageMagick inside container, mounts input/output
```

---

## Architecture

### Package Separation

**wallpaper-core package:**
- Entry point: `wallpaper-core` (renamed from `wallpaper-process`)
- Execution: Local, using host's ImageMagick
- User responsibility: Install ImageMagick and dependencies
- Use case: Direct control, no container overhead

**wallpaper-orchestrator package:**
- Entry point: `wallpaper-process`
- Execution: Containerized via Docker/Podman
- Dependencies: Bundled in container image
- Use case: Isolation, reproducibility, portability

### Command Routing

**Commands that run in containers:**
- `process effect` → `ContainerManager.run_process("effect", ...)`
- `process composite` → `ContainerManager.run_process("composite", ...)`
- `process preset` → `ContainerManager.run_process("preset", ...)`
- `batch effect/composite/preset` → Loop with `run_process()`

**Commands that run on host:**
- `show effects/composites/presets` → Delegate to core (read-only, lightweight)
- `info` → Delegate to core (config display)
- `version` → Show orchestrator version
- `install/uninstall` → Container image management

---

## Task Breakdown

### Task 1: Rename Core CLI Entry Point

**Goal**: Change core's command name to `wallpaper-core` for clear separation.

**Changes:**
- `packages/core/pyproject.toml`: Change `[project.scripts]` from `wallpaper-process` to `wallpaper-core`
- `packages/core/README.md`: Update all examples to use `wallpaper-core`
- Update all core tests to use new command name
- Update core's CLI help text to reflect new name

**Breaking change**: Existing users of standalone core will need to update scripts.

**Commit**: `refactor(core): rename CLI from wallpaper-process to wallpaper-core`

---

### Task 2: Implement ContainerManager.run_process()

**Goal**: Add container execution capability to ContainerManager.

**Method signature:**
```python
def run_process(
    self,
    command_type: str,  # "effect", "composite", or "preset"
    command_name: str,  # e.g., "blur", "dark", etc.
    input_path: Path,
    output_path: Path,
    additional_args: list[str] = None,
) -> subprocess.CompletedProcess:
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
        PermissionError: If output directory not writable
    """
```

**Implementation steps:**

1. **Validate prerequisites:**
   - Check container image exists via `is_image_available()`
   - Validate input file exists and is readable
   - Ensure output directory exists (create if needed)
   - Check output directory is writable

2. **Build volume mounts:**
   - Input: `{input_path.absolute()}:/input/image.jpg:ro` (read-only)
   - Output: `{output_path.parent.absolute()}:/output:rw` (read-write)
   - Use absolute paths to avoid mount issues

3. **Construct container command:**
   ```python
   cmd = [
       self.engine,  # "docker" or "podman"
       "run",
       "--rm",  # Remove container after execution
       "-v", f"{input_path.absolute()}:/input/image.jpg:ro",
       "-v", f"{output_path.parent.absolute()}:/output:rw",
       self.get_image_name(),  # "wallpaper-effects:latest"
       "process",
       command_type,  # "effect", "composite", or "preset"
       "/input/image.jpg",
       f"/output/{output_path.name}",
       command_name,  # e.g., "blur"
   ]

   if additional_args:
       cmd.extend(additional_args)
   ```

4. **Execute and return:**
   ```python
   result = subprocess.run(
       cmd,
       capture_output=True,
       text=True,
       check=False,  # Don't raise on non-zero exit
   )
   return result
   ```

**Error handling:**
- Image not available → Raise `RuntimeError` with install instructions
- Input not found → Raise `FileNotFoundError` with clear message
- Permission denied → Raise `PermissionError` with directory path
- Container failure → Return CompletedProcess (caller handles exit code)

**File**: `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`

**Tests**: `packages/orchestrator/tests/test_container_manager.py`
- Mock subprocess.run
- Test volume mount construction
- Test command building for docker and podman
- Test error cases (missing image, missing file, permissions)
- Test successful execution returns CompletedProcess

**Commit**: `feat(orchestrator): implement ContainerManager.run_process for container execution`

---

### Task 3: Implement Orchestrator Process Commands

**Goal**: Replace CLI delegation with actual container execution.

**Changes to `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py`:**

Remove the core CLI delegation code (lines 24-46) and replace with new command implementations:

```python
@app.command()
def process_effect(
    input_file: Path = typer.Argument(..., help="Input image file"),
    output_file: Path = typer.Argument(..., help="Output image file"),
    effect: str = typer.Argument(..., help="Effect name to apply"),
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

        console.print(f"[green]✓ Output written to:[/green] {output_file}")

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@app.command()
def process_composite(
    input_file: Path = typer.Argument(..., help="Input image file"),
    output_file: Path = typer.Argument(..., help="Output image file"),
    composite: str = typer.Argument(..., help="Composite name to apply"),
) -> None:
    """Apply composite effect to image (runs in container)."""
    # Similar implementation to process_effect
    # ... (call manager.run_process with command_type="composite")


@app.command()
def process_preset(
    input_file: Path = typer.Argument(..., help="Input image file"),
    output_file: Path = typer.Argument(..., help="Output image file"),
    preset: str = typer.Argument(..., help="Preset name to apply"),
) -> None:
    """Apply preset to image (runs in container)."""
    # Similar implementation to process_effect
    # ... (call manager.run_process with command_type="preset")
```

**Keep these commands as delegation (no container):**
```python
@app.command()
def show_effects() -> None:
    """List available effects (runs on host)."""
    from wallpaper_core.cli.show import list_effects
    list_effects()

@app.command()
def info() -> None:
    """Show configuration (runs on host)."""
    from wallpaper_core.cli.main import info as core_info
    core_info()

@app.command()
def version() -> None:
    """Show version (runs on host)."""
    from wallpaper_orchestrator import __version__
    console.print(f"wallpaper-orchestrator v{__version__}")
```

**Tests**: `packages/orchestrator/tests/test_cli_process.py`
- Mock ContainerManager.run_process
- Test each command calls run_process with correct args
- Test error handling (missing image, container failure)
- Test success output formatting

**Commit**: `feat(orchestrator): implement process commands with container execution`

---

### Task 4: Implement Orchestrator Batch Commands

**Goal**: Add batch processing via containers.

**Implementation in `orchestrator/cli/main.py`:**

```python
@app.command()
def batch_effect(
    input_file: Path = typer.Argument(..., help="Input image file"),
    output_dir: Path = typer.Option(..., "--output-dir", "-o", help="Output directory"),
    effects: list[str] = typer.Option(..., "--effect", "-e", help="Effects to apply"),
) -> None:
    """Apply multiple effects to image (runs in container).

    Each effect runs in a separate container execution.

    Examples:
        wallpaper-process batch effect input.jpg -o output/ -e blur -e darken -e saturate
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if not manager.is_image_available():
            console.print("[red]Container image not found. Run: wallpaper-process install[/red]")
            raise typer.Exit(1)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Process each effect
        with Progress() as progress:
            task = progress.add_task(f"Processing {len(effects)} effects...", total=len(effects))

            for effect_name in effects:
                output_file = output_dir / f"{input_file.stem}_{effect_name}{input_file.suffix}"

                result = manager.run_process(
                    command_type="effect",
                    command_name=effect_name,
                    input_path=input_file,
                    output_path=output_file,
                )

                if result.returncode != 0:
                    console.print(f"[red]✗ Failed:[/red] {effect_name}\n{result.stderr}")
                else:
                    console.print(f"[green]✓ Processed:[/green] {effect_name} → {output_file}")

                progress.advance(task)

        console.print(f"\n[green]Batch processing complete![/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
```

Similar implementations for `batch_composite` and `batch_preset`.

**Tests**: `packages/orchestrator/tests/test_cli_batch.py`
- Mock run_process
- Verify loop calls run_process for each effect
- Test progress display
- Test partial failures (some effects succeed, some fail)

**Commit**: `feat(orchestrator): implement batch commands with container execution`

---

### Task 5: Update Tests

**Goal**: Update all tests for new architecture.

**Core tests:**
- Update `packages/core/tests/` to use `wallpaper-core` command name
- No functional changes, just command name updates
- Verify all tests still pass

**Orchestrator tests:**
- Update existing tests that mock core CLI delegation
- Add new tests for container execution
- Mock subprocess.run in all container tests
- Test error paths comprehensively

**New test files:**
- `test_container_execution.py` - Integration tests for run_process
- `test_cli_process.py` - Tests for process commands
- `test_cli_batch.py` - Tests for batch commands

**Commit**: `test(core,orchestrator): update tests for new CLI architecture`

---

### Task 6: Update Documentation

**Goal**: Document new architecture and usage patterns.

**Updates needed:**

1. **packages/core/README.md:**
   - Update all command examples to use `wallpaper-core`
   - Add note about orchestrator package for containerized execution
   - Document that users must install ImageMagick

2. **packages/orchestrator/README.md:**
   - Update command examples to use `wallpaper-process`
   - Add architecture diagram showing core vs orchestrator
   - Document container execution model
   - Add troubleshooting section (Docker not found, image not installed, etc.)

3. **Root README.md** (if exists):
   - Add section explaining package structure
   - Guide users on which package to install:
     - Core: For direct control, local execution
     - Orchestrator: For isolation, reproducibility

**Commit**: `docs: update documentation for Phase 4 architecture`

---

### Task 7: Integration Testing

**Goal**: Verify end-to-end functionality with real container execution.

**Manual testing checklist:**
1. Install core only, verify `wallpaper-core` works locally
2. Install orchestrator, verify `wallpaper-process` builds image
3. Run process commands via orchestrator, verify container execution
4. Test batch processing with multiple effects
5. Test error cases (missing image, invalid effect, etc.)
6. Verify both Docker and Podman work

**Optional automated integration tests:**
- Add `tests/integration/` directory (if not already present)
- Tests that actually build and run containers (skip in CI if Docker unavailable)
- Marked with `@pytest.mark.integration` for selective execution

**Commit**: `test: add integration tests for container execution`

---

## Container Execution Details

### Volume Mounting Strategy

Direct mounting approach - no file copying:

**Input file mount:**
```
Host: /absolute/path/to/input.jpg
Container: /input/image.jpg:ro (read-only)
```

**Output directory mount:**
```
Host: /absolute/path/to/output/
Container: /output:rw (read-write)
```

**Container command:**
```bash
docker run --rm \
  -v /host/input.jpg:/input/image.jpg:ro \
  -v /host/output:/output:rw \
  wallpaper-effects:latest \
  process effect /input/image.jpg /output/result.jpg blur
```

### Path Handling

**Always use absolute paths:**
- `input_path.absolute()` before mounting
- `output_path.parent.absolute()` for output directory
- Avoids issues with relative path interpretation

**Output filename preservation:**
- User specifies: `/path/to/output.jpg`
- Mount directory: `/path/to` → `/output`
- Container writes: `/output/output.jpg`
- Result appears at: `/path/to/output.jpg`

---

## Error Handling

### Error Scenarios

**1. Container image not available**
```
Error: Container image not found

The orchestrator requires a container image to run effects.

To install:
  wallpaper-process install

To check status:
  docker images | grep wallpaper-effects
```
- Check: `manager.is_image_available()`
- Action: Prompt user to run install
- Exit code: 1

**2. Input file not found**
```
Error: Input file not found: /path/to/missing.jpg

Please check:
  - File path is correct
  - File exists and is readable
```
- Check: `input_path.exists()` before container execution
- Action: Clear error message with file path
- Exit code: 1

**3. Container execution failure**
```
Error: Effect 'blur' failed in container

Container output:
  magick: invalid parameter -blur 0x0

Check effect configuration in effects.yaml
```
- Capture: `result.stderr` from subprocess
- Show: Actual ImageMagick error for debugging
- Exit code: Same as container's exit code

**4. Permission errors**
```
Error: Cannot write to output directory: /protected/path

Ensure you have write permissions to the output location.
```
- Check: `os.access(output_dir, os.W_OK)` before execution
- Action: Clear permission error message
- Exit code: 1

**5. Container engine not available**
```
Error: Container engine 'docker' not found

Install Docker or Podman, or configure a different engine:

Config file: ~/.config/wallpaper-effects/settings.toml
  [orchestrator.container]
  engine = "podman"
```
- Check: `shutil.which(engine)` before execution
- Action: Guide to installation or config change
- Exit code: 1

### Success Output

```
✓ Processing input.jpg with effect 'blur'
✓ Output written to: /path/to/output.jpg
```

For batch operations:
```
Processing 3 effects...
✓ Processed: blur → output/image_blur.jpg
✓ Processed: darken → output/image_darken.jpg
✓ Processed: saturate → output/image_saturate.jpg

Batch processing complete!
```

---

## Testing Strategy

### Unit Tests

**ContainerManager tests:**
```python
def test_run_process_builds_correct_command():
    """Verify docker/podman run command construction."""

def test_run_process_validates_image_exists():
    """Verify image availability check."""

def test_run_process_handles_missing_input():
    """Verify input validation."""

def test_run_process_creates_output_directory():
    """Verify output directory creation."""

def test_run_process_uses_absolute_paths():
    """Verify paths are made absolute."""
```

**CLI command tests:**
```python
def test_process_effect_calls_run_process():
    """Verify CLI calls ContainerManager correctly."""

def test_process_effect_handles_container_failure():
    """Verify error handling for failed container."""

def test_batch_effect_loops_correctly():
    """Verify batch processes all effects."""
```

### Integration Tests

**Manual verification checklist:**
- [ ] Core CLI renamed to `wallpaper-core`
- [ ] Orchestrator uses `wallpaper-process`
- [ ] `wallpaper-process install` builds image
- [ ] Process commands execute in containers
- [ ] Batch commands work with multiple effects
- [ ] Show/info/version work without containers
- [ ] Error messages are clear and actionable
- [ ] Both Docker and Podman work

### Test Mocking Strategy

**Always mock subprocess.run:**
```python
@patch("subprocess.run")
def test_container_execution(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    # Test container manager behavior
```

**Don't require Docker in tests:**
- All unit tests mock container execution
- Integration tests can optionally use real containers
- Mark integration tests for selective execution

---

## Migration Guide

### For Existing Core Users

**Before Phase 4:**
```bash
$ wallpaper-process process effect input.jpg output.jpg blur
```

**After Phase 4:**
```bash
$ wallpaper-core process effect input.jpg output.jpg blur
```

**Action required:**
- Update scripts/aliases to use `wallpaper-core`
- Or install orchestrator for containerized execution

### For New Users

**Choose your execution model:**

**Local execution (wallpaper-core):**
- Install: `uv pip install wallpaper-core`
- Requires: ImageMagick installed on system
- Command: `wallpaper-core`
- Use case: Direct control, no container overhead

**Containerized execution (wallpaper-orchestrator):**
- Install: `uv pip install wallpaper-orchestrator`
- Requires: Docker or Podman installed
- Command: `wallpaper-process`
- Use case: Isolation, reproducibility, no ImageMagick install needed

---

## Success Criteria

Phase 4 is complete when:

1. ✅ Core CLI renamed to `wallpaper-core`
2. ✅ Orchestrator CLI uses `wallpaper-process`
3. ✅ `ContainerManager.run_process()` executes commands in containers
4. ✅ Process commands (effect/composite/preset) run via containers
5. ✅ Batch commands work with containerized execution
6. ✅ Show/info/version delegate to core (no container)
7. ✅ All tests pass with mocked container execution
8. ✅ Error handling provides clear, actionable messages
9. ✅ Documentation updated for new architecture
10. ✅ Both Docker and Podman supported equally

---

## Next Steps

After Phase 4 completion:
- Phase 5: Project cleanup (archive old directories, update root docs)
- Phase 6: End-to-end examples and tutorials
- Future: Container health checks, multi-stage processing, optimization

---

## Reference

- **Color-scheme reference**: `/home/inumaki/Development/color-scheme`
- **Phase 3 plan**: `docs/plans/2026-02-03-phase3-orchestrator.md`
- **Docker best practices**: Official Docker documentation
- **Pydantic validation**: For input validation before container execution
