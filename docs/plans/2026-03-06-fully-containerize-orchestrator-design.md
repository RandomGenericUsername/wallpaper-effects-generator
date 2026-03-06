# Design: Fully Containerize wallpaper-process batch

**Date:** 2026-03-06
**Status:** Approved — ready for implementation

---

## Problem Statement

`wallpaper-process` is the containerized CLI for the wallpaper effects generator. Its explicit contract is that image-processing commands run inside a Docker/Podman container so the host does not need ImageMagick installed. However, the `batch` group of commands (`effects`, `composites`, `presets`, `all`) breaks this contract: they run directly on the host by re-importing and re-registering callbacks from `wallpaper_core.cli.batch`, which ultimately calls `BatchGenerator → CommandExecutor → subprocess.run("magick ...")` on the host. If ImageMagick is not installed on the host, all `wallpaper-process batch` commands silently fail.

This bug propagated consistently through every layer of the project: the code was wrong, the tests were built to confirm the wrong behavior, and the docs accurately documented the wrong behavior.

---

## Audit: All 13 Findings

### Code (C)

| ID | File | Finding |
|----|------|---------|
| C-1 | `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:565-612` | `batch_app` re-registers core callbacks via `core_batch_module.app.registered_commands` loop; `batch_callback` sets up core context objects. Batch runs on host via `BatchGenerator → CommandExecutor → subprocess.run("magick...")`. |
| C-2 | `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:567` | Help string hardcoded as `"Batch generate effects (runs on host)"`. |

### Tests (T)

| ID | File | Finding |
|----|------|---------|
| T-1 | `packages/orchestrator/tests/test_cli_integration.py:72-272` | `TestBatchCommands` (13 tests) invokes `wallpaper-process batch` and asserts host filesystem file creation. Tests mock `wallpaper_core.engine.executor.subprocess.run` to simulate magick — the wrong code path. After containerization batch goes through `ContainerManager.run_batch()`, not the core executor. Full rewrite required. |
| T-2 | `packages/orchestrator/tests/conftest.py:67-90` | `mock_subprocess_for_integration_tests` autouse fixture patches `wallpaper_core.engine.executor.subprocess.run` and `shutil.which("magick")`. After fix, batch never reaches that code path; the mock becomes silently irrelevant for batch, masking any regressions. |
| T-3 | `packages/orchestrator/tests/conftest.py:122-144` | `use_tmp_default_output` fixture patches `config.core.output.default_dir` and is used only by the T-1 tests to verify host file creation. Fixture itself is not wrong (output dir is still resolved on host as a volume mount arg), but its usage context needs to change with T-1. |
| T-4 | `packages/orchestrator/tests/test_integration.py:64-78` | `test_cli_commands_registered` only verifies `install`, `uninstall`, `info`. Does not assert that `batch`, `show`, or `process` sub-apps are registered. |

### Documentation (D)

| ID | File | Finding |
|----|------|---------|
| D-1 | `docs/reference/cli-orchestrator.md:1-4` | Opening sentence: "Batch, show, info, and version commands run on the host." — wrong for batch. |
| D-2 | `docs/reference/cli-orchestrator.md:12-16` | Commands overview table shows `batch effects/composites/presets/all → Host`. |
| D-3 | `docs/reference/cli-orchestrator.md:169` | "Runs batch generation on the **host** (not inside the container). Delegates to the core batch engine. (BHV-0081)" — explicitly documents wrong behavior. Missing container invocation format. |
| D-4 | `docs/explanation/host-vs-container.md:65` | "What runs where" table: `batch | On host | On host (delegates to core batch engine)`. |
| D-5 | `docs/explanation/host-vs-container.md:88` | "Switching from host to container mode is as simple as replacing `wallpaper-core` with `wallpaper-process`." — currently false for batch, will become true after fix. |
| D-6 | `docs/how-to/run-in-container.md:70-78` | Section "Run batch in the container environment" says batch "delegates to the core batch engine and runs **on the host** (not in the container)". BHV-0081 referenced. Also: `docs/how-to/batch-process.md` has zero `wallpaper-process batch` examples. |

