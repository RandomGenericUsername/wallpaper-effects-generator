---
id: OPS-001
title: "Re-pin contracts v0.2.0 and release weg v0.2.0"
kind: ops-task
status: in-progress
lane: 1
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-001/
branch: ticket/OPS-001-contracts-v020-repin
---

# Re-pin contracts v0.2.0 and release weg v0.2.0

> `ops-task` read as `chore` (Shortcut mapping). No `parent:` by design.
> Git discipline holds: `scripts/worktree-guard.sh check-clean` → exit 0 on `main` at `be0bbd6`,
> worktree `.worktrees/OPS-001/` on `ticket/OPS-001-contracts-v020-repin`.

## Why no OpenSpec change (recorded choice)

`contracts` released `v0.2.0` (annotated object
`442fb9abdc73fa109115ba804911a10af9f4cad1`, peeled
`c6c3ab5d523d06210f8e87535c464d3190d005c0`). Its `CHANGELOG.md` `[0.2.0]` records an **additive**
change: the `itr` record gains `ICON_RENDERER__TEMPLATES__DIR` in `clis.itr.env`; `csg` and `weg` are
unchanged and no CLI's `argv` or `artifacts` moved. `CONTRACT_VERSION` goes `0.1.0` → `0.2.0` and
`DATA_VERSION` goes `1` → `2` (the `load()` strictness is what forces every consumer to re-pin, not a
weg behaviour change).

This repo's observable behaviour changes in exactly one place — the `--version` contract token that
`cli/main.py` already reads from `CONTRACT_VERSION` — so there is no new requirement to specify and
no capability delta to record. The work is a pin bump, a package version bump and a release:
`ops-task`, lane 1 (XS direct), no OpenSpec change, no BMAD.

Deferred: the illustrative literals in `openspec/specs/weg-cli/spec.md` (`0.1.0 contract 0.1.0`) and
`openspec/specs/weg-container-mode/spec.md` still name `0.1.0`. Main specs change through an
OpenSpec change, so they are left untouched here and noted as follow-up work.

## Work

1. `pyproject.toml`: `cli-invocation-contract` source tag `v0.1.0` → `v0.2.0`; package version
   `0.1.0` → `0.2.0`; `src/wallpaper_effects_generator/__init__.py` `__version__` likewise.
2. `uv lock`; prove `uv.lock` records the peeled commit `c6c3ab5d…`.
3. `tests/unit/cli/test_version_flag.py`: derive the contract token from
   `cli_invocation_contract.CONTRACT_VERSION` and assert `0.2.0` explicitly (so a stale pin fails
   loudly instead of silently agreeing with itself).
4. `CHANGELOG.md` `0.2.0` entry, `README.md` pin/version examples, and the CI `image` job tag
   (derive from `pyproject.toml` instead of the hard-coded `v0.1.0`).
5. Gates: `make gates`, `uv build`, `make image IMAGE_TAG=v0.2.0` + `weg --version` in the image.
6. Commit, ff-merge to `main`, push, annotated tag `v0.2.0`, GitHub Release with wheel + sdist from
   the tag, isolated tag install, anonymous `ls-remote`, CI green.

## Done-when

`v0.2.0` is tagged on a green `main` whose `uv.lock` records `contracts` `c6c3ab5d…`, whose image
and isolated tag install both print `0.2.0 contract 0.2.0`, and whose GitHub Release carries the
wheel and sdist built from the tag.
