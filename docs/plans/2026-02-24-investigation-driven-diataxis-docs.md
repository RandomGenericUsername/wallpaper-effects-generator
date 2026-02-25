# Investigation-Driven Diátaxis Documentation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Run the investigation framework's full audit + Diátaxis synthesis pipeline against the wallpaper-effects-generator monorepo, producing test-evidence-backed documentation in `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, and `docs/explanation/`.

**Architecture:** Two sequential phases. Audit phase (8 iterations) reads the full repo and 566 tests, populates living artifact files under `docs/investigation/audit/`, and terminates when metrics pass. Synthesis phase reads those artifacts and writes Diátaxis docs directly into `docs/`.

**Tech Stack:** Python 3.12, uv workspace, pytest, Typer/Rich CLI, Pydantic, ImageMagick (mocked in tests), investigation-framework state machine.

---

## Before starting

Framework reference: `/home/inumaki/Development/investigation-framework/`
Project root: `/home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator/`

All artifact files live under `docs/investigation/`. The audit artifact directory is `docs/investigation/audit/`. The synthesis artifact directory is `docs/investigation/synthesis/`. Final docs go into `docs/` root (replacing existing content, except `docs/plans/` and `docs/investigation/`).

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

Copy `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md` → `docs/investigation/audit/00_RULES.md` (do not modify).

Copy `/home/inumaki/Development/investigation-framework/synthesis-agent/00_SYNTHESIS_RULES.md` → `docs/investigation/synthesis/00_SYNTHESIS_RULES.md` (do not modify).

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

Copy the template content exactly from the framework for each file:
- `02_STATE.md` → start at iteration 0001, PHASE_1_INVENTORY
- `03_INVENTORY.md` through `11_NEXT_ACTIONS.md` → copy blank templates from `/home/inumaki/Development/investigation-framework/audit-agent/`
- `iterations/0001_CHECKPOINT.md` → "Initialized workspace."
- Synthesis files → copy templates from `/home/inumaki/Development/investigation-framework/synthesis-agent/`

**Step 4: Write `docs/investigation/synthesis/01_OUTPUT_TARGET.md`**

```markdown
# Output Target

OUTPUT_PROFILE = diataxis
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
git commit -m "chore: initialize investigation workspace"
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

Walk the entire repo root. For each file, assign:
- **Type**: `code` | `test` | `config` | `doc` | `example` | `lock` | `binary`
- **Status**: `in-scope` | `ignored` | `binary` | `too-large`

Key paths to catalog (non-exhaustive, walk everything):
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
packages/*/CHANGELOG.md                 doc      in-scope (if present)
packages/*/effects.yaml (or .toml)      config   in-scope
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

Read every file marked `in-scope` in `03_INVENTORY.md`. For each, identify:
- **Primary topics**: What this file is mainly about
- **Secondary topics**: What it references
- **Key entities**: Classes, functions, CLI commands, config keys, effect names

Suggested topic taxonomy for this project:
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

Read every `tests/**/*.py` and `packages/*/tests/**/*.py` file. For each test function, extract the behavior being asserted. Group by behavior, not by test file.

Key test paths to read:
```
packages/settings/tests/
packages/core/tests/
packages/effects/tests/
packages/orchestrator/tests/
tests/smoke/
```

**Step 4: Assign BHV-XXXX IDs and populate `05_TEST_SPEC.md`**

For each distinct behavior, create an entry. Required fields:
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

Publicity levels:
- `public` — user-facing CLI commands, config keys, effect names
- `internal` — helper functions, private methods
- `deprecated` — old behavior still tested

Aim to extract at least one BHV per test file. Expect 30–60 distinct public behaviors.

**Step 5: Record unknowns for anything ambiguous**

If a test's intent is unclear, add a `U-XXXX` entry to `09_UNKNOWNS.md` rather than guessing.

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

**Step 2: Enrich each BHV entry**

Re-read each public BHV from `05_TEST_SPEC.md`. Cross-reference with source code (read actual implementation files) to fill in any gaps:

- Exact CLI flag names and default values (read `packages/core/src/` and `packages/orchestrator/src/`)
- Exact config key names and schema (read Pydantic models in `packages/settings/src/` and `packages/effects/src/`)
- Error messages as they appear in code
- Edge cases visible in implementation but not in tests → flag as `U-XXXX` if unverified by test

Read these files specifically to enrich behaviors:
```
packages/core/src/wallpaper_core/cli.py (or equivalent)
packages/orchestrator/src/wallpaper_orchestrator/cli.py
packages/settings/src/layered_settings/
packages/effects/src/wallpaper_effects/
```

Do NOT invent — if a behavior is only in code but has no test evidence, mark it `internal` or add an unknown.

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

For each factual claim in the docs, create a `DOC-XXXX` entry. Split compound claims into atomic ones.

```markdown
- DOC-0001:
  - Text: "The default output directory is ./wallpapers-output"
  - Source: README.md:42
  - Category: reference
  - Evidence status: unverified
  - Evidence:
