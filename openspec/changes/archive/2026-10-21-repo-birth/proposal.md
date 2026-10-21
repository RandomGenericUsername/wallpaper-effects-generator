# repo-birth

## Why

`wallpaper-effects-generator` is the first container-mode CLI extracted from `dotfiles-v3` in the
CLI/split programme (spine `SLICES.md` § S5). The package is green in-tree and its Dockerfile was
already rewritten in S3 to copy only package-relative paths, but a repository is not a valid
extraction target until it is mu-strict from its first commit (spine **AD-12**) and the image is
proven to build from **its own repo root** (AD-5).

Evidence: the package has 30 test modules, a package-relative Dockerfile and no sibling path inside
it. Verify: `git -C /home/inumaki/Development/dotfiles-v3 ls-tree -r --name-only master --
src/cli-tools/wallpaper-effects-generator | grep -c '^tests/.*test_.*\.py$'` → `30`;
`rg -n "src/shared|src/cli-tools|\.\./" src/wallpaper_effects_generator/adapters/docker/` → exit 1.

Evidence: the split must preserve history with `git subtree split`, not a fresh-root import
(spine OPEN-8, `SLICES.md` § Slice template step 2).
Verify: `git -C /home/inumaki/Development/dotfiles-v3 subtree split -P
src/cli-tools/wallpaper-effects-generator -b split/wallpaper-effects-generator` → exit 0, branch
tip `810e72b`, 65 commits.

Evidence: the harness must be copied from `mu`, not re-authored (AD-12).
Verify: `diff -r /home/inumaki/Development/mu/_bmad _bmad` → empty; same for
`scripts/worktree-guard.sh`, `skills-lock.json`, `.agents/skills`, `.opencode`, `tickets/_template`,
`tickets/_fixtures`, `tickets/LIFECYCLE.md`.

## What Changes

- Create the public repo `RandomGenericUsername/wallpaper-effects-generator`, default branch `main`,
  from the `git subtree split` result of `src/cli-tools/wallpaper-effects-generator` (65 commits
  preserved).
- Install the mu-strict harness **byte-for-byte**: `scripts/worktree-guard.sh`, `skills-lock.json`,
  `_bmad/`, `.agents/skills/`, `.opencode/`, `tickets/_template/`, `tickets/_fixtures/`,
  `tickets/LIFECYCLE.md`.
- Add the repo contract: `AGENTS.md` (evidence rule verbatim, charter = `weg` with container mode,
  ticket routing, never work on main, planning vs implementation, release ritual), `CLAUDE.md` →
  `AGENTS.md`.
- Add the work ledger: `tickets/INDEX.md` (counting rule header), `tickets/REQ-001-repo-birth/`.
- Add the OpenSpec root: `openspec/config.yaml` (evidence rules, repo context),
  `openspec/specs/{weg-cli,weg-container-mode}/` (the imported capability specs) and this change.
- Add a fresh-clone Makefile (`sync`, `test`, `lint`, `format`, `check`, `hermetic`, `lock-check`,
  `docs-check`, `gates`, `gates-ci`, `build`, `install`, `image`, `clean`, `ci-gates-parity`),
  `.github/workflows/gates.yml` (one job per gate + `ci-gates-parity` + `image` + tag release),
  `scripts/ci-gates-parity.py`, MIT `LICENSE`, `README.md`, `CHANGELOG.md`, `.gitignore`.
- Keep packaging honest: the four sibling dependencies stay git-tag sources with compatibility
  ranges and a current committed `uv.lock`; `uv build` produces
  `wallpaper_effects_generator-0.1.0` sdist + wheel.
- Add `--image-tag` to `weg install` with Docker tag validation and tests, so provisioning can
  pass the pin (`v0.1.0`) explicitly instead of relying on `settings.toml`.

## Out of scope

- Rewiring `dotfiles-v3` to the `{name, repo, tag}` pin and deleting the in-tree package.
- Any processing/catalog behaviour change; the only product change is `install --image-tag`.
- Changes to the invocation-contract record.
- PyPI publication.
