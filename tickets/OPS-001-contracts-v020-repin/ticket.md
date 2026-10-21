---
id: OPS-001
title: "Re-pin contracts v0.2.0 and release weg v0.2.0"
kind: ops-task
status: done
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

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| `main` was clean before branching | `bash scripts/worktree-guard.sh check-clean`; `git rev-parse HEAD` | exit 0; `be0bbd6e27cb1752688df652c8f34eb7fc651c00` |
| worktree + branch | `bash scripts/worktree-guard.sh create OPS-001 contracts-v020-repin` | `.worktrees/OPS-001/` on `ticket/OPS-001-contracts-v020-repin` |
| tag facts match the remote | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/RandomGenericUsername/contracts 'refs/tags/v0.2.0*'` | `442fb9abdc73fa109115ba804911a10af9f4cad1 refs/tags/v0.2.0` + `c6c3ab5d523d06210f8e87535c464d3190d005c0 refs/tags/v0.2.0^{}` |
| contract change is itr-only | `git -C ../contracts diff v0.1.0 v0.2.0 -- src/`; `sed -n '/## \[0.2.0\]/,/## \[0.1.0\]/p' ../contracts/CHANGELOG.md` | `CONTRACT_VERSION 0.1.0 → 0.2.0`, `DATA_VERSION 1 → 2`, no `weg` record edit; "`csg` and `weg` are unchanged, and no CLI's `argv` or `artifacts` changed" |
| lock records the peeled commit | `uv lock`; `rg -n c6c3ab5d523d06210f8e87535c464d3190d005c0 uv.lock` | exit 0; `Resolved 26 packages`; `uv.lock:26: source = { git = "…/contracts?tag=v0.2.0#c6c3ab5d523d06210f8e87535c464d3190d005c0" }`; `uv.lock:25: version = "0.2.0"` |
| installed contract is 0.2.0 / data 2 | `.venv/bin/python -c "import cli_invocation_contract as c; print(c.CONTRACT_VERSION, c.DATA_VERSION)"` | `0.2.0 2` |
| CLI reports both versions | `.venv/bin/weg --version` | `0.2.0 contract 0.2.0` |
| pin assertion | `uv run pytest -q tests/unit/cli/test_version_flag.py` | `2 passed` (derived token + explicit `CONTRACT_VERSION == "0.2.0"`) |
| suite | `uv run pytest -q -rs` | `350 passed in 5.22s` (349 before, +1 pin assertion) |
| gates | `make gates` | exit 0; `350 passed` ×2 (test + hermetic), `All checks passed!`, `Resolved 26 packages` |
| CI gate parity | `make ci-gates-parity` | exit 0; `PASS gates=[…5] jobs=[…8] exempt=['ci-gates-parity','image','release']` |
| packaging | `uv build` | exit 0; `wallpaper_effects_generator-0.2.0-py3-none-any.whl` (60 309 B) + `.tar.gz` (77 306 B) |
| image at the pin | `make image IMAGE_TAG=v0.2.0` | exit 0; image `d176da2881d5`, `Successfully tagged localhost/wallpaper-effects-generator:v0.2.0`; run prints `0.2.0 contract 0.2.0` |
| merged + pushed | `git merge --ff-only ticket/OPS-001-contracts-v020-repin`; `git push origin main` | `be0bbd6..9fe62a3 main -> main`; released commit `9fe62a3b151988fae6a77ede47061a92e734310e` |
| annotated tag | `git tag -a v0.2.0 …`; `git cat-file -t v0.2.0`; `git rev-parse v0.2.0`; `git rev-parse 'v0.2.0^{commit}'` | `tag`; object `95d85f00175416245812edda6cf6c2ebbeac1860`; peeled `9fe62a3b151988fae6a77ede47061a92e734310e` |
| anonymous fetch, one line | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/RandomGenericUsername/wallpaper-effects-generator 'refs/tags/v0.2.0' \| wc -l` | exactly one line: `95d85f00… refs/tags/v0.2.0` |
| isolated tag install | `UV_TOOL_DIR=… UV_TOOL_BIN_DIR=… uv tool install --force git+…@v0.2.0`; `…/bin/weg --version` | install exit 0, resolved to `9fe62a3b…` (`wallpaper-effects-generator==0.2.0`); `0.2.0 contract 0.2.0` |
| release carries both artifacts | `gh release view v0.2.0 --json tagName,isDraft,isPrerelease,assets` | `v0.2.0`, not draft, not prerelease; `wallpaper_effects_generator-0.2.0-py3-none-any.whl` 60 309 B + `.tar.gz` 77 306 B, both `uploaded` (same sizes as the local `uv build` at `9fe62a3`) |
| CI on `main` | `gh run view 39657271889` | `completed` / `success` (7 gates, `image`; `release` skipped — a branch push has no tag) |
| CI on the tag | `gh run view 39657283780 --json jobs` | `completed` / `success`, all 8 jobs incl. `release`; `image` log line `0.2.0 contract 0.2.0` |
| specs still validate | `openspec validate --specs --strict` | `3 passed, 0 failed (3 items)`, exit 0 |

