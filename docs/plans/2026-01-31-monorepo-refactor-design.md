# Wallpaper Effects Generator - Monorepo Refactor Design

**Date:** 2026-01-31
**Status:** Preliminary - Awaiting Settings Audit
**Architecture Reference:** `.archive/GENERIC_ARCHITECTURE.md`

---

## Overview

Refactor the wallpaper effects generator into a 3-package monorepo following the generic Core + Orchestrator architecture pattern:

1. **`layered_settings`** - Generic, reusable layered configuration system supporting TOML and YAML
2. **`wallpaper_core`** - Wallpaper effects processor with CLI (`wallpaper-process`)
3. **`wallpaper_orchestrator`** - Container wrapper around core (future implementation)

---

## Decisions Made

### 1. File Format Strategy
**Decision:** Keep effects as YAML, settings as TOML, with the settings module handling both.

**Rationale:**
- Effects.yaml is working well with user customizations
- YAML is better for command templates (multiline strings)
- TOML is better for configuration hierarchies
- Settings module abstracts both formats behind unified API

### 2. Package Structure
**Decision:** Create `packages/` directory with three packages in uv workspace.

**Structure:**
```
wallpaper-effects-generator/
├── packages/
│   ├── settings/      # layered_settings
│   ├── core/          # wallpaper_core
│   └── orchestrator/  # wallpaper_orchestrator
└── pyproject.toml     # workspace root
```

**Rationale:**
- Follows uv workspace conventions
- Clear separation of concerns
- Each package is independently testable

### 3. Package Naming
**Decision:**
- `layered_settings` (generic, reusable)
- `wallpaper_core` (domain-specific)
- `wallpaper_orchestrator` (domain-specific)

**Rationale:**
- Settings package is generic enough to extract/reuse in other projects
- Could publish `layered_settings` separately later
- Core and orchestrator clearly belong to this project

### 4. CLI Entry Points
**Decision:** Both core and orchestrator use `wallpaper-process` command.

**Behavior:**
- Installing only core: `wallpaper-process` runs core CLI
- Installing orchestrator: `wallpaper-process` runs orchestrator CLI (overwrites core)
- Orchestrator wraps/extends core functionality

**Rationale:**
- Simpler, cleaner name than `wallpaper-effects-process`
- Follows architecture pattern (same command, orchestrator overwrites)
- Users get appropriate version based on what they install

### 5. Namespace Organization
**Decision:** Separate namespaces for different config sources.

**Namespaces:**
- `config.core` - from `core/config/settings.toml` (execution, output, paths)
- `config.effects` - from `core/effects/effects.yaml` (effect definitions)
- `config.orchestrator` - from `orchestrator/config/settings.toml` (container settings)

**Rationale:**
- Cleaner separation of concerns
- Effects are conceptually different from execution settings
- Easier to understand: `config.effects.blur` vs `config.core.effects.blur`
- More flexible for future additions

### 6. Effects vs Settings Ownership
**Decision:** Effects.yaml is the single source of truth for all effect definitions.

**What goes where:**
- `effects.yaml` - effect definitions, composites, presets, parameter defaults
- `settings.toml` (core) - execution settings, output settings, path settings

**Migration:**
- Remove `[defaults.*]` and `[presets.*]` sections from current `core/config/settings.toml`
- Keep all effect definitions in `effects.yaml`

**Rationale:**
- Single source of truth prevents confusion
- Effects.yaml has richer schema for effect definitions
- Settings.toml focuses on runtime behavior

### 7. Effects.yaml Location
**Decision:** Keep effects in separate `effects/` directory.

**Structure:**
```
core/
├── src/wallpaper_core/
│   └── config/
│       └── settings.toml
└── effects/
    └── effects.yaml
```

**Rationale:**
- Effects are substantial and domain-specific
- Keeps config/ focused on runtime settings
- Easier to find and edit
- Matches current working structure

### 8. Implementation Approach
**Decision:** Sequential build - settings → core → orchestrator.

**Phases:**
1. **Phase 1:** Create `packages/settings/` (layered_settings package)
   - Implement generic layered config loader
   - Support TOML and YAML
   - Registry pattern, merge algorithm, layer discovery

2. **Phase 2:** Create `packages/core/` (migrate from current core/)
   - Integrate layered_settings from day one
   - Register both settings.toml and effects.yaml
   - Migrate working processor code

3. **Phase 3:** Build `packages/orchestrator/` (new implementation)
   - Container management
   - Wraps core functionality

