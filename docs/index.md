# Wallpaper Effects Generator Documentation

**wallpaper-effects-generator** is a layered wallpaper effects processor with support
for effects, composites, and presets. Run it directly on the host via `wallpaper-core`
or inside a container via `wallpaper-process`.

---

## Documentation layout

This documentation follows the [Diataxis](https://diataxis.fr) framework, which
organizes content into four types based on what a reader needs:

| Type | Directory | When to read it |
|------|-----------|-----------------|
| **Tutorial** | [`tutorials/`](tutorials/getting-started.md) | Learning — follow a complete worked example from installation to first effect |
| **How-to** | [`how-to/`](how-to/apply-single-effect.md) | Doing — find step-by-step instructions for a specific task |
| **Reference** | [`reference/`](reference/cli-core.md) | Looking up — find exact CLI flags, config keys, and effect definitions |
| **Explanation** | [`explanation/`](explanation/architecture.md) | Understanding — read about design, rationale, and mental models |

---

## Start here

New to wallpaper-effects-generator? Start with the tutorial:

→ **[Apply Your First Effect](tutorials/getting-started.md)**

---

## How-to guides

| Guide | What it covers |
|-------|----------------|
| [Apply a Single Effect](how-to/apply-single-effect.md) | Run one named effect with `wallpaper-core process effect`, output options, and per-effect parameter overrides |
| [Apply a Composite](how-to/apply-composite.md) | Chain multiple effects with `wallpaper-core process composite` |
| [Apply a Preset](how-to/apply-preset.md) | Use a named preset configuration with `wallpaper-core process preset` |
| [Batch Process](how-to/batch-process.md) | Generate all effects, composites, or presets for an image in one command |
| [Dry Run](how-to/dry-run.md) | Preview any command's ImageMagick invocations without executing them |
| [Override Config](how-to/override-config.md) | Use CLI flags as highest-priority overrides for output directory and other settings |
| [Run in Container](how-to/run-in-container.md) | Execute effects inside Docker or Podman without installing ImageMagick on the host |
| [Install the Container](how-to/install-container.md) | Build or remove the `wallpaper-effects:latest` container image |

---

## Reference

| Reference | What it covers |
|-----------|----------------|
| [wallpaper-core CLI](reference/cli-core.md) | All commands, flags, and exit codes for the host-side effects CLI |
| [wallpaper-process CLI](reference/cli-orchestrator.md) | All commands, flags, and exit codes for the container-orchestration CLI |
| [Configuration](reference/config.md) | All config keys, defaults, file locations, and four-layer precedence |
| [Effects](reference/effects.md) | Built-in effects, composites, and presets; user override mechanism |

---

## Explanation

| Article | What it covers |
|---------|----------------|
| [Architecture](explanation/architecture.md) | Monorepo layout, the four packages, and how they interact |
| [Layered Configuration](explanation/layered-config.md) | How four config layers compose and why they are ordered as they are |
| [Host vs Container](explanation/host-vs-container.md) | When to use `wallpaper-core` directly versus `wallpaper-process` with a container |
| [Contributing](explanation/contributing.md) | Development setup, tooling, and workflow for contributors |
