---
id: OPS-002
title: "Prove weg's own side of the invocation contract in CI (artifact conformance)"
kind: ops-task
status: done
lane: 1
links:
  openspec: none
  bmad: none
worktree: .worktrees/OPS-002/
branch: ticket/OPS-002-contract-artifacts-ci
---

# Prove weg's own side of the invocation contract in CI (artifact conformance)

> `ops-task` read as `chore` (Shortcut mapping). No `parent:` by design.
> Git discipline holds: `scripts/worktree-guard.sh check-clean` → exit 0 on `main` at `8221000`,
> worktree `.worktrees/OPS-002/` on `ticket/OPS-002-contract-artifacts-ci`.
> Lane 1 (XS direct): one bounded capability (a CI-enforced conformance test + its CI support),
> fully understood, no architectural unknown and no public-surface delta.

## Why no OpenSpec change (recorded choice)

The runtime↔CLI invocation contract is **not owned here**: it lives in the `contracts` repo as
`cli-invocation-contract` (spine AD-4), and `AGENTS.md` already makes
`cli_invocation_contract.testkit` the source of invocation assertions, with an explicit ban on
duplicating argv/env/artifact literals in tests. This item adds no behaviour and no spec-level
capability: `weg`'s argv, env, exit codes and artifact shape are unchanged. It closes a
**verification** gap — the repo's own side of the contract (a real `batch all` producing real
artifacts) was never asserted, so a regression in the local backend would be caught by the
`contracts` consumer tests or by hand, not by this repo's gates.

Therefore: no OpenSpec change, no BMAD; a lane-1 ops-task with a test + CI-support delta.

## Work

1. `tests/contract/test_invocation_contract.py`: load the `weg` record with
   `cli_invocation_contract.get("weg")`, render its `argv`/`env` templates against a checked-in
   PNG fixture, a temp output directory and the scrubbed environment the suite already enforces,
   run the repo's installed `weg` console script, and hand the run to
   `assert_cli_writes_artifacts(record, "weg", run, cwd)`. No argv/env/artifact literal is typed
   in the test — the record is the only source.
2. The local backend shells out to ImageMagick **7** (`magick`); the unit/CLI suites use the fake
   `magick` from `tests/conftest.py`. Give the contract test an explicit opt-out marker so it runs
   against the **real** backend, and make a missing `magick` a **failure**, never a skip — the
   artifacts must be real pixels.
3. CI: the GitHub Ubuntu runner has no ImageMagick 7 (`magick`); add a pinned, checksum-verified
   install of the upstream static build to the two jobs that run pytest (`test`, `hermetic`) so
   the new test really runs. The `GATES` set and the job set are unchanged, so
   `scripts/ci-gates-parity.py` must keep passing without edits.
4. Gates: `make gates`, `make ci-gates-parity`, `uv build`; record the artifact count from a real
   run.
5. Commit (planning and implementation as separate commits), ff-merge to `main`, push. No version
   bump and no tag: tests + CI support only, no shipped behaviour change.

## Done-when

`make gates` and `make ci-gates-parity` are green on the ticket branch with the contract test
executing for real (artifact count > 0 and every artifact non-empty), CI installs the pinned
ImageMagick 7 in the pytest jobs, the branch is ff-merged into `main` and pushed, and `main` is
clean.

## Evidence

Every row is `command → observed`.

