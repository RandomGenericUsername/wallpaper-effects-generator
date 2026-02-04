# Python API Reference

Python library reference for `wallpaper_processor`.

---

## Modules

| Module | Description |
|--------|-------------|
| `config.loader` | Configuration loading |
| `config.schema` | Pydantic models for effects |
| `config.settings` | Pydantic models for settings |
| `engine.executor` | Command execution |
| `engine.chain` | Effect chain execution |
| `engine.batch` | Batch generation |
| `console.output` | Rich console output |
| `console.progress` | Progress bars |

---

## ConfigLoader

Load and manage configuration.

```python
from wallpaper_processor.config import ConfigLoader

loader = ConfigLoader()

# Load effects configuration
config = loader.load_effects()

# Load settings
settings = loader.load_settings()

# Access effects
for name, effect in config.effects.items():
    print(f"{name}: {effect.description}")
```

---

## CommandExecutor

Execute single ImageMagick commands.

```python
from pathlib import Path
from wallpaper_processor.config import ConfigLoader
from wallpaper_processor.engine import CommandExecutor

loader = ConfigLoader()
config = loader.load_effects()

executor = CommandExecutor(config)

# Execute an effect
result = executor.execute(
    effect_name="blur",
    input_path=Path("input.png"),
    output_path=Path("output.png"),
    params={"blur": "0x12"},
)

print(f"Success: {result.success}, Duration: {result.duration:.2f}s")
```

---

## ChainExecutor

Execute composite effects.

```python
from pathlib import Path
from wallpaper_processor.config import ConfigLoader
from wallpaper_processor.engine import ChainExecutor

loader = ConfigLoader()
config = loader.load_effects()

executor = ChainExecutor(config)

# Execute a composite
result = executor.execute_composite(
    composite_name="blur-brightness80",
    input_path=Path("input.png"),
    output_path=Path("output.png"),
)

print(f"Success: {result.success}")
```

---

## BatchGenerator

Generate multiple effects.

```python
from pathlib import Path
from wallpaper_processor.config import ConfigLoader
from wallpaper_processor.engine import BatchGenerator

loader = ConfigLoader()
config = loader.load_effects()

generator = BatchGenerator(
    config=config,
    parallel=True,
    strict=False,
)

# Generate all effects
result = generator.generate_all_effects(
    input_path=Path("input.png"),
    output_dir=Path("/output"),
)

print(f"Generated {result.succeeded}/{result.total} effects")
```

---

## RichOutput

Console output with verbosity levels.

```python
from wallpaper_processor.console import RichOutput
from wallpaper_processor.config import Verbosity

output = RichOutput(verbosity=Verbosity.VERBOSE)

output.success("Effect applied successfully")
output.error("Failed to apply effect")
output.command("magick input.png -blur 0x8 output.png")
```

---

## See Also

- [CLI Reference](../cli/)
- [Architecture](../../architecture/)

