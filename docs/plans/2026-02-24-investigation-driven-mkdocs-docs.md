# Investigation-Driven MkDocs Documentation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Run the investigation framework's full audit + MkDocs synthesis pipeline against the wallpaper-effects-generator monorepo, producing test-evidence-backed documentation as a MkDocs site under `docs/`.

**Architecture:** Two sequential phases. Audit phase (8 iterations) reads the full repo and 566 tests, populates living artifact files under `docs/investigation/audit/`, and terminates when metrics pass. Synthesis phase reads those artifacts and writes a MkDocs site (`mkdocs.yml` + structured `docs/` pages).

**Tech Stack:** Python 3.12, uv workspace, pytest, Typer/Rich CLI, Pydantic, ImageMagick (mocked in tests), investigation-framework state machine.

---

## Before starting

Framework reference: `/home/inumaki/Development/investigation-framework/`
Project root: `/home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator/`

Audit artifacts: `docs/investigation/audit/`
Synthesis artifacts: `docs/investigation/synthesis/`
Final output: `docs/` root (preserving `docs/plans/` and `docs/investigation/`) + `mkdocs.yml` at project root.

Supersedes: `docs/plans/2026-02-24-investigation-driven-diataxis-docs.md` (profile changed from Diátaxis to MkDocs).

---

## Output structure (MkDocs)

```
mkdocs.yml                         ← MkDocs site config + navigation
docs/
├── investigation/                 ← audit artifacts (preserved, not published)
├── plans/                         ← design docs (preserved)
├── index.md                       ← overview + quickstart  [REQUIRED by framework]
├── getting-started.md             ← installation + first effect, step by step
├── reference.md                   ← normalized reference summary  [REQUIRED by framework]
├── cli-reference.md               ← full CLI reference (wallpaper-core + wallpaper-process)
├── configuration.md               ← all config layers, keys, types, defaults, precedence
├── effects-catalog.md             ← all named effects, composites, presets with parameters
├── guides/
│   ├── apply-effect.md
│   ├── batch-processing.md
│   ├── container-mode.md
│   └── configure-output-directory.md
└── concepts/
    ├── architecture.md            ← 4-package design, data flow, dependency graph
    └── layered-config.md          ← rationale and mechanics of layered configuration
```

Framework conformance requirements (MkDocs profile):
- `docs/index.md` must exist
- `docs/reference.md` must exist
- Verification policy satisfied
- No S0 findings reproduced

---

## Task 0: Configure workspace

**Files:**
- Create: `docs/investigation/audit/00_RULES.md`
- Create: `docs/investigation/audit/01_REQUIREMENTS.md`
- Create: `docs/investigation/audit/02_STATE.md`
- Create: `docs/investigation/audit/03_INVENTORY.md`
- Create: `docs/investigation/audit/04_TOPIC_MAP.md`
- Create: `docs/investigation/audit/05_TEST_SPEC.md`
- Create: `docs/investigation/audit/06_DOC_CLAIMS.md`
- Create: `docs/investigation/audit/07_TRACEABILITY.md`
- Create: `docs/investigation/audit/08_FINDINGS.md`
- Create: `docs/investigation/audit/09_UNKNOWNS.md`
- Create: `docs/investigation/audit/10_METRICS.md`
- Create: `docs/investigation/audit/11_NEXT_ACTIONS.md`
- Create: `docs/investigation/audit/iterations/0001_CHECKPOINT.md`
- Create: `docs/investigation/synthesis/00_SYNTHESIS_RULES.md`
- Create: `docs/investigation/synthesis/01_OUTPUT_TARGET.md`
- Create: `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
- Create: `docs/investigation/synthesis/03_DOC_PLAN.md`
- Create: `docs/investigation/synthesis/04_CONFORMANCE.md`
- Create: `docs/investigation/synthesis/05_CHANGELOG.md`
- Create: `docs/investigation/synthesis/iterations/0001_SYNTH_CHECKPOINT.md`

**Step 1: Copy rule files verbatim from framework**

Copy `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
→ `docs/investigation/audit/00_RULES.md` (do not modify).

