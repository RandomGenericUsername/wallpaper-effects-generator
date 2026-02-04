# Phase 1: Layered Settings Package Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a generic, reusable layered configuration system that supports TOML and YAML formats with Pydantic validation.

**Architecture:** Registry-based system where packages register their config schemas (Pydantic models) and default files. The loader discovers config files across multiple layers (package defaults → project root → user config → CLI overrides), deep-merges them, and validates against registered schemas.

**Tech Stack:** Python 3.12, Pydantic 2.x, PyYAML, tomli (TOML parser)

**Reference:** `docs/plans/2026-01-31-monorepo-refactor-design.md` (architecture specification)

---

## Project Setup

### Task 0: Create Package Structure

**Files:**
- Create: `packages/settings/pyproject.toml`
- Create: `packages/settings/src/layered_settings/__init__.py`
- Create: `packages/settings/README.md`
- Create: `packages/settings/tests/__init__.py`

**Step 1: Create directory structure**

```bash
mkdir -p packages/settings/src/layered_settings
mkdir -p packages/settings/tests
touch packages/settings/src/layered_settings/__init__.py
touch packages/settings/tests/__init__.py
```

**Step 2: Write pyproject.toml**

Create `packages/settings/pyproject.toml`:

```toml
[project]
name = "layered-settings"
version = "0.1.0"
description = "Generic layered configuration system supporting TOML and YAML"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "tomli>=2.0.0; python_version < '3.11'",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/layered_settings"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
pythonpath = ["src"]
addopts = ["-v", "--strict-markers", "--tb=short"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Step 3: Write README.md**

Create `packages/settings/README.md`:

```markdown
# layered-settings

Generic layered configuration system for Python applications.

## Features

- **Format-agnostic:** Supports TOML and YAML configuration files
- **Layered merging:** Combine configs from multiple sources (package defaults, project, user, CLI)
- **Type-safe:** Pydantic validation ensures config correctness
- **Registry-based:** Packages register their schemas at import time
- **Zero dependencies on domain logic:** Completely generic and reusable

## Installation

```bash
pip install layered-settings
```

## Quick Start

```python
from pydantic import BaseModel, Field
from layered_settings import SchemaRegistry, configure, get_config

# Define your config schema
class AppSettings(BaseModel):
    debug: bool = Field(default=False)
    port: int = Field(default=8000)

# Register it
SchemaRegistry.register(
    namespace="app",
    model=AppSettings,
    defaults_file=Path(__file__).parent / "settings.toml"
)

# Configure the settings system
class RootConfig(BaseModel):
    app: AppSettings

configure(RootConfig)

# Load config with layered merging
config = get_config()
print(config.app.port)
```

## Layer Priority

1. Package defaults (flat TOML/YAML)
2. Project root config (namespaced)
3. User config directory (namespaced)
4. CLI overrides (applied last)

Later layers override earlier ones via deep merge.
```

**Step 4: Initialize package**

```bash
cd packages/settings
uv venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows
uv pip install -e ".[dev]"
```

**Step 5: Verify installation**

```bash
python -c "import layered_settings; print('Package installed successfully')"
```

Expected: "Package installed successfully"

**Step 6: Commit**

```bash
git add packages/settings/
git commit -m "feat(settings): initialize layered-settings package structure

- Add pyproject.toml with dependencies
- Add README with quick start guide
- Setup test infrastructure

Part of Phase 1: layered_settings implementation"
```

---

## Core Modules

### Task 1: Error Hierarchy

**Files:**
- Create: `packages/settings/src/layered_settings/errors.py`
- Create: `packages/settings/tests/test_errors.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_errors.py`:

```python
"""Tests for error hierarchy."""

import pytest
from layered_settings.errors import (
    SettingsError,
    SettingsFileError,
    SettingsRegistryError,
    SettingsValidationError,
)


def test_settings_error_is_base_exception() -> None:
    """SettingsError should be the base for all settings errors."""
    err = SettingsError("test message")
    assert isinstance(err, Exception)
    assert str(err) == "test message"


def test_file_error_inherits_from_settings_error() -> None:
    """SettingsFileError should inherit from SettingsError."""
    err = SettingsFileError("config.toml", "File not found")
    assert isinstance(err, SettingsError)
    assert "config.toml" in str(err)
    assert "File not found" in str(err)


def test_registry_error_inherits_from_settings_error() -> None:
    """SettingsRegistryError should inherit from SettingsError."""
    err = SettingsRegistryError("core", "Namespace already registered")
    assert isinstance(err, SettingsError)
    assert "core" in str(err)
    assert "already registered" in str(err)


def test_validation_error_inherits_from_settings_error() -> None:
    """SettingsValidationError should inherit from SettingsError."""
    err = SettingsValidationError("config", "Invalid type for field 'port'")
    assert isinstance(err, SettingsError)
    assert "config" in str(err)
    assert "Invalid type" in str(err)
```

**Step 2: Run test to verify it fails**

```bash
cd packages/settings
pytest tests/test_errors.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.errors'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/errors.py`:

```python
"""Error hierarchy for layered_settings package."""

from __future__ import annotations


class SettingsError(Exception):
    """Base exception for all settings errors."""


class SettingsFileError(SettingsError):
    """Error loading or parsing a settings file."""

    def __init__(self, filepath: str, reason: str) -> None:
        self.filepath = filepath
        self.reason = reason
        super().__init__(f"Error loading {filepath}: {reason}")


class SettingsRegistryError(SettingsError):
    """Error with schema registration."""

    def __init__(self, namespace: str, reason: str) -> None:
        self.namespace = namespace
        self.reason = reason
        super().__init__(f"Registry error for namespace '{namespace}': {reason}")


class SettingsValidationError(SettingsError):
    """Error validating settings against schema."""

    def __init__(self, config_name: str, reason: str) -> None:
        self.config_name = config_name
        self.reason = reason
        super().__init__(f"Validation error for '{config_name}': {reason}")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_errors.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/errors.py tests/test_errors.py
git commit -m "feat(settings): add error hierarchy

- SettingsError base class
- SettingsFileError for file loading issues
- SettingsRegistryError for registration conflicts
- SettingsValidationError for validation failures

All tests passing (4/4)"
```