## Diffstat (`be0bbd6..9fe62a3`)

```
 .github/workflows/gates.yml                    |  2 +-
 CHANGELOG.md                                   | 33 +++++++++++++++
 README.md                                      | 26 +++++++-----
 pyproject.toml                                 |  6 +--
 src/wallpaper_effects_generator/__init__.py    |  2 +-
 src/wallpaper_effects_generator/cli/options.py |  2 +-
 tests/unit/cli/test_version_flag.py            | 11 +++++
 tickets/INDEX.md                               |  2 +-
 tickets/OPS-001-contracts-v020-repin/ticket.md | 57 ++++++++++++++++++++++++++
 uv.lock                                        |  8 ++--
 10 files changed, 127 insertions(+), 22 deletions(-)
```

## Commits

- `e83a034` `plan(OPS-001)`: the ticket + INDEX entry (planning commit, no code).
- `9fe62a3` `feat(release)`: pin bump, version bump, lock, version test, CHANGELOG/README, CI image tag.
- closeout (this commit): ticket `done` + INDEX flip + this evidence.

## Deviations

1. **The CI `image` job no longer hard-codes a tag.** It read `IMAGE_TAG=v0.1.0` while
   `pyproject.toml` said `0.2.0`, so a 0.2.0 tree would have been labelled `v0.1.0`. It now takes
   the Makefile default (`v$(VERSION)`), which is self-maintaining. `make ci-gates-parity` still
   exits 0 (the job set is unchanged).
2. **Two extra stale literals were refreshed** besides the pin itself: the `--image-tag` help
   example in `cli/options.py` and the `cli-invocation-contract>=0.1.0` floor in `pyproject.toml`
   (`>=0.2.0`, since `DATA_VERSION 2` is what the loader now requires).
3. **`openspec/specs/*` literals were NOT changed.** `weg-cli/spec.md:17` and
   `weg-container-mode/spec.md:58` still print `0.1.0 contract 0.1.0` in their scenarios. Main specs
   change through an OpenSpec change (AGENTS §4/§5) and this item deliberately carries none, so the
   refresh is deferred — recorded in `CHANGELOG.md` and in the "Why no OpenSpec change" note above.
   `openspec validate --specs --strict` is unaffected (it does not evaluate scenario literals).

## MISSING

- The `dotfiles-v3` consumer pin is still `v0.1.0` (`dotfiles/provisioning/cli-tools.yaml`, `name:
  weg`). Re-pinning it is that repo's own commit (AGENTS §6) and is out of scope here; no work was
  done there.
- No `openspec/specs/` refresh for the `0.1.0 contract 0.1.0` scenario literals (deviation 3).

