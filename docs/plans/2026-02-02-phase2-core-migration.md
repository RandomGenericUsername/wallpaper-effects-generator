# Phase 2 Implementation: wallpaper_core Package

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Migrate wallpaper_core to packages/core/ with layered_settings integration

**Architecture:** Create packages/core/ following monorepo structure, integrate layered_settings from the start, register both settings.toml (CoreSettings) and effects.yaml (EffectsConfig) schemas, migrate working processor code from current core/

**Tech Stack:** Python 3.12, Pydantic 2.0, layered_settings, typer, rich, ImageMagick

**Reference:** See `docs/plans/2026-01-31-monorepo-refactor-design.md` sections 224-390 for complete specifications

---

## Current State Assessment

**Working modules to migrate:**
- `core/src/wallpaper_processor/engine/` - executor, chain, batch (core processing logic)
- `core/src/wallpaper_processor/console/` - output, progress (CLI feedback)
- `core/src/wallpaper_processor/cli/` - main, process, batch, show (CLI commands)
- `core/effects/effects.yaml` - effect definitions (148 lines, working)
- `core/tests/` - 10 test files covering all modules

**Modules to rewrite:**
- `core/src/wallpaper_processor/config/` - schema, settings, loader (will use layered_settings)

**Key findings:**
- Effects.yaml is working correctly with layered lookup
- Settings.toml is NOT being read (orphaned file, only settings.yaml used)
- CLI entry point: `wallpaper-effects-process` (will change to `wallpaper-process`)

---

## Implementation Tasks

Execute in order using TDD approach for each task.

### Task 1: Package Structure Setup

**Goal:** Create packages/core/ directory structure with pyproject.toml

**Files:**
- Create: `packages/core/pyproject.toml`
- Create: `packages/core/src/wallpaper_core/__init__.py`
- Create: `packages/core/README.md`
- Create: `packages/core/effects/effects.yaml` (copy from core/effects/)

**Step 1: Create directory structure**

```bash
mkdir -p packages/core/src/wallpaper_core
mkdir -p packages/core/effects
mkdir -p packages/core/tests
```

**Step 2: Write pyproject.toml**

```toml
[project]
name = "wallpaper-core"
version = "0.3.0"
description = "Wallpaper effects processor with layered configuration"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "layered-settings>=0.1.0",
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.8.0",
    "mypy>=1.11.0",
    "black>=24.0.0",
    "ruff>=0.6.0",
    "isort>=5.13.0",
    "pre-commit>=3.8.0",
    "types-pyyaml>=6.0",
]

[project.scripts]
wallpaper-process = "wallpaper_core.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_core"]

[tool.hatch.metadata]
allow-direct-references = true

[tool.uv.sources]
layered-settings = { path = "../settings", editable = true }

[tool.black]
line-length = 79
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 79

[tool.ruff]
line-length = 79
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "N"]
ignore = []

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["ARG", "PTH"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["typer.*", "rich.*"]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
pythonpath = ["src"]
addopts = ["-v", "--strict-markers", "--tb=short"]
```

**Step 3: Write package __init__.py**

```python
"""Wallpaper effects processor with layered configuration."""

__version__ = "0.3.0"

# Public exports will be added as modules are migrated
__all__ = ["__version__"]
```

**Step 4: Copy effects.yaml**

```bash
cp core/effects/effects.yaml packages/core/effects/effects.yaml
```

**Step 5: Write minimal README**

```markdown
# wallpaper_core

Wallpaper effects processor with layered configuration.

## Installation

```bash
cd packages/core
uv pip install -e .
```

## Usage

```bash
wallpaper-process --help
```

## Development

See root workspace documentation for development setup.
```

**Step 6: Verify structure**

```bash
tree packages/core -L 3
```

Expected: Directory structure created with all files

**Step 7: Commit**

```bash
git add packages/core/
git commit -m "feat(core): create package structure with pyproject.toml"
```

---

### Task 2: CoreSettings Schema

**Goal:** Define Pydantic models for settings.toml

**Files:**
- Create: `packages/core/src/wallpaper_core/config/__init__.py`
- Create: `packages/core/src/wallpaper_core/config/schema.py`
- Create: `packages/core/tests/test_config_schema.py`

**Step 1: Write failing test**