Copy `/home/inumaki/Development/investigation-framework/synthesis-agent/00_SYNTHESIS_RULES.md`
→ `docs/investigation/synthesis/00_SYNTHESIS_RULES.md` (do not modify).

**Step 2: Write `docs/investigation/audit/01_REQUIREMENTS.md`**

```markdown
# Investigation Requirements

## Repository
- Repo root: /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator
- Primary language/ecosystem: Python 3.12, uv workspace (4 packages)
- Project type: CLI / monorepo

## Scope
- Documentation roots: README.md, DEVELOPMENT.md, CHANGELOG.md, packages/settings/README.md, packages/core/README.md, packages/effects/README.md, packages/orchestrator/README.md, tests/smoke/README.md
- Interfaces of interest: wallpaper-core CLI, wallpaper-process CLI, effects/composites/presets YAML config system, layered settings API

## Tests
- Preferred test command: uv run pytest
- Run from: repo root
- Test categories: unit, integration (smoke tests require ImageMagick — skip with `-m "not smoke"` if unavailable)
- Environment notes: 566 test functions across 4 packages; ImageMagick is mocked for unit/integration tests

## Contracts
- No OpenAPI/proto. Pydantic models in packages/settings/src/, packages/core/src/, packages/effects/src/, packages/orchestrator/src/

## Acceptance thresholds
- S0 must be: 0
- S1 must be: <= 3
- Open Unknowns must be: <= 5
```

**Step 3: Write all other artifact files with blank/init content**

Copy template content exactly from the framework:
- `02_STATE.md` → iteration 0001, phase PHASE_1_INVENTORY
- `03_INVENTORY.md` through `11_NEXT_ACTIONS.md` → blank templates from `/home/inumaki/Development/investigation-framework/audit-agent/`
- `iterations/0001_CHECKPOINT.md` → "Initialized workspace."
- Synthesis files → templates from `/home/inumaki/Development/investigation-framework/synthesis-agent/`

**Step 4: Write `docs/investigation/synthesis/01_OUTPUT_TARGET.md`**

```markdown
# Output Target

OUTPUT_PROFILE = mkdocs
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users
OUTPUT_DIR = ../../  # relative to docs/investigation/synthesis/ → resolves to docs/

Scope:
- Interfaces: wallpaper-core CLI, wallpaper-process CLI, effects/composites/presets config
- Exclusions: internal implementation details, private helpers

Formatting:
- Language: English
- Tone: technical, direct
- Examples runnable: yes
- Include BHV IDs near examples: yes
```

**Step 5: Commit**

```bash
git add docs/investigation/
git commit -m "chore: initialize investigation workspace (mkdocs profile)"
```

---

