# weg-container-mode Specification

## Purpose
Defines the container backend: the ImageMagick image this repo owns, its build context, the tag
pin, and the argv the CLI hands to a reachable engine.

## Requirements

### Requirement: the image builds from this repo root
The image SHALL be built with the repository root as context, and
`src/wallpaper_effects_generator/adapters/docker/Dockerfile.imagemagick` SHALL copy only
repo-relative paths (`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`). No Dockerfile
path may name a sibling repo or a parent directory.

Source: spine AD-5; `Dockerfile.imagemagick` lines 13–14.

#### Scenario: build with no monorepo present
- **WHEN** `podman build -t wallpaper-effects-generator:v0.1.0 -f
  src/wallpaper_effects_generator/adapters/docker/Dockerfile.imagemagick .` runs in a standalone
  checkout
- **THEN** the build exits 0

#### Scenario: no sibling or parent references
- **WHEN** `rg -n "src/shared|src/cli-tools|\.\./" src/wallpaper_effects_generator/adapters/docker/`
  runs
- **THEN** it exits 1 with no matches

### Requirement: git dependencies are fetched at build time, fail-closed
The build stage SHALL carry `uv` at the pinned version plus `git` and CA certificates, and SHALL
install from the committed lock (`uv sync --frozen --no-dev --no-editable`) so an unreachable pin
fails the build instead of resolving a newer commit.

Source: spine AD-3/AD-5; `Dockerfile.imagemagick` lines 6–17.

#### Scenario: locked install
- **WHEN** the image builds with the committed `uv.lock`
- **THEN** the same sibling tags recorded in the lock are the ones installed

### Requirement: the image tag is the pin
The rendered/effective image tag SHALL equal the repo tag (`vX.Y.Z`) rather than `latest`, and the
CLI SHALL accept that tag explicitly (`--image-tag`) so provisioning can assert the exact image.

Source: spine AD-7; `src/wallpaper_effects_generator/cli/install.py`.

#### Scenario: tag-qualified image exists
- **WHEN** `podman images --format '{{.Repository}}:{{.Tag}}'` runs after an install at `v0.1.0`
- **THEN** a `weg-podman:v0.1.0` (or `weg-docker:v0.1.0`) line exists and no `weg*:latest` line is
  produced by the pin path

### Requirement: the image runs the pinned CLI
The built image SHALL expose `weg` on `PATH` and report the package and contract versions when run
without a checkout mounted.

Source: `Dockerfile.imagemagick` (`ENV PATH`, `CMD`); spine AD-5.

#### Scenario: version inside the image
- **WHEN** `podman run --rm wallpaper-effects-generator:v0.1.0 weg --version` runs
- **THEN** it prints `0.1.0 contract 0.1.0` and exits 0
