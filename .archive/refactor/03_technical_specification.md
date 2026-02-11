# Technical Specification: Wallpaper Effects Generator

## 1. Package Configuration

### 1.1 Core Package (`packages/core/pyproject.toml`)

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
    "pytest>=8.4.2",
    "pytest-cov>=4.1.0",
    "mypy>=1.11.0",
    "ruff>=0.6.0",
]

[project.scripts]
wallpaper-effects = "wallpaper_effects.cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_effects"]
```

### 1.2 Orchestrator Package (`packages/orchestrator/pyproject.toml`)

```toml
[project]
name = "wallpaper-effects-orchestrator"
version = "1.0.0"
description = "Container orchestrator for wallpaper-effects-core"
requires-python = ">=3.12"
license = { text = "MIT" }

dependencies = [
    "wallpaper-effects-core>=1.0.0",
    "container-manager>=0.1.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
wallpaper-effects = "wallpaper_effects_orchestrator.cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/wallpaper_effects_orchestrator"]

[tool.uv.sources]
wallpaper-effects-core = { path = "../core", editable = true }
container-manager = { git = "https://github.com/RandomGenericUsername/container-manager.git" }
```

---

## 2. Public API Specification

### 2.1 Core Package Exports (`wallpaper_effects/__init__.py`)

```python
"""Wallpaper Effects - ImageMagick-based image effect processing."""

from ._version import __version__

# Configuration
from .loader import ConfigLoader

# Models - Effects
from .models import (
    EffectDefinition,
    ParameterDefinition,
    ParameterType,
    ChainStep,
    CompositeDefinition,
    PresetDefinition,
    EffectsConfig,
)

# Models - Settings
from .models import (
    Settings,
    ExecutionSettings,
    OutputSettings,
    PathSettings,
    Verbosity,
)

# Engine
from .engine import (
    CommandExecutor,
    ChainExecutor,
    BatchGenerator,
    BatchResult,
    ExecutionResult,
)

# Console
from .console import RichOutput, BatchProgress

__all__ = [
    "__version__",
    "ConfigLoader",
    "EffectDefinition", "ParameterDefinition", "ParameterType",
    "ChainStep", "CompositeDefinition", "PresetDefinition", "EffectsConfig",
    "Settings", "ExecutionSettings", "OutputSettings", "PathSettings", "Verbosity",
    "CommandExecutor", "ChainExecutor", "BatchGenerator",
    "BatchResult", "ExecutionResult",
    "RichOutput", "BatchProgress",
]
```

### 2.2 Orchestrator Package Exports (`wallpaper_effects_orchestrator/__init__.py`)

```python
"""Wallpaper Effects Orchestrator - Container-based execution."""

from ._version import __version__

from .container import (
    ContainerRunner,
    ImageBuilder,
    ContainerResult,
)

__all__ = [
    "__version__",
    "ContainerRunner",
    "ImageBuilder",
    "ContainerResult",
]
```

---

## 3. Data Types

### 3.1 Effect Models

```python
from pydantic import BaseModel, Field
from typing import Any

class ParameterType(BaseModel):
    """Reusable parameter type definition."""
    type: str                           # string, integer, float, boolean
    pattern: str | None = None          # Regex for validation
    min: int | float | None = None
    max: int | float | None = None
    default: Any = None
    description: str = ""

class ParameterDefinition(BaseModel):
    """Parameter for an effect."""
    type: str                           # Reference to parameter_types
    cli_flag: str                       # e.g., "--blur"
    default: Any = None
    description: str = ""

class EffectDefinition(BaseModel):
    """Atomic effect definition."""
    description: str = ""
    command: str                        # Shell template: 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
    parameters: dict[str, ParameterDefinition] = {}

class ChainStep(BaseModel):
    """Step in composite effect chain."""
    effect: str                         # Effect name
    params: dict[str, Any] = {}         # Override params

class CompositeDefinition(BaseModel):
    """Composite effect (chain of effects)."""
    description: str = ""
    chain: list[ChainStep]

