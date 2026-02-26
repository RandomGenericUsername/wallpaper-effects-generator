# Reference: wallpaper-core CLI

`wallpaper-core` is the host-side CLI for applying ImageMagick effects to images. It reads layered configuration and effects from `effects.yaml`.

<!-- BHV IDs: BHV-0037, BHV-0038, BHV-0039, BHV-0043, BHV-0044, BHV-0045, BHV-0046, BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0052, BHV-0053, BHV-0054, BHV-0057, BHV-0058, BHV-0059, BHV-0065 -->

---

## Global options

These flags appear before the subcommand and apply to all commands. (BHV-0065)

| Flag | Description |
|---|---|
| `-q`, `--quiet` | Quiet mode: only errors are printed. Overrides `core.output.verbosity`. |
| `-v`, `--verbose` | Verbose mode: extra progress information. |
| `-vv` | Debug mode: maximum verbosity. |
| `--help` | Show help and exit. |

On startup, `wallpaper-core` configures layered settings (package defaults, `./settings.toml`, `~/.config/wallpaper-effects-generator/settings.toml`) and loads `effects.yaml` with the same layered discovery. (BHV-0038)

---

## version

```bash
wallpaper-core version
```

Prints the installed version string, e.g., `wallpaper-effects v0.1.0`. Exits 0. (BHV-0046)

---

## info

```bash
wallpaper-core info
```

Displays the current resolved configuration and effects summary. Output includes: (BHV-0045)

```
=== Core Settings ===
Parallel: True
Strict: True
Max Workers: 0
Verbosity: NORMAL
Backend Binary: magick

=== Effects ===
Version: 1.0
Effects defined: 8

Available effects:
  - blackwhite: Convert to grayscale
  - blur: Apply Gaussian blur
  ...
```

Runs on the host. Does not spawn a container.

---

## show

Display available effects, composites, or presets. (BHV-0044)

### show effects

```bash
wallpaper-core show effects
```

Prints a table with columns: Name, Description, Parameters.

### show composites

```bash
wallpaper-core show composites
```

Prints a table with columns: Name, Description, Chain (e.g., `blur -> brightness`).

### show presets

```bash
wallpaper-core show presets
```

Prints a table with columns: Name, Description, Type (effect/composite), Target.

### show all

```bash
wallpaper-core show all
```

Prints all three tables sequentially.

---

## process

Apply an effect, composite, or preset to a single image.

### process effect

```bash
wallpaper-core process effect <input-file> --effect <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--effect` | `-e` | Effect name to apply. Required. | — |
| `--output-dir` | `-o` | Output directory. | `core.output.default_dir` |
| `--flat` | | Omit type subdirectory in output path. | false |
| `--dry-run` | | Preview command without executing. | false |
| `--blur` | | Override blur geometry (e.g., `0x16`). | effect default |
| `--brightness` | | Override brightness percentage. | effect default |
| `--contrast` | | Override contrast percentage. | effect default |
| `--saturation` | | Override saturation level. | effect default |
| `--strength` | | Override vignette strength. | effect default |
| `--color` | | Override overlay color (hex). | effect default |
| `--opacity` | | Override overlay opacity percentage. | effect default |

(BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0054)

**Output path (default, hierarchical):**
```
<output-dir>/<input-stem>/effects/<effect-name><ext>
```

**Output path (with `--flat`):**
```
<output-dir>/<input-stem>/<effect-name><ext>
```

The output directory is created automatically if it does not exist.

### process composite

```bash
wallpaper-core process composite <input-file> --composite <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--composite` | `-c` | Composite name to apply. Required. | — |
| `--output-dir` | `-o` | Output directory. | `core.output.default_dir` |
| `--flat` | | Omit type subdirectory in output path. | false |
| `--dry-run` | | Preview command chain without executing. | false |

(BHV-0052, BHV-0049, BHV-0050, BHV-0054)

**Output path (hierarchical):**
```
<output-dir>/<input-stem>/composites/<composite-name><ext>
```

### process preset

```bash
wallpaper-core process preset <input-file> --preset <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--preset` | `-p` | Preset name to apply. Required. | — |
| `--output-dir` | `-o` | Output directory. | `core.output.default_dir` |
| `--flat` | | Omit type subdirectory in output path. | false |
| `--dry-run` | | Preview command without executing. | false |

(BHV-0053, BHV-0049, BHV-0050, BHV-0054)

**Output path (hierarchical):**
```
<output-dir>/<input-stem>/presets/<preset-name><ext>
```

---

## batch

Generate multiple effects, composites, or presets for a single image.

All batch subcommands share this set of flags:

| Flag | Description | Default |
|---|---|---|
| `-o`, `--output-dir` | Output directory. | `core.output.default_dir` |
| `--parallel` / `--sequential` | Enable or disable parallel execution. | parallel (from `core.execution.parallel`) |
| `--strict` / `--no-strict` | Abort on first error or continue. | strict (from `core.execution.strict`) |
| `--flat` | Omit type subdirectories. | false |
| `--dry-run` | Preview all planned commands. | false |

(BHV-0057, BHV-0058, BHV-0059)

### batch effects

```bash
wallpaper-core batch effects <input-file> [options]
```

Generates all effects. Output under `<output-dir>/<stem>/effects/`.

### batch composites

```bash
wallpaper-core batch composites <input-file> [options]
```

Generates all composites. Output under `<output-dir>/<stem>/composites/`.

### batch presets

```bash
wallpaper-core batch presets <input-file> [options]
```

Generates all presets. Output under `<output-dir>/<stem>/presets/`.

### batch all

```bash
wallpaper-core batch all <input-file> [options]
```

Generates all effects, composites, and presets. Output organized into three subdirectories.

---

## Output path conventions

| Mode | Path template |
|---|---|
| Hierarchical (default) | `<output-dir>/<stem>/<type>/<name><ext>` |
| Flat (`--flat`) | `<output-dir>/<stem>/<name><ext>` |

Where `<type>` is `effects`, `composites`, or `presets`. The output directory is always created automatically.

---

## Layered effects merge

At startup, `wallpaper-core` merges three effects layers: package defaults (`packages/core/effects/effects.yaml`), project root (`./effects.yaml`), and user config (`~/.config/wallpaper-effects-generator/effects.yaml`). The merged result is what `show`, `process`, and `batch` commands operate on. (BHV-0043)

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (or `--dry-run` completed). |
| 1 | Error (bad input, unknown effect, execution failure, config error). |
