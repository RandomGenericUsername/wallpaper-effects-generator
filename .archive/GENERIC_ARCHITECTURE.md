# Core + Orchestrator Architecture Pattern

A reusable architecture for Python CLI applications with layered configuration, exposing functionality via both Python module imports and CLI.

---

## 1. Package Structure

Three uv-managed packages in a monorepo:

```
project/
├── packages/
│   ├── settings/           # Shared config infrastructure
│   │   ├── src/project_settings/
│   │   └── pyproject.toml
│   │
│   ├── core/               # Business logic + CLI
│   │   ├── src/project_core/
│   │   └── pyproject.toml
│   │
│   └── orchestrator/       # Wraps core (e.g., containerization)
│       ├── src/project_orchestrator/
│       └── pyproject.toml
```

**Dependency direction:**
```
settings  ←──  core  ←──  orchestrator
```

---

## 2. Local Package Dependencies (uv)

Each package declares dependencies on sibling packages via `[tool.uv.sources]`:

```toml
# core/pyproject.toml
[project]
dependencies = [
    "project-settings>=0.1.0",
]

[tool.uv.sources]
project-settings = { path = "../settings", editable = true }
```

```toml
# orchestrator/pyproject.toml
[project]
dependencies = [
    "project-core>=0.1.0",
    "project-settings>=0.1.0",
]

[tool.uv.sources]
project-core = { path = "../core", editable = true }
project-settings = { path = "../settings", editable = true }
```

---

## 3. Core Package: Python API Exposure

### 3.1 Module Structure

```
core/src/project_core/
├── __init__.py              # Version, top-level exports
├── core/
│   ├── __init__.py          # Public API exports
│   ├── base.py              # Abstract interfaces
│   ├── types.py             # Data models (Pydantic)
│   └── exceptions.py        # Error hierarchy
├── config/
│   ├── __init__.py          # Schema registration
│   ├── config.py            # Pydantic settings models
│   └── settings.toml        # Package defaults
├── cli/
│   └── main.py              # Typer CLI
└── [domain modules]/        # Business logic
```

### 3.2 Public API via `__init__.py`

```python
# core/src/project_core/core/__init__.py
from project_core.core.base import BaseProcessor
from project_core.core.types import InputData, OutputData, ProcessorConfig
from project_core.core.exceptions import (
    CoreError,
    ValidationError,
    ProcessingError,
)

__all__ = [
    "BaseProcessor",
    "InputData",
    "OutputData",
    "ProcessorConfig",
    "CoreError",
    "ValidationError",
    "ProcessingError",
]
```

### 3.3 CLI Entry Point

```toml
# core/pyproject.toml
[project.scripts]
myapp = "project_core.cli.main:main"
```

```python
# core/src/project_core/cli/main.py
import typer
from project_settings import configure, get_config

class CoreOnlyConfig(BaseModel):
    """Unified config for standalone core usage."""
    core: AppConfig

configure(CoreOnlyConfig)

app = typer.Typer()

@app.command()
def process(...):
    config = get_config()
    # Use config.core.*
```

---

## 4. Orchestrator Package: Wrapping Core

### 4.1 Module Structure

```
orchestrator/src/project_orchestrator/
├── __init__.py
├── config/
│   ├── __init__.py          # Schema registration
│   ├── settings.py          # Orchestrator-specific settings
│   ├── settings.toml        # Package defaults
│   └── unified.py           # UnifiedConfig composing both schemas
├── cli/
│   └── main.py              # Typer CLI (same command name as core)
└── [orchestration modules]/ # Container management, etc.
```

### 4.2 Importing Core's Python API

```python
# orchestrator/src/project_orchestrator/cli/main.py
from project_core.core.types import InputData, OutputData
from project_core.config.enums import ProcessorType
from project_core.cli.main import some_command as core_some_command

# Direct delegation to core
core_some_command.callback(arg1=..., arg2=...)

# Or use core's types while adding orchestration layer
```

### 4.3 UnifiedConfig Composition

