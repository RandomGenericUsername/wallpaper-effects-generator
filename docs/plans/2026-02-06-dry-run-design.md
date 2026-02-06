# Dry-Run Commands Design

**Date:** 2026-02-06
**Status:** Draft
**Author:** Claude (via brainstorming session)

## Overview

Add `--dry-run` flag to all commands with side effects across both wallpaper-core and wallpaper-orchestrator CLIs. When passed, the command resolves everything (config, parameters, commands, output paths) and prints a comprehensive preview with pre-flight validation — but executes nothing. Zero files written, zero containers spawned, zero images built.

## Goals

1. Show users exactly what a command will do before it runs
2. Surface configuration and environment problems early (pre-flight validation)
3. Provide debugging-friendly output with resolved commands users can copy-paste
4. Scale detail with existing verbosity flags (`-q`, `-v`, `-vv`)
5. Cover all mutating commands in both CLIs

## Scope

### Commands with `--dry-run` (17 total)

**wallpaper-core (7 commands):**
- `process effect ... --dry-run`
- `process composite ... --dry-run`
- `process preset ... --dry-run`
- `batch effects ... --dry-run`
- `batch composites ... --dry-run`
- `batch presets ... --dry-run`
- `batch all ... --dry-run`

**wallpaper-process (10 commands):**
- `install --dry-run`
- `uninstall --dry-run`
- `process effect ... --dry-run`
- `process composite ... --dry-run`
- `process preset ... --dry-run`
- `batch effects ... --dry-run`
- `batch composites ... --dry-run`
- `batch presets ... --dry-run`
- `batch all ... --dry-run`

### Excluded (read-only, no side effects)

- `version`, `info`, `show effects/composites/presets/all` — both CLIs

## Design Decisions

### 1. Flag Placement: Per-Command

**Decision:** `--dry-run` is a per-command option, not a global flag.

**Rationale:**
- Only appears on commands where it makes sense
- No ambiguity about what it applies to
- Read-only commands don't carry a useless flag

**Alternatives considered:**
- Global flag (rejected — pollutes read-only commands)
- Both global and per-command (rejected — unnecessary complexity)

### 2. Output Content: Structured Summary + Resolved Commands

**Decision:** Show both a human-readable structured summary (effect name, paths, parameters) and the raw resolved command(s) that would execute.

**Rationale:**
- Summary gives quick at-a-glance understanding
- Resolved commands enable copy-paste debugging
- Users get the best of both worlds

