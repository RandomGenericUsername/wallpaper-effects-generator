# AI Implementation Guide: Wallpaper Effects Migration

> **Purpose**: This document provides explicit instructions for AI assistants to correctly implement the package restructure. Follow these rules EXACTLY to avoid costly mistakes.

---

## ⛔ MANDATORY AI BEHAVIOR PROTOCOL

### YOU ARE NOT ALLOWED TO:
1. **Make design decisions** — All decisions come from docs or the user
2. **Assume anything** — If it's not in docs/tests/code, ASK
3. **Rewrite existing code** — COPY and update imports ONLY
4. **Change frameworks** — Typer, Pydantic, Rich are LOCKED
5. **Skip verification gates** — Every gate MUST pass before proceeding
6. **Create new abstractions** — No new classes/patterns unless docs specify
7. **Simplify or "improve"** — The code works; preserve it exactly
8. **Proceed when uncertain** — STOP and ASK the user

### YOU MUST:
1. **Read source files BEFORE writing** — Use `git show HEAD:<path>`
2. **Verify line counts after copy** — Should match within ±10 lines
3. **Run validation commands** — Every phase has mandatory checks
4. **Report verification results** — Show user what passed/failed
5. **Ask for clarification** — When ANYTHING is ambiguous
6. **Quote the doc** — Reference which doc section you're following

---

## 🔒 VERIFICATION GATE SYSTEM

### How Gates Work:
1. Each phase ends with a **VERIFICATION GATE**
2. Gates contain specific commands that MUST be run
3. **ALL checks must pass** to proceed to next phase
4. If ANY check fails → **STOP and report to user**
5. User must explicitly approve proceeding

### Gate Failure Protocol:
```
IF gate fails:
  1. Report EXACTLY which check failed
  2. Show the actual vs expected output
  3. DO NOT attempt to fix without user input
  4. ASK: "How should I proceed?"
```

---

## ❓ DECISION TREE: WHEN TO ASK

### ASK the user when:
- [ ] A file to copy doesn't exist at expected path
- [ ] Import path is ambiguous (multiple possible targets)
- [ ] A class/function is referenced but not found
- [ ] Tests reference code that doesn't match docs
- [ ] Line count differs by more than 20% after copy
- [ ] Any verification command fails
- [ ] Docs say one thing, code does another
- [ ] You need to create a NEW file not mentioned in docs
- [ ] You're unsure which doc section applies
- [ ] Framework/library choice seems wrong

### DO NOT ASK, just do it:
- [ ] Copying a file that exists exactly where docs say
- [ ] Import replacement that's explicitly listed
- [ ] Running verification commands
- [ ] Creating directories listed in target structure

---

## 🚨 CRITICAL RULES - READ FIRST

### Rule 1: COPY, DON'T REWRITE
```
❌ WRONG: "I'll create a new implementation of the config loader"
✅ RIGHT: "I'll copy the existing config_loader.py and update its imports"
```

**The existing code is WORKING and TESTED. Your job is to MOVE it, not REPLACE it.**

### Rule 2: PRESERVE FRAMEWORKS
The project uses these frameworks - DO NOT CHANGE THEM:
| Component | Framework | DO NOT USE |
|-----------|-----------|------------|
| CLI | **Typer** | ~~Click~~, ~~argparse~~ |
| Models | **Pydantic BaseModel** | ~~dataclass~~, ~~attrs~~ |
| Output | **Rich** | ~~print()~~, ~~logging~~ |
| Config | **PyYAML** | Keep as-is |

### Rule 3: VERIFY BEFORE PROCEEDING
After EACH phase, run verification commands. Do not proceed if verification fails.

### Rule 4: ASK IF UNCERTAIN
If any instruction is unclear, ASK the user rather than making assumptions.

---

## 🔄 CONTINUOUS VERIFICATION PROTOCOL

### Before EVERY File Operation:

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE WRITING ANY FILE, COMPLETE THIS CHECKLIST:         │
├─────────────────────────────────────────────────────────────┤
│  □ 1. Did I READ the source file first? (git show HEAD:)   │
│  □ 2. Is this file listed in the migration table?          │
│  □ 3. Are import replacements EXPLICITLY listed?           │
│  □ 4. Am I COPYING (not rewriting)?                        │
│  □ 5. Will I verify line count after?                      │
│                                                             │
│  IF ANY BOX IS UNCHECKED → STOP AND ASK USER               │
└─────────────────────────────────────────────────────────────┘
```

### After EVERY File Operation:

```bash
# Immediately verify the file was copied correctly
wc -l <source_file>      # Note original line count
wc -l <destination_file> # Compare - should be within ±10 lines

# Verify key patterns are preserved
grep -c "BaseModel" <file>      # For model files
grep -c "typer" <file>          # For CLI files  
grep -c "from rich" <file>      # For console files
```

### Phase Gate Template:

```
╔═══════════════════════════════════════════════════════════════╗
║  🚧 VERIFICATION GATE: PHASE [N] COMPLETE                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  MANDATORY CHECKS (run ALL, report ALL results):              ║
║                                                               ║
║  1. [ ] Check 1 command → Expected: X                         ║
║  2. [ ] Check 2 command → Expected: Y                         ║
║  3. [ ] Check 3 command → Expected: Z                         ║
║                                                               ║
║  GATE STATUS: □ ALL PASSED  □ SOME FAILED                     ║
║                                                               ║
║  IF ANY FAILED:                                               ║
║    → STOP immediately                                         ║
║    → Report which check failed                                ║
║    → Show actual vs expected output                           ║
║    → ASK: "Check [N] failed. Actual: [X]. Expected: [Y].      ║
║           How should I proceed?"                              ║
║                                                               ║
║  IF ALL PASSED:                                               ║
║    → Report: "Gate [N] passed. Proceeding to Phase [N+1]"     ║
║    → WAIT for user confirmation before proceeding             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 🛡️ ANTI-DEVIATION SAFEGUARDS

