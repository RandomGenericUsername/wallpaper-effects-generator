# wallpaper-effects-generator (`weg`)

Wallpaper effects generator for the dotfiles CLI toolchain: applies an ImageMagick effects catalog
(effects, composites, presets) to wallpapers, locally or inside a container, with layered
configuration and runnable batch generation.

This repo **owns its container image and build verb** (spine AD-5/AD-7): the Dockerfile lives at
`src/wallpaper_effects_generator/adapters/docker/Dockerfile.imagemagick`, its build context is this
repo root, and the image tag is the pin (`vX.Y.Z`), never `latest`.

## Public surface

```console
weg process effect IMAGE --effect NAME [--param K=V] [--output-dir DIR] \
                          [--config FILE] [--effects FILE] [--runtime {local,container}]
weg process composite IMAGE --composite NAME ...
weg process preset IMAGE --preset NAME ...
weg show effects|composites|presets|catalog [...]
weg batch effects|composites|presets|all -- IMAGE [--output-dir DIR] [--flat] ...
weg info [--config FILE] [--effects FILE]
weg install [--config FILE] [--container-engine {docker,podman}] \
            [--context DIR | --source-root DIR] [--image-tag TAG] \
            [--dump-config] [--dump-effects]
weg uninstall [--config FILE] [--container-engine {docker,podman}]
weg dump-config [--output FILE]
weg dump-effects [--output FILE]
weg version
weg --version
```

- `--version` prints `<package version> contract <contracts version>`, e.g.
  `0.2.0 contract 0.2.0`. The contract token comes from
  `cli_invocation_contract.CONTRACT_VERSION`, not from `cli-output`.
- Global flags: `--output-format {json,plain,rich}`, `-v/-vv/-vvv`, `-q`.
- Exit codes: `0` success, non-zero a domain/config error with the message on the output stream.

## Container mode

`weg install` builds `Dockerfile.imagemagick` against a **single-package repo root** resolved by
`oci_runtime.resolve_build_context` (override `--context`, env `WEG_SOURCE_ROOT`, PEP 610, package
walk). The Dockerfile copies only repo-relative paths (`pyproject.toml`, `uv.lock`, `README.md`,
`LICENSE`, `src/`); the pinned sibling
dependencies are fetched from their git tags at build time (the stage carries `uv==0.9.22`, `git`
and CA certificates), so an unreachable pin fails closed. No path outside this repo is referenced.

```bash
make image                                  # podman build -t wallpaper-effects-generator:v0.2.0 .
weg install --context . --container-engine podman --image-tag v0.2.0
podman run --rm weg-podman:v0.2.0 weg --version   # 0.2.0 contract 0.2.0
```

`--image-tag` overrides `[container] image_tag` for one build and is validated against Docker's
tag grammar before the engine is touched. Invalid tags are rejected (`invalid image tag`).

## Configuration

Settings are resolved with this precedence (highest first):

1. CLI flag
2. env `WALLPAPER__SECTION__KEY` (double underscore = nesting)
3. `WALLPAPER_CONFIG_FILE_PATH`
4. `settings.toml` in the CWD or up to two parent levels
5. `$XDG_CONFIG_HOME/weg/settings.toml`
6. packaged defaults (`src/wallpaper_effects_generator/defaults/settings.toml`)

Effects discovery mirrors it with `WALLPAPER_EFFECTS_CONFIG_FILE_PATH`, `effects.yaml` and
`$XDG_CONFIG_HOME/weg/effects.yaml`. `[runtime] mode` chooses **where** processing runs
(`local`/`container`) and `[container] engine` chooses **which** OCI runtime
(`docker`/`podman`).

## Install

From a checkout (development):

```bash
make sync          # uv sync --frozen
make imagemagick   # pinned ImageMagick 7 static build (skipped when `magick` exists)
make gates         # test + lint + hermetic + lock-check + docs-check
make build         # sdist + wheel in dist/
make image         # build the container image from this repo root
```

`make test` (and therefore `make gates`) includes `tests/contract/`: it renders the `weg`
record from `cli-invocation-contract` and runs the installed console script for real, asserting the
artifacts with `assert_cli_writes_artifacts`. The catalog shells out to `magick`, so a host
without ImageMagick 7 fails that test instead of skipping it; `make imagemagick` installs the same
pinned, checksum-verified static build the CI pytest jobs use.

As a consumer, pin an immutable tag — never a path and never a branch:

```toml
# pyproject.toml
dependencies = ["wallpaper-effects-generator>=0.2.0"]

[tool.uv.sources]
wallpaper-effects-generator = { git = "https://github.com/RandomGenericUsername/wallpaper-effects-generator", tag = "v0.2.0" }
```

```bash
uv tool install "git+https://github.com/RandomGenericUsername/wallpaper-effects-generator@v0.2.0"
weg --version    # 0.2.0 contract 0.2.0
```

A published tag is never moved or deleted; a fix ships as a new tag.

## What `dotfiles-v3` pins

`dotfiles-v3` addresses this repo as `{name: weg, repo: <this repo>, tag: vX.Y.Z}` in
`provisioning/cli-tools.yaml`; the `cli_tools` role shallow-clones that tag, installs `weg` from the
checkout, builds with `--context <checkout> --image-tag <tag>`, and `verify` asserts the image
exists at that exact tag. Provisioning owns the pin, clone, install and image tag; it never writes
or patches this repo's Dockerfile (spine AD-7/AD-10).

That pin is currently `v0.1.0` (evidence: `dotfiles-v3`
`dotfiles/provisioning/cli-tools.yaml`, the `name: weg` entry). Moving it to `v0.2.0` is
`dotfiles-v3`'s own commit — a consumer pin bump never lands in this repo (AGENTS §6).

## Sibling pins

This repo consumes four sibling repos by immutable tag (spine AD-3):

| Distribution | Tag | Source |
| --- | --- | --- |
| `cli-output` | `v0.1.0` | `https://github.com/RandomGenericUsername/cli-output` |
| `config-assembler-engine` | `v0.1.0` | `https://github.com/RandomGenericUsername/config-assembler-engine` |
| `oci-runtime` | `v0.5.0` | `https://github.com/RandomGenericUsername/oci-runtime` |
| `cli-invocation-contract` | `v0.2.0` | `https://github.com/RandomGenericUsername/contracts` |

## Release

Version in `pyproject.toml` + `CHANGELOG.md` entry → annotated tag `vX.Y.Z` → GitHub Actions runs
the gates and the image build, then attaches the sdist and wheel to the GitHub Release. PyPI is not
used.

## Repo harness

- `AGENTS.md` (with `CLAUDE.md` symlinked to it) is the operating contract: evidence rule,
  worktree discipline, planning-vs-implementation commits.
- `tickets/` is the work ledger (`INDEX.md`, `LIFECYCLE.md`, `_template/`).
- `openspec/` holds the specs and the change log (`config.yaml`, `specs/`, `changes/`).
- `scripts/worktree-guard.sh create <id> <slug>` makes `.worktrees/<id>/` on
  `ticket/<id>-<slug>`; never work on `main`.
- `.agents/skills/` + `skills-lock.json` and `_bmad/` are hash-pinned copies of the `mu` harness.

## License

MIT — see `LICENSE`.
