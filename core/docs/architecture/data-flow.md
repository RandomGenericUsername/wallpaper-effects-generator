# Data Flow

Processing pipeline for effects.

---

## Single Effect Flow

```
┌─────────┐     ┌────────────────┐     ┌─────────────────┐
│  Input  │────▶│ CommandExecutor│────▶│     Output      │
│  Image  │     │                │     │     Image       │
└─────────┘     └────────────────┘     └─────────────────┘
                       │
                       ▼
               ┌───────────────┐
               │ ImageMagick   │
               │ Shell Command │
               └───────────────┘
```

### Steps:

1. Load effect definition from `EffectsConfig`
2. Substitute variables in command template
3. Execute ImageMagick command via shell
4. Return result (success/failure, duration)

---

## Composite Effect Flow

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐
│  Input  │────▶│  Effect 1   │────▶│  Effect 2   │────▶│  Output  │
│  Image  │     │ (temp file) │     │ (temp file) │     │  Image   │
└─────────┘     └─────────────┘     └─────────────┘     └──────────┘
                       │                   │
                       ▼                   ▼
               ┌───────────────┐   ┌───────────────┐
               │  magick cmd   │   │  magick cmd   │
               └───────────────┘   └───────────────┘
```

### Steps:

1. Load composite definition (chain of effects)
2. Create temp directory for intermediate files
3. For each step in chain:
   - Execute effect with input from previous step
   - Output to temp file
4. Copy final temp file to output path
5. Clean up temp directory

---

## Batch Generation Flow

```
┌─────────┐
│  Input  │
│  Image  │
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────┐
│              BatchGenerator                 │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Effect1 │  │ Effect2 │  │ Effect3 │ ... │  (parallel)
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │           │
└───────┼────────────┼────────────┼───────────┘
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ out1.png│  │ out2.png│  │ out3.png│
   └─────────┘  └─────────┘  └─────────┘
```

### Steps:

1. Create output directory structure
2. Collect all items to generate (effects/composites/presets)
3. For each item (parallel or sequential):
   - Execute effect/composite
   - Write to output subdirectory
   - Update progress bar
4. Return BatchResult with statistics

---

## Configuration Loading Flow

```
┌─────────────────────────────────┐
│    Package Defaults             │
│  (effects/effects.yaml)         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    User Overrides               │
│  (~/.config/wallpaper-effects/  │
│   effects.yaml)                 │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Deep Merge                   │
│  (user overrides package)       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Pydantic Validation          │
│  (EffectsConfig model)          │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Cached Config                │
│  (reused for all operations)    │
└─────────────────────────────────┘
```

---

## See Also

- [Architecture Overview](overview.md)
- [Extending Effects](../guides/extending-effects.md)