## Task 1: PHASE_1_INVENTORY

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/03_INVENTORY.md`
- Modify: `docs/investigation/audit/11_NEXT_ACTIONS.md`
- Create: `docs/investigation/audit/iterations/0002_CHECKPOINT.md`

**Step 1: Read mandatory files (in order)**

Read:
1. `docs/investigation/audit/00_RULES.md`
2. `docs/investigation/audit/01_REQUIREMENTS.md`
3. `docs/investigation/audit/02_STATE.md`
4. `docs/investigation/audit/iterations/0001_CHECKPOINT.md`

Confirm current phase is `PHASE_1_INVENTORY`.

**Step 2: Enumerate all files in the repo**

Walk the entire repo root. For each file assign:
- **Type**: `code` | `test` | `config` | `doc` | `example` | `lock` | `binary`
- **Status**: `in-scope` | `ignored` | `binary` | `too-large`

Key paths to catalog (non-exhaustive — walk everything):
```
pyproject.toml                          config   in-scope
uv.lock                                 lock     ignored
Makefile                                config   in-scope
README.md                               doc      in-scope
DEVELOPMENT.md                          doc      in-scope
CHANGELOG.md                            doc      in-scope
settings.toml                           config   in-scope
packages/settings/pyproject.toml        config   in-scope
packages/settings/src/**/*.py           code     in-scope
packages/settings/tests/**/*.py         test     in-scope
packages/core/pyproject.toml            config   in-scope
packages/core/src/**/*.py               code     in-scope
packages/core/tests/**/*.py             test     in-scope
packages/effects/pyproject.toml         config   in-scope
packages/effects/src/**/*.py            code     in-scope
packages/effects/tests/**/*.py          test     in-scope
packages/orchestrator/pyproject.toml    config   in-scope
packages/orchestrator/src/**/*.py       code     in-scope
packages/orchestrator/tests/**/*.py     test     in-scope
tests/smoke/**/*                        test     in-scope
packages/*/README.md                    doc      in-scope
```

Ignore: `__pycache__/`, `.git/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`, `uv.lock`.

**Step 3: Populate `docs/investigation/audit/03_INVENTORY.md`**

Fill the `## Files` table with every discovered file. Classify binaries and lock files as `ignored`. Total count must be deterministic.

**Step 4: Update `docs/investigation/audit/02_STATE.md`**

```markdown
## Iteration
- Current iteration: 0002
- Phase: PHASE_2_TOPIC_MAP

## Progress
Completed:
- PHASE_1_INVENTORY (iteration 0002)

Current focus:
- Build topic-to-file mapping.
```

**Step 5: Append `docs/investigation/audit/iterations/0002_CHECKPOINT.md`**

```markdown
# Checkpoint 0002

- Phase: PHASE_1_INVENTORY → complete
- Files cataloged: N (fill actual count)
- Notable: 4 packages, X test files, Y doc files
```

**Step 6: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-1): complete repo inventory"
```

---

## Task 2: PHASE_2_TOPIC_MAP

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/04_TOPIC_MAP.md`
- Create: `docs/investigation/audit/iterations/0003_CHECKPOINT.md`

**Step 1: Read mandatory files**

Read rules, requirements, current state (expect `PHASE_2_TOPIC_MAP`), latest checkpoint.

**Step 2: Read all in-scope source and doc files**

For each, identify primary topics, secondary topics, and key entities (CLI commands, config keys, effect names, classes, functions).

Suggested topic taxonomy:
- `cli/wallpaper-core` — core CLI commands and flags
- `cli/wallpaper-process` — orchestrator CLI commands and flags
- `effects` — effect definitions, YAML structure
- `composites` — composite effect chains
- `presets` — preset configurations
- `config/layered-settings` — 4-layer config system
- `config/effects-config` — effects-specific config layers
- `output-directory` — output path handling, defaults
- `batch-processing` — batch commands, parallelism
- `dry-run` — dry-run mode
- `container/docker` — Docker/Podman orchestration
- `container/volumes` — volume mount management
- `testing` — test infrastructure, fixtures
- `architecture` — package structure, dependencies

**Step 3: Populate `docs/investigation/audit/04_TOPIC_MAP.md`**

Fill `## File summaries` table and `## Topic index`. Every in-scope file must appear in at least one topic.

**Step 4: Update state → PHASE_3_TEST_SPEC, write checkpoint**

**Step 5: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-2): complete topic map"
```

---

## Task 3: PHASE_3_TEST_SPEC

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/05_TEST_SPEC.md`
- Modify: `docs/investigation/audit/09_UNKNOWNS.md`
- Create: `docs/investigation/audit/iterations/0004_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_3_TEST_SPEC`.

**Step 2: Run tests and record result**

```bash
cd /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator
uv run pytest -v --tb=short 2>&1 | head -100
```

Record in `05_TEST_SPEC.md`:
```markdown
## Test execution
- Test command used: uv run pytest
- Last run result: PASS or FAIL
- Notes: N tests collected, N passed, N failed
```

If smoke tests fail due to missing ImageMagick, rerun with:
```bash
uv run pytest -v --tb=short -m "not smoke"
```

**Step 3: Read all test files**

Read every `tests/**/*.py` and `packages/*/tests/**/*.py`. For each test function, extract the behavior being asserted. Group by behavior, not by test file.

Key test paths:
```
packages/settings/tests/
packages/core/tests/
packages/effects/tests/
packages/orchestrator/tests/
tests/smoke/
```

**Step 4: Assign BHV-XXXX IDs and populate `05_TEST_SPEC.md`**

For each distinct behavior:
```markdown
- BHV-0001:
  - Title: Apply a single named effect to an image
  - Publicity: public
  - Preconditions: ImageMagick installed, valid input image path
  - Steps: Run `wallpaper-core process <image> --effect <name>`
  - Expected: Output image written to ./wallpapers-output/<basename>/effects/<name>.png
  - Errors: FileNotFoundError if image missing; ValueError if effect unknown
  - Evidence: packages/core/tests/test_cli.py::test_apply_effect_creates_output
