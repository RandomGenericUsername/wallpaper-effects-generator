# Architecture Overview

High-level design of `wallpaper-effects-process`.

---

## Design Principles

1. **YAML-driven**: All effects defined in configuration, not code
2. **Shell-only processing**: ImageMagick commands, no Python image libraries
3. **Composable**: Build complex effects from simple ones
4. **Extensible**: Users can add effects without modifying code

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (Typer)                          │
│  ┌─────────┐  ┌─────────────┐  ┌─────────┐  ┌───────────┐  │
│  │  show   │  │   process   │  │  batch  │  │  version  │  │
│  └────┬────┘  └──────┬──────┘  └────┬────┘  └───────────┘  │
└───────┼──────────────┼──────────────┼──────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                     Console Output                         │
│         (RichOutput, BatchProgress, Verbosity)             │
└───────────────────────────────────────────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                      Engine Layer                          │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │ CommandExecutor│  │  ChainExecutor │  │BatchGenerator│  │
│  │ (single cmd)   │  │ (effect chain) │  │(parallel/seq)│  │
│  └────────────────┘  └────────────────┘  └─────────────┘  │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                   Configuration Layer                      │
│  ┌─────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │ConfigLoader │  │  EffectsConfig  │  │   Settings    │  │
│  │(YAML parser)│  │(effects,composites,presets)        │  │
│  └─────────────┘  └─────────────────┘  └───────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
src/wallpaper_processor/
├── __init__.py
├── cli/                    # Command-line interface
│   ├── main.py             # App entry point
│   ├── show.py             # show command
│   ├── process.py          # process command
│   └── batch.py            # batch command
├── config/                 # Configuration handling
│   ├── loader.py           # YAML loading and merging
│   ├── schema.py           # Pydantic models for effects.yaml
│   └── settings.py         # Pydantic models for settings.yaml
├── console/                # Output handling
│   ├── output.py           # Rich console with verbosity
│   └── progress.py         # Progress bars for batch
└── engine/                 # Processing engine
    ├── executor.py         # Execute single commands
    ├── chain.py            # Execute effect chains
    └── batch.py            # Batch generation
```

---

## Key Components

### ConfigLoader

Loads and merges YAML configuration:

1. Load package defaults (`effects/effects.yaml`)
2. Load user overrides (`~/.config/wallpaper-effects/effects.yaml`)
3. Deep merge user config over defaults
4. Cache results for performance

### CommandExecutor

Executes single ImageMagick commands:

1. Substitute variables (`$INPUT`, `$OUTPUT`, `$PARAM`)
2. Run shell command
3. Return success/failure with duration

### ChainExecutor

Executes composite effects:

1. Create temp files for intermediate steps
2. Execute effects in sequence
3. Clean up temp files
4. Copy final result to output

### BatchGenerator

Parallel/sequential batch processing:

1. Collect all effects/composites/presets
2. Execute using ThreadPoolExecutor (parallel) or sequentially
3. Track progress with Rich progress bar
4. Return BatchResult with statistics

---

## See Also

- [Data Flow](data-flow.md)
- [Extending Effects](../guides/extending-effects.md)