```

Categories:
- `how-to` — step-by-step instructions
- `reference` — flags, config keys, defaults, effect names
- `concept` — explanations of how/why something works
- `contract` — guaranteed behavior (error codes, schema)
- `troubleshooting` — problem/solution pairs

Leave `Evidence status` as `unverified` — that gets filled in PHASE_6.

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

In `07_TRACEABILITY.md`, populate the first table:

```markdown
## BHV → Documentation coverage
| Behavior | Covered by DOC claims | Coverage status | Notes |
|----------|-----------------------|-----------------|-------|
| BHV-0001 | DOC-0003, DOC-0017 | covered | |
| BHV-0002 | (none) | gap | No doc claim mentions this |
```

Coverage status: `covered` | `gap` | `partial`

**Step 3: Build DOC → Evidence table**

For each DOC claim, find its evidence in the BHV catalog or code:

```markdown
## DOC → Evidence
| Doc claim | Evidence | Evidence status | Notes |
|-----------|----------|-----------------|-------|
| DOC-0001 | BHV-0007 (test: test_default_output_dir) | verified | |
| DOC-0009 | (none found) | contradicted | Test shows different default |
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

From the traceability matrix, for each `gap` or `contradicted` entry, create a finding:

```markdown
## S0 Critical
- S0-0001:
  - Summary: DOC-0009 claims default output dir is X, but BHV-0007 (test evidence) shows Y
  - Location: README.md:42
  - Evidence: packages/core/tests/test_cli.py::test_default_output_dir
  - Proposed fix: Update README.md to state the correct default

## S1 Major
- S1-0001:
  - Summary: BHV-0023 (batch --presets command) has no documentation coverage
  - Location: (no doc location — gap)
  - Evidence: packages/core/tests/test_batch.py::test_batch_presets
  - Proposed fix: Add how-to guide for batch preset processing
```

Severity guide:
- S0: Doc claim actively contradicts test evidence (wrong default, wrong flag name, wrong behavior)
- S1: Public BHV with no doc coverage at all
- S2: Partial coverage (flag documented but default missing, missing error case)
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

If thresholds not met, document blockers in `11_NEXT_ACTIONS.md` and re-investigate (return to appropriate phase). This plan assumes thresholds are met on first pass.

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
- S1 <= 3? If not, BLOCKED — investigate missing coverage.
- Open unknowns <= 5? If not, resolve or accept remaining unknowns.

**Step 3: Set final status**

Update `10_METRICS.md`:
```markdown
- INVESTIGATION_STATUS = PASS
```

Update `02_STATE.md`:
```markdown
## Phase: INVESTIGATION_COMPLETE
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

## Task 9: Configure and initialize synthesis

**Files:**
- Modify: `docs/investigation/synthesis/01_OUTPUT_TARGET.md` (verify correct)
- Modify: `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
- Modify: `docs/investigation/synthesis/03_DOC_PLAN.md`
- Create: `docs/investigation/synthesis/iterations/0002_SYNTH_CHECKPOINT.md`

**Step 1: Read synthesis mandatory files (in order)**

1. `docs/investigation/synthesis/00_SYNTHESIS_RULES.md`
2. `docs/investigation/synthesis/01_OUTPUT_TARGET.md`
3. `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
4. `docs/investigation/synthesis/iterations/0001_SYNTH_CHECKPOINT.md`
5. Profile files from `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/`
6. Audit artifacts: `05_TEST_SPEC.md`, `07_TRACEABILITY.md`, `08_FINDINGS.md`, `04_TOPIC_MAP.md`

**Step 2: Build `03_DOC_PLAN.md` — concrete page plan**

Map public BHVs to Diátaxis categories and assign to concrete pages:

```markdown
# Documentation Plan

## tutorials/getting-started.md
Covers: BHV-0001, BHV-0002, BHV-0003
Purpose: First-run experience — install, apply first effect, see output

## how-to/apply-an-effect.md
Covers: BHV-0004, BHV-0005, BHV-0006
Purpose: Apply a named effect or composite to an image

## how-to/run-batch-processing.md
Covers: BHV-0010, BHV-0011, BHV-0012
Purpose: Generate all effects/composites/presets for an image in one command

## how-to/use-container-mode.md
Covers: BHV-0020, BHV-0021, BHV-0022
Purpose: Install and use the Docker/Podman container instead of local ImageMagick

## how-to/configure-output-directory.md
Covers: BHV-0015, BHV-0016
Purpose: Override the default output directory at each config layer

## reference/cli.md
Covers: all public BHVs with CLI surface
Purpose: All commands, subcommands, flags, defaults

## reference/effects-catalog.md
Covers: BHV-0030+
Purpose: Every named effect, composite, and preset with parameters

## reference/configuration.md
Covers: BHV-0040+
Purpose: All config layers, keys, types, defaults, precedence

## explanation/architecture.md
Covers: (no BHV — conceptual)
Purpose: 4-package structure, data flow, dependency graph