**Alternatives considered:**
- Command only (rejected — lacks context)
- Summary only (rejected — can't copy-paste to debug)

### 3. Batch Output: Table + Commands

**Decision:** Batch dry-run shows a Rich table listing all items (name, output path, parameters/chain) followed by all resolved commands numbered sequentially.

**Rationale:**
- Table gives structured overview of all N items
- Commands section provides full debugging detail
- Rich tables are already used throughout the project (`show` commands)

### 4. Container Output: Both Layers

**Decision:** Orchestrator dry-run shows both the host container command (`podman run ...`) and the inner ImageMagick command (`magick ...`) that runs inside the container.

**Rationale:**
- Full transparency into what happens at each layer
- Host command useful for debugging container/volume issues
- Inner command useful for debugging effect/parameter issues

### 5. Validation: Full Pre-Flight Check

**Decision:** Dry-run validates all preconditions and reports pass/fail for each.

**Checks performed:**
- Input file exists
- Output directory exists (notes it would be created)
- `magick` binary found on PATH (core)
- Container engine binary found (orchestrator)
- Container image available (orchestrator)
- Effect/composite/preset name found in config
- Install: Dockerfile exists, image already exists (would overwrite)
- Uninstall: image exists (can be removed)

**Rationale:**
- Surfaces environment problems before committing to a run
- Especially valuable for batch commands (catch issues before processing 20+ items)
- Makes dry-run a genuine debugging tool, not just a preview

### 6. Verbosity Scaling

**Decision:** Dry-run output scales with existing `-q`/`-v` flags.

**Quiet (`-q --dry-run`):**
- Just the resolved command(s), one per line
- Useful for scripting/piping

**Normal (`--dry-run`):**
- Structured summary (input, output, effect, params with defaults noted)
- Resolved command
- Validation checklist

**Verbose (`-v --dry-run`):**
- Everything in normal, plus:
- Layer source for each parameter (package/project/user)
- Command template before substitution
- File sizes, binary versions/paths in validation
- For batch: layer source per item

### 7. Architecture: Shared Base in layered-settings

**Decision:** Shared formatting base class in layered-settings, extended by core and orchestrator with domain-specific renderers.

**Rationale:**
- Follows existing dependency graph (both packages depend on layered-settings)
- Prevents formatting drift across 17 commands
- Each package owns its domain logic
- Shared base is small (formatting utilities only, no domain knowledge)

**Alternatives considered:**
- All rendering in core, orchestrator imports (rejected — orchestrator shouldn't depend on core for its own concerns)
- Inline per-command (rejected — formatting duplicated across 17 commands)
- Each package has independent renderer (rejected — formatting drift, unnecessary duplication)

## Output Examples

### Single Process (Normal)

```
Dry Run: process effect

  Input:   /home/user/wallpaper.jpg
  Output:  /home/user/output/blur.jpg
  Effect:  blur
  Params:  blur=0x8 (default)

  Command:
    magick "input.jpg" -blur 0x8 "output.jpg"

  Validation:
    ✓ Input file exists
    ✓ magick binary found
    ✓ Effect 'blur' found in config
    ✗ Output directory does not exist (would be created)
```

### Single Process (Verbose)

```
Dry Run: process effect

  Input:   /home/user/wallpaper.jpg
  Output:  /home/user/output/blur.jpg
  Effect:  blur (source: package)
  Params:
    blur = 0x8 (default from package layer)

  Command template: magick "$INPUT" -blur $BLUR "$OUTPUT"
  Resolved command: magick "input.jpg" -blur 0x8 "output.jpg"

  Validation:
    ✓ Input file exists (/home/user/wallpaper.jpg, 2.4 MB)
    ✓ magick binary found (/usr/bin/magick, v7.1.1)
    ✓ Effect 'blur' found in config (package layer)
    ✗ Output directory does not exist (would be created: /home/user/output/)
```

### Single Process (Quiet)

```
magick "input.jpg" -blur 0x8 "output.jpg"
```

### Batch All (Normal)

```
Dry Run: batch all (15 items)

  Input:    /home/user/wallpaper.jpg
  Output:   /output/wallpaper/
  Mode:     parallel (4 workers)
  Strict:   yes

  Effects (9):
  ┌──────────────┬────────────────────────────────────────────┬────────────┐
  │ Name         │ Output Path                                │ Params     │
  ├──────────────┼────────────────────────────────────────────┼────────────┤
  │ blur         │ /output/wallpaper/effects/blur.jpg         │ blur=0x8   │
  │ blackwhite   │ /output/wallpaper/effects/blackwhite.jpg   │ —          │
  │ brightness   │ /output/wallpaper/effects/brightness.jpg   │ percent=0  │
  │ ...          │ ...                                        │ ...        │
  └──────────────┴────────────────────────────────────────────┴────────────┘

  Composites (4):
  ┌─────────────────────┬──────────────────────────────────────────────────┬───────────────────┐
  │ Name                │ Output Path                                      │ Chain             │
  ├─────────────────────┼──────────────────────────────────────────────────┼───────────────────┤
  │ blur-brightness80   │ /output/wallpaper/composites/blur-brightness80…  │ blur → brightness │
  │ ...                 │ ...                                              │ ...               │
  └─────────────────────┴──────────────────────────────────────────────────┴───────────────────┘

  Presets (2):
  ┌─────────────┬────────────────────────────────────────────────┬───────────┬───────────────────┐
  │ Name        │ Output Path                                    │ Type      │ Target            │
  ├─────────────┼────────────────────────────────────────────────┼───────────┼───────────────────┤
  │ dark_blur   │ /output/wallpaper/presets/dark_blur.jpg        │ composite │ blur-brightness80 │
  │ subtle_blur │ /output/wallpaper/presets/subtle_blur.jpg      │ effect    │ blur              │
  └─────────────┴────────────────────────────────────────────────┴───────────┴───────────────────┘

  Commands (15):
    1. magick "input.jpg" -blur 0x8 "/output/wallpaper/effects/blur.jpg"
    2. magick "input.jpg" -colorspace Gray "/output/wallpaper/effects/blackwhite.jpg"
    ...

  Validation:
    ✓ Input file exists
    ✓ magick binary found
    ✓ All 15 items resolved successfully
    ✗ Output directory does not exist (would be created)
```

### Container Process (Normal)

```
Dry Run: process effect (container)

  Input:      /home/user/wallpaper.jpg
  Output:     /home/user/output/blur.jpg
  Effect:     blur
  Engine:     podman
  Image:      wallpaper-effects:latest

  Host command:
    podman run --rm --userns=keep-id \
      -v /home/user/wallpaper.jpg:/input/image.jpg:ro \
      -v /home/user/output:/output:rw \
      wallpaper-effects:latest \
      process effect /input/image.jpg /output/blur.jpg --effect blur

  Inner command (runs inside container):
    magick "/input/image.jpg" -blur 0x8 "/output/blur.jpg"

  Validation:
    ✓ Input file exists
    ✓ podman binary found
    ✓ Container image 'wallpaper-effects:latest' available
    ✓ Effect 'blur' found in config
    ✗ Output directory does not exist (would be created)
```

### Install (Normal)

```
Dry Run: install

  Engine:     podman
  Image:      wallpaper-effects:latest
  Dockerfile: /home/user/Dev/wallpaper.../docker/Dockerfile.imagemagick

  Command:
    podman build -f /home/.../Dockerfile.imagemagick \
      -t wallpaper-effects:latest /home/.../wallpaper-effects-generator

  Validation:
    ✓ podman binary found
    ✓ Dockerfile exists
    ✗ Image 'wallpaper-effects:latest' already exists (would be overwritten)
```

### Uninstall (Normal)

```
Dry Run: uninstall

  Engine:     podman
  Image:      wallpaper-effects:latest

  Command:
    podman rmi wallpaper-effects:latest

  Validation:
    ✓ podman binary found
    ✓ Image 'wallpaper-effects:latest' exists
```

## Architecture

### Module Structure

**layered-settings** (shared base):
```
packages/settings/src/layered_settings/
├── dry_run.py          # DryRunBase, ValidationCheck, formatting utilities
└── ...existing files
```

**wallpaper-core** (extends base):
```
packages/core/src/wallpaper_core/
├── dry_run.py          # CoreDryRun(DryRunBase)
└── ...existing files
```

**wallpaper-orchestrator** (extends base):
```
packages/orchestrator/src/wallpaper_orchestrator/
├── dry_run.py          # OrchestratorDryRun(DryRunBase)
└── ...existing files
```

### DryRunBase (layered-settings)

Provides generic formatting utilities with no domain knowledge:

```python
@dataclass
class ValidationCheck:
    name: str
    passed: bool
    detail: str = ""

class DryRunBase:
    def __init__(self, output: RichOutput) -> None: ...
    def render_header(self, title: str) -> None: ...
    def render_field(self, label: str, value: str) -> None: ...
    def render_validation(self, checks: list[ValidationCheck]) -> None: ...
    def render_command(self, label: str, command: str) -> None: ...
    def render_table(self, title: str, columns: list[str], rows: list[list[str]]) -> None: ...
```

### CoreDryRun (wallpaper-core)

Extends base with ImageMagick and effects domain logic:

```python
class CoreDryRun(DryRunBase):
    def render_process(self, effect, input_path, output_path, params, command) -> None: ...
    def render_batch(self, items, input_path, output_dir, settings) -> None: ...
    def validate_core(self, input_path, effect_name, config) -> list[ValidationCheck]: ...
```

### OrchestratorDryRun (wallpaper-orchestrator)

Extends base with container domain logic:

```python
class OrchestratorDryRun(DryRunBase):
    def render_container_process(self, effect, input_path, output_path, host_cmd, inner_cmd) -> None: ...
    def render_install(self, engine, image, dockerfile, build_cmd) -> None: ...
    def render_uninstall(self, engine, image, cmd) -> None: ...
    def validate_container(self, engine, image_name) -> list[ValidationCheck]: ...
```

### Command Integration Pattern

Each command gains a `--dry-run` flag with an early-return pattern:

```python
def process_effect(
    ctx: typer.Context,
    input_file: Path,
    output_file: Path,
    effect: str,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without executing")] = False,
):
    # ...resolve effect, build params, build command (existing logic)...

    if dry_run:
        renderer = CoreDryRun(output=ctx.obj["output"])
        checks = renderer.validate_core(input_file, effect, config)
        renderer.render_process(effect, input_file, output_file, params, command)
        renderer.render_validation(checks)
        raise typer.Exit(0)

    # ...existing execution logic unchanged...
```

Key principle: all existing code paths remain untouched. The `if dry_run` block is a clean early-return that exits before any side effects. No changes to `CommandExecutor`, `ChainExecutor`, `BatchGenerator`, or `ContainerManager`.

## Testing Strategy

### layered-settings tests (`test_dry_run.py`)

- `DryRunBase` formatting methods produce expected Rich output
- `ValidationCheck` dataclass renders pass/fail correctly
- Table rendering with various column/row configurations

### wallpaper-core tests (`test_dry_run.py`)

- `test_process_dry_run_shows_command` — resolved command appears in output
- `test_process_dry_run_shows_params` — parameters with defaults/overrides shown
- `test_process_dry_run_no_file_created` — output file does NOT exist after dry-run
- `test_batch_dry_run_shows_table` — all items appear in table
- `test_batch_dry_run_no_files_created` — zero output files after dry-run
- `test_validation_input_missing` — warns when input file doesn't exist
- `test_validation_magick_missing` — warns when magick binary not found
- `test_validation_effect_not_found` — warns when effect name invalid
- `test_verbosity_quiet_shows_only_command` — quiet mode output is minimal
- `test_verbosity_verbose_shows_layer_source` — verbose adds layer info

### wallpaper-orchestrator tests (`test_dry_run.py`)

- `test_container_dry_run_shows_both_commands` — host and inner commands shown
- `test_container_dry_run_no_container_spawned` — no `docker run` executed
- `test_install_dry_run_shows_build_command` — build command shown
- `test_install_dry_run_no_image_built` — no `docker build` executed
- `test_uninstall_dry_run_no_image_removed` — no `docker rmi` executed
- `test_validation_engine_missing` — warns when docker/podman not found
- `test_validation_image_missing` — warns when container image not built

All tests use CLI runner (`typer.testing.CliRunner`) to invoke commands with `--dry-run` and inspect stdout. Side-effect tests verify no filesystem or subprocess changes occurred.

## Implementation Order

1. Add `DryRunBase` and `ValidationCheck` to layered-settings
2. Add `CoreDryRun` to wallpaper-core
3. Add `--dry-run` to core `process effect/composite/preset` commands
4. Add `--dry-run` to core `batch effects/composites/presets/all` commands
5. Add `OrchestratorDryRun` to wallpaper-orchestrator
6. Add `--dry-run` to orchestrator `process effect/composite/preset` commands
7. Add `--dry-run` to orchestrator `install` and `uninstall` commands
8. Add `--dry-run` to orchestrator `batch` commands (delegated to core)
9. Add tests for all three packages
10. Update `test-all-commands.sh` with dry-run test cases

## Future Enhancements

- `--dry-run --json` output mode for machine-readable previews
- Dry-run diff: compare what would change vs what already exists in output directory
- Batch dry-run cost estimate (estimated time based on effect complexity)