### Safeguard 1: Source-First Reading
**BEFORE writing ANY destination file:**
```bash
# ALWAYS read source first to understand what you're copying
git show HEAD:<source_path> | head -50  # Check structure
git show HEAD:<source_path> | wc -l     # Note line count
```

### Safeguard 2: Framework Fingerprint Check
**AFTER writing files, verify correct frameworks:**
```bash
# Models MUST use Pydantic
grep -r "from pydantic" packages/core/src/wallpaper_effects/models/
# Expected: Multiple matches

# Models must NOT use dataclass for main models
grep -r "@dataclass" packages/core/src/wallpaper_effects/models/*.py
# Expected: 0 matches (dataclass only in engine for results)

# CLI MUST use Typer
grep -r "import typer" packages/core/src/wallpaper_effects/cli/
# Expected: Multiple matches

# CLI must NOT use Click
grep -r "import click" packages/core/src/wallpaper_effects/cli/
# Expected: 0 matches

# Console MUST use Rich
grep -r "from rich" packages/core/src/wallpaper_effects/console/
# Expected: Multiple matches
```

### Safeguard 3: Content Integrity Check
**AFTER copying effects.yaml:**
```bash
# Count effects - MUST have 9+ effects
grep -c "^  [a-z_]*:" packages/core/src/wallpaper_effects/data/effects.yaml
# Expected: 15+ (effects + composites + presets sections)

# Verify specific effects exist
grep -E "^  (blur|blackwhite|negate|brightness|contrast|saturation|sepia|vignette|color_overlay):" \
  packages/core/src/wallpaper_effects/data/effects.yaml | wc -l
# Expected: 9
```

### Safeguard 4: Import Consistency Check
**AFTER updating imports in a module:**
```bash
# No old import paths should remain
grep -r "wallpaper_processor" packages/core/src/
# Expected: 0 matches

grep -r "wallpaper_effects_shared" packages/core/src/
# Expected: 0 matches
```

---

## 📋 MANDATORY QUESTIONS BEFORE PROCEEDING

At each phase transition, the AI MUST ask these questions if anything is unclear:

### Phase 1 → Phase 2 Transition:
> "I've created the directory structure. Before copying files:
> 1. The source models are in `shared/src/wallpaper_effects_shared/models/` - is this correct?
> 2. The effects.yaml is in `shared/data/effects.yaml` - is this correct?
> 3. Should I proceed with the file migration?"

### Phase 2 → Phase 3 Transition:
> "I've copied all source files. Verification results:
> - Models: [X] files copied, all use Pydantic BaseModel
> - CLI: [X] files copied, all use Typer
> - effects.yaml: [X] effects loaded
> 
> Should I proceed to create pyproject.toml and __init__.py?"

### Phase 3 → Phase 4 Transition:
> "Core package configuration complete. Test results:
> - `uv sync`: [PASS/FAIL]
> - `pytest`: [X/Y] tests passed
> - `show effects`: [X] effects displayed
> 
> Should I proceed to orchestrator migration?"

### Phase 4 → Phase 5 Transition:
> "Orchestrator migration complete. Before final verification:
> - CLI delegates to core (not subprocess): [YES/NO]
> - Container module exists: [YES/NO]
> 
> Should I run final verification?"

---

## 📋 Pre-Implementation Checklist

Before starting ANY code changes, complete these steps:

### Step 1: Verify Working State
```bash
# Run from project root
cd /home/inumaki/Development/wallpaper-effects-generator

# Verify original code exists and works
git status  # Should show original core/, shared/, orchestrator/
cd core && uv sync && uv run pytest tests/ -v
cd ../shared && uv sync && uv run pytest tests/ -v
```

**STOP if tests fail. Report to user.**

### Step 2: Understand the Source Structure
Read and confirm understanding of these source locations:
```
ORIGINAL STRUCTURE (to copy FROM):
├── shared/src/wallpaper_effects_shared/
│   ├── models/          # Pydantic models
│   │   ├── __init__.py
│   │   ├── effects.py   # EffectDefinition, ChainStep, etc.
│   │   ├── config.py    # EffectsConfig
│   │   └── settings.py  # Settings, Verbosity
│   └── loader/          # ConfigLoader
│       ├── __init__.py
│       ├── config_loader.py
│       └── paths.py
├── shared/data/
│   └── effects.yaml     # FULL effects configuration (15+ effects)
├── core/src/wallpaper_processor/
│   ├── cli/             # Typer CLI (main, batch, process, show)
│   ├── console/         # Rich output (output.py, progress.py)
│   └── engine/          # Execution (executor, chain, batch)
└── orchestrator/src/wallpaper_effects/
    ├── cli/             # Typer CLI with container commands
    ├── services/        # Container services
    └── volume/          # Volume mount handling
```