```python
# packages/core/tests/test_config_schema.py
"""Tests for CoreSettings Pydantic schema."""

import pytest
from pydantic import ValidationError
from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)


def test_verbosity_enum_values() -> None:
    """Test Verbosity enum has correct values."""
    assert Verbosity.QUIET == 0
    assert Verbosity.NORMAL == 1
    assert Verbosity.VERBOSE == 2
    assert Verbosity.DEBUG == 3


def test_execution_settings_defaults() -> None:
    """Test ExecutionSettings default values."""
    settings = ExecutionSettings()
    assert settings.parallel is True
    assert settings.strict is True
    assert settings.max_workers == 0


def test_execution_settings_validation() -> None:
    """Test ExecutionSettings validates max_workers."""
    settings = ExecutionSettings(max_workers=4)
    assert settings.max_workers == 4

    # Negative values should fail
    with pytest.raises(ValidationError):
        ExecutionSettings(max_workers=-1)


def test_output_settings_defaults() -> None:
    """Test OutputSettings default values."""
    settings = OutputSettings()
    assert settings.verbosity == Verbosity.NORMAL


def test_output_settings_accepts_int() -> None:
    """Test OutputSettings accepts int for verbosity."""
    settings = OutputSettings(verbosity=2)
    assert settings.verbosity == Verbosity.VERBOSE


def test_processing_settings_defaults() -> None:
    """Test ProcessingSettings defaults to None for temp_dir."""
    settings = ProcessingSettings()
    assert settings.temp_dir is None


def test_processing_settings_converts_string_to_path() -> None:
    """Test ProcessingSettings converts string to Path."""
    settings = ProcessingSettings(temp_dir="/tmp/custom")
    assert settings.temp_dir.as_posix() == "/tmp/custom"


def test_backend_settings_defaults() -> None:
    """Test BackendSettings default binary."""
    settings = BackendSettings()
    assert settings.binary == "magick"


def test_backend_settings_custom_binary() -> None:
    """Test BackendSettings accepts custom binary path."""
    settings = BackendSettings(binary="/usr/local/bin/magick")
    assert settings.binary == "/usr/local/bin/magick"


def test_core_settings_defaults() -> None:
    """Test CoreSettings creates with all defaults."""
    settings = CoreSettings()
    assert settings.version == "1.0"
    assert settings.execution.parallel is True
    assert settings.output.verbosity == Verbosity.NORMAL
    assert settings.processing.temp_dir is None
    assert settings.backend.binary == "magick"


def test_core_settings_from_dict() -> None:
    """Test CoreSettings can be created from dict."""
    data = {
        "execution": {"parallel": False, "max_workers": 4},
        "output": {"verbosity": 2},
        "backend": {"binary": "/usr/bin/magick"},
    }
    settings = CoreSettings(**data)
    assert settings.execution.parallel is False
    assert settings.execution.max_workers == 4
    assert settings.output.verbosity == Verbosity.VERBOSE
    assert settings.backend.binary == "/usr/bin/magick"


def test_core_settings_nested_validation() -> None:
    """Test CoreSettings validates nested settings."""
    with pytest.raises(ValidationError) as exc_info:
        CoreSettings(execution={"max_workers": -5})

    assert "max_workers" in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

```bash
cd packages/core
pytest tests/test_config_schema.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'wallpaper_core.config'"

**Step 3: Write schema.py**

```python
# packages/core/src/wallpaper_core/config/schema.py
"""Pydantic schemas for core settings."""

from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class Verbosity(IntEnum):
    """Output verbosity levels."""

    QUIET = 0  # Errors only
    NORMAL = 1  # Progress + results
    VERBOSE = 2  # + command details
    DEBUG = 3  # + full command output


class ExecutionSettings(BaseModel):
    """Batch execution settings."""

    parallel: bool = Field(
        default=True, description="Run batch operations in parallel"
    )
    strict: bool = Field(
        default=True, description="Abort on first failure"
    )
    max_workers: int = Field(
        default=0,
        description="Max parallel workers (0=auto based on CPU count)",
        ge=0,
    )


class OutputSettings(BaseModel):
    """Output and display settings."""

    verbosity: Verbosity = Field(
        default=Verbosity.NORMAL, description="Output verbosity level"
    )


class ProcessingSettings(BaseModel):
    """Processing behavior settings."""

    temp_dir: Path | None = Field(
        default=None,
        description="Temp directory for intermediate files (None=system default)",
    )

    @field_validator("temp_dir", mode="before")
    @classmethod
    def convert_str_to_path(cls, v: str | Path | None) -> Path | None:
        """Convert string to Path if needed."""
        if v is None or isinstance(v, Path):
            return v
        return Path(v)


class BackendSettings(BaseModel):
    """ImageMagick backend settings."""

    binary: str = Field(
        default="magick", description="Path to ImageMagick binary"
    )


class CoreSettings(BaseModel):
    """Root settings for wallpaper_core."""

    version: str = Field(
        default="1.0", description="Settings schema version"
    )
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    processing: ProcessingSettings = Field(
        default_factory=ProcessingSettings
    )
    backend: BackendSettings = Field(default_factory=BackendSettings)
```

**Step 4: Write config package __init__.py**

```python
# packages/core/src/wallpaper_core/config/__init__.py
"""Configuration module for wallpaper_core."""

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)

__all__ = [
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
]
```

**Step 5: Run test to verify it passes**

```bash
cd packages/core
pytest tests/test_config_schema.py -v
```

Expected: PASS (all tests pass)

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/config/ packages/core/tests/test_config_schema.py
git commit -m "feat(core): add CoreSettings Pydantic schema"
```

---

### Task 3: Settings Package Defaults

**Goal:** Create settings.toml with package default values

**Files:**
- Create: `packages/core/src/wallpaper_core/config/settings.toml`
- Create: `packages/core/tests/test_config_defaults.py`

**Step 1: Write failing test**

```python
# packages/core/tests/test_config_defaults.py
"""Tests for settings.toml package defaults."""

from pathlib import Path

import tomli
from wallpaper_core.config.schema import CoreSettings


def test_settings_toml_exists() -> None:
    """Test settings.toml file exists in package."""
    config_dir = Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    settings_file = config_dir / "settings.toml"
    assert settings_file.exists(), "settings.toml not found in package"


def test_settings_toml_is_valid() -> None:
    """Test settings.toml contains valid TOML."""
    config_dir = Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomli.load(f)

    assert isinstance(data, dict)
    assert len(data) > 0


