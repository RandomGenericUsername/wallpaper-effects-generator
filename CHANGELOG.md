# Changelog

Notable changes to the `wallpaper-effects-generator` repo. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow the git tags
(`vMAJOR.MINOR.PATCH`, annotated, never moved).

## [Unreleased]

## [0.2.0] - 2026-10-21

Re-pin the invocation contract at `contracts` `v0.2.0` and release `weg` `0.2.0`. `weg`'s
invocation record is unchanged: the contract release is additive and `itr`-only, so the only
observable delta here is the contract token in `--version`.

### Changed

- `pyproject.toml` `[tool.uv.sources]`: `cli-invocation-contract` tag `v0.1.0` → `v0.2.0`
  (`contracts` annotated tag object `442fb9abdc73fa109115ba804911a10af9f4cad1`, peeled
  `c6c3ab5d523d06210f8e87535c464d3190d005c0`). `uv.lock` records that peeled commit.
  `CONTRACT_VERSION` is now `0.2.0` and `DATA_VERSION` `2`; the version-strict loader refuses a
  v2 document from a 0.1.x client, which is why every consumer must re-pin.
- Package version `0.1.0` → `0.2.0` (`pyproject.toml`, `src/wallpaper_effects_generator/__init__.py`).
  `weg --version` now prints `0.2.0 contract 0.2.0`.
- `tests/unit/cli/test_version_flag.py` asserts the pinned token explicitly
  (`CONTRACT_VERSION == "0.2.0"`) next to the derived-token assertion, so a stale tag pin fails the
  suite instead of agreeing with itself. Suite: 350 tests.
- CI `image` job no longer hard-codes `IMAGE_TAG=v0.1.0`; it takes the Makefile default
  (`v$(VERSION)` from `pyproject.toml`), so the image tag tracks the release.
- `README.md`: `--version` examples, container-mode examples, consumer pin snippets and the sibling
  pin table name `v0.2.0` / `0.2.0 contract 0.2.0`.

### Notes

- The contract release also adds `ICON_RENDERER__TEMPLATES__DIR` to `clis.itr.env`; nothing in the
  `weg` record (`argv`, `env`, `artifacts`, `exit_codes`, `timeout`) moved, and no `weg` code changed.
- The `dotfiles-v3` consumer pin is still `v0.1.0`; re-pinning it is that repo's own commit (AGENTS
  §6: consumer pin bump in its own commit).
- The illustrative literals in `openspec/specs/weg-cli/spec.md` and
  `openspec/specs/weg-container-mode/spec.md` still read `0.1.0 contract 0.1.0`. Main specs change
  through an OpenSpec change, so that refresh is deferred rather than folded into this pin bump.

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
- Suite: 349 tests, green in the ambient and hermetic environments, and independent of a
  host-installed ImageMagick (the tests provide a deterministic fake `magick`).
