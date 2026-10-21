# Design — repo birth

## Decisions

### D1. History comes from `git subtree split`, not a fresh root commit

The in-tree package has 65 commits, including the S3 Dockerfile rewrite to package-relative COPY
paths, the S0b hermetic fixture and the sibling tag pins. A fresh import would lose those "why"
records. `git subtree split -P src/cli-tools/wallpaper-effects-generator` writes a branch whose tree
is the package directory and whose commits are the ones that touched it.

Evidence: `git -C /home/inumaki/Development/dotfiles-v3 rev-list --count
split/wallpaper-effects-generator` → `65`; the split tip is
`810e72baa91beb61de32e4e083cbe8c8d5c3ab14`.
Verify: `git log --oneline | wc -l` in this repo → `65` before the scaffold commit.

### D2. Harness files are copied, not re-authored

AD-12 requires the same `worktree-guard.sh` and the same `skills-lock.json` hashes as `mu`. The
copy set is exactly: `scripts/worktree-guard.sh`, `skills-lock.json`, `_bmad/`, `.agents/skills/`,
`.opencode/`, `tickets/_template/`, `tickets/_fixtures/`, `tickets/LIFECYCLE.md`.
`tickets/INDEX.md` is repo-specific, and `AGENTS.md` is retargeted but keeps the evidence rule
verbatim.

Evidence: `diff` per path against `mu` is empty (ticket evidence table).
Verify: `diff -r /home/inumaki/Development/mu/_bmad _bmad && diff
/home/inumaki/Development/mu/skills-lock.json skills-lock.json`.

### D3. The image builds from this repo root only

The Dockerfile's context is the repo root and it copies only repo-relative paths
(`pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `src/`).
The S3 rewrite already removed every `src/shared`/`src/cli-tools` path; this repo proves it by
building with no monorepo present. The build stage carries `uv==0.9.22`, `git` and CA certificates
because the sibling dependencies are fetched from their tags at build time; determinism comes from
the lock + tag, and an unreachable pin fails the build closed (AD-5).

Evidence: `Dockerfile.imagemagick` lines 6–17; `podman build ... .` → exit 0.
Verify: `rg -n "src/shared|src/cli-tools|\.\./" src/wallpaper_effects_generator/adapters/docker/`
→ exit 1.

### D4. The build verb accepts the pin explicitly

`[container] image_tag` defaults to `latest` in the bundled settings, which is fine for a
developer's local build but wrong for provisioning (AD-7: the pin is the tag). `weg install
--image-tag TAG` overrides the setting per invocation, validates Docker's tag grammar before the
engine is touched, and therefore lets provisioning render `image_tag = v0.1.0` and assert the exact
image. The flag is not `latest` by default; the default remains the settings value.

Evidence: `install.py` validation + `tests/test_cli.py` tag tests.
Verify: `uv run pytest -q tests/test_cli.py -k image_tag` → 2 passed.

### D5. The Makefile's `GATES` is the single gate list; CI is compared to it

The workflow has one job per gate so a failure names the gate, but a hand-maintained job list
drifts. `scripts/ci-gates-parity.py` parses `GATES` from the `Makefile` and the job keys from the
workflow and fails on any unmatched entry in either direction. CI-only jobs (`ci-gates-parity`,
`image`, `release`) are declared with a reason; a stale declaration fails.

Evidence: `make ci-gates-parity` → `PASS gates=[...] jobs=[...] exempt=[...]`.
Verify: `make ci-gates-parity`.

### D6. Hermetic means hermetic, not "green on this host"

AD-8 is implemented in the imported tests (`tests/conftest.py` + `tests/test_hermetic_canary.py`).
The Makefile adds `hermetic`, which runs the suite with `HOME` and all four `XDG_*` roots pointed at
fresh temp dirs; the fixture does the `chdir`. `make gates` includes it.

Evidence: the canary asserts `XDG_CONFIG_HOME` is under the pytest tmp root.
Verify: `make hermetic` → exit 0 with the same count as `make test`.

### D7. `image` is a CI job but not a `make gates` member

A real image build needs an engine and network access to the pinned git tags; making it a gate
would make every local gate run depend on Podman/Docker. It is a first-class verb (`make image`),
runs in CI as a declared CI-only job, and is proven locally in the birth ticket. The parity script
records the exemption, so the gap is explicit rather than silent.

Evidence: `CI_ONLY_EXEMPT` in `scripts/ci-gates-parity.py`; `image` job in the workflow.
Verify: `make ci-gates-parity` → exit 0 with `image` listed as exempt.

## Verification plan

| Decision | Command | Expected |
| --- | --- | --- |
| D1 | `git log --oneline \| wc -l` | `65` imported commits before the scaffold |
| D2 | `diff -r <mu-path> <path>` for each copied path | empty output, exit 0 |
| D3 | `make image` | build exit 0; `0.1.0 contract 0.1.0` from inside the image |
| D4 | `uv run pytest -q tests/test_cli.py -k image_tag` | `2 passed` |
| D5 | `make ci-gates-parity` | `PASS ...`, exit 0 |
| D6 | `make hermetic` | exit 0, same test count as `make test` |
| Packaging | `uv lock --check && uv build` | exit 0; `dist/wallpaper_effects_generator-0.1.0-{whl,tar.gz}` |
| Release | `git ls-remote --tags origin v0.1.0` | exactly one line (tag object) + peeled commit |