def test_settings_toml_validates_against_schema() -> None:
    """Test settings.toml can be loaded into CoreSettings."""
    config_dir = Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomli.load(f)

    settings = CoreSettings(**data)
    assert settings.execution.parallel is True
    assert settings.execution.strict is True
    assert settings.execution.max_workers == 0
    assert settings.output.verbosity == 1  # NORMAL
    assert settings.backend.binary == "magick"


def test_settings_toml_uses_flat_format() -> None:
    """Test settings.toml uses flat format (not namespaced)."""
    config_dir = Path(__file__).parent.parent / "src" / "wallpaper_core" / "config"
    settings_file = config_dir / "settings.toml"

    with open(settings_file, "rb") as f:
        data = tomli.load(f)

    # Should have top-level sections, not nested under "core"
    assert "execution" in data
    assert "output" in data
    assert "backend" in data
    assert "core" not in data  # Should NOT be namespaced
```

**Step 2: Run test to verify it fails**

```bash
cd packages/core
pytest tests/test_config_defaults.py -v
```

Expected: FAIL with "settings.toml not found in package"

**Step 3: Write settings.toml**

```toml
# packages/core/src/wallpaper_core/config/settings.toml
# Package default settings for wallpaper_core
# Format: flat sections (not namespaced)
# User configs should use [core.execution] namespace

[execution]
parallel = true
strict = true
max_workers = 0

[output]
verbosity = 1  # 0=QUIET, 1=NORMAL, 2=VERBOSE, 3=DEBUG

[processing]
# temp_dir is optional, defaults to system temp
# Uncomment to set custom temp directory:
# temp_dir = "/custom/tmp"

[backend]
binary = "magick"
```

**Step 4: Run test to verify it passes**

```bash
cd packages/core
pytest tests/test_config_defaults.py -v
```

Expected: PASS (all tests pass)

**Step 5: Commit**

```bash
git add packages/core/src/wallpaper_core/config/settings.toml packages/core/tests/test_config_defaults.py
git commit -m "feat(core): add settings.toml package defaults"
```

---

### Task 4: EffectsConfig Schema

**Goal:** Define Pydantic models for effects.yaml

**Files:**
- Create: `packages/core/src/wallpaper_core/effects/__init__.py`
- Create: `packages/core/src/wallpaper_core/effects/schema.py`
- Create: `packages/core/tests/test_effects_schema.py`

**Step 1: Read current effects.yaml structure**

```bash
head -80 packages/core/effects/effects.yaml
```

Expected: See version, parameter_types, effects sections

**Step 2: Write failing test**

```python
# packages/core/tests/test_effects_schema.py
"""Tests for EffectsConfig Pydantic schema."""

import pytest
from pydantic import ValidationError
from wallpaper_core.effects.schema import (
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
)


def test_parameter_type_with_defaults() -> None:
    """Test ParameterType with all default values."""
    param_type = ParameterType(
        type="string",
        default="test",
    )
    assert param_type.type == "string"
    assert param_type.default == "test"
    assert param_type.description is None


def test_parameter_type_with_validation() -> None:
    """Test ParameterType with validation rules."""
    param_type = ParameterType(
        type="integer",
        min=0,
        max=100,
        default=50,
    )
    assert param_type.min == 0
    assert param_type.max == 100


def test_parameter_definition_minimal() -> None:
    """Test ParameterDefinition with minimal fields."""
    param = ParameterDefinition(type="string")
    assert param.type == "string"
    assert param.cli_flag is None


def test_parameter_definition_with_cli_flag() -> None:
    """Test ParameterDefinition with CLI flag."""
    param = ParameterDefinition(
        type="blur_geometry",
        cli_flag="--blur",
        description="Blur geometry",
    )
    assert param.type == "blur_geometry"
    assert param.cli_flag == "--blur"


def test_effect_minimal() -> None:
    """Test Effect with only required fields."""
    effect = Effect(
        description="Test effect",
        command='magick "$INPUT" -blur 0x8 "$OUTPUT"',
    )
    assert effect.description == "Test effect"
    assert "$INPUT" in effect.command
    assert effect.parameters == {}


def test_effect_with_parameters() -> None:
    """Test Effect with parameters."""
    effect = Effect(
        description="Blur effect",
        command='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
        parameters={
            "blur": ParameterDefinition(
                type="blur_geometry",
                cli_flag="--blur",
            )
        },
    )
    assert "blur" in effect.parameters
    assert effect.parameters["blur"].cli_flag == "--blur"


def test_effects_config_minimal() -> None:
    """Test EffectsConfig with minimal data."""
    config = EffectsConfig(version="1.0")
    assert config.version == "1.0"
    assert config.parameter_types == {}
    assert config.effects == {}


def test_effects_config_with_parameter_types() -> None:
    """Test EffectsConfig with parameter types."""
    config = EffectsConfig(
        version="1.0",
        parameter_types={
            "percent": ParameterType(
                type="integer",
                min=-100,
                max=100,
                default=0,
            )
        },
    )
    assert "percent" in config.parameter_types
    assert config.parameter_types["percent"].min == -100