### Step 3: Understand the Target Structure
```
TARGET STRUCTURE (to copy TO):
└── packages/
    ├── core/
    │   ├── pyproject.toml
    │   ├── src/wallpaper_effects/
    │   │   ├── __init__.py      # Public API exports
    │   │   ├── _version.py      # __version__ = "1.0.0"
    │   │   ├── models/          # FROM shared/
    │   │   ├── loader/          # FROM shared/
    │   │   ├── data/effects.yaml # FROM shared/data/
    │   │   ├── engine/          # FROM core/
    │   │   ├── console/         # FROM core/
    │   │   └── cli/             # FROM core/
    │   └── tests/               # FROM core/tests/
    └── orchestrator/
        ├── pyproject.toml
        ├── src/wallpaper_effects_orchestrator/
        │   ├── __init__.py
        │   ├── _version.py
        │   ├── cli/             # FROM orchestrator/ + new container cmds
        │   └── container/       # FROM orchestrator/services/
        └── tests/
```

---

## 🔧 Phase 1: Create Directory Structure

### Commands to Execute
```bash
cd /home/inumaki/Development/wallpaper-effects-generator

# Create core package structure
mkdir -p packages/core/src/wallpaper_effects/{models,loader,engine,console,cli,data}
mkdir -p packages/core/tests

# Create orchestrator package structure  
mkdir -p packages/orchestrator/src/wallpaper_effects_orchestrator/{container,cli}
mkdir -p packages/orchestrator/tests
```

### Verification
```bash
# Confirm structure exists
find packages -type d | head -20
```

**Expected output should show all directories created.**

### 🚧 VERIFICATION GATE 1: Directory Structure

```bash
# Run ALL of these checks:

# Check 1: Core directories exist
ls -la packages/core/src/wallpaper_effects/
# Expected: models/ loader/ engine/ console/ cli/ data/

# Check 2: Orchestrator directories exist  
ls -la packages/orchestrator/src/wallpaper_effects_orchestrator/
# Expected: container/ cli/

# Check 3: Test directories exist
ls -d packages/core/tests packages/orchestrator/tests
# Expected: Both directories exist
```

**GATE 1 CHECKLIST:**
- [ ] Check 1 passed (6 subdirectories in core)
- [ ] Check 2 passed (2 subdirectories in orchestrator)
- [ ] Check 3 passed (both test directories exist)

**⛔ IF ANY CHECK FAILS → STOP and report to user**
**✅ IF ALL PASS → Report results and ask: "Gate 1 passed. Proceed to Phase 2?"**

---

## 🔧 Phase 2: Migrate Core Package (COPY + UPDATE IMPORTS)

### 2.1 Models Migration

**Source → Destination mapping:**
| Source | Destination |
|--------|-------------|
| `shared/src/wallpaper_effects_shared/models/__init__.py` | `packages/core/src/wallpaper_effects/models/__init__.py` |
| `shared/src/wallpaper_effects_shared/models/effects.py` | `packages/core/src/wallpaper_effects/models/effects.py` |
| `shared/src/wallpaper_effects_shared/models/config.py` | `packages/core/src/wallpaper_effects/models/config.py` |
| `shared/src/wallpaper_effects_shared/models/settings.py` | `packages/core/src/wallpaper_effects/models/settings.py` |

**Process for EACH file:**
1. Read the ENTIRE source file using `git show HEAD:<path>`
2. Copy content EXACTLY
3. Apply ONLY these import replacements:
   - `from wallpaper_effects_shared.` → `from wallpaper_effects.`
   - `import wallpaper_effects_shared.` → `import wallpaper_effects.`
4. Write to destination
5. Verify file exists and has same line count (±5 lines for import changes)

**Example - effects.py:**
```bash
# Step 1: Read original
git show HEAD:shared/src/wallpaper_effects_shared/models/effects.py > /tmp/original.py

# Step 2: The file should contain Pydantic models like:
# - class ParameterType(BaseModel)
# - class ParameterDefinition(BaseModel)  
# - class EffectDefinition(BaseModel)
# - class ChainStep(BaseModel)
# - class CompositeDefinition(BaseModel)
# - class PresetDefinition(BaseModel)

# Step 3: Copy with import updates (if any needed)
# In this case, effects.py has no cross-module imports to update

# Step 4: Write to destination
# packages/core/src/wallpaper_effects/models/effects.py
```

**⚠️ VALIDATION CHECK:**
After copying models, verify Pydantic is used:
```bash
grep -l "BaseModel" packages/core/src/wallpaper_effects/models/*.py | wc -l
# Expected: At least 3 files should contain BaseModel
```

### 2.2 Loader Migration

**Source → Destination mapping:**
| Source | Destination |
|--------|-------------|
| `shared/src/wallpaper_effects_shared/loader/__init__.py` | `packages/core/src/wallpaper_effects/loader/__init__.py` |
| `shared/src/wallpaper_effects_shared/loader/config_loader.py` | `packages/core/src/wallpaper_effects/loader/config_loader.py` |
| `shared/src/wallpaper_effects_shared/loader/paths.py` | `packages/core/src/wallpaper_effects/loader/paths.py` |

**Import replacements needed:**
```python
# In config_loader.py:
# OLD:
from wallpaper_effects_shared.models.config import EffectsConfig
from wallpaper_effects_shared.models.settings import Settings

# NEW:
from wallpaper_effects.models.config import EffectsConfig
from wallpaper_effects.models.settings import Settings
```

