# Implementation Plan: Wallpaper Effects Restructure

## Pre-Implementation Checklist

- [ ] Backup current project state (git commit or archive)
- [ ] Ensure all current tests pass
- [ ] Document any known issues

---

## Phase 1: Create Package Directory Structure

### 1.1 Create directories

```bash
mkdir -p packages/core/src/wallpaper_effects/{models,loader,engine,console,cli,data}
mkdir -p packages/core/tests
mkdir -p packages/orchestrator/src/wallpaper_effects_orchestrator/{container,cli}
mkdir -p packages/orchestrator/tests
```

### 1.2 Create package marker files

| File | Content |
|------|---------|
| `packages/core/src/wallpaper_effects/__init__.py` | Public API exports |
| `packages/core/src/wallpaper_effects/_version.py` | `__version__ = "1.0.0"` |
| `packages/orchestrator/src/wallpaper_effects_orchestrator/__init__.py` | Orchestrator exports |
| `packages/orchestrator/src/wallpaper_effects_orchestrator/_version.py` | `__version__ = "1.0.0"` |

---

## Phase 2: Migrate Core Package Files

### 2.1 Models (from shared → core)

| Source | Destination |
|--------|-------------|
| `shared/src/wallpaper_effects_shared/models/__init__.py` | `packages/core/src/wallpaper_effects/models/__init__.py` |
| `shared/src/wallpaper_effects_shared/models/effects.py` | `packages/core/src/wallpaper_effects/models/effects.py` |
| `shared/src/wallpaper_effects_shared/models/config.py` | `packages/core/src/wallpaper_effects/models/config.py` |
| `shared/src/wallpaper_effects_shared/models/settings.py` | `packages/core/src/wallpaper_effects/models/settings.py` |

**Import updates required in these files**:
- Change relative imports to use `wallpaper_effects.models`

### 2.2 Loader (from shared → core)

| Source | Destination |
|--------|-------------|
| `shared/src/wallpaper_effects_shared/loader/__init__.py` | `packages/core/src/wallpaper_effects/loader/__init__.py` |
| `shared/src/wallpaper_effects_shared/loader/config_loader.py` | `packages/core/src/wallpaper_effects/loader/config_loader.py` |
| `shared/src/wallpaper_effects_shared/loader/paths.py` | `packages/core/src/wallpaper_effects/loader/paths.py` |

**Import updates required**:
- `from wallpaper_effects_shared.models` → `from wallpaper_effects.models`
- Update path calculation in `paths.py` for new package location

### 2.3 Data files

| Source | Destination |
|--------|-------------|
| `shared/data/effects.yaml` | `packages/core/src/wallpaper_effects/data/effects.yaml` |

**Update `paths.py`** to find `effects.yaml` relative to new location.

### 2.4 Engine (from core → packages/core)

| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/engine/__init__.py` | `packages/core/src/wallpaper_effects/engine/__init__.py` |
| `core/src/wallpaper_processor/engine/executor.py` | `packages/core/src/wallpaper_effects/engine/executor.py` |
| `core/src/wallpaper_processor/engine/chain.py` | `packages/core/src/wallpaper_effects/engine/chain.py` |
| `core/src/wallpaper_processor/engine/batch.py` | `packages/core/src/wallpaper_effects/engine/batch.py` |

**Import updates required**:
- `from wallpaper_processor` → `from wallpaper_effects`
- `from wallpaper_processor.config` → `from wallpaper_effects.loader` / `from wallpaper_effects.models`

### 2.5 Console (from core → packages/core)

| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/console/__init__.py` | `packages/core/src/wallpaper_effects/console/__init__.py` |
| `core/src/wallpaper_processor/console/output.py` | `packages/core/src/wallpaper_effects/console/output.py` |
| `core/src/wallpaper_processor/console/progress.py` | `packages/core/src/wallpaper_effects/console/progress.py` |

**Import updates required**:
- `from wallpaper_processor.config` → `from wallpaper_effects.models`

### 2.6 CLI (from core → packages/core)

| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/cli/__init__.py` | `packages/core/src/wallpaper_effects/cli/__init__.py` |
| `core/src/wallpaper_processor/cli/main.py` | `packages/core/src/wallpaper_effects/cli/main.py` |
| `core/src/wallpaper_processor/cli/process.py` | `packages/core/src/wallpaper_effects/cli/process.py` |
| `core/src/wallpaper_processor/cli/batch.py` | `packages/core/src/wallpaper_effects/cli/batch.py` |
| `core/src/wallpaper_processor/cli/show.py` | `packages/core/src/wallpaper_effects/cli/show.py` |

**Import updates required**:
- All `wallpaper_processor` → `wallpaper_effects`
- Update CLI entry point function

### 2.7 Tests (from core → packages/core)

| Source | Destination |
|--------|-------------|
| `core/tests/*.py` | `packages/core/tests/` |
| `core/tests/conftest.py` | `packages/core/tests/conftest.py` |

**Import updates**: All test imports need updating.

---

## Phase 3: Create Package Configuration Files

### 3.1 Core pyproject.toml

Create `packages/core/pyproject.toml` with:
- name: `wallpaper-effects-core`
- version: `1.0.0`
- dependencies: pydantic, pyyaml, typer, rich
- script: `wallpaper-effects = "wallpaper_effects.cli.main:main"`
- hatch wheel packages: `["src/wallpaper_effects"]`

### 3.2 Orchestrator pyproject.toml

Create `packages/orchestrator/pyproject.toml` with:
- name: `wallpaper-effects-orchestrator`
- version: `1.0.0`
- dependencies: wallpaper-effects-core, container-manager, typer, rich
- script: `wallpaper-effects = "wallpaper_effects_orchestrator.cli.main:main"`
- hatch wheel packages: `["src/wallpaper_effects_orchestrator"]`
- uv.sources for dev dependencies

### 3.3 README files

Create `packages/core/README.md` and `packages/orchestrator/README.md`.

---

## Phase 4: Create Orchestrator Package

### 4.1 Container module

Create new files:
- `packages/orchestrator/src/wallpaper_effects_orchestrator/container/__init__.py`
- `packages/orchestrator/src/wallpaper_effects_orchestrator/container/dockerfile.py`
- `packages/orchestrator/src/wallpaper_effects_orchestrator/container/image.py`
- `packages/orchestrator/src/wallpaper_effects_orchestrator/container/runner.py`

### 4.2 CLI module

Create new files:
- `packages/orchestrator/src/wallpaper_effects_orchestrator/cli/__init__.py`
- `packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py` (delegates to core)
- `packages/orchestrator/src/wallpaper_effects_orchestrator/cli/container.py`

---

## Phase 5: Update Root Project Files

### 5.1 Update Makefile

Change all paths:
- `core/` → `packages/core/`
- `orchestrator/` → `packages/orchestrator/`
- Remove `shared/` references

### 5.2 Update .gitignore

Add new venv paths if needed.

---

## Phase 6: Cleanup

### 6.1 Remove old directories

After verification:
```bash
rm -rf core/
rm -rf shared/
rm -rf reference/
```

### 6.2 Commit changes

```bash
git add packages/ Makefile
git commit -m "feat: restructure to core/orchestrator packages"
```

---

## Verification Checklist

### Core Package

- [ ] `cd packages/core && uv sync` succeeds
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run wallpaper-effects --help` shows commands
- [ ] `uv run wallpaper-effects show effects` lists effects
- [ ] `uv run wallpaper-effects process effect test.jpg out.jpg -e blur` works
- [ ] Python import works:
  ```python
  from wallpaper_effects import ConfigLoader, CommandExecutor
  ConfigLoader.load_effects()
  ```

### Orchestrator Package

- [ ] `cd packages/orchestrator && uv sync` succeeds
- [ ] `uv run wallpaper-effects --help` shows container subcommand
- [ ] `uv run wallpaper-effects show effects` works (delegated)
- [ ] `uv run wallpaper-effects container --help` shows container commands
- [ ] `uv run wallpaper-effects version` shows both versions

### Container Operations

- [ ] `uv run wallpaper-effects container build` creates image
- [ ] `docker images` / `podman images` shows `wallpaper-effects:latest`
- [ ] `uv run wallpaper-effects container status` works

---

## Rollback Plan

If issues arise:
1. `git checkout HEAD~1` to revert
2. Or restore from backup archive
