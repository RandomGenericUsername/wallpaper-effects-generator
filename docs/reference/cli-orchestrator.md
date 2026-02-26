# Reference: wallpaper-process CLI

`wallpaper-process` is the container-orchestration CLI. It wraps `wallpaper-core` by running process commands inside a Docker or Podman container. Batch, show, info, and version commands run on the host.

<!-- BHV IDs: BHV-0067, BHV-0068, BHV-0071, BHV-0074, BHV-0075, BHV-0076, BHV-0077, BHV-0078, BHV-0079, BHV-0081, BHV-0082 -->

---

## Overview of commands

| Command | Runs where |
|---|---|
| `install` | Host |
| `uninstall` | Host |
| `process effect/composite/preset` | Inside container |
| `batch effects/composites/presets/all` | Host |
| `show effects/composites/presets/all` | Host |
| `info` | Host |
| `version` | Host |

(BHV-0067)

---

## Global options

| Flag | Description |
|---|---|
| `-q`, `--quiet` | Quiet mode (errors only). |
| `-v` | Verbose mode. |
| `-vv` | Debug mode. |
| `--help` | Show help and exit. |

These flags are the same as `wallpaper-core` and override `core.output.verbosity`. (BHV-0082)

On startup, `wallpaper-process` configures all three config namespaces (`core`, `effects`, `orchestrator`) from the same layered files as `wallpaper-core`. (BHV-0068)

---

## version

```bash
wallpaper-process version
```

Prints the version string. Runs on the host. (BHV-0046 equivalent)

---

## info

```bash
wallpaper-process info
```

Displays current core settings and effects summary (same output as `wallpaper-core info`). Runs on the host without spawning a container.

---

## install

```bash
wallpaper-process install [options]
```

Builds the `wallpaper-effects:latest` container image. The image bundles `wallpaper-core` and ImageMagick. (BHV-0075)

| Flag | Short | Description | Default |
|---|---|---|---|
| `--engine` | `-e` | Container engine: `docker` or `podman`. | From `orchestrator.container.engine` config |
| `--dry-run` | | Preview the build command without executing. | false |

**`--dry-run` behavior:** Prints the full `docker build -f <Dockerfile> -t wallpaper-effects:latest <project-root>` command, plus validation checks (Dockerfile exists, engine binary found). No build is performed. (BHV-0077)

Must be run before any `process` command. (BHV-0075)

---

## uninstall

```bash
wallpaper-process uninstall [options]
```

Removes the `wallpaper-effects:latest` container image. (BHV-0076)

| Flag | Short | Description | Default |
|---|---|---|---|
| `--yes` | `-y` | Skip confirmation prompt. | false |
| `--engine` | `-e` | Container engine: `docker` or `podman`. | From `orchestrator.container.engine` config |
| `--dry-run` | | Preview the removal command without executing. | false |

**`--dry-run` behavior:** Prints the `docker rmi wallpaper-effects:latest` command. No image is removed. (BHV-0077)

If the image does not exist when running without `--dry-run`, the command exits 0 with a message indicating the image was already removed.

---

## process

Run an effect, composite, or preset inside the container.

### process effect

```bash
wallpaper-process process effect <input-file> --effect <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--effect` | | Effect name. Required. | — |
| `--output-dir` | `-o` | Output directory on host. | `core.output.default_dir` |
| `--flat` | | Flat output structure. | false |
| `--dry-run` | | Preview host and inner commands. | false |

(BHV-0078)

**Container invocation:**
```
docker run --rm \
  -v <abs-input>:/input/<filename>:ro \
  -v <abs-output-dir>:/output:rw \
  wallpaper-effects:latest \
  process effect /input/<filename> --effect <name> -o /output [--flat]
```

> The input file is mounted at its original filename (e.g., `/input/wallpaper.jpg`),
> not a fixed `/input/image.jpg`. `<filename>` is the basename of the path you pass
> as the `<input-file>` argument.

With Podman, `--userns=keep-id` is added. (BHV-0074)

**`--dry-run` behavior:** Prints both the host `docker run ...` command and the inner `magick ...` command that will execute inside the container. No container is spawned. (BHV-0079)

### process composite

```bash
wallpaper-process process composite <input-file> --composite <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--composite` | | Composite name. Required. | — |
| `--output-dir` | `-o` | Output directory on host. | `core.output.default_dir` |
| `--flat` | | Flat output structure. | false |
| `--dry-run` | | Preview host and inner commands. | false |

(BHV-0078, BHV-0079)

### process preset

```bash
wallpaper-process process preset <input-file> --preset <name> [options]
```

| Flag | Short | Description | Default |
|---|---|---|---|
| `--preset` | | Preset name. Required. | — |
| `--output-dir` | `-o` | Output directory on host. | `core.output.default_dir` |
| `--flat` | | Flat output structure. | false |
| `--dry-run` | | Preview host and inner commands. | false |

(BHV-0078, BHV-0079)

---

## batch

Runs batch generation on the **host** (not inside the container). Delegates to the core batch engine. (BHV-0081)

Supports the same subcommands and flags as `wallpaper-core batch`:

```bash
wallpaper-process batch effects <input-file> [options]
wallpaper-process batch composites <input-file> [options]
wallpaper-process batch presets <input-file> [options]
wallpaper-process batch all <input-file> [options]
```

Flags: `-o`, `--parallel`/`--sequential`, `--strict`/`--no-strict`, `--flat`, `--dry-run`.

---

## show

Displays available effects, composites, and presets. Runs on the host.

```bash
wallpaper-process show effects
wallpaper-process show composites
wallpaper-process show presets
wallpaper-process show all
```

(BHV-0067)

---

## Container image naming

The default image name is `wallpaper-effects:latest`. (BHV-0071)

To use a custom registry prefix, set `image_registry` in settings:

```toml
[orchestrator.container]
image_registry = "ghcr.io/myusername"
```

The full image name becomes `ghcr.io/myusername/wallpaper-effects:latest`. (BHV-0071)

---

## Container engine configuration

The default engine is `docker`. To use Podman, configure:

```toml
[orchestrator.container]
engine = "podman"
```

Or pass `--engine podman` at the command line. (BHV-0068)

---

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (or `--dry-run` completed). |
| 1 | Error (container image not found, engine error, config error). |