**Rationale:**
- Clear milestones, test each package independently
- Less risk of breaking working code
- Working reusable settings package as first deliverable

---

## Package Details

### Package 1: layered_settings

**Purpose:** Generic layered configuration system supporting multiple file formats.

**Module Structure:**
```
packages/settings/
├── src/layered_settings/
│   ├── __init__.py         # Public API: configure, get_config, SchemaRegistry
│   ├── registry.py         # Schema registration
│   ├── loader.py           # File loading (TOML/YAML detection and parsing)
│   ├── merger.py           # Deep merge algorithm
│   ├── builder.py          # Build validated Pydantic config
│   ├── layers.py           # Layer discovery (package, project, user, CLI)
│   └── errors.py           # Error hierarchy
├── tests/
│   ├── test_registry.py
│   ├── test_loader.py
│   ├── test_merger.py
│   └── test_integration.py
└── pyproject.toml
```

**Key Features:**
- Format-agnostic schema registry
- Automatic file format detection (by extension)
- Layered config merging (package → project → user → CLI)
- Pydantic validation
- Zero domain knowledge (completely generic)

**Layer Priority:**
```
1. Package defaults     packages/core/config/settings.toml         (flat sections)
                        packages/core/effects/effects.yaml         (flat structure)
2. Project root         ./settings.toml                            (namespaced)
3. User config          ~/.config/wallpaper-effects/settings.toml  (namespaced)
4. CLI arguments        Applied via overrides dict
```

**TOML Format Examples:**

Package defaults (flat):
```toml
# packages/core/config/settings.toml
[execution]
parallel = true
strict = true
max_workers = 0

[output]
verbosity = 1
format = "preserve"
quality = 90
```

Project/User config (namespaced):
```toml
# ./settings.toml or ~/.config/wallpaper-effects/settings.toml
[core.execution]
parallel = false
max_workers = 4

[core.output]
verbosity = 2

[orchestrator.container]
engine = "podman"
```

### Package 2: wallpaper_core

**Purpose:** Wallpaper effects processor with CLI.

**Module Structure:**
```
packages/core/
├── src/wallpaper_core/
│   ├── __init__.py             # Version, public exports
│   ├── config/
│   │   ├── __init__.py         # Register schemas with layered_settings
│   │   ├── schema.py           # Pydantic models for settings
│   │   └── settings.toml       # Package defaults
│   ├── effects/
│   │   ├── __init__.py         # Register effects schema
│   │   └── schema.py           # Pydantic models for effects
│   ├── cli/
│   │   ├── main.py             # Typer CLI entry point
│   │   ├── process.py          # Process commands
│   │   ├── batch.py            # Batch commands
│   │   └── show.py             # Show commands
│   ├── engine/                 # Migrated from current core
│   │   ├── executor.py
│   │   ├── chain.py
│   │   └── batch.py
│   ├── console/                # Migrated from current core
│   │   ├── output.py
│   │   └── progress.py
│   └── [other modules from current core]
├── effects/
│   └── effects.yaml            # Effect definitions
├── tests/
└── pyproject.toml
```

**Schema Registration:**
```python
# packages/core/src/wallpaper_core/config/__init__.py
from pathlib import Path
from layered_settings import SchemaRegistry
from wallpaper_core.config.schema import CoreSettings

SchemaRegistry.register(
    namespace="core",
    model=CoreSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

# packages/core/src/wallpaper_core/effects/__init__.py
from pathlib import Path
from layered_settings import SchemaRegistry
from wallpaper_core.effects.schema import EffectsConfig

# Note: effects.yaml is outside src/, so path goes up to package root
_package_root = Path(__file__).parent.parent.parent.parent
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_package_root / "effects" / "effects.yaml",
)
```

**CLI Bootstrap:**
```python
# packages/core/src/wallpaper_core/cli/main.py
from layered_settings import configure, get_config
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig
from pydantic import BaseModel

class CoreOnlyConfig(BaseModel):
    """Config for standalone core usage."""
    core: CoreSettings
    effects: EffectsConfig

configure(CoreOnlyConfig)

app = typer.Typer()

@app.command()
def process(...):
    config = get_config()
    # Access: config.core.execution.parallel
    #         config.effects.blur.parameters
```

**Dependencies:**
```toml
# packages/core/pyproject.toml
[project]
name = "wallpaper-core"
version = "0.3.0"
dependencies = [
    "layered-settings>=0.1.0",
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
wallpaper-process = "wallpaper_core.cli.main:app"

[tool.uv.sources]
layered-settings = { path = "../settings", editable = true }
```