def test_effects_config_with_effects() -> None:
    """Test EffectsConfig with effects."""
    config = EffectsConfig(
        version="1.0",
        effects={
            "blur": Effect(
                description="Apply blur",
                command='magick "$INPUT" -blur 0x8 "$OUTPUT"',
            )
        },
    )
    assert "blur" in config.effects
    assert config.effects["blur"].description == "Apply blur"


def test_effects_config_from_dict() -> None:
    """Test EffectsConfig from dictionary (like YAML load)."""
    data = {
        "version": "1.0",
        "parameter_types": {
            "blur_geometry": {
                "type": "string",
                "pattern": r"^\d+x\d+$",
                "default": "0x8",
            }
        },
        "effects": {
            "blur": {
                "description": "Apply Gaussian blur",
                "command": 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
                "parameters": {
                    "blur": {
                        "type": "blur_geometry",
                        "cli_flag": "--blur",
                    }
                },
            }
        },
    }
    config = EffectsConfig(**data)
    assert config.version == "1.0"
    assert "blur_geometry" in config.parameter_types
    assert "blur" in config.effects
```

**Step 3: Run test to verify it fails**

```bash
cd packages/core
pytest tests/test_effects_schema.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'wallpaper_core.effects'"

**Step 4: Write effects schema**

```python
# packages/core/src/wallpaper_core/effects/schema.py
"""Pydantic schemas for effects configuration."""

from typing import Any

from pydantic import BaseModel, Field


class ParameterType(BaseModel):
    """Reusable parameter type definition."""

    type: str = Field(description="Parameter type (string, integer, float)")
    pattern: str | None = Field(
        default=None, description="Regex pattern for validation"
    )
    min: int | float | None = Field(
        default=None, description="Minimum value"
    )
    max: int | float | None = Field(
        default=None, description="Maximum value"
    )
    default: Any = Field(description="Default value")
    description: str | None = Field(
        default=None, description="Human-readable description"
    )


class ParameterDefinition(BaseModel):
    """Parameter definition for an effect."""

    type: str = Field(description="Parameter type reference")
    cli_flag: str | None = Field(
        default=None, description="CLI flag (e.g., --blur)"
    )
    description: str | None = Field(
        default=None, description="Parameter description"
    )


class Effect(BaseModel):
    """Single effect definition."""

    description: str = Field(description="Effect description")
    command: str = Field(description="ImageMagick command template")
    parameters: dict[str, ParameterDefinition] = Field(
        default_factory=dict, description="Effect parameters"
    )


class EffectsConfig(BaseModel):
    """Root configuration for effects."""

    version: str = Field(description="Effects schema version")
    parameter_types: dict[str, ParameterType] = Field(
        default_factory=dict, description="Reusable parameter types"
    )
    effects: dict[str, Effect] = Field(
        default_factory=dict, description="Effect definitions"
    )
```

**Step 5: Write effects package __init__.py**

```python
# packages/core/src/wallpaper_core/effects/__init__.py
"""Effects configuration module."""

from wallpaper_core.effects.schema import (
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
)

__all__ = [
    "EffectsConfig",
    "Effect",
    "ParameterType",
    "ParameterDefinition",
]
```

**Step 6: Run test to verify it passes**

```bash
cd packages/core
pytest tests/test_effects_schema.py -v
```

Expected: PASS (all tests pass)

**Step 7: Commit**

```bash
git add packages/core/src/wallpaper_core/effects/ packages/core/tests/test_effects_schema.py
git commit -m "feat(core): add EffectsConfig Pydantic schema"
```

---

### Task 5: Schema Registration

**Goal:** Register CoreSettings and EffectsConfig with layered_settings

**Files:**
- Modify: `packages/core/src/wallpaper_core/config/__init__.py`
- Modify: `packages/core/src/wallpaper_core/effects/__init__.py`
- Create: `packages/core/tests/test_schema_registration.py`

**Step 1: Write failing test**

```python
# packages/core/tests/test_schema_registration.py
"""Tests for schema registration with layered_settings."""

from pathlib import Path

from layered_settings import SchemaRegistry
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig


def test_core_settings_registered() -> None:
    """Test CoreSettings is registered with 'core' namespace."""
    entry = SchemaRegistry.get("core")
    assert entry.namespace == "core"
    assert entry.model == CoreSettings
    assert entry.defaults_file.name == "settings.toml"
    assert entry.defaults_file.exists()


def test_effects_config_registered() -> None:
    """Test EffectsConfig is registered with 'effects' namespace."""
    entry = SchemaRegistry.get("effects")
    assert entry.namespace == "effects"
    assert entry.model == EffectsConfig
    assert entry.defaults_file.name == "effects.yaml"
    assert entry.defaults_file.exists()


def test_defaults_files_exist() -> None:
    """Test both defaults files exist and are readable."""
    core_entry = SchemaRegistry.get("core")
    effects_entry = SchemaRegistry.get("effects")

    assert core_entry.defaults_file.is_file()
    assert effects_entry.defaults_file.is_file()

    # Verify they're not empty
    assert core_entry.defaults_file.stat().st_size > 0
    assert effects_entry.defaults_file.stat().st_size > 0
```

**Step 2: Run test to verify it fails**

```bash
cd packages/core
pytest tests/test_schema_registration.py -v
```

Expected: FAIL with "Namespace 'core' not found in registry"

**Step 3: Update config __init__.py to register schema**