| Claim | Command | Observed |
| --- | --- | --- |
| `main` was clean before branching | `bash scripts/worktree-guard.sh check-clean`; `git rev-parse HEAD` | exit 0; `8221000585ea965c55b44d7ef94b8be6629f038f` |
| worktree + branch | `bash scripts/worktree-guard.sh create OPS-002 contract-artifacts-ci` | `.worktrees/OPS-002/` on `ticket/OPS-002-contract-artifacts-ci` |
| the record is the test's only source | `.venv/bin/python -c "import json; from cli_invocation_contract import get; print(json.dumps(get('weg'), indent=2))"` | `argv=["batch","all","--","{wallpaper}"]`; `env.required=["WALLPAPER__OUTPUT__DIRECTORY"]`, `env.injected={"WALLPAPER__OUTPUT__DIRECTORY":"{output_dir}"}`; `artifacts.match="suffix"`, `recursive=true`, `min_count=1`; `exit_codes.success=0`; `timeout=600` |
| fixture is a real, tiny PNG | `magick -size 32x24 gradient:'#1e1e2e'-'#cba6f7' -strip png24:tests/fixtures/wallpaper.png`; `file`; `sha256sum` | 116 B; `PNG image data, 32 x 24, 8-bit/color RGB`; `ba7158ac9ef899006433d4563a6d4e855425e76b8c2cfa18a9111ca6412f24ea` |
| contract test green against the real backend | `.venv/bin/python -m pytest tests/contract -q -rs` | `1 passed in 0.86s` |
| real artifacts, counted | `.venv/bin/python -m pytest tests/contract -q --basetemp=/tmp/opencode/weg-basetemp`; `find … -name '*.png' \| wc -l`; `file` | `1 passed in 0.91s`; `count=20` (`effect=9`, `composite=4`, `preset=7`, 8 071 B total); `PNG image data, 32 x 24, 8-bit colormap`; smallest artifact 273 B |
| a fake backend cannot pass | `PATH=/tmp/opencode/fakebin:$PATH .venv/bin/python -m pytest tests/contract -q` (fake `magick` = the suite's empty-file stub) | `1 failed` — `artifacts exist but carry no pixels (fake backend?)` listing all 20 paths |
| a missing backend fails, never skips | `PATH=/tmp/opencode/emptybin .venv/bin/python -m pytest tests/contract -q` | `1 failed in 0.07s` — `magick (ImageMagick 7) is not on PATH …` (no skip) |
| installer works with no host `magick` | `env -i PATH=<restricted-bin-without-magick> HOME=/tmp/… GITHUB_PATH=/tmp/… IMAGEMAGICK_PREFIX=/tmp/… bash scripts/install-imagemagick7.sh` | `downloading …/7.1.2-34/ImageMagick-7.1.2-34-gcc-x86_64.AppImage`; `…AppImage: OK` (SHA-256); `installed: …/bin/magick (Version: ImageMagick 7.1.2-34 Q16-HDRI x86_64 …)`; `appended … to GITHUB_PATH`; exit 0 |
| the installed build is usable scrubbed | `env -i PATH=<prefix>/bin:/usr/bin:/bin magick -version`; `… magick -size 4x4 xc:red probe.png` | `Version: ImageMagick 7.1.2-34 Q16-HDRI …`; probe is `PNG image data, 4 x 4` |
| installer is idempotent | rerun with a host `magick` on PATH | `magick already available: /usr/bin/magick (Version: ImageMagick 7.1.2-32 …)`; exit 0 |
| suite | `.venv/bin/python -m pytest -q -rs` | `351 passed in 6.32s` (350 before; +1 contract test) |
| gates | `make gates` | exit 0; `351 passed` ×2 (test + hermetic), `All checks passed!`, `Resolved 26 packages` |
| CI-like hermetic run on the pinned build | `PATH=/tmp/opencode/im7-install/bin:$PATH make hermetic` | `command -v magick` → `/tmp/opencode/im7-install/bin/magick` (`7.1.2-34`); `351 passed in 5.49s` |
| CI gate parity | `make ci-gates-parity` | exit 0; `PASS gates=['docs-check','hermetic','lint','lock-check','test'] jobs=[…8] exempt=['ci-gates-parity','image','release']` — unchanged, no new job |
| packaging | `uv build` | exit 0; `wallpaper_effects_generator-0.2.0-py3-none-any.whl` (60 531 B), `.tar.gz` (80 155 B); sdist carries `tests/contract/test_invocation_contract.py` and `tests/fixtures/wallpaper.png` |
| merged + pushed | `git merge --ff-only ticket/OPS-002-contract-artifacts-ci`; `git push origin main` | `8221000..863066f main -> main` |
| CI on the merged `main` | `gh run view 39665901804 --json jobs` | `completed` / `success`; `lint`, `docs-check`, `ci-gates-parity`, `image`, `lock-check`, `test`, `hermetic` all success; `release` skipped (branch push, no tag) |
| CI installs the real backend | `gh run view 39665901804 --log --job <test>` | `downloading …7.1.2-34-gcc-x86_64.AppImage`; `…: OK`; `installed: /home/runner/.local/opt/imagemagick-7.1.2-34/bin/magick (Version: ImageMagick 7.1.2-34 Q16-HDRI …)`; `appended … to GITHUB_PATH` |
| the contract test really runs in CI | test + hermetic job logs | `351 passed in 2.13s` (test) and `351 passed in 3.12s` (hermetic); the previous `main` run was `350 passed in 2.19s`; `-rs` printed no skip |
| CI parity on the merged commit | `gh run view 39665901804 --log --job <ci-gates-parity>` | `PASS gates=[…5] jobs=[…8] exempt=['ci-gates-parity','image','release']` |

## Diffstat (`8221000..863066f`)

```
 .github/workflows/gates.yml                      |  9 ++
 CHANGELOG.md                                     | 15 +++
 Makefile                                         | 10 +-
 README.md                                        |  7 ++
 pyproject.toml                                   |  3 +
 scripts/install-imagemagick7.sh                  | 81 +++++++++++++++
 tests/conftest.py                                | 10 +-
 tests/contract/__init__.py                       |  0
 tests/contract/test_invocation_contract.py       | 125 ++++++++++++++++++
 tests/fixtures/wallpaper.png                     | Bin 0 -> 116 bytes
 tests/test_hermetic_canary.py                    |  1 +
 tickets/INDEX.md                                 |  2 +-
 tickets/OPS-002-contract-artifacts-ci/ticket.md  | 65 ++++++++++++
 13 files changed, 325 insertions(+), 3 deletions(-)
```

## Commits

- `7a4633c` `plan(OPS-002)`: ticket + INDEX entry (planning only).
- `863066f` `test(contract)`: the contract test, the `real_imagemagick` opt-out, the pinned-CI
  install and the docs/CHANGELOG entry.
- closeout (this commit): ticket `done`, INDEX moved to Done, evidence below.

## Deviations

1. **No new CI job.** The task allowed "existing `test` job or a dedicated `contract` job"; the
   existing gates were chosen so `GATES`, the workflow job set and `scripts/ci-gates-parity.py`
   stay untouched (the parity check still passes byte-identically). It also means the gate is red
   — not quietly skipped — when the backend is absent.
2. **The runner's package manager is not used for ImageMagick.** Ubuntu's `imagemagick` package is
   ImageMagick 6, which exposes no `magick`, and the shipped catalog commands hardcode `magick`
   (`src/wallpaper_effects_generator/defaults/effects.yaml:14` onwards). The installer therefore
   pins the upstream static AppImage (`7.1.2-34`, verified SHA-256), extracts it (no FUSE) and
   appends its `bin` via `$GITHUB_PATH`. `apt` would have needed a fake `magick` shim, which the
   artifact assertion would rightly reject.
3. **One extra hermeticity fix.** `WALLPAPER_EFFECTS_CONFIG_FILE_PATH` was missing from the
   scrub list in `tests/conftest.py` (and the canary), so a host effects file could silently
   change the catalog the contract test exercises. It is now scrubbed and canary-asserted.
4. **`tests/contract/__init__.py`** matches the existing `tests/unit/__init__.py` layout.
5. **Pre-existing `ruff format` drift in `tests/conftest.py`** (an extra blank line before
   `FakeProcessor`) is left as-is: `make lint` only checks `src/`, the drift predates this ticket,
   and reformatting it would mix an unrelated hunk into this change.
6. **The Makefile gains `imagemagick`** as CI support, documented as not a gate; `make help`
   lists it.

## MISSING

- **No version bump and no tag.** Tests + CI support only; the `CHANGELOG.md` `[Unreleased]`
  section records the change. Nothing in the shipped wheel's behaviour moved.
- **Single-run CI evidence.** `gh run view 39665901804` is one `ubuntu-latest` x86_64 run; the
  installer fails closed on other platforms and has no arm64/macOS path.
- **Artifact count is not asserted.** The record requires `min_count=1`; the observed 20
  (`effect=9`, `composite=4`, `preset=7`) is evidence, not a test bound, so a catalog that silently
  shrinks would not fail this test.
- **The container path is not covered by this test.** `make image` still only runs
  `weg --version`; running the contract test inside the image (where ImageMagick is Alpine's) is
  not proven here.
- **The ImageMagick pin is manual.** Bumping it means editing the version *and* the SHA-256 in
  `scripts/install-imagemagick7.sh`; nothing checks upstream for a newer release.