### Smoke Tests (S)

| ID | File | Finding |
|----|------|---------|
| S-1 | `tests/smoke/run-smoke-tests.sh` | Zero `wallpaper-process batch` smoke tests. `wallpaper-core batch` has full coverage (effects, composites, presets, all, default dir, flat); the orchestrator batch section is entirely absent. |

---

## Chosen Approach: Single Container Invocation per Batch Run

`wallpaper-process batch effects input.jpg` → `podman run --rm -v ... wallpaper-effects:latest batch effects /input/input.jpg -o /output`

The container already has `wallpaper-core batch` installed and working. One container is started per batch call. Parallelism (`--parallel`) runs inside the container via the existing `ThreadPoolExecutor` in `BatchGenerator`. No Dockerfile changes required.

**Rejected alternatives:**
- Per-item container invocations: N container startups for N items — startup overhead dominates.
- Long-running daemon container: lifecycle management complexity not justified for a CLI tool.

---

## Design

### 1. `ContainerManager.run_batch()` — new method

**File:** `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py`

New method mirroring `run_process()` in structure and guards:

```python
def run_batch(
    self,
    batch_type: str,        # "effects" | "composites" | "presets" | "all"
    input_path: Path,
    output_dir: Path,
    flat: bool = False,
    parallel: bool = True,
    strict: bool = True,
) -> subprocess.CompletedProcess[str]:
```

**Guards (identical to `run_process()`):**
1. `batch_type` must be one of `{"effects", "composites", "presets", "all"}` — `ValueError` otherwise.
2. Container image must be available — `RuntimeError` otherwise.
3. Input file must exist — `FileNotFoundError` otherwise.
4. Output directory is created with `mkdir(parents=True, exist_ok=True)` and `chmod(0o777)` — `PermissionError` propagated.

**Container command built:**
```
[engine, "run", "--rm",
 "--userns=keep-id",          # podman only
 "-v", "{abs_input}:/input/{filename}:ro",
 "-v", "{abs_output_dir}:/output:rw",
 image_name,
 "batch", batch_type,
 f"/input/{filename}",
 "-o", "/output",
 "--flat",                    # if flat=True
 "--parallel"/"--sequential", # based on parallel flag
 "--strict"/"--no-strict",   # based on strict flag
]
```

### 2. CLI `batch_app` rewrite — `cli/main.py`

**Removed:**
- `from wallpaper_core.cli import batch as core_batch_module` import
- `batch_callback()` function (context setup for core commands — no longer needed)
- The re-registration loop: `for cmd_info in core_batch_module.app.registered_commands`

**Added:**
Four dedicated command functions registered directly on `batch_app`:

```python
@batch_app.command("effects")
def batch_effects(
    input_file: Annotated[Path, typer.Argument(...)],
    output_dir: Annotated[Path | None, typer.Option("-o", "--output-dir", ...)] = None,
    flat: Annotated[bool, typer.Option("--flat", ...)] = False,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", ...)] = False,
) -> None:
    """Generate all effects for an image (runs in container)."""
```

Same pattern for `batch_composites`, `batch_presets`, `batch_all`.

Each command:
1. Calls `get_config()` and constructs `ContainerManager`.
2. Resolves `output_dir` from `config.core.output.default_dir` if not provided.
3. Handles `--dry-run` (see §4 below) before touching the container.
4. Checks `manager.is_image_available()` → exit 1 with install hint if not.
5. Calls `manager.run_batch(batch_type, input_path, output_dir, flat, parallel, strict)`.
6. Handles `returncode != 0` → exit 1 with stderr.
7. Wraps in `try/except (RuntimeError, FileNotFoundError, PermissionError)` and generic `Exception`.