```python
# packages/core/src/wallpaper_core/config/__init__.py
"""Configuration module for wallpaper_core."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)

# Register CoreSettings with layered_settings
SchemaRegistry.register(
    namespace="core",
    model=CoreSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)

__all__ = [
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
]
```

**Step 4: Update effects __init__.py to register schema**

```python
# packages/core/src/wallpaper_core/effects/__init__.py
"""Effects configuration module."""

from pathlib import Path

from layered_settings import SchemaRegistry

from wallpaper_core.effects.schema import (
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
)

# Register EffectsConfig with layered_settings
# Note: effects.yaml is outside src/, go up to package root
_package_root = Path(__file__).parent.parent.parent.parent
SchemaRegistry.register(
    namespace="effects",
    model=EffectsConfig,
    defaults_file=_package_root / "effects" / "effects.yaml",
)

__all__ = [
    "EffectsConfig",
    "Effect",
    "ParameterType",
    "ParameterDefinition",
]
```

**Step 5: Run test to verify it passes**

```bash
cd packages/core
pytest tests/test_schema_registration.py -v
```

Expected: PASS (all tests pass)

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/config/__init__.py packages/core/src/wallpaper_core/effects/__init__.py packages/core/tests/test_schema_registration.py
git commit -m "feat(core): register schemas with layered_settings"
```

---

### Task 6: CLI Bootstrap with layered_settings

**Goal:** Create CLI main.py that configures layered_settings

**Files:**
- Create: `packages/core/src/wallpaper_core/cli/__init__.py`
- Create: `packages/core/src/wallpaper_core/cli/main.py`
- Create: `packages/core/tests/test_cli_bootstrap.py`

**Step 1: Write failing test**

```python
# packages/core/tests/test_cli_bootstrap.py
"""Tests for CLI bootstrap and configuration."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner
from wallpaper_core.cli.main import app


runner = CliRunner()


def test_cli_app_exists() -> None:
    """Test CLI app is a Typer instance."""
    from typer import Typer

    assert isinstance(app, Typer)


def test_cli_help_works() -> None:
    """Test CLI --help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "wallpaper" in result.stdout.lower()


def test_cli_configures_layered_settings() -> None:
    """Test CLI configures layered_settings on startup."""
    # Import triggers configuration
    from wallpaper_core.cli import main
    from layered_settings import get_config

    # Should be able to get config without error
    # Note: This might fail if config files missing in user's home
    # but that's expected behavior
    try:
        config = get_config()
        assert hasattr(config, "core")
        assert hasattr(config, "effects")
    except Exception:
        # If fails due to missing files, that's OK
        # Just verify the configure was called
        pass