class PresetDefinition(BaseModel):
    """Named configuration preset."""
    description: str = ""
    effect: str | None = None           # Single effect
    composite: str | None = None        # Composite reference
    params: dict[str, Any] = {}

class EffectsConfig(BaseModel):
    """Root configuration."""
    version: str = "1.0"
    parameter_types: dict[str, ParameterType] = {}
    effects: dict[str, EffectDefinition] = {}
    composites: dict[str, CompositeDefinition] = {}
    presets: dict[str, PresetDefinition] = {}
```

### 3.2 Settings Models

```python
from enum import IntEnum

class Verbosity(IntEnum):
    QUIET = 0    # Errors only
    NORMAL = 1   # Progress + results
    VERBOSE = 2  # + command details
    DEBUG = 3    # + full output

class ExecutionSettings(BaseModel):
    parallel: bool = True
    strict: bool = True
    max_workers: int = 0  # 0 = auto

class OutputSettings(BaseModel):
    verbosity: Verbosity = Verbosity.NORMAL
    format: str = "preserve"
    quality: int = 90

class PathSettings(BaseModel):
    effects_config: Path | None = None
    user_effects_dir: Path | None = None

class Settings(BaseModel):
    version: str = "1.0"
    execution: ExecutionSettings = ExecutionSettings()
    output: OutputSettings = OutputSettings()
    paths: PathSettings = PathSettings()
```

### 3.3 Engine Types

```python
from dataclasses import dataclass, field

@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    command: str
    stdout: str
    stderr: str
    return_code: int
    duration: float = 0.0

@dataclass
class BatchResult:
    """Result of batch generation."""
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    results: dict[str, ExecutionResult] = field(default_factory=dict)
    output_dir: Path | None = None

    @property
    def success(self) -> bool:
        return self.failed == 0