```

Publicity levels: `public` | `internal` | `deprecated`

Expect 30–60 distinct public behaviors across the 4 packages.

**Step 5: Record unknowns for anything ambiguous**

If a test's intent is unclear, add a `U-XXXX` to `09_UNKNOWNS.md` rather than guessing.

**Step 6: Update state → PHASE_4_BEHAVIOR_CATALOG, write checkpoint**

**Step 7: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-3): complete test spec and behavior catalog"
```

---

## Task 4: PHASE_4_BEHAVIOR_CATALOG

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/05_TEST_SPEC.md` (enrich existing entries)
- Modify: `docs/investigation/audit/09_UNKNOWNS.md`
- Create: `docs/investigation/audit/iterations/0005_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_4_BEHAVIOR_CATALOG`.

**Step 2: Enrich each BHV entry via source code**

Cross-reference each public BHV with implementation files to fill in gaps:
- Exact CLI flag names and defaults (read `packages/core/src/` and `packages/orchestrator/src/`)
- Exact config key names and schema (read Pydantic models in `packages/settings/src/` and `packages/effects/src/`)
- Error messages as they appear in code
- Edge cases in implementation not covered by tests → flag as `U-XXXX`

Do NOT invent — if a behavior has no test evidence, mark it `internal` or add an unknown.

**Step 3: Update state → PHASE_5_DOC_CLAIMS, write checkpoint**

**Step 4: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-4): enrich behavior catalog"
```

---

## Task 5: PHASE_5_DOC_CLAIMS

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/06_DOC_CLAIMS.md`
- Create: `docs/investigation/audit/iterations/0006_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_5_DOC_CLAIMS`.

**Step 2: Read all doc files**

```
README.md
DEVELOPMENT.md
CHANGELOG.md
packages/settings/README.md
packages/core/README.md
packages/effects/README.md
packages/orchestrator/README.md
tests/smoke/README.md
```

**Step 3: Extract atomic claims into `06_DOC_CLAIMS.md`**

For each factual claim, create a `DOC-XXXX` entry. Split compound claims into atomic ones.

```markdown
- DOC-0001:
  - Text: "The default output directory is ./wallpapers-output"
  - Source: README.md:42
  - Category: reference
  - Evidence status: unverified
  - Evidence:
```

Categories: `how-to` | `reference` | `concept` | `contract` | `troubleshooting`

Leave `Evidence status` as `unverified` — filled in PHASE_6.

**Step 4: Update state → PHASE_6_TRACEABILITY, write checkpoint**

**Step 5: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-5): extract documentation claims"
```

---

## Task 6: PHASE_6_TRACEABILITY

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/06_DOC_CLAIMS.md` (update evidence status)
- Modify: `docs/investigation/audit/07_TRACEABILITY.md`
- Create: `docs/investigation/audit/iterations/0007_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_6_TRACEABILITY`.

**Step 2: Build BHV → DOC coverage table**

```markdown
## BHV → Documentation coverage
| Behavior | Covered by DOC claims | Coverage status | Notes |
|----------|-----------------------|-----------------|-------|
| BHV-0001 | DOC-0003, DOC-0017    | covered         |       |
| BHV-0002 | (none)                | gap             | No doc claim mentions this |
```

Coverage status: `covered` | `gap` | `partial`

**Step 3: Build DOC → Evidence table**

```markdown
## DOC → Evidence
| Doc claim | Evidence                                  | Evidence status | Notes |
|-----------|-------------------------------------------|-----------------|-------|
| DOC-0001  | BHV-0007 (test: test_default_output_dir)  | verified        |       |
| DOC-0009  | (none found)                              | contradicted    | Test shows different default |
```

Update `evidence status` in `06_DOC_CLAIMS.md` to match.

**Step 4: Update state → PHASE_7_REVIEW_FINDINGS, write checkpoint**

**Step 5: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-6): complete traceability matrix"
```

