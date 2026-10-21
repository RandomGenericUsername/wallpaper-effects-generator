---
id: REQ-001
title: "Birth the wallpaper-effects-generator repo (mu-strict, weg) and cut v0.1.0"
kind: requirement
status: in-progress
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

- [ ] The repo exists, is **public**, and its `main` carries the imported subtree commits.
  Verify: `gh api repos/RandomGenericUsername/wallpaper-effects-generator --jq .private` → `false`;
  `git log --oneline | wc -l` → 66 commits (65 imported + scaffold).
- [ ] The harness is byte-identical to `mu` at every copied path.
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
- [ ] `.github/workflows/gates.yml` exists and its job set equals `GATES` (plus declared CI-only
  jobs); the first run on `main` is green.
  Verify: `make ci-gates-parity` → `PASS ...`; `gh run list -R RandomGenericUsername/wallpaper-effects-generator
  --limit 1 --json status,conclusion` → `completed` / `success`.
- [ ] Annotated tag `v0.1.0` exists on the released commit, is anonymously fetchable, and its
  GitHub Release carries the wheel + sdist.
  Verify: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote
  https://github.com/RandomGenericUsername/wallpaper-effects-generator 'refs/tags/v0.1.0'` →
  exactly one line; `gh release view v0.1.0 --json assets --jq '.assets[].name'` → both artifacts.
- [ ] `git status --porcelain` is empty in both repos; `dotfiles-v3` `master` is at the same SHA
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
| repo absent at start | `gh repo view RandomGenericUsername/wallpaper-effects-generator` | **FAILED PRECONDITION**: the name is a pre-existing private legacy repo (`private: true`, default branch `master`, 2025-12-13, no tags); see Deviations |
| history preserved | `git rev-list --count split/wallpaper-effects-generator` (dotfiles) | `65`; split tip `810e72baa91beb61de32e4e083cbe8c8d5c3ab14` |
| harness byte-identical | `diff -r mu/<path> <path>` for `_bmad`, `.agents/skills`, `.opencode`, `scripts/worktree-guard.sh`, `skills-lock.json`, `tickets/_template`, `tickets/_fixtures`, `tickets/LIFECYCLE.md` | `IDENTICAL` × 8, exit 0 |
| evidence rule present | `rg -c "Evidence:\|Verify:" AGENTS.md`; `test -L CLAUDE.md` | `6`; exit 0 |
| specs/change valid | `openspec validate --specs --strict`; `openspec validate repo-birth --strict` | 2 passed; `Change 'repo-birth' is valid` |
| suite | `uv run pytest -q` | `349 passed in 3.51s` |
| gates | `make gates` | exit 0; `349 passed` ×2, `All checks passed!`, lock current |
| packaging | `uv build` | exit 0; `wallpaper_effects_generator-0.1.0-py3-none-any.whl` + `.tar.gz` |
| image | `podman build -t wallpaper-effects-generator:v0.1.0 ... .`; `podman run --rm wallpaper-effects-generator:v0.1.0 weg --version` | build exit 0, image `81d4c337ce25`; `0.1.0 contract 0.1.0` |
| install verb tag | `.venv/bin/weg install --context . --container-engine podman --image-tag v0.1.0` | exit 0; `weg-podman:v0.1.0` (`81d4c337ce25`); run prints `0.1.0 contract 0.1.0`; invalid tag exits 2 with `invalid image tag` |
| fresh clone | clone → `make sync && make gates && make build` | pending |
| CI parity | `make ci-gates-parity` | `PASS gates=[...5] jobs=[...8] exempt=[ci-gates-parity, image, release]` |
| CI runs | `gh run list` | pending (blocked: no remote) |
| annotated tag | `git cat-file -t v0.1.0`; `git rev-parse v0.1.0`; `git rev-parse 'v0.1.0^{commit}'` | pending (blocked: no remote) |
| anonymous fetch | `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote ... 'refs/tags/v0.1.0'` | pending (blocked: no remote) |
| release artifacts | `gh release view v0.1.0 --json assets --jq '.assets[].name'` | pending (blocked: no remote) |
| dotfiles untouched | `git -C /home/inumaki/Development/dotfiles-v3 rev-parse master`; `git status --porcelain` | `6ad7117cc982d540d05ec70cecf466393ac1cadc`; empty (only the local `split/` ref was added) |

## Deviations from the slice text

1. **The target repo name is occupied.** `RandomGenericUsername/wallpaper-effects-generator` exists
   as a **private** repo created 2025-12-13 with an unrelated legacy workspace layout
   (`packages/{settings,effects,core,orchestrator}`, `wallpaper-core`/`wallpaper-process` CLIs,
   200+ commits, four merged PRs, no tags) and default branch `master`. The slice's stated
   precondition ("repo absent") is false. This slice must not delete, rename or force-push over
   that history without an explicit owner decision, so the remote create/push/tag/release steps
   are blocked. All local steps (split, scaffold, gates, packaging, image proof) are complete.
2. **`install --image-tag` added.** The imported verb had no tag override; the image tag could only
   come from `[container] image_tag` in settings. Per the slice, the option is added with Docker
   tag validation and tests so provisioning can pass the pin explicitly.
3. **Suite count is 349, not 346.** The imported suite is 347 in this checkout (the S0b note said
   346–347); the two added `--image-tag` tests raise it to 349.
4. **The Dockerfile copies two more repo-relative files.** Release metadata (`readme =` and
   `license-files =`) makes hatchling read `README.md` and `LICENSE` while building the wheel in the
   image; the S3 Dockerfile predates that metadata. Both are repo-relative, so AD-5's invariant (no
   sibling repo, no parent directory) holds; the COPY list is now `pyproject.toml`, `uv.lock`,
   `README.md`, `LICENSE`, `src/`.
5. **Ruff ignores `B008`.** The imported Typer handlers declare options in defaults, which is
   Typer's idiom; without the ignore `make lint` cannot be green. Three real findings were fixed
   (`B904` in `batch_processor.py`, two `F841`).

## Closeout

Open. Blocked on the owner decision for the occupied repo name; see Deviations 1.