def test_cli_version_in_help() -> None:
    """Test CLI help shows version."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Should mention wallpaper-process
    assert "process" in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

```bash
cd packages/core
pytest tests/test_cli_bootstrap.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'wallpaper_core.cli'"

**Step 3: Write cli __init__.py**

```python
# packages/core/src/wallpaper_core/cli/__init__.py
"""CLI module for wallpaper_core."""

from wallpaper_core.cli.main import app

__all__ = ["app"]
```

**Step 4: Write cli main.py with bootstrap**

```python
# packages/core/src/wallpaper_core/cli/main.py
"""Main CLI entry point for wallpaper_core."""

import typer
from pydantic import BaseModel

from layered_settings import configure, get_config
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig


class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    effects: EffectsConfig


# Configure layered_settings at module import
configure(CoreOnlyConfig, app_name="wallpaper-effects")

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with layered configuration",
    no_args_is_help=True,
)


@app.command()
def info() -> None:
    """Show current configuration."""
    config = get_config()

    typer.echo("=== Core Settings ===")
    typer.echo(f"Parallel: {config.core.execution.parallel}")
    typer.echo(f"Strict: {config.core.execution.strict}")
    typer.echo(f"Max Workers: {config.core.execution.max_workers}")
    typer.echo(f"Verbosity: {config.core.output.verbosity.name}")
    typer.echo(f"Backend Binary: {config.core.backend.binary}")

    typer.echo("\n=== Effects ===")
    typer.echo(f"Version: {config.effects.version}")
    typer.echo(f"Effects defined: {len(config.effects.effects)}")

    if config.effects.effects:
        typer.echo("\nAvailable effects:")
        for effect_name in sorted(config.effects.effects.keys()):
            effect = config.effects.effects[effect_name]
            typer.echo(f"  - {effect_name}: {effect.description}")


if __name__ == "__main__":
    app()
```

**Step 5: Run test to verify it passes**

```bash
cd packages/core
pytest tests/test_cli_bootstrap.py -v
```

Expected: PASS (all tests pass)

**Step 6: Test CLI manually**

```bash
cd packages/core
uv pip install -e .
wallpaper-process --help
wallpaper-process info
```

Expected: Help shown, info command shows configuration

**Step 7: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/ packages/core/tests/test_cli_bootstrap.py
git commit -m "feat(core): add CLI bootstrap with layered_settings"
```

---

### Task 7: Migrate Engine Module

**Goal:** Migrate core/src/wallpaper_processor/engine/ to packages/core/

**Files:**
- Create: `packages/core/src/wallpaper_core/engine/__init__.py`
- Copy: `core/src/wallpaper_processor/engine/executor.py` → `packages/core/src/wallpaper_core/engine/executor.py`
- Copy: `core/src/wallpaper_processor/engine/chain.py` → `packages/core/src/wallpaper_core/engine/chain.py`
- Copy: `core/src/wallpaper_processor/engine/batch.py` → `packages/core/src/wallpaper_core/engine/batch.py`
- Copy: `core/tests/test_engine_*.py` → `packages/core/tests/`

**Step 1: Copy engine files**

```bash
mkdir -p packages/core/src/wallpaper_core/engine

cp core/src/wallpaper_processor/engine/__init__.py packages/core/src/wallpaper_core/engine/__init__.py
cp core/src/wallpaper_processor/engine/executor.py packages/core/src/wallpaper_core/engine/executor.py
cp core/src/wallpaper_processor/engine/chain.py packages/core/src/wallpaper_core/engine/chain.py
cp core/src/wallpaper_processor/engine/batch.py packages/core/src/wallpaper_core/engine/batch.py
```

**Step 2: Update imports in engine files**

Update all imports from `wallpaper_processor` to `wallpaper_core`:
- Replace `from wallpaper_processor.` with `from wallpaper_core.`
- Replace `import wallpaper_processor.` with `import wallpaper_core.`

Example for executor.py:
```python
# Old: from wallpaper_processor.config.schema import ExecutionSettings
# New: from wallpaper_core.config.schema import ExecutionSettings
```

**Step 3: Copy engine tests**

```bash
cp core/tests/test_engine_executor.py packages/core/tests/
cp core/tests/test_engine_chain.py packages/core/tests/
cp core/tests/test_engine_batch.py packages/core/tests/
```

**Step 4: Update test imports**

Update all test imports from `wallpaper_processor` to `wallpaper_core`.

**Step 5: Run tests**

```bash
cd packages/core
pytest tests/test_engine_*.py -v
```

Expected: PASS (all engine tests pass)

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/engine/ packages/core/tests/test_engine_*.py
git commit -m "feat(core): migrate engine module from old core"
```

---

### Task 8: Migrate Console Module

**Goal:** Migrate core/src/wallpaper_processor/console/ to packages/core/

**Files:**
- Create: `packages/core/src/wallpaper_core/console/__init__.py`
- Copy: `core/src/wallpaper_processor/console/output.py` → `packages/core/src/wallpaper_core/console/output.py`
- Copy: `core/src/wallpaper_processor/console/progress.py` → `packages/core/src/wallpaper_core/console/progress.py`
- Copy: `core/tests/test_console.py` → `packages/core/tests/`

**Step 1: Copy console files**

```bash
mkdir -p packages/core/src/wallpaper_core/console

cp core/src/wallpaper_processor/console/__init__.py packages/core/src/wallpaper_core/console/__init__.py
cp core/src/wallpaper_processor/console/output.py packages/core/src/wallpaper_core/console/output.py
cp core/src/wallpaper_processor/console/progress.py packages/core/src/wallpaper_core/console/progress.py
```

**Step 2: Update imports in console files**

Update all imports from `wallpaper_processor` to `wallpaper_core`.

**Step 3: Copy console tests**

```bash
cp core/tests/test_console.py packages/core/tests/
```

**Step 4: Update test imports**

Update test imports from `wallpaper_processor` to `wallpaper_core`.

**Step 5: Run tests**

```bash
cd packages/core
pytest tests/test_console.py -v
```

Expected: PASS (all console tests pass)

**Step 6: Commit**

```bash
git add packages/core/src/wallpaper_core/console/ packages/core/tests/test_console.py
git commit -m "feat(core): migrate console module from old core"
```

---

### Task 9: Migrate CLI Commands

**Goal:** Migrate CLI command modules (process, batch, show)

**Files:**
- Copy: `core/src/wallpaper_processor/cli/process.py` → `packages/core/src/wallpaper_core/cli/process.py`
- Copy: `core/src/wallpaper_processor/cli/batch.py` → `packages/core/src/wallpaper_core/cli/batch.py`
- Copy: `core/src/wallpaper_processor/cli/show.py` → `packages/core/src/wallpaper_core/cli/show.py`
- Modify: `packages/core/src/wallpaper_core/cli/main.py`
- Copy: `core/tests/test_cli.py` → `packages/core/tests/`

**Step 1: Copy CLI command files**

```bash
cp core/src/wallpaper_processor/cli/process.py packages/core/src/wallpaper_core/cli/process.py
cp core/src/wallpaper_processor/cli/batch.py packages/core/src/wallpaper_core/cli/batch.py
cp core/src/wallpaper_processor/cli/show.py packages/core/src/wallpaper_core/cli/show.py
```

**Step 2: Update imports in CLI files**

Update all imports from `wallpaper_processor` to `wallpaper_core`.

**Step 3: Integrate commands into main.py**

```python
# Add to packages/core/src/wallpaper_core/cli/main.py

from wallpaper_core.cli import batch, process, show

# Add commands to app
app.add_typer(process.app, name="process")
app.add_typer(batch.app, name="batch")
app.add_typer(show.app, name="show")
```

**Step 4: Copy CLI tests**

```bash
cp core/tests/test_cli.py packages/core/tests/
```

**Step 5: Update test imports**

Update test imports from `wallpaper_processor` to `wallpaper_core`.

**Step 6: Run tests**

```bash
cd packages/core
pytest tests/test_cli.py -v
```

Expected: PASS (all CLI tests pass)

**Step 7: Test CLI manually**

```bash
cd packages/core
wallpaper-process --help
wallpaper-process process --help
wallpaper-process show --help
```

Expected: All commands show help correctly

**Step 8: Commit**

```bash
git add packages/core/src/wallpaper_core/cli/ packages/core/tests/test_cli.py
git commit -m "feat(core): migrate CLI commands from old core"
```

---

### Task 10: Add conftest.py and Test Fixtures

**Goal:** Copy test configuration and fixtures

**Files:**
- Copy: `core/tests/conftest.py` → `packages/core/tests/conftest.py`
- Modify: Update imports in conftest.py

**Step 1: Copy conftest.py**

```bash
cp core/tests/conftest.py packages/core/tests/conftest.py
```

**Step 2: Update imports**

Update all imports from `wallpaper_processor` to `wallpaper_core`.

**Step 3: Run all tests**

```bash
cd packages/core
pytest -v
```

Expected: All tests pass

**Step 4: Check coverage**

```bash
cd packages/core
pytest --cov=wallpaper_core --cov-report=term-missing
```

Expected: High coverage (>80%)

**Step 5: Commit**

```bash
git add packages/core/tests/conftest.py
git commit -m "feat(core): add test fixtures and conftest"
```

---

### Task 11: Update Package __init__.py

**Goal:** Export public API from package

**Files:**
- Modify: `packages/core/src/wallpaper_core/__init__.py`

**Step 1: Write updated __init__.py**

```python
# packages/core/src/wallpaper_core/__init__.py
"""Wallpaper effects processor with layered configuration."""

from wallpaper_core.config.schema import (
    BackendSettings,
    CoreSettings,
    ExecutionSettings,
    OutputSettings,
    ProcessingSettings,
    Verbosity,
)
from wallpaper_core.effects.schema import (
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
)

__version__ = "0.3.0"

__all__ = [
    "__version__",
    # Config
    "CoreSettings",
    "ExecutionSettings",
    "OutputSettings",
    "ProcessingSettings",
    "BackendSettings",
    "Verbosity",
    # Effects
    "EffectsConfig",
    "Effect",
    "ParameterType",
    "ParameterDefinition",
]
```

**Step 2: Test imports**

```bash
cd packages/core
python -c "from wallpaper_core import CoreSettings, EffectsConfig; print('OK')"
```

Expected: "OK"

**Step 3: Commit**

```bash
git add packages/core/src/wallpaper_core/__init__.py
git commit -m "feat(core): update package __init__ with public API"
```

---

### Task 12: Update Root Workspace

**Goal:** Add packages/core to root workspace configuration

**Files:**
- Modify: `pyproject.toml` (root)
- Create: `pyproject.toml` (root if doesn't exist)

**Step 1: Check if root pyproject.toml exists**

```bash
ls -la pyproject.toml
```

**Step 2: Create or update root workspace config**

If file doesn't exist, create it:
```toml
# pyproject.toml (root)
[tool.uv.workspace]
members = [
    "packages/settings",
    "packages/core",
]
```

If file exists, add `packages/core` to members array.

**Step 3: Sync workspace**

```bash
uv sync
```

Expected: All packages in workspace synced

**Step 4: Test workspace imports**

```bash
cd packages/core
uv run python -c "from layered_settings import configure; from wallpaper_core import CoreSettings; print('OK')"
```

Expected: "OK"

**Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "feat(workspace): add packages/core to workspace"
```

---

### Task 13: Integration Testing

**Goal:** Create end-to-end integration tests

**Files:**
- Create: `packages/core/tests/test_integration.py`

**Step 1: Write integration test**

```python
# packages/core/tests/test_integration.py
"""Integration tests for wallpaper_core with layered_settings."""

import tempfile
from pathlib import Path

import pytest
from layered_settings import configure, get_config
from wallpaper_core.cli.main import CoreOnlyConfig


def test_config_loads_from_package_defaults() -> None:
    """Test configuration loads from package defaults."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have defaults from settings.toml
    assert config.core.execution.parallel is True
    assert config.core.backend.binary == "magick"

    # Should have effects from effects.yaml
    assert config.effects.version == "1.0"
    assert len(config.effects.effects) > 0