**Help string changed:** `"Batch generate effects (runs on host)"` → `"Batch generate effects (runs in container)"`

### 3. Dry-run

**`OrchestratorDryRun.render_container_batch()` — new method**

File: `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py`

Shows two layers (mirrors `render_container_process()`):
- Header: `batch <type> (container)`
- Fields: Input, Output directory, Batch type, Engine, Image
- Host command: `docker run --rm -v ... wallpaper-effects:latest batch <type> /input/... -o /output [flags]`
- Inner commands table: individual `magick ...` commands computed on host using `_resolve_batch_items()` from `wallpaper_core.cli.batch` (still available as a dependency)

**Per-command dry-run logic** (inside each new `batch_*` function, before `run_batch()`):
1. Build the container command string.
2. Call `_resolve_batch_items()` to compute inner commands.
3. Call `renderer.render_container_batch(...)`.
4. Call `renderer.validate_container(engine, image_name)`.
5. `raise typer.Exit(0)` — no container spawned.

### 4. Tests

#### `test_container_manager.py` — new tests for `run_batch()`

Covers:
- Invalid `batch_type` → `ValueError`
- Image not available → `RuntimeError`
- Input file not found → `FileNotFoundError`
- Permission error on output dir → `PermissionError`
- Command structure for all four types: verifies `"batch"`, type name, `/input/filename`, `-o`, `/output` present in subprocess args
- `--flat` flag forwarded
- `--parallel` / `--sequential` forwarded
- `--strict` / `--no-strict` forwarded
- Podman engine adds `--userns=keep-id`
- Docker engine does not add `--userns=keep-id`
- Returns `CompletedProcess` with correct returncode/stderr passthrough

#### New `test_cli_batch.py` — replaces `TestBatchCommands` in `test_cli_integration.py`

Mirrors `test_cli_process.py` structure. All tests mock `ContainerManager`. Covers all four batch types:
- With and without `-o` flag (default from config)
- `--flat` flag forwarded
- `--parallel` / `--sequential` forwarded
- `--strict` / `--no-strict` forwarded
- Image not available → exit 1 + "Container image not found" message
- Container execution failure (`returncode=1`) → exit 1
- `RuntimeError` from `run_batch()` → exit 1
- `run_batch()` is NOT called in dry-run mode

#### `test_cli_dry_run.py` — new `TestBatchContainerDryRun` class

Covers all four batch types:
- Shows host command (`docker run ... wallpaper-core batch <type> ...`)
- Shows inner `magick` commands
- `run_batch()` not called
- Podman variant shows `--userns`
- Uses original input filename (not hardcoded)
- dry-run exits 0

#### `test_integration.py` — fix `test_cli_commands_registered`

Extend to assert `batch`, `show`, `process` sub-apps are present in the registered typer groups.

#### `test_cli_integration.py` — rewrite `TestBatchCommands`

Replace all 13 tests with mock-based tests that verify:
- `ContainerManager.run_batch()` is called with correct `batch_type`, `input_path`, `output_dir`, `flat`, `parallel`, `strict`
- No host filesystem file creation is asserted
- `use_tmp_default_output` fixture usage removed from batch tests (no longer relevant)

#### `conftest.py` — update autouse fixture comment

The `mock_subprocess_for_integration_tests` autouse fixture remains valid for show/info/other tests that still use core machinery. Add a comment clarifying it does not apply to batch commands after containerization, and that batch is tested via `ContainerManager` mocks.

### 5. Documentation

