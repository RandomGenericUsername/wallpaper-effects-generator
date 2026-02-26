# How-to: Preview Commands Without Executing (Dry Run)

Use `--dry-run` to inspect what commands would be executed without actually running them. This works for `process`, `batch`, `install`, and `uninstall` commands.

<!-- BHV IDs: BHV-0054, BHV-0059, BHV-0077, BHV-0079 -->

---

## Prerequisites

- `wallpaper-core` or `wallpaper-process` is installed.

---

## Dry run for process commands (wallpaper-core)

### Single effect

```bash
wallpaper-core process effect wallpaper.jpg --effect blur --dry-run
```

Prints:
- The resolved `magick ...` command with all parameter substitutions applied.
- The expected output path.
- Validation checks:
  - Input file exists
  - ImageMagick binary found
  - Effect (or composite/preset) found in config
  - Output directory exists (or notes it would be created)

No file is written. (BHV-0054)

### Composite

```bash
wallpaper-core process composite wallpaper.jpg --composite blur-brightness80 --dry-run
```

Prints each step in the chain as a separate `magick ...` command. (BHV-0054)

### Preset

```bash
wallpaper-core process preset wallpaper.jpg --preset dark_blur --dry-run
```

Prints the resolved command(s) for the underlying effect or composite. (BHV-0054)

---

## Dry run for batch commands (wallpaper-core)

```bash
wallpaper-core batch all wallpaper.jpg --dry-run
```

Prints a full table of all planned batch items: name, type, expected output path, and the resolved command. No commands are executed. (BHV-0059)

Works with all batch subcommands:

```bash
wallpaper-core batch effects wallpaper.jpg --dry-run
wallpaper-core batch composites wallpaper.jpg --dry-run
wallpaper-core batch presets wallpaper.jpg --dry-run
```

---

## Dry run for process commands (wallpaper-process)

The orchestrator's `--dry-run` for process commands shows **two** pieces of information: (BHV-0079)

1. The host command: the full `docker run ...` (or `podman run ...`) invocation with all volume mounts. The input file is mounted at its original filename (e.g., `-v /abs/wallpaper.jpg:/input/wallpaper.jpg:ro`).
2. The inner command: the `magick ...` command that would execute inside the container.

Example:

```bash
wallpaper-process process effect wallpaper.jpg --effect blur --dry-run
```

No container is spawned.

```bash
wallpaper-process process composite wallpaper.jpg --composite dark --dry-run
wallpaper-process process preset wallpaper.jpg --preset dark_blur --dry-run
```

(BHV-0079)

---

## Dry run for install and uninstall (wallpaper-process)

### Install dry run

```bash
wallpaper-process install --dry-run
```

Prints the `docker build ...` command with the Dockerfile path and build context, plus validation checks (Dockerfile exists, engine binary found). No image is built. (BHV-0077)

### Uninstall dry run

```bash
wallpaper-process uninstall --dry-run
```

Prints the `docker rmi wallpaper-effects:latest` command. No image is removed. (BHV-0077)

---

## Quiet dry run output

Add `-q` to suppress the formatted output and print only the raw commands:

```bash
wallpaper-core -q process effect wallpaper.jpg --effect blur --dry-run
```

This outputs only the `magick ...` command, suitable for scripting. (BHV-0065)

---

## See also

- [Apply a Single Effect](apply-single-effect.md)
- [Batch-Process Images](batch-process.md)
- [Install/Uninstall the Container Image](install-container.md)
- [wallpaper-core CLI Reference](../reference/cli-core.md)
- [wallpaper-process CLI Reference](../reference/cli-orchestrator.md)