---

## Task 7: PHASE_7_REVIEW_FINDINGS

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/08_FINDINGS.md`
- Modify: `docs/investigation/audit/10_METRICS.md`
- Create: `docs/investigation/audit/iterations/0008_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_7_REVIEW_FINDINGS`.

**Step 2: Classify every gap and contradiction**

From the traceability matrix, for each `gap` or `contradicted` entry:

```markdown
## S0 Critical
- S0-0001:
  - Summary: DOC-0009 claims default output dir is X, but BHV-0007 (test evidence) shows Y
  - Location: README.md:42
  - Evidence: packages/core/tests/test_cli.py::test_default_output_dir
  - Proposed fix: Update README to state the correct default

## S1 Major
- S1-0001:
  - Summary: BHV-0023 (batch --presets command) has no documentation coverage
  - Location: (no doc location — gap)
  - Evidence: packages/core/tests/test_batch.py::test_batch_presets
  - Proposed fix: Add guide for batch preset processing
```

Severity:
- S0: Doc claim contradicts test evidence (wrong default, wrong flag, wrong behavior)
- S1: Public BHV with zero doc coverage
- S2: Partial coverage (missing default, missing error case)
- S3: Formatting, typo, low-impact clarity

**Step 3: Update `10_METRICS.md`**

```markdown
## Counts
- S0: N
- S1: N
- S2: N
- S3: N
- Unknowns open: N

## Investigation status
- INVESTIGATION_STATUS = PASS  # if S0=0, S1<=3, unknowns<=5
```

**Step 4: Update state → PHASE_8_FINALIZE_INVESTIGATION, write checkpoint**

**Step 5: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-7): review findings and update metrics"
```

---

## Task 8: PHASE_8_FINALIZE_INVESTIGATION

**Files:**
- Modify: `docs/investigation/audit/02_STATE.md`
- Modify: `docs/investigation/audit/10_METRICS.md`
- Create: `docs/investigation/audit/iterations/0009_CHECKPOINT.md`

**Step 1: Read mandatory files**

Confirm phase is `PHASE_8_FINALIZE_INVESTIGATION`.

**Step 2: Verify acceptance thresholds**

Check `10_METRICS.md`:
- S0 = 0? If not, BLOCKED — return to PHASE_7.
- S1 <= 3? If not, investigate missing coverage.
- Open unknowns <= 5? If not, resolve or accept remaining unknowns.

**Step 3: Set final status**

```markdown
# 10_METRICS.md
- INVESTIGATION_STATUS = PASS

# 02_STATE.md
Phase: INVESTIGATION_COMPLETE
```

**Step 4: Write final checkpoint**

```markdown
# Checkpoint 0009

- INVESTIGATION_STATUS = PASS
- S0: 0, S1: N, S2: N, S3: N, Unknowns: N
- Public BHVs cataloged: N
- DOC claims extracted: N
- Investigation complete. Proceeding to synthesis.
```

**Step 5: Commit**

```bash
git add docs/investigation/audit/
git commit -m "audit(phase-8): finalize investigation — PASS"
```

---

## Task 9: Configure synthesis and build MkDocs doc plan

