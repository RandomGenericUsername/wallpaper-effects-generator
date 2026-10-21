---
id: REQ-001
title: "Birth the wallpaper-effects-generator repo (mu-strict, weg) and cut v0.1.0"
kind: requirement
status: done
lane: 3
links:
  openspec: repo-birth
  bmad: none
worktree: none
branch: main
---

# Birth the wallpaper-effects-generator repo (mu-strict, weg) and cut v0.1.0

## Requirement

Slice **S5a** of the CLI-repos split SHALL create
`RandomGenericUsername/wallpaper-effects-generator` as a public repo whose root is the imported
`src/cli-tools/wallpaper-effects-generator` package, preserve that package's history with
`git subtree split`, install the `mu` harness byte-for-byte, prove the container image builds from
the repo root (spine AD-5/AD-7), and cut the repo's first tag (`v0.1.0`) only after the gates,
packaging, image proof and CI exist.

The package owns its Dockerfile and its `install` build verb. The image build context is this repo
root and the image tag is the pin (`v0.1.0`), never `latest`. `dotfiles-v3` is not modified — the
consumer rewire and the in-tree deletion are the remaining S5 steps in that repo.

## Acceptance

- [x] The repo exists, is **public**, and its `main` carries the imported subtree commits.
  Verify: `gh api repos/RandomGenericUsername/wallpaper-effects-generator --jq .private` → `false`;
  `git log --oneline | wc -l` → 65 imported commits before the scaffold.
- [x] The harness is byte-identical to `mu` at every copied path.
  Verify: `diff -r` per path (see the evidence table) → empty, exit 0.
- [x] `AGENTS.md` carries the evidence rule and this repo's charter; `CLAUDE.md` is a symlink.
  Verify: `rg -c "Evidence:|Verify:" AGENTS.md` → ≥ 2; `test -L CLAUDE.md` → exit 0.
- [x] `tickets/INDEX.md` lists this ticket with the same status as the frontmatter, and the
  OpenSpec change validates strictly.
  Verify: `openspec validate --specs --strict` → exit 0; `openspec validate repo-birth --strict`
  → exit 0.
- [x] A fresh clone passes `make sync && make gates && make build` and the suite count is 349.
  Verify: `uv sync --frozen && uv run pytest -q` → `349 passed`; `make gates` → exit 0;
  `ls dist/wallpaper_effects_generator-0.1.0-*` → wheel + sdist.
- [x] The image builds from the repo root at the pin tag and reports the contract version.
  Verify: `podman build -t wallpaper-effects-generator:v0.1.0 -f
  src/wallpaper_effects_generator/adapters/docker/Dockerfile.imagemagick .` → exit 0;
  `podman run --rm wallpaper-effects-generator:v0.1.0 weg --version` → `0.1.0 contract 0.1.0`.
- [x] `weg install --image-tag v0.1.0` builds the tag-qualified image; an invalid tag is rejected.
  Verify: `weg install --context . --container-engine podman --image-tag v0.1.0` → image
  `weg-podman:v0.1.0`; `weg install --image-tag 'bad tag'` → non-zero, `invalid image tag`.
- [x] `.github/workflows/gates.yml` exists and its job set equals `GATES` (plus declared CI-only
  jobs); the first run on `main` is green.
  Verify: `make ci-gates-parity` → `PASS ...`; `gh run list -R RandomGenericUsername/wallpaper-effects-generator
  --limit 1 --json status,conclusion` → `completed` / `success`.
- [x] Annotated tag `v0.1.0` exists on the released commit, is anonymously fetchable, and its
  GitHub Release carries the wheel + sdist.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote
  https://github.com/RandomGenericUsername/wallpaper-effects-generator 'refs/tags/v0.1.0'` →
  exactly one line; `gh release view v0.1.0 --json assets --jq '.assets[].name'` → both artifacts.
- [x] `git status --porcelain` is empty in both repos; `dotfiles-v3` `master` is at the same SHA
  as before the slice.
  Verify: `git status --porcelain` → empty; `git -C /home/inumaki/Development/dotfiles-v3 rev-parse
  master` → `6ad7117cc982d540d05ec70cecf466393ac1cadc`.

## Out of scope

