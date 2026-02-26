# How-to: Override Configuration via CLI Flags

Several `wallpaper-core` (and `wallpaper-process`) flags act as highest-priority configuration overrides, taking precedence over all config files.

<!-- BHV IDs: BHV-0039, BHV-0065, BHV-0082 -->

---

## Prerequisites

- `wallpaper-core` or `wallpaper-process` is installed.

---

## Verbosity flags

The verbosity flags override `core.output.verbosity` for the duration of the command:

| Flag | Verbosity level |
|---|---|
| `-q` / `--quiet` | QUIET (errors only) |
| (none) | NORMAL |
| `-v` / `--verbose` | VERBOSE |
| `-vv` | DEBUG |

Examples:

```bash
# Suppress all output except errors
wallpaper-core -q process effect wallpaper.jpg --effect blur

# Show verbose progress
wallpaper-core -v batch all wallpaper.jpg

# Show debug output
wallpaper-core -vv process effect wallpaper.jpg --effect blur
```

(BHV-0065)

These flags must appear before the subcommand name (they are global flags on the root app).

---

## Parallel processing flag

`--sequential` (or `--no-parallel`) overrides `core.execution.parallel` for batch commands:

```bash
wallpaper-core batch all wallpaper.jpg --sequential
```

The `--parallel` flag re-enables parallel processing if it has been disabled in config:

```bash
wallpaper-core batch all wallpaper.jpg --parallel
```

(BHV-0039, BHV-0057)

---

## Strict mode flag

`--strict` / `--no-strict` overrides `core.execution.strict` for batch commands:

```bash
# Continue on errors (override strict=true in config)
wallpaper-core batch all wallpaper.jpg --no-strict
```

(BHV-0039)

---

## Orchestrator: the same override behavior applies

`wallpaper-process` applies the same override logic because the orchestrator registers all three config namespaces (`core`, `effects`, `orchestrator`) and CLI flags act as the top-most layer. (BHV-0082)

```bash
wallpaper-process -q process effect wallpaper.jpg --effect blur
wallpaper-process -v batch all wallpaper.jpg --sequential
```

---

## See also

- [Configuration Reference](../reference/config.md) — for file-based config keys
- [How Layered Configuration Works](../explanation/layered-config.md)