### Package 3: wallpaper_orchestrator

**Purpose:** Container wrapper around core (future implementation).

**Module Structure:**
```
packages/orchestrator/
├── src/wallpaper_orchestrator/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py         # Register schema
│   │   ├── schema.py           # OrchestratorSettings
│   │   ├── settings.toml       # Package defaults
│   │   └── unified.py          # UnifiedConfig composition
│   ├── cli/
│   │   └── main.py             # CLI (wraps/extends core)
│   └── [orchestration modules]
├── tests/
└── pyproject.toml
```

**UnifiedConfig:**
```python
# packages/orchestrator/src/wallpaper_orchestrator/config/unified.py
from pydantic import BaseModel, Field
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_orchestrator.config.schema import OrchestratorSettings

class UnifiedConfig(BaseModel):
    """Root config composing all namespaces."""
    core: CoreSettings = Field(default_factory=CoreSettings)
    effects: EffectsConfig = Field(default_factory=EffectsConfig)
    orchestrator: OrchestratorSettings = Field(default_factory=OrchestratorSettings)
```

**CLI Bootstrap:**
```python
# packages/orchestrator/src/wallpaper_orchestrator/cli/main.py
from layered_settings import configure, get_config
from wallpaper_orchestrator.config.unified import UnifiedConfig

configure(UnifiedConfig)

app = typer.Typer()

@app.command()
def process(...):
    config = get_config()
    # Access: config.core.execution.parallel
    #         config.effects.blur
    #         config.orchestrator.container.engine
```

**Dependencies:**
```toml
# packages/orchestrator/pyproject.toml
[project]
name = "wallpaper-orchestrator"
version = "0.1.0"
dependencies = [
    "wallpaper-core>=0.3.0",
    "layered-settings>=0.1.0",
]

[project.scripts]
wallpaper-process = "wallpaper_orchestrator.cli.main:app"

[tool.uv.sources]
wallpaper-core = { path = "../core", editable = true }
layered-settings = { path = "../settings", editable = true }
```

---

## TODO: Settings Audit

**STATUS: NOT YET COMPLETED**

Before finalizing the core settings schema, we need to audit the current implementation to identify all settings actually used.

### Audit Objectives

1. **Identify all config access points:**
   - Where is config/settings accessed in the code?
   - What values are actually read?
   - Are there CLI arguments that affect behavior?

2. **Compare schema vs. usage:**
   - What does `config/settings.py` define?
   - What's actually used vs. defined?
   - Any hardcoded values that should be configurable?

3. **Catalog current settings:**
   - Execution settings (parallel, strict, max_workers, etc.)
   - Output settings (verbosity, format, quality, etc.)
   - Path settings (effects_config, user_effects_dir, output_dir?, etc.)
   - Backend settings (from old settings.toml)?
   - Any other settings?

4. **Identify missing settings:**
   - Output directory configuration
   - Metadata writing preferences
   - Error handling behavior
   - Any other configurable behavior currently hardcoded?

### Recommended Audit Approach

Use the Explore agent to systematically examine the current core:

```
Task: Audit current core settings usage

Areas to investigate:
1. All imports/uses of config or settings modules
2. CLI argument definitions (typer.Option, typer.Argument)
3. Hardcoded paths or configuration values
4. Environment variable usage
5. Default values in function signatures
6. Current Settings Pydantic model vs. actual usage
```

### Expected Output

A comprehensive list of settings organized by category:

**Execution Settings:**
- [ ] parallel (bool) - Run batch operations in parallel
- [ ] strict (bool) - Abort on first failure
- [ ] max_workers (int) - Max parallel workers
- [ ] ... (identify from audit)

**Output Settings:**
- [ ] verbosity (int/enum) - Output verbosity level
- [ ] format (str) - Output format
- [ ] quality (int) - Quality for lossy formats
- [ ] output_dir (Path?) - Default output directory?
- [ ] write_metadata (bool?) - Write metadata.json?
- [ ] ... (identify from audit)

**Path Settings:**
- [ ] effects_config (Path?) - Custom effects.yaml path
- [ ] user_effects_dir (Path?) - User-defined effects directory
- [ ] ... (identify from audit)

**Other Settings:**
- [ ] ... (identify from audit)

### Next Steps After Audit

1. Update `packages/core/config/schema.py` with complete settings models
2. Update `packages/core/config/settings.toml` with all defaults
3. Ensure CLI arguments map to config overrides
4. Update this design document with final settings schema

---

## Migration Notes

### Current Core State