## explanation/layered-config.md
Covers: (no BHV — conceptual)
Purpose: Why layered config, how deep merge works, mental model
```

Coverage check: >= 90% of public BHVs must appear in the plan.

**Step 3: Commit plan**

```bash
git add docs/investigation/synthesis/
git commit -m "synthesis: build documentation plan from BHV catalog"
```

---

## Task 10: Synthesis — write Diátaxis docs

**Files:**
- Create: `docs/tutorials/getting-started.md`
- Create: `docs/how-to/apply-an-effect.md`
- Create: `docs/how-to/run-batch-processing.md`
- Create: `docs/how-to/use-container-mode.md`
- Create: `docs/how-to/configure-output-directory.md`
- Create: `docs/reference/cli.md`
- Create: `docs/reference/effects-catalog.md`
- Create: `docs/reference/configuration.md`
- Create: `docs/explanation/architecture.md`
- Create: `docs/explanation/layered-config.md`
- Modify: `docs/investigation/synthesis/02_SYNTHESIS_STATE.md`
- Create: `docs/investigation/synthesis/iterations/0003_SYNTH_CHECKPOINT.md`

**Step 1: Read all audit artifacts before writing**

Read (in this order):
1. `docs/investigation/audit/05_TEST_SPEC.md` — all BHV entries
2. `docs/investigation/audit/07_TRACEABILITY.md` — coverage and evidence
3. `docs/investigation/audit/08_FINDINGS.md` — S0–S3 issues (do NOT reproduce S0 claims)
4. `docs/investigation/synthesis/03_DOC_PLAN.md` — page-to-BHV mapping

**Step 2: Write each doc using its Diátaxis template**

Use the templates from `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/templates/`.

Rules for every doc:
- Every factual statement must be traceable to a BHV or DOC evidence entry
- Include `(BHV-XXXX)` citations near examples
- Use `verified-only` policy: omit any claim that is `unverified` or `contradicted`
- Do not reproduce S0 findings (contradicted claims from docs)
- All CLI examples must use exact flag names from BHV evidence

**tutorials/getting-started.md** template:
```markdown
# Tutorial: Getting Started with Wallpaper Effects Generator

## Goal
## Prerequisites
## Steps
## Verification (BHV IDs)
```

**how-to/*.md** template:
```markdown
# How-to: <Task>

## Prerequisites
## Steps
## Verification (BHV IDs)
```

**reference/*.md** template:
```markdown
# Reference: <Topic>

## CLI / Config / Effects (as appropriate)
## Verification
```

**explanation/*.md** template:
```markdown
# <Concept>

## Concepts
## Mental model
## Rationale
```

**Step 3: Remove old root-level docs (excluding plans/ and investigation/)**

Only remove files that are being superseded by the Diátaxis structure. Do NOT remove:
- `docs/plans/`
- `docs/investigation/`
- `README.md` (project root — keep as brief entry point pointing to docs/)
- `DEVELOPMENT.md` (developer guide — keep)
- `CHANGELOG.md` (keep)

**Step 4: Commit**

```bash
git add docs/tutorials/ docs/how-to/ docs/reference/ docs/explanation/
git commit -m "docs: write Diátaxis documentation from investigation artifacts"
```

---

## Task 11: Synthesis conformance check

**Files:**
- Modify: `docs/investigation/synthesis/04_CONFORMANCE.md`
- Modify: `docs/investigation/synthesis/05_CHANGELOG.md`
- Create: `docs/investigation/synthesis/iterations/0004_SYNTH_CHECKPOINT.md`

**Step 1: Run conformance checks per Diátaxis profile**

From `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/03_CONFORMANCE_CHECKS.md`:

```
1. All four dirs exist with >= 1 file?
   - docs/tutorials/ → check
   - docs/how-to/ → check
   - docs/reference/ → check
   - docs/explanation/ → check

2. Public BHV coverage >= 90%?
   Count public BHVs in 05_TEST_SPEC.md.
   Count distinct BHV IDs cited across all docs.
   Coverage = cited / total public >= 0.90

3. verified-only policy satisfied?
   No unverified or contradicted claims appear in output.

4. No S0 findings reproduced?
   Cross-check 08_FINDINGS.md S0 entries against doc content.
```

**Step 2: Populate `04_CONFORMANCE.md`**

```markdown
# Documentation Conformance

- OUTPUT_PROFILE: diataxis
- Structure conformance: PASS
- Coverage conformance (public BHVs): X/Y (N%)
- Policy conformance: PASS
- Safety (no S0 reproduction): PASS

SYNTHESIS_STATUS = PASS
```

If any check fails, fix the relevant doc(s) before marking PASS.

**Step 3: Write `05_CHANGELOG.md`**

```markdown
# Documentation Change Log

## 2026-02-24
- Initial Diátaxis documentation generated via investigation framework
- N public behaviors documented across tutorials, how-to, reference, explanation
- Investigation artifacts preserved under docs/investigation/
```

**Step 4: Final commit**

```bash
git add docs/investigation/synthesis/
git commit -m "docs: synthesis conformance PASS — Diátaxis docs complete"
```

---

## Done

The Diátaxis documentation is complete. All docs under `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, and `docs/explanation/` are grounded in test evidence via the investigation artifacts in `docs/investigation/`.