**Files:**
- Modify: `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
- Modify: `docs/investigation/synthesis/03_DOC_PLAN.md`
- Create: `docs/investigation/synthesis/iterations/0002_SYNTH_CHECKPOINT.md`

**Step 1: Read synthesis mandatory files (in order)**

1. `docs/investigation/synthesis/00_SYNTHESIS_RULES.md`
2. `docs/investigation/synthesis/01_OUTPUT_TARGET.md` — confirm `OUTPUT_PROFILE = mkdocs`
3. `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
4. `docs/investigation/synthesis/iterations/0001_SYNTH_CHECKPOINT.md`
5. MkDocs profile files from `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/mkdocs/`
6. Audit artifacts: `05_TEST_SPEC.md`, `07_TRACEABILITY.md`, `08_FINDINGS.md`, `04_TOPIC_MAP.md`

**Step 2: Build `03_DOC_PLAN.md` — concrete page plan**

Map public BHVs to MkDocs pages. Both `index.md` and `reference.md` are required by the framework.

```markdown
# Documentation Plan (MkDocs profile)

## docs/index.md  [REQUIRED]
Covers: BHV-0001, BHV-0002, BHV-0003
Content: Project overview, what it does, 5-minute quickstart showing install → apply first effect → see output

## docs/getting-started.md
Covers: BHV-0001 through BHV-0006
Content: Full installation guide (host mode and container mode), first-run walkthrough, verification

## docs/reference.md  [REQUIRED]
Covers: all public BHVs (normalized summary form)
Content: Normalized reference index — one-line summaries of all CLI commands, config keys, and effect names with links to detailed pages

## docs/cli-reference.md
Covers: all CLI BHVs (wallpaper-core + wallpaper-process commands)
Content: Every command, subcommand, flag, default, and example

## docs/configuration.md
Covers: config-layer BHVs
Content: All 4 config layers, every key, type, default, and precedence rules

## docs/effects-catalog.md
Covers: effects/composites/presets BHVs
Content: Every named effect, composite chain, and preset with parameters and output

## docs/guides/apply-effect.md
Covers: BHV-00xx
Content: Apply a single named effect to an image

## docs/guides/batch-processing.md
Covers: BHV-00xx
Content: Generate all effects/composites/presets for one image in one command

## docs/guides/container-mode.md
Covers: BHV-00xx
Content: Install Docker image, run effects without local ImageMagick

## docs/guides/configure-output-directory.md
Covers: BHV-00xx
Content: Override the output directory at each config layer

## docs/concepts/architecture.md
Covers: (conceptual — cite topic map, not BHVs)
Content: 4-package structure, data flow, dependency graph

## docs/concepts/layered-config.md
Covers: (conceptual — cite BHV evidence for config merge behavior)
Content: Why layered config, how deep merge works, mental model
```

Coverage check: >= 90% of public BHVs must appear in the plan.

**Step 3: Commit plan**

```bash
git add docs/investigation/synthesis/
git commit -m "synthesis: build MkDocs documentation plan from BHV catalog"
```

---

## Task 10: Synthesis — write MkDocs site

**Files:**
- Create: `mkdocs.yml`
- Create: `docs/index.md`
- Create: `docs/getting-started.md`
- Create: `docs/reference.md`
- Create: `docs/cli-reference.md`
- Create: `docs/configuration.md`
- Create: `docs/effects-catalog.md`
- Create: `docs/guides/apply-effect.md`
- Create: `docs/guides/batch-processing.md`
- Create: `docs/guides/container-mode.md`
- Create: `docs/guides/configure-output-directory.md`
- Create: `docs/concepts/architecture.md`
- Create: `docs/concepts/layered-config.md`
- Modify: `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
- Create: `docs/investigation/synthesis/iterations/0003_SYNTH_CHECKPOINT.md`

**Step 1: Read all audit artifacts before writing**

Read in this order:
1. `docs/investigation/audit/05_TEST_SPEC.md` — all BHV entries
2. `docs/investigation/audit/07_TRACEABILITY.md` — coverage and evidence
3. `docs/investigation/audit/08_FINDINGS.md` — do NOT reproduce S0 claims
4. `docs/investigation/synthesis/03_DOC_PLAN.md` — page-to-BHV mapping

**Step 2: Write `mkdocs.yml`**

```yaml
site_name: Wallpaper Effects Generator
site_description: Apply layered image effects using ImageMagick
docs_dir: docs

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Guides:
    - Apply an Effect: guides/apply-effect.md
    - Batch Processing: guides/batch-processing.md
    - Container Mode: guides/container-mode.md
    - Configure Output Directory: guides/configure-output-directory.md
  - Reference:
    - Reference Overview: reference.md
    - CLI Reference: cli-reference.md
    - Configuration: configuration.md
    - Effects Catalog: effects-catalog.md
  - Concepts:
    - Architecture: concepts/architecture.md
    - Layered Configuration: concepts/layered-config.md