**⚠️ CRITICAL for paths.py:**
Update the path calculation to find `effects.yaml` in new location:
```python
# The function get_package_effects_path() needs to return:
# packages/core/src/wallpaper_effects/data/effects.yaml
# 
# Original likely uses: Path(__file__).parent.parent / "data" / "effects.yaml"
# This should still work if data/ is sibling to loader/
```

### 2.3 Data Files Migration

```bash
# Copy effects.yaml (DO NOT MODIFY CONTENT)
cp shared/data/effects.yaml packages/core/src/wallpaper_effects/data/effects.yaml

# Verify it's the full file (should have 15+ effects)
grep -c "^  [a-z_]*:$" packages/core/src/wallpaper_effects/data/effects.yaml
# Expected: 15 or more
```

**⚠️ DO NOT create a new simplified effects.yaml. The original has:**
- Parameter type definitions
- 15+ atomic effects with command templates
- Composite effects (chains)
- Presets

### 2.4 Engine Migration

**Source → Destination mapping:**
| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/engine/__init__.py` | `packages/core/src/wallpaper_effects/engine/__init__.py` |
| `core/src/wallpaper_processor/engine/executor.py` | `packages/core/src/wallpaper_effects/engine/executor.py` |
| `core/src/wallpaper_processor/engine/chain.py` | `packages/core/src/wallpaper_effects/engine/chain.py` |
| `core/src/wallpaper_processor/engine/batch.py` | `packages/core/src/wallpaper_effects/engine/batch.py` |

**Import replacements needed:**
```python
# OLD:
from wallpaper_processor.config import ...
from wallpaper_processor.console.output import RichOutput
from wallpaper_processor.engine.executor import CommandExecutor

# NEW:
from wallpaper_effects.loader import ...       # or wallpaper_effects.models
from wallpaper_effects.console.output import RichOutput
from wallpaper_effects.engine.executor import CommandExecutor
```

**⚠️ VALIDATION CHECK:**
```bash
# executor.py should have ExecutionResult dataclass and CommandExecutor class
grep -E "class (ExecutionResult|CommandExecutor)" packages/core/src/wallpaper_effects/engine/executor.py
# Expected: 2 matches
```

### 2.5 Console Migration

**Source → Destination mapping:**
| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/console/__init__.py` | `packages/core/src/wallpaper_effects/console/__init__.py` |
| `core/src/wallpaper_processor/console/output.py` | `packages/core/src/wallpaper_effects/console/output.py` |
| `core/src/wallpaper_processor/console/progress.py` | `packages/core/src/wallpaper_effects/console/progress.py` |

**Import replacements:**
```python
# OLD:
from wallpaper_processor.config import Verbosity

# NEW:
from wallpaper_effects.models import Verbosity
# OR
from wallpaper_effects.models.settings import Verbosity
```

**⚠️ VALIDATION CHECK:**
```bash
# Should use Rich library
grep -l "from rich" packages/core/src/wallpaper_effects/console/*.py | wc -l
# Expected: 2 (output.py and progress.py)
```

### 2.6 CLI Migration

**Source → Destination mapping:**
| Source | Destination |
|--------|-------------|
| `core/src/wallpaper_processor/cli/__init__.py` | `packages/core/src/wallpaper_effects/cli/__init__.py` |
| `core/src/wallpaper_processor/cli/main.py` | `packages/core/src/wallpaper_effects/cli/main.py` |
| `core/src/wallpaper_processor/cli/process.py` | `packages/core/src/wallpaper_effects/cli/process.py` |
| `core/src/wallpaper_processor/cli/batch.py` | `packages/core/src/wallpaper_effects/cli/batch.py` |
| `core/src/wallpaper_processor/cli/show.py` | `packages/core/src/wallpaper_effects/cli/show.py` |

**Import replacements:**
```python
# OLD:
from wallpaper_processor.cli.batch import batch_app
from wallpaper_processor.config import ConfigLoader, Verbosity
from wallpaper_processor.console.output import RichOutput

# NEW:
from wallpaper_effects.cli.batch import batch_app
from wallpaper_effects.loader import ConfigLoader
from wallpaper_effects.models import Verbosity
from wallpaper_effects.console.output import RichOutput
```

**⚠️ CRITICAL VALIDATION:**
```bash
# CLI MUST use Typer, NOT Click
grep -l "import typer" packages/core/src/wallpaper_effects/cli/*.py | wc -l
# Expected: All CLI files (4-5 files)

# Should NOT have Click
grep -l "import click" packages/core/src/wallpaper_effects/cli/*.py | wc -l
# Expected: 0
```

### 2.7 Tests Migration

```bash
# Copy all test files
cp -r core/tests/* packages/core/tests/

# Update imports in test files
# wallpaper_processor → wallpaper_effects
```

### 🚧 VERIFICATION GATE 2: Core Files Migration

