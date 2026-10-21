---
id: OPS-002
title: "Prove weg's own side of the invocation contract in CI (artifact conformance)"
kind: ops-task
status: in-progress
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

Filled at closeout; each row is `command → observed`.