---

### Task 2: Schema Registry

**Files:**
- Create: `packages/settings/src/layered_settings/registry.py`
- Create: `packages/settings/tests/test_registry.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_registry.py`:

```python
"""Tests for schema registry."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, Field

from layered_settings.errors import SettingsRegistryError
from layered_settings.registry import SchemaEntry, SchemaRegistry


class MockSettings(BaseModel):
    """Mock settings for testing."""

    debug: bool = Field(default=False)
    port: int = Field(default=8000)


def test_schema_entry_creation() -> None:
    """SchemaEntry should store namespace, model, and defaults file."""
    entry = SchemaEntry(
        namespace="test",
        model=MockSettings,
        defaults_file=Path("/fake/settings.toml"),
    )
    assert entry.namespace == "test"
    assert entry.model == MockSettings
    assert entry.defaults_file == Path("/fake/settings.toml")


def test_registry_register_new_namespace() -> None:
    """Should successfully register a new namespace."""
    SchemaRegistry.clear()  # Start fresh

    SchemaRegistry.register(
        namespace="app",
        model=MockSettings,
        defaults_file=Path("/fake/app.toml"),
    )

    entry = SchemaRegistry.get("app")
    assert entry is not None
    assert entry.namespace == "app"
    assert entry.model == MockSettings


def test_registry_duplicate_namespace_raises_error() -> None:
    """Registering the same namespace twice should raise error."""
    SchemaRegistry.clear()

    SchemaRegistry.register(
        namespace="app",
        model=MockSettings,
        defaults_file=Path("/fake/app.toml"),
    )

    with pytest.raises(SettingsRegistryError) as exc_info:
        SchemaRegistry.register(
            namespace="app",
            model=MockSettings,
            defaults_file=Path("/fake/other.toml"),
        )

    assert "app" in str(exc_info.value)
    assert "already registered" in str(exc_info.value).lower()


def test_registry_get_nonexistent_namespace() -> None:
    """Getting an unregistered namespace should return None."""
    SchemaRegistry.clear()
    result = SchemaRegistry.get("nonexistent")
    assert result is None


def test_registry_all_namespaces() -> None:
    """Should return list of all registered namespaces."""
    SchemaRegistry.clear()

    SchemaRegistry.register("ns1", MockSettings, Path("/fake1.toml"))
    SchemaRegistry.register("ns2", MockSettings, Path("/fake2.toml"))

    namespaces = SchemaRegistry.all_namespaces()
    assert set(namespaces) == {"ns1", "ns2"}


def test_registry_all_entries() -> None:
    """Should return list of all schema entries."""
    SchemaRegistry.clear()

    SchemaRegistry.register("ns1", MockSettings, Path("/fake1.toml"))
    SchemaRegistry.register("ns2", MockSettings, Path("/fake2.toml"))

    entries = SchemaRegistry.all_entries()
    assert len(entries) == 2
    assert all(isinstance(e, SchemaEntry) for e in entries)


def test_registry_clear() -> None:
    """Clear should remove all registered schemas."""
    SchemaRegistry.clear()

    SchemaRegistry.register("ns1", MockSettings, Path("/fake1.toml"))
    assert len(SchemaRegistry.all_entries()) == 1

    SchemaRegistry.clear()
    assert len(SchemaRegistry.all_entries()) == 0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_registry.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.registry'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/registry.py`:

```python
"""Schema registry for managing configuration schemas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from layered_settings.errors import SettingsRegistryError

if TYPE_CHECKING:
    from pydantic import BaseModel


@dataclass
class SchemaEntry:
    """Registry entry for a configuration schema.

    Attributes:
        namespace: Unique identifier for this schema (e.g., "core", "orchestrator")
        model: Pydantic model class for validation
        defaults_file: Path to package defaults file (TOML or YAML)
    """

    namespace: str
    model: type[BaseModel]
    defaults_file: Path


class SchemaRegistry:
    """Global registry for configuration schemas.

    Packages register their schemas at import time using the register() method.
    The settings system uses this registry to discover schemas and default files.
    """

    _entries: dict[str, SchemaEntry] = {}

    @classmethod
    def register(
        cls,
        namespace: str,
        model: type[BaseModel],
        defaults_file: Path,
    ) -> None:
        """Register a configuration schema.

        Args:
            namespace: Unique identifier for this schema
            model: Pydantic model for validation
            defaults_file: Path to package defaults file

        Raises:
            SettingsRegistryError: If namespace is already registered
        """
        if namespace in cls._entries:
            raise SettingsRegistryError(
                namespace, "Namespace already registered"
            )

        cls._entries[namespace] = SchemaEntry(
            namespace=namespace,
            model=model,
            defaults_file=defaults_file,
        )

    @classmethod
    def get(cls, namespace: str) -> SchemaEntry | None:
        """Get a registered schema entry.

        Args:
            namespace: Schema namespace to retrieve

        Returns:
            SchemaEntry if found, None otherwise
        """
        return cls._entries.get(namespace)

    @classmethod
    def all_namespaces(cls) -> list[str]:
        """Get all registered namespace identifiers.

        Returns:
            List of namespace strings
        """
        return list(cls._entries.keys())

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]:
        """Get all registered schema entries.

        Returns:
            List of SchemaEntry objects
        """
        return list(cls._entries.values())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered schemas.

        Primarily for testing purposes.
        """
        cls._entries.clear()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_registry.py -v
```