```bash
# Run ALL of these checks:

# Check 1: Models use Pydantic (NOT dataclass for models)
grep -l "BaseModel" packages/core/src/wallpaper_effects/models/*.py | wc -l
# Expected: 3 or more files

# Check 2: CLI uses Typer (NOT Click)
grep -l "import typer" packages/core/src/wallpaper_effects/cli/*.py | wc -l
# Expected: 4 or more files

grep -l "import click" packages/core/src/wallpaper_effects/cli/*.py | wc -l
# Expected: 0

# Check 3: Console uses Rich
grep -l "from rich" packages/core/src/wallpaper_effects/console/*.py | wc -l
# Expected: 2 files

# Check 4: effects.yaml has all effects
grep -c "^  [a-z_]*:" packages/core/src/wallpaper_effects/data/effects.yaml
# Expected: 15 or more entries

# Check 5: No old import paths remain
grep -r "wallpaper_processor\|wallpaper_effects_shared" packages/core/src/ | wc -l
# Expected: 0

# Check 6: Key classes exist
grep -l "class ConfigLoader" packages/core/src/wallpaper_effects/loader/*.py
# Expected: config_loader.py

grep -l "class CommandExecutor" packages/core/src/wallpaper_effects/engine/*.py
# Expected: executor.py

grep -l "class RichOutput" packages/core/src/wallpaper_effects/console/*.py
# Expected: output.py
```

**GATE 2 CHECKLIST:**
- [ ] Check 1: Models use Pydantic (≥3 files)
- [ ] Check 2a: CLI uses Typer (≥4 files)
- [ ] Check 2b: CLI does NOT use Click (0 files)
- [ ] Check 3: Console uses Rich (2 files)
- [ ] Check 4: effects.yaml complete (≥15 entries)
- [ ] Check 5: No old imports (0 matches)
- [ ] Check 6: Key classes exist (all found)

**⛔ IF ANY CHECK FAILS → STOP and report:**
> "Gate 2 Check [N] failed. 
> Expected: [X]
> Actual: [Y]
> This indicates [problem description].
> How should I proceed?"

**✅ IF ALL PASS → Report: "Gate 2 passed. Proceed to Phase 3?"**

---

## 🔧 Phase 3: Create Package Configuration

### 3.1 Core pyproject.toml

Create `packages/core/pyproject.toml` with EXACTLY this content:

```toml
[project]
name = "wallpaper-effects-core"
version = "1.0.0"
description = "ImageMagick-based wallpaper effect processing"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.11.0",
    "ruff>=0.6.0",
]

[project.scripts]
wallpaper-effects = "wallpaper_effects.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_effects"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
pythonpath = ["src"]
```

**⚠️ NOTICE:**
- Entry point is `wallpaper_effects.cli.main:app` (Typer app object)
- Dependencies include `typer[all]` and `pydantic>=2.0`
- NO click dependency

### 3.2 Core __init__.py (Public API)

Create `packages/core/src/wallpaper_effects/__init__.py`:

```python
"""Wallpaper Effects - ImageMagick-based image effect processing."""

from wallpaper_effects._version import __version__

# Configuration
from wallpaper_effects.loader import ConfigLoader

# Models - Effects
from wallpaper_effects.models import (
    EffectDefinition,
    ParameterDefinition,
    ParameterType,
    ChainStep,
    CompositeDefinition,
    PresetDefinition,
    EffectsConfig,
)

# Models - Settings
from wallpaper_effects.models import (
    Settings,
    Verbosity,
    ExecutionSettings,
    OutputSettings,
    PathSettings,
)

# Engine
from wallpaper_effects.engine import (
    CommandExecutor,
    ChainExecutor,
    BatchGenerator,
    BatchResult,
    ExecutionResult,
)

# Console
from wallpaper_effects.console import RichOutput, BatchProgress

__all__ = [
    "__version__",
    # Loader
    "ConfigLoader",
    # Models - Effects
    "EffectDefinition",
    "ParameterDefinition", 
    "ParameterType",
    "ChainStep",
    "CompositeDefinition",
    "PresetDefinition",
    "EffectsConfig",
    # Models - Settings
    "Settings",
    "Verbosity",
    "ExecutionSettings",
    "OutputSettings",
    "PathSettings",
    # Engine
    "CommandExecutor",
    "ChainExecutor",
    "BatchGenerator",
    "BatchResult",
    "ExecutionResult",
    # Console
    "RichOutput",
    "BatchProgress",
]
```

### 3.3 Core _version.py

Create `packages/core/src/wallpaper_effects/_version.py`:

```python
__version__ = "1.0.0"
```

### 🚧 VERIFICATION GATE 3: Package Configuration

```bash
# Run ALL of these checks:

# Check 1: pyproject.toml has correct dependencies
grep -E "typer|pydantic|rich|pyyaml" packages/core/pyproject.toml | wc -l
# Expected: 4 (all four dependencies listed)

# Check 2: Entry point is correct
grep 'wallpaper-effects = "wallpaper_effects.cli.main:app"' packages/core/pyproject.toml
# Expected: Match found

# Check 3: __init__.py exports key classes
grep -E "ConfigLoader|CommandExecutor|EffectDefinition|RichOutput" packages/core/src/wallpaper_effects/__init__.py | wc -l
# Expected: 4 or more

# Check 4: Package installs correctly
cd packages/core && uv sync
# Expected: Resolves without errors

# Check 5: CLI runs
cd packages/core && uv run wallpaper-effects --help
# Expected: Shows help with process, batch, show subcommands
```

**GATE 3 CHECKLIST:**
- [ ] Check 1: All 4 dependencies in pyproject.toml
- [ ] Check 2: Entry point correctly configured
- [ ] Check 3: Public API exports key classes
- [ ] Check 4: `uv sync` succeeds
- [ ] Check 5: CLI shows help

