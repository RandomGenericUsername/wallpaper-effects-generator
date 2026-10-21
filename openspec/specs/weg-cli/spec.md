# weg-cli Specification

## Purpose
Defines the `weg` command-line surface: local and container processing, catalog inspection, batch
generation, configuration dumps, and the container image build/removal verbs.

## Requirements

### Requirement: `--version` reports both pins
`weg --version` SHALL print `<package version> contract <contracts version>` where the contract
token comes from `cli_invocation_contract.CONTRACT_VERSION`.

Source: spine AD-4/AD-11; `src/wallpaper_effects_generator/cli/main.py` `_version_callback`.

#### Scenario: version handshake
- **WHEN** `weg --version` runs against the installed 0.1.0 wheel
- **THEN** it prints `0.1.0 contract 0.1.0` and exits 0

### Requirement: processing selects local or container execution
`process` and `batch` SHALL execute in the runtime selected by `[runtime] mode` (`local` or
`container`), and `--runtime` SHALL override it for the invocation.

Source: `src/wallpaper_effects_generator/cli/process.py`;
`src/wallpaper_effects_generator/cli/batch.py`.

#### Scenario: batch writes one output per catalog item
- **WHEN** `weg batch all -- <wallpaper>` runs with an output directory configured
- **THEN** the exit code is 0 and one output per effects/composite/preset item exists under that
  directory

### Requirement: `install` builds from this repo root
`weg install` SHALL resolve its build context with `oci_runtime.resolve_build_context` and build
`adapters/docker/Dockerfile.imagemagick` against it. `--context`/`--source-root` and
`--container-engine` SHALL be accepted; a missing context SHALL fail loudly.

Source: spine AD-5/AD-7; `src/wallpaper_effects_generator/cli/install.py`.

#### Scenario: explicit context
- **WHEN** `weg install --context <checkout> --container-engine podman` runs
- **THEN** the engine receives that checkout as the build context and the command exits 0

### Requirement: `install --image-tag` overrides and validates the tag
`--image-tag TAG` SHALL override `[container] image_tag` and SHALL reject a tag outside
`[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}` before invoking the engine.

Source: spine AD-7; `src/wallpaper_effects_generator/cli/install.py`.

#### Scenario: explicit pin tag
- **WHEN** `weg install --context <checkout> --container-engine podman --image-tag v0.1.0` runs
- **THEN** the engine receives image `weg-podman:v0.1.0` and the command exits 0

#### Scenario: invalid tag is rejected
- **WHEN** `weg install --image-tag 'bad tag'` runs
- **THEN** the exit code is non-zero, the message names `invalid image tag`, and no build is
  attempted

### Requirement: `uninstall` removes the tag-qualified image
`weg uninstall` SHALL remove the engine-qualified image named by the effective settings and SHALL
report a no-op when the image is absent.

Source: `src/wallpaper_effects_generator/cli/uninstall.py`.

#### Scenario: absent image is a clean no-op
- **WHEN** `weg uninstall` runs and the engine reports no image
- **THEN** the exit code is 0 and the message contains `nothing to uninstall`