- Rewiring `dotfiles-v3` (`provisioning/cli-tools.yaml`, `roles/cli_tools`, `roles/verify`,
  `deploy-coverage`) to the `{name, repo, tag}` pin and deleting
  `src/cli-tools/wallpaper-effects-generator` — those are the remaining S5 steps in that repo.
- Any package behaviour change outside the added `install --image-tag` option.
- Changes to the invocation-contract content.
- PyPI publication; the channel is the git tag plus GitHub Release artifacts.

## Evidence

| Claim | Command | Observed |
| --- | --- | --- |
| name freed, repo created public | `gh api repos/RandomGenericUsername/wallpaper-effects-generator --jq '{private,created_at}'` | `{"private":false,"created_at":"2026-10-21T02:40:15Z"}`; default branch `main` |
| legacy preserved | `gh api repos/RandomGenericUsername/wallpaper-effects-generator-legacy --jq .private` | `true` (renamed, intact) |
| history preserved | `git rev-list --count split/wallpaper-effects-generator` (dotfiles) | `65`; split tip `810e72baa91beb61de32e4e083cbe8c8d5c3ab14` |
| harness byte-identical | `diff -r mu/<path> <path>` for `_bmad`, `.agents/skills`, `.opencode`, `scripts/worktree-guard.sh`, `skills-lock.json`, `tickets/_template`, `tickets/_fixtures`, `tickets/LIFECYCLE.md` | `IDENTICAL` × 8, exit 0 |
| evidence rule present | `rg -c "Evidence:\|Verify:" AGENTS.md`; `test -L CLAUDE.md` | `6`; exit 0 |
| specs/change valid | `openspec validate --specs --strict`; `openspec validate repo-birth --strict` | 2 passed; `Change 'repo-birth' is valid` |
| suite | `uv run pytest -q` | `349 passed` |
| gates | `make gates` | exit 0; `349 passed` ×2, `All checks passed!`, lock current |
| packaging | `uv build` | exit 0; `wallpaper_effects_generator-0.1.0-py3-none-any.whl` + `.tar.gz` |
| image | `podman build -t wallpaper-effects-generator:v0.1.0 ... .`; `podman run --rm wallpaper-effects-generator:v0.1.0 weg --version` | build exit 0, image `81d4c337ce25`; `0.1.0 contract 0.1.0` |
| image from a clone | `make image` in `/tmp/opencode/weg-fresh` | exit 0, image `65df6cbb6798`; `0.1.0 contract 0.1.0` |
| install verb tag | `.venv/bin/weg install --context . --container-engine podman --image-tag v0.1.0` | exit 0; `weg-podman:v0.1.0` (`81d4c337ce25`); run prints `0.1.0 contract 0.1.0` |
| invalid tag | `weg install --image-tag 'bad tag'` | exit 2; `invalid image tag`; no build |
| fresh clone (public) | `git clone https://github.com/... /tmp/opencode/weg-remote` at `v0.1.0`; `make sync && make gates && make hermetic && uv lock --check && make build` | all exit 0; `349 passed` ×2; wheel + sdist; HEAD `9672d89`, `git describe` → `v0.1.0` |
| CI parity | `make ci-gates-parity` | `PASS gates=[...5] jobs=[...8] exempt=[ci-gates-parity, image, release]` |
| first main run | `gh run view 39534341072` | **failure**: 11 tests needed a host `magick`; fixed in tests |
| second main run | `gh run view 39534659796` | **failure**: 1 wrapped-message assertion; fixed |
| third main run | `gh run view 39534789496` | **failure**: ANSI styling split the option name; fixed |
| green main run | `gh run view 39534905975` | **success** (test, lint, hermetic, lock-check, docs-check, ci-gates-parity, image) |
| tag CI run | `gh run view 39534972375` | **success**, all 8 jobs incl. `release` |
| annotated tag | `git cat-file -t v0.1.0`; `git rev-parse v0.1.0`; `git rev-parse 'v0.1.0^{commit}'` | `tag`; `093d405129ef34a7d1bd78c64b692bca17129cb9`; `9672d89c117709afa6eb5b574bd8fdb71469f801` |
| anonymous fetch | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote ... 'refs/tags/v0.1.0'` | exactly one line: `093d4051… refs/tags/v0.1.0` |
| release artifacts | `gh release view v0.1.0 --json assets` | `wallpaper_effects_generator-0.1.0-py3-none-any.whl` (60 204 B) + `.tar.gz` (76 035 B), both `uploaded` |
| tag install + batch | `uv tool install git+…@v0.1.0`; `weg --version`; `WALLPAPER__OUTPUT__DIRECTORY=… weg batch all -- input.png` | `0.1.0 contract 0.1.0`; batch exit 0; **20 output files** |
| dotfiles untouched | `git -C /home/inumaki/Development/dotfiles-v3 rev-parse master`; `git status --porcelain` | `6ad7117cc982d540d05ec70cecf466393ac1cadc`; empty (only the local `split/` ref was added) |

## Deviations from the slice text

1. **The target repo name was occupied at start, then freed by the owner.** The name initially
   resolved to a private legacy repo (`wallpaper-effects-generator`, 2025-12-13, default branch
   `master`, unrelated workspace layout, 200+ commits, no tags). I did not delete, rename or
   force-push it; the remote steps were paused and reported. The owner then renamed it to
   `wallpaper-effects-generator-legacy` (private, intact), and the exact slice command created the
   new public repo. The old URL still returns the legacy repo for a bare `ls-remote` via GitHub's
   rename redirect; the new repo's own refs are correct.
2. **`install --image-tag` added.** The imported verb had no tag override; the image tag could only
   come from `[container] image_tag` in settings. The option is added with Docker tag validation
   and tests so provisioning can pass the pin explicitly.
3. **Suite count is 349, not 346.** The imported suite is 347 in this checkout (the S0b note said
   346–347); the two added `--image-tag` tests raise it to 349.
4. **The Dockerfile copies two more repo-relative files.** Release metadata (`readme =` and
   `license-files =`) makes hatchling read `README.md` and `LICENSE` while building the wheel in the
   image; the S3 Dockerfile predates that metadata. Both are repo-relative, so AD-5's invariant (no
   sibling repo, no parent directory) holds; the COPY list is `pyproject.toml`, `uv.lock`,
   `README.md`, `LICENSE`, `src/`.
5. **Ruff ignores `B008`.** The imported Typer handlers declare options in defaults, which is
   Typer's idiom; without the ignore `make lint` cannot be green. Three real findings were fixed
   (`B904` in `batch_processor.py`, two `F841`).
6. **Three CI-driven test fixes, all in `tests/`.** (a) An autouse fixture puts a deterministic fake
   `magick` on PATH, so the 11 tests that constructed the real runner no longer need a host
   ImageMagick (`673f368`). (b) The `--explicit-output` assertion checks the two message fragments
   instead of one line, because Rich boxes/wraps it (`bd53ec2`). (c) It strips ANSI before asserting,
   because CI forces color and Rich can split the option name (`9672d89`). Verified locally with
   `PATH` lacking `magick`, `COLUMNS=40`, and `FORCE_COLOR=1`.

## Closeout

Closed 2026-10-21. The public repo was created after the owner freed the name, `main` was pushed at
71 commits (65 imported + planning `34a8c8f`, implementation `657a53d`, evidence `5a35456`, and the
three test fixes `673f368`/`bd53ec2`/`9672d89`), and CI on `9672d89` is green. The annotated tag
`v0.1.0` points at the tested commit `9672d89` (tag object `093d4051`); the tag-triggered run
`39534972375` built and attached both artifacts to the GitHub Release. A fresh clone of the public
repo at `v0.1.0` passes the full gate set, and the tagged tool installs and runs a real 20-output
batch. This closeout commit follows the tag and carries no product change.

`dotfiles-v3` remains at `6ad7117cc982d540d05ec70cecf466393ac1cadc` with a clean tree; the only
change there is the local `split/wallpaper-effects-generator` branch. The remaining S5 work lives in
`dotfiles-v3` (manifest/role/verify pin, `deploy-coverage` shape assertions, in-tree deletion).

### Birth-worktree exception

The scaffold commits were made on `main` in the fresh repo (the slice instruction), as in the
sibling births: `scripts/worktree-guard.sh create` needs a clean `main` to branch from, and the repo
had no scaffold commit yet. Every later item uses a ticket worktree.