**⛔ IF ANY CHECK FAILS → STOP and report to user**
**✅ IF ALL PASS → Report: "Gate 3 passed. Proceed to Phase 4?"**

---

## 🔧 Phase 4: Migrate Orchestrator Package

### 4.1 CLI Migration (with delegation)

The orchestrator CLI should:
1. Import core's Typer app
2. Add container subcommand group
3. Re-export combined CLI

**Create `packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py`:**

```python
"""Orchestrator CLI - extends core with container support."""

import typer

# Import core's CLI components directly (NOT via subprocess)
from wallpaper_effects.cli.main import app as core_app
from wallpaper_effects.cli.batch import batch_app
from wallpaper_effects.cli.process import process_app
from wallpaper_effects.cli.show import show_app

from wallpaper_effects_orchestrator.cli.container import container_app
from wallpaper_effects_orchestrator._version import __version__ as orchestrator_version
from wallpaper_effects import __version__ as core_version

# Create orchestrator app
app = typer.Typer(
    name="wallpaper-effects",
    help="Wallpaper Effects - Apply ImageMagick effects to images",
    no_args_is_help=True,
)

# Add core subcommands
app.add_typer(process_app, name="process")
app.add_typer(batch_app, name="batch")
app.add_typer(show_app, name="show")

# Add orchestrator-specific subcommand
app.add_typer(container_app, name="container")


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"wallpaper-effects-orchestrator v{orchestrator_version}")
    typer.echo(f"wallpaper-effects-core v{core_version}")


if __name__ == "__main__":
    app()
```

### 4.2 Container Module

Copy and adapt from `orchestrator/src/wallpaper_effects/services/`:
- `container_runner.py` → `packages/orchestrator/.../container/runner.py`
- `image_builder.py` → `packages/orchestrator/.../container/image.py`

### 4.3 Orchestrator pyproject.toml

```toml
[project]
name = "wallpaper-effects-orchestrator"
version = "1.0.0"
description = "Container orchestrator for wallpaper-effects-core"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "wallpaper-effects-core>=1.0.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
wallpaper-effects = "wallpaper_effects_orchestrator.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_effects_orchestrator"]

[tool.uv.sources]
wallpaper-effects-core = { path = "../core", editable = true }
```

### 🚧 VERIFICATION GATE 4: Orchestrator Migration

```bash
# Run ALL of these checks:

# Check 1: Orchestrator CLI imports core directly (NOT subprocess)
grep -E "from wallpaper_effects" packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py
# Expected: Multiple import lines from wallpaper_effects

grep "subprocess" packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py
# Expected: 0 matches (should NOT use subprocess for CLI delegation)

# Check 2: Uses Typer for CLI
grep "import typer" packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py
# Expected: Match found

# Check 3: Has container subcommand
grep "container" packages/orchestrator/src/wallpaper_effects_orchestrator/cli/main.py
# Expected: Match found

# Check 4: pyproject.toml depends on core
grep "wallpaper-effects-core" packages/orchestrator/pyproject.toml
# Expected: Match found

# Check 5: Package installs
cd packages/orchestrator && uv sync
# Expected: Resolves without errors
```

**GATE 4 CHECKLIST:**
- [ ] Check 1a: CLI imports from wallpaper_effects (direct import)
- [ ] Check 1b: CLI does NOT use subprocess for delegation
- [ ] Check 2: Uses Typer
- [ ] Check 3: Has container subcommand
- [ ] Check 4: Depends on wallpaper-effects-core
- [ ] Check 5: `uv sync` succeeds

**⛔ IF ANY CHECK FAILS → STOP and report to user**
**✅ IF ALL PASS → Report: "Gate 4 passed. Proceed to final verification?"**

---

## ✅ Phase 5: Verification

### 5.1 Core Package Verification

```bash
cd packages/core

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Test CLI
uv run wallpaper-effects --help
uv run wallpaper-effects show effects

# Test Python imports
uv run python -c "
from wallpaper_effects import ConfigLoader, CommandExecutor, EffectsConfig
config = ConfigLoader.load_effects()
print(f'Loaded {len(config.effects)} effects')
print(f'Effects: {list(config.effects.keys())[:5]}...')
"
```

**Expected output for Python import test:**
```
Loaded 15 effects
Effects: ['blur', 'blackwhite', 'negate', 'brightness', 'contrast']...
```

### 5.2 Orchestrator Package Verification

```bash
cd packages/orchestrator

# Install dependencies
uv sync

# Test CLI
uv run wallpaper-effects --help
# Should show: process, batch, show, container, version

uv run wallpaper-effects container --help
# Should show container subcommands

uv run wallpaper-effects version
# Should show both versions
```

### 🚧 VERIFICATION GATE 5: FINAL ACCEPTANCE