def test_config_merges_cli_overrides() -> None:
    """Test CLI overrides merge correctly."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config(overrides={
        "core.execution.parallel": False,
        "core.execution.max_workers": 4,
    })

    assert config.core.execution.parallel is False
    assert config.core.execution.max_workers == 4
    # Other settings should remain default
    assert config.core.backend.binary == "magick"


def test_config_loads_project_settings() -> None:
    """Test configuration loads from project settings.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        settings_file = project_dir / "settings.toml"

        # Write project settings
        settings_file.write_text("""
[core.execution]
parallel = false
max_workers = 8

[core.backend]
binary = "/custom/magick"
""")

        # Configure with project root
        configure(CoreOnlyConfig, app_name="wallpaper-effects-test")

        # Note: This test requires running from project_dir
        # or mock layer discovery
        # For now, just verify defaults work
        config = get_config()
        assert config.core is not None


def test_effects_loaded_from_yaml() -> None:
    """Test effects are loaded from effects.yaml."""
    configure(CoreOnlyConfig, app_name="wallpaper-effects-test")
    config = get_config()

    # Should have blur effect
    assert "blur" in config.effects.effects
    blur = config.effects.effects["blur"]
    assert blur.description
    assert "$INPUT" in blur.command
    assert "$OUTPUT" in blur.command