**Working:**
- Effects.yaml layered loading (package → user → user/effects.d/)
- ImageMagick effect processing
- CLI commands (process, batch, show)
- Parallel execution

**Broken/Incomplete:**
- Settings.toml is NOT being read (orphaned file)
- Code only reads settings.yaml from user config
- Settings schema doesn't match settings.toml structure

### Migration Strategy

1. **Preserve current core:** Keep `core/` directory until migration complete
2. **Build new packages in `packages/`:** Fresh start with proper architecture
3. **Migrate modules incrementally:** Move working code to new structure
4. **Test thoroughly:** Each module as it's migrated
5. **Cutover:** Delete old `core/`, update docs
6. **User migration:** Provide migration guide for user configs

### User Config Migration

Users with existing configs at `~/.config/wallpaper-effects/`:

**Current files:**
- `settings.yaml` (currently used, but incomplete schema)
- `effects.yaml` (currently used, working)
- `effects.d/*.yaml` (currently used, working)

**New files (after migration):**
- `settings.toml` (replaces settings.yaml, TOML format)
- `effects.yaml` (unchanged, same format)
- `effects.d/*.yaml` (unchanged, same format)

**Migration path:**
- Provide conversion tool: `wallpaper-process migrate-config`
- Auto-detect old YAML format, convert to new TOML
- Preserve effects.yaml as-is

---

## Error Handling

### Settings Package Errors

```python
# layered_settings/errors.py
class SettingsError(Exception):
    """Base for all settings errors."""

class SettingsFileError(SettingsError):
    """File parse error (TOML/YAML syntax)."""

class SettingsValidationError(SettingsError):
    """Pydantic validation failed."""

class SettingsRegistryError(SettingsError):
    """Namespace conflict or not registered."""
```

### Core Package Errors

```python
# wallpaper_core/errors.py
class CoreError(Exception):
    """Base for all core errors."""

class ConfigError(CoreError):
    """Configuration error."""

class EffectError(CoreError):
    """Effect execution error."""

class ProcessorError(CoreError):
    """Image processing error."""
```

---

## Testing Strategy

### Settings Package Tests

- [ ] Registry: registration, conflicts, retrieval
- [ ] Loader: TOML parsing, YAML parsing, format detection
- [ ] Merger: deep merge algorithm, edge cases
- [ ] Layers: discovery, priority, file resolution
- [ ] Integration: end-to-end config loading with validation
- [ ] Edge cases: missing files, invalid syntax, validation errors

### Core Package Tests

- [ ] Config registration: schemas register correctly
- [ ] Settings loading: layered TOML loading works
- [ ] Effects loading: layered YAML loading works
- [ ] CLI: commands work with config
- [ ] Processor: effects execute correctly (migrate existing tests)
- [ ] Integration: full workflow tests

### Orchestrator Package Tests

- [ ] UnifiedConfig: composition works
- [ ] CLI: wraps core correctly
- [ ] Container management: (when implemented)

---

## Open Questions

1. **Settings audit completion** - Need to identify all actual settings used (see TODO section)
2. **User migration timing** - When to deprecate old YAML settings format?
3. **Backward compatibility** - How long to support old config locations?
4. **Documentation** - Update all docs to reflect new structure?

---

## Next Actions

### Immediate (Before Implementation)

1. **Complete settings audit** (using Explore agent)
2. **Finalize core settings schema** based on audit results
3. **Update this document** with complete settings list

### Implementation (Phase 1: Settings Package)

1. Create `packages/settings/` directory structure
2. Implement registry module
3. Implement loader module (TOML/YAML)
4. Implement merger module
5. Implement layers module
6. Implement builder module
7. Write comprehensive tests
8. Document public API

### Implementation (Phase 2: Core Migration)

1. Create `packages/core/` directory structure
2. Define settings and effects Pydantic schemas
3. Implement schema registration
4. Migrate processor engine modules
5. Migrate CLI modules
6. Write tests
7. Test against real wallpapers

### Implementation (Phase 3: Orchestrator)

1. Define orchestrator settings schema
2. Create UnifiedConfig
3. Implement CLI wrapper
4. Implement container management
5. Write tests

---

## References

- Architecture: `.archive/GENERIC_ARCHITECTURE.md`
- Current core: `core/`
- Current effects: `core/effects/effects.yaml`
- Current settings (orphaned): `core/config/settings.toml`

---

## Revision History

- **2026-01-31:** Initial design document created
  - Captured all architectural decisions
  - Identified need for settings audit before proceeding
  - Defined three-phase implementation approach