```bash
# Run ALL of these checks - THIS IS THE FINAL GATE

# ═══════════════════════════════════════════════════════════════
# CORE PACKAGE CHECKS
# ═══════════════════════════════════════════════════════════════

cd packages/core

# Check 1: Tests pass
uv run pytest tests/ -v --tb=short 2>&1 | tail -5
# Expected: "X passed" with 0 failures

# Check 2: CLI shows all subcommands
uv run wallpaper-effects --help | grep -E "process|batch|show"
# Expected: All three commands listed

# Check 3: Show effects works and shows 9+ effects
uv run wallpaper-effects show effects 2>&1 | grep -c "│"
# Expected: 9 or more (one row per effect)

# Check 4: Process command works
uv run wallpaper-effects process effect --help | grep -E "\-e|--effect"
# Expected: Effect flag documented

# Check 5: Python library API works
uv run python -c "
from wallpaper_effects import ConfigLoader, CommandExecutor, BatchGenerator
from wallpaper_effects import EffectDefinition, Settings, RichOutput
config = ConfigLoader.load_effects()
assert len(config.effects) >= 9, f'Expected 9+ effects, got {len(config.effects)}'
print(f'✓ API test passed: {len(config.effects)} effects loaded')
"
# Expected: "✓ API test passed: X effects loaded"

# ═══════════════════════════════════════════════════════════════
# ORCHESTRATOR PACKAGE CHECKS
# ═══════════════════════════════════════════════════════════════

cd ../orchestrator

# Check 6: CLI shows container subcommand
uv run wallpaper-effects --help | grep "container"
# Expected: container command listed

# Check 7: Container help works
uv run wallpaper-effects container --help
# Expected: Shows container subcommands (build, run, etc.)

# Check 8: Version shows both packages
uv run wallpaper-effects version
# Expected: Shows orchestrator AND core versions

# Check 9: Core commands still work through orchestrator
uv run wallpaper-effects show effects 2>&1 | head -5
# Expected: Same output as core's show effects

# ═══════════════════════════════════════════════════════════════
# INTEGRITY CHECKS
# ═══════════════════════════════════════════════════════════════

cd ../..

# Check 10: No old code remnants
ls -d core shared 2>/dev/null && echo "WARNING: Old directories still exist"
# Expected: No output (directories should be removed)

# Check 11: No framework violations
grep -r "import click" packages/*/src/ | wc -l
# Expected: 0

grep -r "@dataclass" packages/core/src/wallpaper_effects/models/*.py | wc -l  
# Expected: 0

# Check 12: Correct frameworks confirmed
grep -r "BaseModel" packages/core/src/wallpaper_effects/models/*.py | wc -l
# Expected: 3 or more

grep -r "import typer" packages/*/src/*/cli/*.py | wc -l
# Expected: 5 or more
```

**GATE 5 FINAL CHECKLIST:**

| # | Check | Expected | Actual | Pass? |
|---|-------|----------|--------|-------|
| 1 | Core tests pass | 0 failures | | |
| 2 | Core CLI subcommands | process, batch, show | | |
| 3 | Show effects count | ≥9 effects | | |
| 4 | Process help works | --effect flag shown | | |
| 5 | Python API works | ≥9 effects loaded | | |
| 6 | Container subcommand | Listed | | |
| 7 | Container help | Shows subcommands | | |
| 8 | Version command | Both versions | | |
| 9 | Delegated commands | Work correctly | | |
| 10 | Old dirs removed | Not found | | |
| 11 | No Click imports | 0 matches | | |
| 12 | Pydantic confirmed | ≥3 matches | | |

**⛔ IF ANY CHECK FAILS:**
> Report the full checklist with actual values
> Highlight which specific checks failed
> ASK: "Final gate has [N] failures. Details above. How should I proceed?"

**✅ IF ALL PASS:**
> "🎉 MIGRATION COMPLETE - All 12 final verification checks passed.
> 
> Summary:
> - Core: [X] tests passing, [Y] effects, CLI working
> - Orchestrator: Container commands available, delegation working
> - Integrity: No framework violations, old code removed
> 
> Ready to commit?"

---

## 🚫 Common Mistakes to AVOID

### Mistake 1: Rewriting Instead of Copying
```
❌ "I'll implement a simpler version of the config loader"
✅ "I'll copy config_loader.py and update the imports"
```

### Mistake 2: Changing Frameworks
```
❌ Using Click instead of Typer
❌ Using dataclass instead of Pydantic BaseModel
❌ Using subprocess to delegate CLI commands
```

### Mistake 3: Simplifying Data Files
```
❌ Creating a new effects.yaml with only 4 effects
✅ Copying the full effects.yaml with all 15+ effects
```

### Mistake 4: Skipping Verification
```
❌ Moving to next phase without testing
✅ Running verification commands after each phase
```

### Mistake 5: Making Assumptions
```
❌ "I think the entry point should be cli:cli"
✅ "The spec says wallpaper_effects.cli.main:app, I'll use that"
```

---

## 🚨 RED FLAGS - STOP IMMEDIATELY IF YOU SEE THESE

**If you find yourself doing ANY of these, STOP and ask the user:**

### Code Red Flags:
| If you're about to... | STOP! Instead... |
|----------------------|------------------|
| Write `import click` | Ask: "Docs say Typer. Should I use Click?" |
| Write `@dataclass` for a model | Ask: "Docs say Pydantic. Should I use dataclass?" |
| Write `subprocess.run` for CLI | Ask: "Docs say direct import. Should I use subprocess?" |
| Create new class not in source | Ask: "This class doesn't exist in source. Should I create it?" |
| Write `def` instead of copying | Ask: "I'm about to write new code. Should I copy instead?" |
| Hardcode fewer than 9 effects | Ask: "Source has 9+ effects. Should I use fewer?" |

