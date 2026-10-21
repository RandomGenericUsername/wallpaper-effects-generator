# Changelog

Notable changes to the `wallpaper-effects-generator` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow the git tags
(`vMAJOR.MINOR.PATCH`, annotated, never moved).

## [Unreleased]

## [0.1.0] - 2026-10-20

First release. The package content is the in-tree `src/cli-tools/wallpaper-effects-generator`
package (version `0.1.0` there) imported with `git subtree split`, history preserved; the
version continues at `0.1.0` (spine AD-9: versions never move backwards).

### Added

- Repo harness copied byte-for-byte from `mu`: `scripts/worktree-guard.sh`, `skills-lock.json`,
  `_bmad/`, `.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/`,
  `tickets/LIFECYCLE.md`.
- `Makefile` fresh-clone verbs (`sync`, `test`, `lint`, `format`, `check`, `hermetic`,
  `lock-check`, `docs-check`, `gates`, `gates-ci`, `image`, `build`, `install`, `clean`,
  `ci-gates-parity`), `.github/workflows/gates.yml`, `scripts/ci-gates-parity.py`.
- `make image` builds `Dockerfile.imagemagick` from this repo root at
  `wallpaper-effects-generator:v<version>` and runs `weg --version` inside the image (AD-5/AD-7).
- MIT `LICENSE`, `README.md`, `AGENTS.md`, `CLAUDE.md` symlink, ticket `REQ-001-repo-birth`,
  the OpenSpec change `repo-birth`, and the imported capability specs `weg-cli` and
  `weg-container-mode`.
- `weg install --image-tag TAG`: explicit, validated image tag override so provisioning can pass
  the pin (`v0.1.0`) instead of `latest`.

### Changed

- `pyproject.toml`: release metadata (`readme`, `license`, `license-files`, classifiers),
  `hatchling>=1.27`, an sdist `only-include` list so the harness trees stay out of the artifact,
  explicit compatibility ranges for the four sibling dependencies, and a dev group carrying
  `pytest`, `pytest-cov` and `ruff`.
- Sibling dependencies are consumed as immutable git tags (spine AD-3): `cli-output` `v0.1.0`,
  `config-assembler-engine` `v0.1.0`, `oci-runtime` `v0.5.0`, and `cli-invocation-contract`
  (`contracts`) `v0.1.0`. `uv.lock` records the resolved commits.
- `make lint` and `make format` keep the imported in-tree scope (`src/`).

### Notes

- The image tag is the pin, not `latest` (spine AD-7). The Dockerfile copies only repo-relative
  paths (`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`); no sibling repo or parent
  directory is referenced.
- Suite: 349 tests, green in the ambient and hermetic environments.