| File | Changes |
|------|---------|
| `docs/reference/cli-orchestrator.md` | Fix opening sentence; update commands table (`batch → Container`); rewrite `## batch` section to document containerized execution with the `docker run` invocation format, all flags, and `--dry-run` behavior. Remove BHV-0081 wrong-behavior reference. |
| `docs/explanation/host-vs-container.md` | Update "What runs where" table: `batch` now "In container" for `wallpaper-process`. Update practical guidance examples to show `wallpaper-process batch`. Fix the "identical syntax" claim to now be accurate. |
| `docs/how-to/run-in-container.md` | Rewrite "Run batch in the container environment" section to show all four batch subcommands running in the container. Remove the "runs on the host" text. |
| `docs/how-to/batch-process.md` | Add a "Using the container (wallpaper-process batch)" section with examples for all four subcommands. Update Prerequisites to distinguish: `wallpaper-core batch` requires ImageMagick; `wallpaper-process batch` requires the container image. |
| `CHANGELOG.md` | Add entry under a new version or Unreleased: fix `wallpaper-process batch` to run inside the container instead of on the host (breaking: removes implicit host ImageMagick dependency for batch in orchestrator). |

### 6. Smoke Tests

**`tests/smoke/run-smoke-tests.sh`** — new section "Orchestrator Batch Commands (containerized)" added after existing orchestrator process tests:

Tests added:
- `wallpaper-process batch effects <image> -o <dir>` — verifies output file count ≥ 9
- `wallpaper-process batch composites <image> -o <dir>` — verifies output file count ≥ 4
- `wallpaper-process batch presets <image> -o <dir>` — verifies output file count ≥ 7
- `wallpaper-process batch all <image> -o <dir>` — verifies total output count > 15
- `wallpaper-process batch effects <image> --dry-run` — verifies `docker run` appears in output, no files created
- `wallpaper-process batch all <image> --flat -o <dir>` — verifies flat directory structure

**`.github/workflows/smoke-test.yml`** — no changes required. The `Install ImageMagick` step stays: it is still needed for `wallpaper-core batch` smoke tests.

---

## What Is NOT Changing

- `wallpaper-core` package: untouched. Continues to provide host-side batch for direct use.
- `show` commands: correctly run on host (read effects YAML, no ImageMagick needed). Stay as-is.
- `info`, `version`: host-side metadata commands. Stay as-is.
- `process` commands: already containerized correctly.
- `install`, `uninstall`: host-side container management. Stay as-is.
- Dockerfile: no changes. Container already has `wallpaper-core batch` installed.
- `ci-orchestrator.yml`: no changes. Tests run without ImageMagick; batch will be fully mocked.

---

## File Change Summary

| File | Change Type |
|------|-------------|
| `packages/orchestrator/src/wallpaper_orchestrator/container/manager.py` | Add `run_batch()` method |
| `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py` | Rewrite `batch_app` section; remove core import and callback loop; add 4 command functions; fix help string |
| `packages/orchestrator/src/wallpaper_orchestrator/dry_run.py` | Add `render_container_batch()` method |
| `packages/orchestrator/tests/test_container_manager.py` | Add `run_batch()` tests |
| `packages/orchestrator/tests/test_cli_batch.py` | **New file** — containerized batch CLI tests |
| `packages/orchestrator/tests/test_cli_dry_run.py` | Add `TestBatchContainerDryRun` class |
| `packages/orchestrator/tests/test_cli_integration.py` | Rewrite `TestBatchCommands` (13 tests) |
| `packages/orchestrator/tests/test_integration.py` | Extend `test_cli_commands_registered` |
| `packages/orchestrator/tests/conftest.py` | Add clarifying comment on autouse fixture scope |
| `docs/reference/cli-orchestrator.md` | Fix batch section throughout |
| `docs/explanation/host-vs-container.md` | Fix table and guidance |
| `docs/how-to/run-in-container.md` | Fix batch section |
| `docs/how-to/batch-process.md` | Add `wallpaper-process batch` examples section |
| `tests/smoke/run-smoke-tests.sh` | Add orchestrator batch smoke tests |
| `CHANGELOG.md` | Add fix entry |

---

## BHV Impact

**BHV-0081** ("batch runs on host for orchestrator") — this behavior is being corrected. All references to BHV-0081 in docs must be updated to reflect the new containerized behavior.