```python
# orchestrator/src/project_orchestrator/config/unified.py
from pydantic import BaseModel, ConfigDict, Field
from project_core.config.config import AppConfig
from project_orchestrator.config.settings import OrchestratorSettings

class UnifiedConfig(BaseModel):
    """Root config composing all namespaces."""
    model_config = ConfigDict(frozen=True)

    core: AppConfig = Field(default_factory=AppConfig)
    orchestrator: OrchestratorSettings = Field(default_factory=OrchestratorSettings)
```

### 4.4 CLI Bootstrap

```python
# orchestrator/src/project_orchestrator/cli/main.py
from project_settings import configure, get_config
from project_orchestrator.config.unified import UnifiedConfig

configure(UnifiedConfig)  # Register composed config

app = typer.Typer()

@app.command()
def process(...):
    config = get_config()
    config.core.some_setting        # Access core settings
    config.orchestrator.engine      # Access orchestrator settings
```

---

## 5. Settings Package: Layered Configuration

### 5.1 Module Structure

```
settings/src/project_settings/
├── __init__.py      # Public API: configure, get_config, SchemaRegistry
├── registry.py      # Schema registration (namespace → model → defaults file)
├── loader.py        # Layer discovery + TOML loading
├── merger.py        # Deep merge algorithm
├── overrides.py     # CLI override application
├── unified.py       # Build validated config from merged layers
├── transforms.py    # Env var resolution, key normalization
└── errors.py        # Error hierarchy
```

### 5.2 Schema Registry

Packages register their config schema at import time. The settings package has **zero knowledge** of specific schemas.

```python
# settings/src/project_settings/registry.py
@dataclass
class SchemaEntry:
    namespace: str           # "core" or "orchestrator"
    model: type[BaseModel]   # Pydantic model class
    defaults_file: Path      # Path to package's settings.toml

class SchemaRegistry:
    _entries: dict[str, SchemaEntry] = {}

    @classmethod
    def register(cls, namespace: str, model: type[BaseModel], defaults_file: Path):
        cls._entries[namespace] = SchemaEntry(namespace, model, defaults_file)

    @classmethod
    def all_entries(cls) -> list[SchemaEntry]: ...
    @classmethod
    def all_namespaces(cls) -> list[str]: ...
```

### 5.3 Registration at Import Time

```python
# core/src/project_core/config/__init__.py
from pathlib import Path
from project_settings import SchemaRegistry
from project_core.config.config import AppConfig

SchemaRegistry.register(
    namespace="core",
    model=AppConfig,
    defaults_file=Path(__file__).parent / "settings.toml",
)
```

```python
# orchestrator/src/project_orchestrator/config/__init__.py
from pathlib import Path
from project_settings import SchemaRegistry
from project_orchestrator.config.settings import OrchestratorSettings

SchemaRegistry.register(
    namespace="orchestrator",
    model=OrchestratorSettings,
    defaults_file=Path(__file__).parent / "settings.toml",
)
```

### 5.4 Layer Priority

```
Priority (lowest → highest):

1. Package defaults     packages/core/config/settings.toml         (flat sections)
                        packages/orchestrator/config/settings.toml  (flat sections)

2. Project root         ./settings.toml                             (namespaced)

3. User config          ~/.config/myapp/settings.toml               (namespaced)

4. CLI arguments        Applied via overrides dict
```

### 5.5 TOML Format

**Package defaults (flat sections):**
```toml
# core/config/settings.toml
[logging]
level = "INFO"

[processing]
default_mode = "fast"
timeout = 30
```

**Project/User config (namespaced sections):**
```toml
# ./settings.toml or ~/.config/myapp/settings.toml
[core.logging]
level = "DEBUG"

[core.processing]
timeout = 60

[orchestrator.container]
engine = "podman"
```

### 5.6 Merge Algorithm

```python
def deep_merge(base: dict, override: dict) -> dict:
    """
    Rules:
    - Dicts: recurse into matching keys
    - Lists: replace entirely (atomic)
    - Scalars: replace entirely
    - New keys: added
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

### 5.7 Public API

```python
# settings/src/project_settings/__init__.py
_config: BaseModel | None = None
_unified_model: type[BaseModel] | None = None