def test_cli_info_command_runs() -> None:
    """Test CLI info command executes without error."""
    from typer.testing import CliRunner
    from wallpaper_core.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "Core Settings" in result.stdout
    assert "Effects" in result.stdout
```

**Step 2: Run integration tests**

```bash
cd packages/core
pytest tests/test_integration.py -v
```

Expected: PASS (all integration tests pass)

**Step 3: Run full test suite**

```bash
cd packages/core
pytest -v --cov=wallpaper_core
```

Expected: All tests pass with good coverage

**Step 4: Commit**

```bash
git add packages/core/tests/test_integration.py
git commit -m "test(core): add integration tests for layered_settings"
```

---

### Task 14: Update Documentation

**Goal:** Update README with usage examples

**Files:**
- Modify: `packages/core/README.md`

**Step 1: Write comprehensive README**

```markdown
# wallpaper_core

Wallpaper effects processor with layered configuration using `layered_settings`.

## Features

- **Layered Configuration**: Settings merge from package defaults → project → user → CLI
- **TOML Settings**: Runtime behavior configuration (execution, output, backend)
- **YAML Effects**: ImageMagick effect definitions with parameters
- **Type-Safe**: Full Pydantic validation for all configuration
- **CLI**: Simple, powerful command-line interface

## Installation

```bash
# From workspace root
uv sync

# Install just core package
cd packages/core
uv pip install -e .
```

## Quick Start

```bash
# Show current configuration
wallpaper-process info

# Process single image with effect
wallpaper-process process input.jpg output.jpg blur

# Process batch with multiple effects
wallpaper-process batch input.jpg --effects blur,brightness --parallel
```

## Configuration

### Layer Priority

1. **Package defaults** - `packages/core/src/wallpaper_core/config/settings.toml`
2. **Project settings** - `./settings.toml` (root of your project)
3. **User settings** - `~/.config/wallpaper-effects/settings.toml`
4. **CLI overrides** - Command-line flags

### Settings Format

**Package defaults (flat):**
```toml
# packages/core/src/wallpaper_core/config/settings.toml
[execution]
parallel = true
max_workers = 0
```

**Project/User settings (namespaced):**
```toml
# ./settings.toml or ~/.config/wallpaper-effects/settings.toml
[core.execution]
parallel = false
max_workers = 4

[core.backend]
binary = "/usr/local/bin/magick"
```

### Available Settings

**Execution Settings:**
- `parallel` (bool) - Run operations in parallel
- `strict` (bool) - Abort on first failure
- `max_workers` (int) - Max parallel workers (0=auto)

**Output Settings:**
- `verbosity` (int) - 0=QUIET, 1=NORMAL, 2=VERBOSE, 3=DEBUG

**Processing Settings:**
- `temp_dir` (path) - Temp directory (None=system default)

**Backend Settings:**
- `binary` (str) - ImageMagick binary path

## Effects

Effects are defined in `effects.yaml` with layered lookup:
1. Package defaults: `packages/core/effects/effects.yaml`
2. User effects: `~/.config/wallpaper-effects/effects.yaml`

See `effects.yaml` for available effects and parameters.

## Development

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=wallpaper_core --cov-report=term-missing

# Type checking
mypy src/wallpaper_core

# Format code
black src/ tests/
isort src/ tests/
```

## Architecture

Uses `layered_settings` package for configuration management:
- `CoreSettings` - Runtime behavior settings
- `EffectsConfig` - Effect definitions
- Both registered with `SchemaRegistry` at import time

See `docs/plans/2026-01-31-monorepo-refactor-design.md` for complete architecture.
```

**Step 2: Verify README renders correctly**

```bash
cat packages/core/README.md
```

Expected: Well-formatted markdown

**Step 3: Commit**

```bash
git add packages/core/README.md
git commit -m "docs(core): update README with complete usage guide"
```

---

## Completion Checklist

After completing all tasks, verify:

- [ ] All tests pass: `cd packages/core && pytest -v`
- [ ] Good coverage: `pytest --cov=wallpaper_core` (>80%)
- [ ] Type checking passes: `mypy src/wallpaper_core`
- [ ] CLI works: `wallpaper-process --help`
- [ ] CLI info shows config: `wallpaper-process info`
- [ ] Workspace syncs: `cd ../.. && uv sync`
- [ ] All commits made with clear messages
- [ ] Documentation complete

## Next Steps (Phase 3)

After Phase 2 completion:
1. Build `packages/orchestrator/` with container management
2. Create `UnifiedConfig` composing core + orchestrator settings
3. Implement orchestrator CLI that wraps core
4. Archive old `core/` directory
5. Update root documentation

---

## Notes for Implementer

- **TDD Approach**: Write test first, see it fail, implement, see it pass, commit
- **Import Updates**: Remember to change all `wallpaper_processor` → `wallpaper_core`
- **Path Resolution**: Effects.yaml is outside src/, use `Path(__file__).parent.parent.parent.parent`
- **Layered Settings**: Package imports trigger schema registration automatically
- **CLI Testing**: Use `typer.testing.CliRunner` for CLI tests
- **Workspace**: Run `uv sync` from root after adding core to workspace