```

---

## 4. Class Specifications

### 4.1 ConfigLoader

```python
class ConfigLoader:
    """Loader for effects and settings configuration.

    Uses class-level caching to ensure configurations are loaded
    only once per process.

    Load order (later overrides earlier):
    1. Package default: wallpaper_effects/data/effects.yaml
    2. User config: ~/.config/wallpaper-effects/effects.yaml
    3. User custom: ~/.config/wallpaper-effects/effects.d/*.yaml
    """

    @classmethod
    def load_effects(cls, force_reload: bool = False) -> EffectsConfig:
        """Load merged effects configuration."""

    @classmethod
    def load_settings(cls, force_reload: bool = False) -> Settings:
        """Load settings configuration."""

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached configurations."""
```

### 4.2 CommandExecutor

```python
class CommandExecutor:
    """Execute shell commands for effects.

    Substitutes variables in command templates:
    - $INPUT: Input file path
    - $OUTPUT: Output file path
    - $PARAM_NAME: Parameter values (uppercase)
    """

    def __init__(self, output: RichOutput | None = None) -> None: ...

    def is_magick_available(self) -> bool:
        """Check if ImageMagick is available."""

    def execute(
        self,
        command_template: str,
        input_path: Path,
        output_path: Path,
        params: dict[str, str | int | float] | None = None,
    ) -> ExecutionResult:
        """Execute a single magick command."""
```

### 4.3 ChainExecutor

```python
class ChainExecutor:
    """Execute chains of effects using temp files.

    Process flow:
    - step1: input -> temp1
    - step2: temp1 -> temp2
    - stepN: tempN-1 -> output
    """

    def __init__(
        self,
        config: EffectsConfig,
        output: RichOutput | None = None,
    ) -> None: ...

    def execute_chain(
        self,
        chain: list[ChainStep],
        input_path: Path,
        output_path: Path,
    ) -> ExecutionResult:
        """Execute a chain of effects."""
```

### 4.4 BatchGenerator

```python
class BatchGenerator:
    """Generate multiple effects in batch."""

    def __init__(
        self,
        config: EffectsConfig,
        output: RichOutput | None = None,
        parallel: bool = True,
        strict: bool = True,
        max_workers: int = 0,
    ) -> None: ...

    def generate_all_effects(
        self, input_path: Path, output_dir: Path, flat: bool = False,
        progress: BatchProgress | None = None,
    ) -> BatchResult: ...

    def generate_all_composites(...) -> BatchResult: ...
    def generate_all_presets(...) -> BatchResult: ...
    def generate_all(...) -> BatchResult: ...
```

---

## 5. CLI Specification

### 5.1 Core CLI Commands

```
wallpaper-effects
├── process
│   ├── effect     # Apply single effect
│   ├── composite  # Apply composite
│   └── preset     # Apply preset
├── batch
│   ├── effects    # Generate all effects
│   ├── composites # Generate all composites
│   ├── presets    # Generate all presets
│   └── all        # Generate everything
├── show
│   ├── effects    # List effects
│   ├── composites # List composites
│   └── presets    # List presets
└── version
```

### 5.2 Orchestrator CLI Commands (Additional)

```
wallpaper-effects container
├── build   # Build ImageMagick container image
├── run     # Run effect in container
├── shell   # Interactive container shell
└── status  # Show container/image status
```

---

## 6. Container Specification

### 6.1 Dockerfile Template

```dockerfile
FROM alpine:3.19

# Install ImageMagick 7
RUN apk add --no-cache imagemagick

# Working directory
WORKDIR /workspace

# Verify installation
RUN magick --version
```

### 6.2 Container Operations

```python
class ContainerRunner:
    """Run effect processing in containers."""

    def __init__(self, runtime: str = "docker") -> None:
        """Initialize with Docker or Podman runtime."""

    def ensure_image(self, tag: str = "wallpaper-effects:latest") -> bool:
        """Build image if not exists."""

    def run_effect(
        self,
        input_path: Path,
        output_path: Path,
        effect: str,
        params: dict | None = None,
    ) -> ContainerResult:
        """Run single effect in container."""

@dataclass
class ContainerResult:
    success: bool
    container_id: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float
```

---

## 7. Configuration Schema

### 7.1 effects.yaml

```yaml
version: "1.0"

parameter_types:
  blur_geometry:
    type: string
    pattern: "^\\d+x\\d+$"
    default: "0x8"
    description: "Blur geometry (RADIUSxSIGMA)"

effects:
  blur:
    description: "Apply Gaussian blur"
    command: 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
    parameters:
      blur:
        type: blur_geometry
        cli_flag: "--blur"

composites:
  blur-brightness80:
    description: "Blur then dim"
    chain:
      - effect: blur
        params: { blur: "0x8" }
      - effect: brightness
        params: { brightness: -20 }

presets:
  dark_blur:
    description: "Dark blurred background"
    composite: blur-brightness80
```

### 7.2 settings.yaml

```yaml
version: "1.0"

execution:
  parallel: true
  strict: true
  max_workers: 0

output:
  verbosity: 1
  format: "preserve"
  quality: 90

paths:
  effects_config: null
  user_effects_dir: null
```

---

## 8. Usage Examples

### 8.1 Library Usage

```python
from pathlib import Path
from wallpaper_effects import (
    ConfigLoader,
    CommandExecutor,
    ChainExecutor,
    BatchGenerator,
)

# Load configuration
config = ConfigLoader.load_effects()

# Single effect
executor = CommandExecutor()
effect = config.effects["blur"]
result = executor.execute(
    effect.command,
    Path("input.jpg"),
    Path("output.jpg"),
    {"blur": "0x10"}
)

# Chain execution
chain_exec = ChainExecutor(config)
composite = config.composites["blur-brightness80"]
result = chain_exec.execute_chain(
    composite.chain,
    Path("input.jpg"),
    Path("output.jpg"),
)

# Batch processing
batch = BatchGenerator(config, parallel=True)
result = batch.generate_all(
    Path("input.jpg"),
    Path("./output/"),
)
print(f"Generated {result.succeeded}/{result.total}")
```

### 8.2 CLI Usage

```bash
# Core CLI
wallpaper-effects process effect input.jpg output.jpg -e blur --blur 0x10
wallpaper-effects batch all input.jpg ./output/
wallpaper-effects show effects

# Orchestrator CLI
wallpaper-effects container build
wallpaper-effects container run input.jpg output.jpg -e blur
wallpaper-effects container status
```