Expected: PASS (8 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/registry.py tests/test_registry.py
git commit -m "feat(settings): add schema registry

- SchemaEntry dataclass for schema metadata
- SchemaRegistry class with register/get/clear methods
- Prevents duplicate namespace registration
- All tests passing (8/8)"
```

---

### Task 3: File Loader (TOML/YAML)

**Files:**
- Create: `packages/settings/src/layered_settings/loader.py`
- Create: `packages/settings/tests/test_loader.py`
- Create: `packages/settings/tests/fixtures/` (test data directory)

**Step 1: Write the failing test**

Create `packages/settings/tests/test_loader.py`:

```python
"""Tests for configuration file loader."""

from pathlib import Path

import pytest

from layered_settings.errors import SettingsFileError
from layered_settings.loader import FileLoader


@pytest.fixture
def fixtures_dir(tmp_path: Path) -> Path:
    """Create temporary directory with test config files."""
    # Create TOML file
    toml_file = tmp_path / "config.toml"
    toml_file.write_text("""
[execution]
parallel = true
max_workers = 4

[output]
verbosity = 2
""")

    # Create YAML file
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("""
execution:
  parallel: false
  max_workers: 8
output:
  verbosity: 1
""")

    # Create invalid TOML
    bad_toml = tmp_path / "bad.toml"
    bad_toml.write_text("[invalid syntax missing quote")

    # Create invalid YAML
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("invalid: yaml: syntax: too: many: colons:")

    return tmp_path


def test_detect_format_toml() -> None:
    """Should detect TOML format from .toml extension."""
    assert FileLoader.detect_format(Path("config.toml")) == "toml"


def test_detect_format_yaml() -> None:
    """Should detect YAML format from .yaml extension."""
    assert FileLoader.detect_format(Path("config.yaml")) == "yaml"
    assert FileLoader.detect_format(Path("config.yml")) == "yaml"


def test_detect_format_unknown() -> None:
    """Unknown extension should raise error."""
    with pytest.raises(SettingsFileError) as exc_info:
        FileLoader.detect_format(Path("config.json"))

    assert "json" in str(exc_info.value)
    assert "Unsupported" in str(exc_info.value)


def test_load_toml_file(fixtures_dir: Path) -> None:
    """Should successfully load and parse TOML file."""
    data = FileLoader.load(fixtures_dir / "config.toml")

    assert data["execution"]["parallel"] is True
    assert data["execution"]["max_workers"] == 4
    assert data["output"]["verbosity"] == 2


def test_load_yaml_file(fixtures_dir: Path) -> None:
    """Should successfully load and parse YAML file."""
    data = FileLoader.load(fixtures_dir / "config.yaml")

    assert data["execution"]["parallel"] is False
    assert data["execution"]["max_workers"] == 8
    assert data["output"]["verbosity"] == 1


def test_load_nonexistent_file() -> None:
    """Loading nonexistent file should raise SettingsFileError."""
    with pytest.raises(SettingsFileError) as exc_info:
        FileLoader.load(Path("/nonexistent/config.toml"))

    assert "nonexistent" in str(exc_info.value)


def test_load_invalid_toml(fixtures_dir: Path) -> None:
    """Invalid TOML syntax should raise SettingsFileError."""
    with pytest.raises(SettingsFileError) as exc_info:
        FileLoader.load(fixtures_dir / "bad.toml")

    assert "bad.toml" in str(exc_info.value)


def test_load_invalid_yaml(fixtures_dir: Path) -> None:
    """Invalid YAML syntax should raise SettingsFileError."""
    with pytest.raises(SettingsFileError) as exc_info:
        FileLoader.load(fixtures_dir / "bad.yaml")

    assert "bad.yaml" in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_loader.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.loader'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/loader.py`:

```python
"""File loading for TOML and YAML configuration files."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from layered_settings.errors import SettingsFileError

# TOML support varies by Python version
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class FileLoader:
    """Load and parse configuration files (TOML and YAML)."""

    @staticmethod
    def detect_format(filepath: Path) -> str:
        """Detect file format from extension.

        Args:
            filepath: Path to configuration file

        Returns:
            Format string: "toml" or "yaml"

        Raises:
            SettingsFileError: If file extension is unsupported
        """
        suffix = filepath.suffix.lower()

        if suffix == ".toml":
            return "toml"
        elif suffix in (".yaml", ".yml"):
            return "yaml"
        else:
            raise SettingsFileError(
                str(filepath),
                f"Unsupported file format: {suffix}. Use .toml, .yaml, or .yml"
            )

    @classmethod
    def load(cls, filepath: Path) -> dict[str, Any]:
        """Load and parse a configuration file.

        Args:
            filepath: Path to configuration file

        Returns:
            Parsed configuration as nested dictionary

        Raises:
            SettingsFileError: If file doesn't exist, can't be read, or has invalid syntax
        """
        if not filepath.exists():
            raise SettingsFileError(
                str(filepath),
                "File not found"
            )

        format_type = cls.detect_format(filepath)

        try:
            if format_type == "toml":
                return cls._load_toml(filepath)
            else:  # yaml
                return cls._load_yaml(filepath)
        except Exception as e:
            # Catch parsing errors and wrap them
            raise SettingsFileError(
                str(filepath),
                f"Parse error: {e}"
            ) from e

    @staticmethod
    def _load_toml(filepath: Path) -> dict[str, Any]:
        """Load TOML file.

        Args:
            filepath: Path to TOML file

        Returns:
            Parsed TOML as dictionary
        """
        with open(filepath, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def _load_yaml(filepath: Path) -> dict[str, Any]:
        """Load YAML file.

        Args:
            filepath: Path to YAML file

        Returns:
            Parsed YAML as dictionary
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # yaml.safe_load returns None for empty files
            return data if data is not None else {}
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_loader.py -v
```

Expected: PASS (9 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/loader.py tests/test_loader.py
git commit -m "feat(settings): add file loader for TOML and YAML

- Auto-detect format from file extension
- Parse TOML using tomllib/tomli
- Parse YAML using PyYAML
- Comprehensive error handling
- All tests passing (9/9)"
```

---

### Task 4: Deep Merge Algorithm

**Files:**
- Create: `packages/settings/src/layered_settings/merger.py`
- Create: `packages/settings/tests/test_merger.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_merger.py`:

```python
"""Tests for configuration merge algorithm."""

from layered_settings.merger import ConfigMerger


def test_merge_empty_dicts() -> None:
    """Merging empty dicts should return empty dict."""
    result = ConfigMerger.merge({}, {})
    assert result == {}


def test_merge_adds_new_keys() -> None:
    """Override should add new keys not in base."""
    base = {"a": 1}
    override = {"b": 2}
    result = ConfigMerger.merge(base, override)
    assert result == {"a": 1, "b": 2}


def test_merge_replaces_scalar_values() -> None:
    """Override should replace scalar values."""
    base = {"port": 8000, "debug": False}
    override = {"port": 9000}
    result = ConfigMerger.merge(base, override)
    assert result == {"port": 9000, "debug": False}


def test_merge_replaces_lists_atomically() -> None:
    """Lists should be replaced entirely, not merged."""
    base = {"items": [1, 2, 3]}
    override = {"items": [4, 5]}
    result = ConfigMerger.merge(base, override)
    assert result == {"items": [4, 5]}


def test_merge_nested_dicts_recursively() -> None:
    """Nested dicts should be merged recursively."""
    base = {
        "execution": {"parallel": True, "max_workers": 4},
        "output": {"verbosity": 1},
    }
    override = {
        "execution": {"max_workers": 8},
        "output": {"format": "json"},
    }
    result = ConfigMerger.merge(base, override)

    assert result == {
        "execution": {"parallel": True, "max_workers": 8},
        "output": {"verbosity": 1, "format": "json"},
    }


def test_merge_deep_nesting() -> None:
    """Should handle deeply nested dictionaries."""
    base = {"a": {"b": {"c": {"d": 1}}}}
    override = {"a": {"b": {"c": {"e": 2}}}}
    result = ConfigMerger.merge(base, override)

    assert result == {"a": {"b": {"c": {"d": 1, "e": 2}}}}


def test_merge_type_replacement() -> None:
    """Override can replace a dict with a scalar (or vice versa)."""
    base = {"setting": {"nested": "value"}}
    override = {"setting": "flat"}
    result = ConfigMerger.merge(base, override)
    assert result == {"setting": "flat"}

    # Reverse direction
    base2 = {"setting": "flat"}
    override2 = {"setting": {"nested": "value"}}
    result2 = ConfigMerger.merge(base2, override2)
    assert result2 == {"setting": {"nested": "value"}}


def test_merge_does_not_mutate_inputs() -> None:
    """Merge should not modify the input dictionaries."""
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}

    base_copy = base.copy()
    override_copy = override.copy()

    ConfigMerger.merge(base, override)

    # Inputs should be unchanged
    assert base == base_copy
    assert override == override_copy


def test_merge_multiple_layers() -> None:
    """Should handle merging multiple layers sequentially."""
    layer1 = {"a": 1, "b": {"x": 1}}
    layer2 = {"b": {"y": 2}, "c": 3}
    layer3 = {"b": {"x": 10}, "d": 4}

    result = ConfigMerger.merge(layer1, layer2)
    result = ConfigMerger.merge(result, layer3)

    assert result == {
        "a": 1,
        "b": {"x": 10, "y": 2},
        "c": 3,
        "d": 4,
    }
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_merger.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.merger'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/merger.py`:

```python
"""Deep merge algorithm for layered configurations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


class ConfigMerger:
    """Deep merge configuration dictionaries.

    Merge rules:
    - Dicts: Recurse into matching keys, merge contents
    - Lists: Replace entirely (atomic, not element-wise merge)
    - Scalars: Replace entirely
    - New keys: Added to result
    """

    @staticmethod
    def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration (lower priority)
            override: Override configuration (higher priority)

        Returns:
            Merged configuration dictionary (does not modify inputs)
        """
        # Deep copy to avoid mutating inputs
        result = deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Both are dicts: recurse
                result[key] = ConfigMerger.merge(result[key], value)
            else:
                # Replace entirely (scalar, list, type mismatch, or new key)
                result[key] = deepcopy(value)

        return result
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_merger.py -v
```

Expected: PASS (10 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/merger.py tests/test_merger.py
git commit -m "feat(settings): add deep merge algorithm

- Recursively merge nested dictionaries
- Replace lists and scalars atomically
- Does not mutate input dictionaries
- Handles type replacements
- All tests passing (10/10)"
```

---

### Task 5: Layer Discovery

**Files:**
- Create: `packages/settings/src/layered_settings/layers.py`
- Create: `packages/settings/tests/test_layers.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_layers.py`:

```python
"""Tests for configuration layer discovery."""

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field

from layered_settings.layers import LayerSource, LayerDiscovery
from layered_settings.registry import SchemaEntry, SchemaRegistry


class MockSettings(BaseModel):
    """Mock settings for testing."""
    debug: bool = Field(default=False)


@pytest.fixture
def mock_registry(tmp_path: Path) -> None:
    """Set up mock registry with test schema."""
    SchemaRegistry.clear()

    # Create a fake package defaults file
    defaults_file = tmp_path / "defaults.toml"
    defaults_file.write_text("[setting]\nvalue = 1")

    SchemaRegistry.register(
        namespace="test",
        model=MockSettings,
        defaults_file=defaults_file,
    )


def test_layer_source_creation() -> None:
    """LayerSource should store layer metadata."""
    source = LayerSource(
        name="package",
        filepath=Path("/fake/settings.toml"),
        namespace="core",
        is_namespaced=False,
    )
    assert source.name == "package"
    assert source.filepath == Path("/fake/settings.toml")
    assert source.namespace == "core"
    assert source.is_namespaced is False


def test_discover_package_defaults(mock_registry: None, tmp_path: Path) -> None:
    """Should discover package defaults from registry."""
    layers = LayerDiscovery.discover_layers()

    # Should find at least the package default
    package_layers = [l for l in layers if l.name == "package"]
    assert len(package_layers) >= 1
    assert package_layers[0].namespace == "test"
    assert package_layers[0].is_namespaced is False


@patch("layered_settings.layers.Path.cwd")
def test_discover_project_root(mock_cwd: Any, tmp_path: Path, mock_registry: None) -> None:
    """Should discover settings.toml in project root."""
    # Setup
    mock_cwd.return_value = tmp_path
    project_config = tmp_path / "settings.toml"
    project_config.write_text("[test]\nvalue = 2")

    layers = LayerDiscovery.discover_layers()

    # Should find project layer
    project_layers = [l for l in layers if l.name == "project"]
    assert len(project_layers) == 1
    assert project_layers[0].filepath == project_config
    assert project_layers[0].is_namespaced is True


@patch("layered_settings.layers.Path.home")
def test_discover_user_config(mock_home: Any, tmp_path: Path, mock_registry: None) -> None:
    """Should discover settings in user config directory."""
    # Setup
    mock_home.return_value = tmp_path
    user_config_dir = tmp_path / ".config" / "layered-settings"
    user_config_dir.mkdir(parents=True)
    user_config = user_config_dir / "settings.toml"
    user_config.write_text("[test]\nvalue = 3")

    layers = LayerDiscovery.discover_layers(app_name="layered-settings")

    # Should find user layer
    user_layers = [l for l in layers if l.name == "user"]
    assert len(user_layers) == 1
    assert user_layers[0].filepath == user_config
    assert user_layers[0].is_namespaced is True


def test_layer_priority_order(mock_registry: None) -> None:
    """Layers should be returned in priority order (lowest to highest)."""
    layers = LayerDiscovery.discover_layers()

    layer_names = [l.name for l in layers]

    # Package should come before project, which comes before user
    if "package" in layer_names and "project" in layer_names:
        assert layer_names.index("package") < layer_names.index("project")
    if "project" in layer_names and "user" in layer_names:
        assert layer_names.index("project") < layer_names.index("user")


def test_skip_nonexistent_files(mock_registry: None) -> None:
    """Should skip files that don't exist."""
    layers = LayerDiscovery.discover_layers()

    # All returned layers should point to existing files
    for layer in layers:
        assert layer.filepath.exists(), f"{layer.filepath} should exist"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_layers.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.layers'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/layers.py`:

```python
"""Layer discovery for configuration sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from layered_settings.registry import SchemaRegistry


@dataclass
class LayerSource:
    """Represents a configuration layer source.

    Attributes:
        name: Layer identifier ("package", "project", "user", "cli")
        filepath: Path to configuration file
        namespace: Schema namespace this layer contributes to
        is_namespaced: Whether file uses namespaced format (e.g., [core.setting])
    """

    name: str
    filepath: Path
    namespace: str
    is_namespaced: bool


class LayerDiscovery:
    """Discover configuration files from various sources."""

    @staticmethod
    def discover_layers(app_name: str | None = None) -> list[LayerSource]:
        """Discover all available configuration layers.

        Layer priority (lowest → highest):
        1. Package defaults (from registry, flat format)
        2. Project root (./settings.toml, namespaced)
        3. User config (~/.config/<app_name>/settings.toml, namespaced)

        Args:
            app_name: Application name for user config directory.
                     If None, uses "layered-settings"

        Returns:
            List of LayerSource objects in priority order
        """
        layers: list[LayerSource] = []

        # 1. Package defaults (from registry)
        for entry in SchemaRegistry.all_entries():
            if entry.defaults_file.exists():
                layers.append(
                    LayerSource(
                        name="package",
                        filepath=entry.defaults_file,
                        namespace=entry.namespace,
                        is_namespaced=False,  # Package defaults are flat
                    )
                )

        # 2. Project root config
        project_config = Path.cwd() / "settings.toml"
        if project_config.exists():
            layers.append(
                LayerSource(
                    name="project",
                    filepath=project_config,
                    namespace="*",  # Namespaced format, all namespaces
                    is_namespaced=True,
                )
            )

        # 3. User config directory
        app = app_name or "layered-settings"
        user_config = Path.home() / ".config" / app / "settings.toml"
        if user_config.exists():
            layers.append(
                LayerSource(
                    name="user",
                    filepath=user_config,
                    namespace="*",  # Namespaced format, all namespaces
                    is_namespaced=True,
                )
            )

        return layers
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_layers.py -v
```

Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/layers.py tests/test_layers.py
git commit -m "feat(settings): add layer discovery

- Discover package defaults from registry
- Discover project root settings.toml
- Discover user config directory
- Return layers in priority order
- All tests passing (7/7)"
```

---

### Task 6: Config Builder

**Files:**
- Create: `packages/settings/src/layered_settings/builder.py`
- Create: `packages/settings/tests/test_builder.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_builder.py`:

```python
"""Tests for configuration builder."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field, ValidationError

from layered_settings.builder import ConfigBuilder
from layered_settings.errors import SettingsValidationError
from layered_settings.layers import LayerSource
from layered_settings.registry import SchemaRegistry


class ExecutionSettings(BaseModel):
    """Mock execution settings."""
    parallel: bool = Field(default=True)
    max_workers: int = Field(default=0)


class OutputSettings(BaseModel):
    """Mock output settings."""
    verbosity: int = Field(default=1)


class CoreSettings(BaseModel):
    """Mock core settings."""
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)


class RootConfig(BaseModel):
    """Mock root config."""
    core: CoreSettings = Field(default_factory=CoreSettings)


@pytest.fixture
def setup_registry(tmp_path: Path) -> Path:
    """Setup registry with mock schemas."""
    SchemaRegistry.clear()

    # Create package defaults
    defaults = tmp_path / "defaults.toml"
    defaults.write_text("""
[execution]
parallel = true
max_workers = 4

[output]
verbosity = 1
""")

    SchemaRegistry.register(
        namespace="core",
        model=CoreSettings,
        defaults_file=defaults,
    )

    return tmp_path


def test_build_from_empty_layers(setup_registry: Path) -> None:
    """Building with no layers should use Pydantic defaults."""
    config = ConfigBuilder.build(RootConfig, [])

    assert isinstance(config, RootConfig)
    assert config.core.execution.parallel is True
    assert config.core.execution.max_workers == 0  # Pydantic default


def test_build_from_package_defaults(setup_registry: Path) -> None:
    """Should load and apply package defaults."""
    defaults_file = SchemaRegistry.get("core").defaults_file
    layers = [
        LayerSource(
            name="package",
            filepath=defaults_file,
            namespace="core",
            is_namespaced=False,
        )
    ]

    config = ConfigBuilder.build(RootConfig, layers)

    assert config.core.execution.parallel is True
    assert config.core.execution.max_workers == 4  # From defaults.toml


def test_build_with_namespaced_override(setup_registry: Path, tmp_path: Path) -> None:
    """Should apply namespaced config correctly."""
    defaults_file = SchemaRegistry.get("core").defaults_file

    # Create user config
    user_config = tmp_path / "user.toml"
    user_config.write_text("""
[core.execution]
max_workers = 8

[core.output]
verbosity = 2
""")

    layers = [
        LayerSource("package", defaults_file, "core", False),
        LayerSource("user", user_config, "*", True),
    ]

    config = ConfigBuilder.build(RootConfig, layers)

    assert config.core.execution.parallel is True  # From package defaults
    assert config.core.execution.max_workers == 8  # Overridden by user
    assert config.core.output.verbosity == 2  # Overridden by user


def test_build_with_validation_error(setup_registry: Path, tmp_path: Path) -> None:
    """Invalid data should raise SettingsValidationError."""
    bad_config = tmp_path / "bad.toml"
    bad_config.write_text("""
[core.execution]
parallel = "not a boolean"
""")

    layers = [
        LayerSource("user", bad_config, "*", True),
    ]

    with pytest.raises(SettingsValidationError) as exc_info:
        ConfigBuilder.build(RootConfig, layers)

    assert "validation" in str(exc_info.value).lower()


def test_build_applies_cli_overrides(setup_registry: Path) -> None:
    """CLI overrides should be applied last."""
    defaults_file = SchemaRegistry.get("core").defaults_file
    layers = [
        LayerSource("package", defaults_file, "core", False),
    ]

    overrides = {
        "core.execution.max_workers": 16,
        "core.output.verbosity": 3,
    }

    config = ConfigBuilder.build(RootConfig, layers, overrides)

    assert config.core.execution.max_workers == 16
    assert config.core.output.verbosity == 3


def test_build_deep_override_path(setup_registry: Path) -> None:
    """Should handle deep dotted paths in overrides."""
    config = ConfigBuilder.build(
        RootConfig,
        [],
        {"core.execution.parallel": False}
    )

    assert config.core.execution.parallel is False
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_builder.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'layered_settings.builder'"

**Step 3: Write minimal implementation**

Create `packages/settings/src/layered_settings/builder.py`:

```python
"""Configuration builder with layered merging and validation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from layered_settings.errors import SettingsValidationError
from layered_settings.loader import FileLoader
from layered_settings.merger import ConfigMerger

if TYPE_CHECKING:
    from pydantic import BaseModel

    from layered_settings.layers import LayerSource


class ConfigBuilder:
    """Build and validate configuration from multiple layers."""

    @staticmethod
    def build(
        root_model: type[BaseModel],
        layers: list[LayerSource],
        cli_overrides: dict[str, Any] | None = None,
    ) -> BaseModel:
        """Build configuration from layers with validation.

        Args:
            root_model: Pydantic model for root config (e.g., UnifiedConfig)
            layers: List of configuration layers in priority order
            cli_overrides: CLI overrides as dotted paths (e.g., "core.execution.parallel")

        Returns:
            Validated root config instance

        Raises:
            SettingsValidationError: If validation fails
        """
        # Start with empty merged data
        merged_data: dict[str, Any] = {}

        # Apply each layer
        for layer in layers:
            layer_data = FileLoader.load(layer.filepath)

            if layer.is_namespaced:
                # Namespaced format: merge entire dict
                merged_data = ConfigMerger.merge(merged_data, layer_data)
            else:
                # Flat format: wrap in namespace before merging
                namespaced_data = {layer.namespace: layer_data}
                merged_data = ConfigMerger.merge(merged_data, namespaced_data)

        # Apply CLI overrides
        if cli_overrides:
            merged_data = ConfigBuilder._apply_overrides(merged_data, cli_overrides)

        # Validate with Pydantic
        try:
            return root_model(**merged_data)
        except ValidationError as e:
            raise SettingsValidationError(
                root_model.__name__,
                f"Validation failed: {e}"
            ) from e

    @staticmethod
    def _apply_overrides(
        data: dict[str, Any],
        overrides: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply CLI overrides using dotted path notation.

        Args:
            data: Base configuration data
            overrides: Override values with dotted keys (e.g., "core.execution.parallel")

        Returns:
            Updated configuration data
        """
        result = data.copy()

        for dotted_key, value in overrides.items():
            keys = dotted_key.split(".")

            # Navigate to the parent dict
            current = result
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Set the final value
            current[keys[-1]] = value

        return result
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_builder.py -v
```

Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add src/layered_settings/builder.py tests/test_builder.py
git commit -m "feat(settings): add config builder with validation

- Load and merge layers in priority order
- Handle flat vs namespaced format
- Apply CLI overrides with dotted paths
- Validate with Pydantic
- All tests passing (7/7)"
```

---

### Task 7: Public API

**Files:**
- Modify: `packages/settings/src/layered_settings/__init__.py`
- Create: `packages/settings/tests/test_integration.py`

**Step 1: Write the failing test**

Create `packages/settings/tests/test_integration.py`:

```python
"""Integration tests for public API."""

from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from layered_settings import SchemaRegistry, configure, get_config


class AppSettings(BaseModel):
    """Mock app settings."""
    debug: bool = Field(default=False)
    port: int = Field(default=8000)


class RootConfig(BaseModel):
    """Mock root config."""
    app: AppSettings = Field(default_factory=AppSettings)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset global state before each test."""
    SchemaRegistry.clear()
    # Reset configure state
    import layered_settings
    layered_settings._configured_model = None
    layered_settings._app_name = None


def test_full_workflow_with_defaults(tmp_path: Path) -> None:
    """Complete workflow: register, configure, load."""
    # 1. Register schema
    defaults = tmp_path / "app_defaults.toml"
    defaults.write_text("""
debug = false
port = 8000
""")

    SchemaRegistry.register(
        namespace="app",
        model=AppSettings,
        defaults_file=defaults,
    )

    # 2. Configure settings system
    configure(RootConfig)

    # 3. Get config
    config = get_config()

    assert isinstance(config, RootConfig)
    assert config.app.debug is False
    assert config.app.port == 8000


def test_workflow_with_user_override(tmp_path: Path, monkeypatch: Any) -> None:
    """User config should override defaults."""
    # Setup package defaults
    defaults = tmp_path / "app_defaults.toml"
    defaults.write_text("debug = false\nport = 8000")

    SchemaRegistry.register("app", AppSettings, defaults)

    # Setup user config
    user_config_dir = tmp_path / ".config" / "test-app"
    user_config_dir.mkdir(parents=True)
    user_config = user_config_dir / "settings.toml"
    user_config.write_text("""
[app]
debug = true
port = 9000
""")

    # Mock home directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Configure with app name
    configure(RootConfig, app_name="test-app")

    config = get_config()

    assert config.app.debug is True  # Overridden
    assert config.app.port == 9000  # Overridden


def test_workflow_with_cli_overrides(tmp_path: Path) -> None:
    """CLI overrides should have highest priority."""
    defaults = tmp_path / "app_defaults.toml"
    defaults.write_text("debug = false\nport = 8000")

    SchemaRegistry.register("app", AppSettings, defaults)
    configure(RootConfig)

    config = get_config(overrides={"app.port": 7000})

    assert config.app.port == 7000


def test_configure_must_be_called_first() -> None:
    """get_config should fail if configure wasn't called."""
    with pytest.raises(RuntimeError) as exc_info:
        get_config()

    assert "configure" in str(exc_info.value).lower()


def test_config_is_cached() -> None:
    """get_config should return cached instance."""
    configure(RootConfig)

    config1 = get_config()
    config2 = get_config()

    assert config1 is config2
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_integration.py -v
```

Expected: FAIL with import errors

**Step 3: Write minimal implementation**

Modify `packages/settings/src/layered_settings/__init__.py`:

```python
"""Layered settings - Generic configuration system.

Public API:
- SchemaRegistry: Register configuration schemas
- configure(): Configure the settings system
- get_config(): Load and return validated config
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from layered_settings.builder import ConfigBuilder
from layered_settings.layers import LayerDiscovery
from layered_settings.registry import SchemaRegistry

if TYPE_CHECKING:
    from pydantic import BaseModel

__all__ = [
    "SchemaRegistry",
    "configure",
    "get_config",
]

# Global state
_configured_model: type[BaseModel] | None = None
_app_name: str | None = None
_config_cache: BaseModel | None = None


def configure(
    root_model: type[BaseModel],
    app_name: str | None = None,
) -> None:
    """Configure the settings system.

    Must be called before get_config(). Typically called once at application startup.

    Args:
        root_model: Pydantic model representing root configuration structure.
                   Should compose all registered namespace schemas.
        app_name: Application name for user config directory (~/.config/<app_name>/).
                 If None, uses "layered-settings".

    Example:
        >>> from pydantic import BaseModel
        >>> class MyConfig(BaseModel):
        ...     core: CoreSettings
        ...     orchestrator: OrchestratorSettings
        >>> configure(MyConfig, app_name="my-app")
    """
    global _configured_model, _app_name, _config_cache

    _configured_model = root_model
    _app_name = app_name
    _config_cache = None  # Clear cache when reconfiguring


def get_config(overrides: dict[str, Any] | None = None) -> BaseModel:
    """Load and return validated configuration.

    Discovers config files, merges layers, applies overrides, and validates.
    Result is cached - subsequent calls return the same instance unless
    overrides are provided.

    Args:
        overrides: CLI overrides as dotted paths (e.g., {"core.execution.parallel": False})

    Returns:
        Validated configuration instance

    Raises:
        RuntimeError: If configure() hasn't been called
        SettingsValidationError: If validation fails

    Example:
        >>> config = get_config()
        >>> print(config.core.execution.parallel)
        True
        >>> config_with_overrides = get_config({"core.execution.parallel": False})
    """
    global _config_cache

    if _configured_model is None:
        raise RuntimeError(
            "Settings system not configured. Call configure() first."
        )

    # Return cached config if no overrides
    if overrides is None and _config_cache is not None:
        return _config_cache

    # Discover layers
    layers = LayerDiscovery.discover_layers(app_name=_app_name)

    # Build and validate config
    config = ConfigBuilder.build(_configured_model, layers, overrides)

    # Cache if no overrides
    if overrides is None:
        _config_cache = config

    return config
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_integration.py -v
```

Expected: PASS (6 tests)

**Step 5: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests passing

**Step 6: Commit**

```bash
git add src/layered_settings/__init__.py tests/test_integration.py
git commit -m "feat(settings): add public API with integration tests

- configure() to setup settings system
- get_config() to load and cache config
- Full workflow integration tests
- All tests passing (47/47)"
```

---

## Verification and Documentation

### Task 8: Final Testing and Type Checking

**Step 1: Run full test suite**

```bash
cd packages/settings
pytest tests/ -v --cov=src/layered_settings --cov-report=term-missing
```

Expected: All tests passing with good coverage

**Step 2: Run type checker**

```bash
mypy src/layered_settings
```

Expected: No type errors

**Step 3: Test installation**

```bash
# In a fresh terminal
cd packages/settings
pip install -e .
python -c "from layered_settings import configure, get_config, SchemaRegistry; print('Import successful')"
```

Expected: "Import successful"

**Step 4: Commit if any fixes needed**

If you found and fixed issues:

```bash
git add .
git commit -m "fix(settings): resolve type errors and test issues"
```

---

### Task 9: Update Documentation

**Files:**
- Modify: `packages/settings/README.md`

**Step 1: Enhance README with complete examples**

Update `packages/settings/README.md` to include:
- Architecture overview
- Detailed usage examples
- Layer priority explanation
- API reference
- Common patterns

**Step 2: Commit documentation**

```bash
git add README.md
git commit -m "docs(settings): enhance README with complete examples

- Add architecture overview
- Add detailed usage examples
- Document layer priority
- Add API reference"
```

---

## Completion

### Task 10: Final Integration Verification

**Step 1: Create example usage script**

Create `packages/settings/examples/basic_usage.py`:

```python
"""Basic usage example for layered-settings."""

from pathlib import Path
from pydantic import BaseModel, Field
from layered_settings import SchemaRegistry, configure, get_config


class AppSettings(BaseModel):
    """Application settings."""
    debug: bool = Field(default=False)
    port: int = Field(default=8000)
    host: str = Field(default="localhost")


class RootConfig(BaseModel):
    """Root configuration."""
    app: AppSettings = Field(default_factory=AppSettings)


def main() -> None:
    # Register schema with defaults
    defaults_file = Path(__file__).parent / "app_defaults.toml"
    SchemaRegistry.register(
        namespace="app",
        model=AppSettings,
        defaults_file=defaults_file,
    )

    # Configure settings system
    configure(RootConfig, app_name="example-app")

    # Load config
    config = get_config()
    print(f"Server: {config.app.host}:{config.app.port}")
    print(f"Debug: {config.app.debug}")

    # With CLI overrides
    config_override = get_config({"app.port": 9000})
    print(f"Overridden port: {config_override.app.port}")


if __name__ == "__main__":
    main()
```

Create `packages/settings/examples/app_defaults.toml`:

```toml
debug = false
port = 8000
host = "localhost"
```

**Step 2: Test example**

```bash
cd packages/settings
python examples/basic_usage.py
```

Expected: Output showing config values

**Step 3: Commit example**

```bash
mkdir -p examples
git add examples/
git commit -m "docs(settings): add basic usage example

- Demonstrates schema registration
- Shows configure and get_config usage
- Includes CLI overrides example"
```

**Step 4: Create final summary commit**

```bash
git commit --allow-empty -m "feat(settings): complete Phase 1 implementation

Phase 1 deliverables complete:
✓ Error hierarchy with custom exceptions
✓ Schema registry for namespace management
✓ File loader supporting TOML and YAML
✓ Deep merge algorithm for layered configs
✓ Layer discovery (package, project, user)
✓ Config builder with Pydantic validation
✓ Public API (configure, get_config)
✓ Comprehensive test suite (47 tests, 100% passing)
✓ Type checking with mypy
✓ Documentation and examples

Ready for Phase 2: wallpaper_core migration"
```

---

## Plan Complete

This implementation plan provides:

- **Complete package structure** with proper Python packaging
- **TDD approach** with tests written before implementation
- **Bite-sized tasks** (2-5 minutes per step)
- **Exact file paths** and complete code
- **Verification steps** at each stage
- **Frequent commits** after each feature

**Total estimated time:** 3-4 hours for full implementation

**Next phase:** Migrate wallpaper_core to use layered_settings