theme:
  name: material
```

**Step 3: Write each doc page**

Rules for every page:
- Every factual statement traceable to a BHV or DOC evidence entry
- Include `<!-- BHV-XXXX -->` citations as HTML comments near examples
- `verified-only` policy: omit any claim that is `unverified` or `contradicted`
- Do not reproduce S0 findings
- All CLI examples use exact flag names from BHV evidence

**`docs/index.md`** (REQUIRED — overview + quickstart per MkDocs mapping rules):
```markdown
# Wallpaper Effects Generator

<project overview>

## Quickstart

<minimal install + first effect, ~5 steps>
```

**`docs/reference.md`** (REQUIRED — normalized reference summary):
```markdown
# Reference

Normalized reference index of all public interfaces.

## CLI Commands
<one-line per command with link to cli-reference.md>

## Configuration Keys
<one-line per key with link to configuration.md>

## Effects
<one-line per effect with link to effects-catalog.md>
```

All other pages follow naturally from the doc plan.

**Step 4: Commit**

```bash
git add mkdocs.yml docs/index.md docs/getting-started.md docs/reference.md \
    docs/cli-reference.md docs/configuration.md docs/effects-catalog.md \
    docs/guides/ docs/concepts/
git commit -m "docs: write MkDocs site from investigation artifacts"
```

---

## Task 11: Synthesis conformance check

**Files:**
- Modify: `docs/investigation/synthesis/04_CONFORMANCE.md`
- Modify: `docs/investigation/synthesis/05_CHANGELOG.md`
- Create: `docs/investigation/synthesis/iterations/0004_SYNTH_CHECKPOINT.md`

**Step 1: Run conformance checks per MkDocs profile**

From `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/mkdocs/03_CONFORMANCE_CHECKS.md`:

```
1. docs/index.md exists?           → check
2. docs/reference.md exists?       → check
3. verified-only policy satisfied?
   No unverified or contradicted claims appear in output docs.
4. No S0 findings reproduced?
   Cross-check 08_FINDINGS.md S0 entries against all doc content.
5. Public BHV coverage >= 90%?
   Count public BHVs in 05_TEST_SPEC.md.
   Count distinct BHV IDs cited across all docs.
   Coverage = cited / total public >= 0.90
```

If any check fails, fix the relevant doc(s) before marking PASS.

**Step 2: Populate `04_CONFORMANCE.md`**

```markdown
# Documentation Conformance

- OUTPUT_PROFILE: mkdocs
- Structure conformance: PASS (index.md ✓, reference.md ✓)
- Coverage conformance (public BHVs): X/Y (N%)
- Policy conformance (verified-only): PASS
- Safety (no S0 reproduction): PASS

SYNTHESIS_STATUS = PASS
```

**Step 3: Write `05_CHANGELOG.md`**

```markdown
# Documentation Change Log

## 2026-02-24
- Initial MkDocs documentation generated via investigation framework
- N public behaviors documented across index, reference, guides, concepts
- Investigation artifacts preserved under docs/investigation/
```

**Step 4: Final commit**

```bash
git add docs/investigation/synthesis/ mkdocs.yml
git commit -m "docs: synthesis conformance PASS — MkDocs site complete"
```

---

## Done

The MkDocs documentation site is complete. All pages under `docs/` are grounded in test evidence via the investigation artifacts in `docs/investigation/`. The site can be previewed with:

```bash
uv run mkdocs serve
```