def configure(unified_model: type[BaseModel], **loader_kwargs):
    """Configure settings system before first load."""
    global _unified_model, _config
    _unified_model = unified_model
    _config = None

def load_config() -> BaseModel:
    """Load, merge, validate. Cached after first call."""
    # 1. discover_layers() → list[LayerSource]
    # 2. merge_layers() → dict per namespace
    # 3. build_unified_config() → validated Pydantic model
    ...

def get_config(overrides: dict | None = None) -> BaseModel:
    """Load config with optional CLI overrides."""
    config = load_config()
    if overrides:
        config = apply_overrides(config, overrides)
    return config
```

### 5.8 CLI Override Application

```python
def apply_overrides(config: BaseModel, overrides: dict) -> BaseModel:
    """
    Keys use dot notation: "core.processing.timeout" → 60
    Returns new validated instance (immutable pattern).
    """
    config_dict = config.model_dump()
    for dotted_key, value in overrides.items():
        # Walk path, set value
        ...
    return config.__class__.model_validate(config_dict)
```

---

## 6. CLI Usage Pattern

```python
@app.command()
def process(
    input_path: Path,
    timeout: int | None = typer.Option(None, "--timeout", "-t"),
):
    # Build overrides from CLI args
    overrides = {}
    if timeout is not None:
        overrides["core.processing.timeout"] = timeout

    # Get config with overrides
    config = get_config(overrides)

    # Use config
    config.core.processing.timeout
    config.orchestrator.container.engine
```

---

## 7. Abstract Interface Pattern (for pluggable implementations)

```python
# core/src/project_core/core/base.py
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, input: InputData, config: ProcessorConfig) -> OutputData:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

### Factory Pattern

```python
# core/src/project_core/factory.py
class ProcessorFactory:
    def __init__(self, settings: AppConfig):
        self.settings = settings

    def create(self, processor_type: ProcessorType) -> BaseProcessor:
        """Create processor, verify availability."""
        processor = self._instantiate(processor_type)
        if not processor.is_available():
            raise ProcessorNotAvailableError(processor.name)
        return processor

    def auto_detect(self) -> ProcessorType:
        """Return first available processor."""
        for ptype in ProcessorType:
            proc = self._instantiate(ptype)
            if proc.is_available():
                return ptype
        raise NoProcessorAvailableError()
```

---

## 8. Error Hierarchy

```python
# core/src/project_core/core/exceptions.py
class CoreError(Exception):
    """Base for all core errors."""

class ValidationError(CoreError):
    def __init__(self, field: str, reason: str): ...

class ProcessingError(CoreError):
    def __init__(self, processor: str, reason: str): ...

class ProcessorNotAvailableError(CoreError):
    def __init__(self, processor: str, reason: str): ...
```

```python
# settings/src/project_settings/errors.py
class SettingsError(Exception):
    """Base for settings errors."""

class SettingsFileError(SettingsError):
    """TOML parse error."""

class SettingsValidationError(SettingsError):
    """Pydantic validation failed."""

class SettingsOverrideError(SettingsError):
    """CLI override key doesn't exist."""

class SettingsRegistryError(SettingsError):
    """Namespace conflict or not registered."""
```

---

## 9. Summary: Key Patterns

| Pattern | Implementation |
|---------|----------------|
| Local package deps | `[tool.uv.sources]` with `path = "../pkg"` |
| Public API | Explicit `__all__` in `__init__.py` |
| Same CLI command | Both packages define same `[project.scripts]` |
| Schema registration | Import-time `SchemaRegistry.register()` |
| Config composition | Consumer defines `UnifiedConfig` model |
| Settings bootstrap | `configure(UnifiedModel)` before `get_config()` |
| Layer merge | Deep merge dicts, replace lists/scalars |
| CLI overrides | Dot-notation keys applied after merge |
| Pluggable impls | Abstract base class + factory |