### Process Red Flags:
| If you notice... | STOP! Instead... |
|------------------|------------------|
| Source file doesn't exist | Ask: "Expected file at X not found. Where is it?" |
| Line count differs by >20% | Ask: "Copied file is X lines vs Y original. Is this correct?" |
| Verification check fails | Ask: "Check X failed. How should I proceed?" |
| Import path is ambiguous | Ask: "Multiple possible imports. Which one?" |
| Docs contradict code | Ask: "Docs say X but code does Y. Which is correct?" |

### Thinking Red Flags:
| If you're thinking... | STOP! Instead... |
|----------------------|------------------|
| "This would be simpler if..." | Ask: "I see a simplification. Should I deviate?" |
| "I'll improve this by..." | Ask: "I want to improve X. Is that okay?" |
| "The original is wrong..." | Ask: "Original seems wrong. Should I fix it?" |
| "I'll just create a new..." | Ask: "I want to create new code. Is that okay?" |
| "This isn't documented but..." | Ask: "X isn't in docs. What should I do?" |

---

## 📝 Progress Tracking Template

Use this checklist to track progress:

```markdown
## Migration Progress

### Phase 1: Directory Structure
- [ ] Created packages/core/src/wallpaper_effects/{models,loader,engine,console,cli,data}
- [ ] Created packages/core/tests
- [ ] Created packages/orchestrator/src/wallpaper_effects_orchestrator/{container,cli}
- [ ] Created packages/orchestrator/tests

### Phase 2: Core Migration
- [ ] models/__init__.py copied and imports updated
- [ ] models/effects.py copied and imports updated
- [ ] models/config.py copied and imports updated
- [ ] models/settings.py copied and imports updated
- [ ] loader/__init__.py copied and imports updated
- [ ] loader/config_loader.py copied and imports updated
- [ ] loader/paths.py copied and imports updated
- [ ] data/effects.yaml copied (FULL file, 15+ effects)
- [ ] engine/__init__.py copied and imports updated
- [ ] engine/executor.py copied and imports updated
- [ ] engine/chain.py copied and imports updated
- [ ] engine/batch.py copied and imports updated
- [ ] console/__init__.py copied and imports updated
- [ ] console/output.py copied and imports updated
- [ ] console/progress.py copied and imports updated
- [ ] cli/__init__.py copied and imports updated
- [ ] cli/main.py copied and imports updated
- [ ] cli/process.py copied and imports updated
- [ ] cli/batch.py copied and imports updated
- [ ] cli/show.py copied and imports updated
- [ ] tests/ copied and imports updated

### Phase 3: Configuration
- [ ] packages/core/pyproject.toml created (with typer, pydantic)
- [ ] packages/core/src/wallpaper_effects/__init__.py created (public API)
- [ ] packages/core/src/wallpaper_effects/_version.py created

### Phase 4: Orchestrator
- [ ] Orchestrator CLI created (imports core directly, NOT subprocess)
- [ ] Container module migrated
- [ ] packages/orchestrator/pyproject.toml created

### Phase 5: Verification
- [ ] `cd packages/core && uv sync` succeeds
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run wallpaper-effects show effects` lists 15+ effects
- [ ] Python import test passes (ConfigLoader loads 15+ effects)
- [ ] `cd packages/orchestrator && uv sync` succeeds
- [ ] `uv run wallpaper-effects container --help` works
```

---

## 🆘 Troubleshooting

### Import Error: Module Not Found
**Cause**: Import path not updated correctly
**Fix**: Check that ALL occurrences of `wallpaper_processor` are changed to `wallpaper_effects`

### CLI Shows Click Instead of Typer
**Cause**: Rewrote CLI instead of copying
**Fix**: Re-copy from `core/src/wallpaper_processor/cli/` and only update imports

### Only 4 Effects Loaded
**Cause**: Created new effects.yaml instead of copying original
**Fix**: `cp shared/data/effects.yaml packages/core/src/wallpaper_effects/data/`

### Pydantic ValidationError
**Cause**: Model structure changed
**Fix**: Re-copy models from `shared/src/wallpaper_effects_shared/models/`

---

## 📜 THE ABSOLUTE RULES (Print This)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        AI IMPLEMENTATION CONTRACT                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  I WILL:                                                                      ║
║  ✓ Read source files BEFORE writing                                          ║
║  ✓ COPY existing code, not rewrite                                           ║
║  ✓ Run ALL verification gates                                                 ║
║  ✓ Report gate results to user                                                ║
║  ✓ STOP and ASK when anything is unclear                                      ║
║  ✓ Quote which doc section I'm following                                      ║
║                                                                               ║
║  I WILL NOT:                                                                  ║
║  ✗ Make design decisions without asking                                       ║
║  ✗ Change frameworks (Typer→Click, Pydantic→dataclass)                       ║
║  ✗ Skip verification gates                                                    ║
║  ✗ Simplify or "improve" working code                                         ║
║  ✗ Create new abstractions not in docs                                        ║
║  ✗ Assume anything not explicitly stated                                      ║
║  ✗ Proceed when uncertain                                                     ║
║                                                                               ║
║  WHEN IN DOUBT:                                                               ║
║  → STOP                                                                       ║
║  → Show what I found vs what I expected                                       ║
║  → ASK: "How should I proceed?"                                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Summary

**The single most important rule:**

> **COPY the existing working code, then UPDATE IMPORTS. Do not rewrite anything.**
> **ASK when uncertain. STOP when verification fails. NEVER assume.**
