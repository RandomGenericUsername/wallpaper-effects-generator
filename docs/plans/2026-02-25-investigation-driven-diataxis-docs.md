# Investigation-Driven Diátaxis Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Produce Diátaxis documentation for `wallpaper-effects-generator` grounded entirely in behaviors extracted from the test suite, with every documented claim traceable to a test, contract, or code location.

**Architecture:** Two-phase AI agent pipeline following the instructions at `/home/inumaki/Development/investigation-framework/`. Phase 1 (audit agent) runs 8 sequential investigation phases, cataloguing behaviors as `BHV-XXXX` IDs from ~43 test files across 4 packages, then identifying gaps in existing docs. Phase 2 (synthesis agent) reads the audit artifacts and writes Diátaxis pages into `docs/` (tutorials/, how-to/, reference/, explanation/). All state lives in `docs/investigation/` in this repository and is committed alongside the output docs.

**Tech Stack:** Python monorepo (packages: settings, core, effects, orchestrator), pytest, ImageMagick, Docker/Podman. Investigation framework: AI agent state machine with pluggable output profiles.

**Framework reference:**
- Audit rules: `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
- Synthesis rules: `/home/inumaki/Development/investigation-framework/synthesis-agent/00_SYNTHESIS_RULES.md`
- Diátaxis profile: `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/`

---

## Pre-flight: Framework artifact templates

The framework's artifact files are the authoritative templates. Before any task, familiarise yourself with their format by reading:
- `audit-agent/03_INVENTORY.md` through `audit-agent/11_NEXT_ACTIONS.md`
- `synthesis-agent/00_SYNTHESIS_RULES.md` and `synthesis-agent/01_OUTPUT_TARGET.md`

These templates define the exact schema each artifact must follow.

---

### Task 1: Set up investigation state in docs/investigation/

**Files:**
- Create: `docs/investigation/00_REQUIREMENTS.md`
- Create: `docs/investigation/01_STATE.md`
- Create: `docs/investigation/02_SYNTHESIS_STATE.md`
- Create: `docs/investigation/03_INVENTORY.md` (blank template)
- Create: `docs/investigation/04_TOPIC_MAP.md` (blank template)
- Create: `docs/investigation/05_TEST_SPEC.md` (blank template)
- Create: `docs/investigation/06_DOC_CLAIMS.md` (blank template)
- Create: `docs/investigation/07_TRACEABILITY.md` (blank template)
- Create: `docs/investigation/08_FINDINGS.md` (blank template)
- Create: `docs/investigation/09_UNKNOWNS.md` (blank template)
- Create: `docs/investigation/10_METRICS.md` (blank template)
- Create: `docs/investigation/11_NEXT_ACTIONS.md` (blank template)

**Step 1: Write docs/investigation/00_REQUIREMENTS.md**

Copy the schema from `audit-agent/01_REQUIREMENTS.md` in the framework, then fill in:

```markdown
# Investigation Requirements

REPO_ROOT = /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator
REPO_LANGUAGE = Python
REPO_TYPE = CLI tool / monorepo (4 packages)

DOCS_ROOTS =
  - README.md
  - DEVELOPMENT.md
  - packages/settings/README.md
  - packages/core/README.md
  - packages/effects/README.md
  - packages/orchestrator/README.md

INTERFACES =
  - packages/core/src (wallpaper-core CLI, public API)
  - packages/orchestrator/src (wallpaper-process CLI, public API)
  - packages/effects/src (effect/composite/preset definitions, public config)
  - packages/settings/src (settings API, used by other packages)

TEST_COMMAND = python -m pytest
TEST_CATEGORIES = unit, integration, smoke
TEST_ROOT = packages/

CONTRACTS = (none — no OpenAPI or JSON Schema files)

ACCEPTANCE_THRESHOLDS:
  S0 = 0
  S1 <= 3
  OPEN_UNKNOWNS <= 5

OUTPUT_PROFILE = diataxis
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users, contributors
OUTPUT_DIR = docs/
```

**Step 2: Write docs/investigation/01_STATE.md**

```markdown
# Audit State

ITERATION = 0001
PHASE = PHASE_1_INVENTORY
S0_COUNT = 0
S1_COUNT = 0
S2_COUNT = 0
S3_COUNT = 0
UNKNOWNS_OPEN = 0
INVESTIGATION_STATUS = RUNNING
LAST_CHECKPOINT = (none)
```

**Step 3: Write docs/investigation/02_SYNTHESIS_STATE.md**

```markdown
# Synthesis State

ITERATION = 0001
STATUS = NOT_STARTED
BLOCKING_REASONS = (none)
LAST_CHECKPOINT = (none)
```

**Step 4: Initialise blank artifact files**

Copy the template scaffolding from each of the framework's corresponding files (`audit-agent/03_INVENTORY.md` through `audit-agent/11_NEXT_ACTIONS.md`) into `docs/investigation/03_INVENTORY.md` through `docs/investigation/11_NEXT_ACTIONS.md`. Keep only the headers and column definitions — no content rows.

**Step 5: Verify**

- `docs/investigation/00_REQUIREMENTS.md` contains correct REPO_ROOT and OUTPUT_DIR
- `docs/investigation/01_STATE.md` shows `PHASE = PHASE_1_INVENTORY` and `ITERATION = 0001`
- All 9 artifact files exist with template headers only

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "chore: initialise investigation state for Diataxis docs"
```

---

### Task 2: Audit Phase 1 — INVENTORY

**Files:**
- Read: all files in `packages/`, `tests/` (if any at root), `README.md`, `DEVELOPMENT.md`
- Write: `docs/investigation/03_INVENTORY.md`
- Write: `docs/investigation/01_STATE.md` (advance phase)
- Write: `docs/investigation/iterations/0001_PHASE1_CHECKPOINT.md`

**Context:** This phase accounts for every file in the repository. Each file gets a row in the inventory with its scope status. Ignore patterns: `node_modules/`, `dist/`, `build/`, `.coverage*`, `.pytest_cache/`, `.mypy_cache/`, `__pycache__/`, `.venv/`, `venv/`, `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.webp`, `*.pdf`, `*.zip`, `*.tar`, `*.gz`, `docs/generated/`, `site/`.

**Step 1: Read framework rules first**

Read in order:
1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/00_REQUIREMENTS.md`
3. `docs/investigation/01_STATE.md`

**Step 2: Walk the repository tree**

Walk `wallpaper-effects-generator/` recursively. For every file not matching ignore patterns, produce a row:

```
| Path (relative) | Type | Status | Role/Notes |
|---|---|---|---|
| packages/settings/src/settings/__init__.py | Python | in-scope | Settings package entrypoint |
| packages/settings/tests/unit/test_config.py | Python test | in-scope | Unit tests for config layer |
| packages/core/README.md | Docs | in-scope | Package user documentation |
| .github/workflows/ci.yml | CI config | in-scope | CI pipeline definition |
| pyproject.toml | Config | in-scope | Root project config |
```

Account for every file. Use status `ignored` for files matching ignore patterns.

**Step 3: Update STATE.md**

```markdown
ITERATION = 0001
PHASE = PHASE_2_TOPIC_MAP
INVESTIGATION_STATUS = RUNNING
LAST_CHECKPOINT = 0001_PHASE1_CHECKPOINT
```

**Step 4: Write checkpoint**

Create `docs/investigation/iterations/0001_PHASE1_CHECKPOINT.md`:
```markdown
# Checkpoint: Phase 1 — INVENTORY

Iteration: 0001
Files inventoried: [N]
In-scope: [N]
Ignored: [N]
Unknowns: [N] (list any files whose purpose is unclear)
Next: PHASE_2_TOPIC_MAP
```

**Step 5: Verify**

- `03_INVENTORY.md` has rows for all Python source files in all 4 packages
- `03_INVENTORY.md` has rows for all test files under `packages/*/tests/`
- No Python `.py` file is missing
- `01_STATE.md` shows `PHASE = PHASE_2_TOPIC_MAP`

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase1): complete file inventory"
```

---

### Task 3: Audit Phase 2 — TOPIC_MAP

**Files:**
- Read: `docs/investigation/03_INVENTORY.md` + all in-scope files (scan, not full read)
- Write: `docs/investigation/04_TOPIC_MAP.md`
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE2_CHECKPOINT.md`

**Context:** Map which files cover which topics. Topics for this project will include at minimum: `configuration`, `effects`, `composites`, `presets`, `CLI`, `batch-processing`, `container-execution`, `host-execution`, `settings-precedence`, `development-workflow`, `testing`, `CI`.

**Step 1: Read framework rules and state**

Read in order:
1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/00_REQUIREMENTS.md`
3. `docs/investigation/01_STATE.md`
4. `docs/investigation/03_INVENTORY.md`

**Step 2: Scan in-scope files and assign topics**

For each in-scope file, record its primary and secondary topics:

```markdown
## File summaries

| File | Primary topics | Secondary topics | Key entities |
|---|---|---|---|
| packages/settings/src/settings/config.py | configuration, settings-precedence | TOML, YAML | LayeredConfig, load_settings() |
| packages/core/src/core/cli.py | CLI, host-execution | batch-processing | wallpaper-core, ImageMagick |
| packages/effects/src/effects/loader.py | effects, composites, presets | YAML | load_effects(), EffectDefinition |
| packages/orchestrator/src/orchestrator/cli.py | CLI, container-execution | Docker, Podman | wallpaper-process |

## Topic index

| Topic | Files |
|---|---|
| configuration | packages/settings/..., packages/core/..., packages/effects/... |
| CLI | packages/core/src/core/cli.py, packages/orchestrator/src/orchestrator/cli.py |
| effects | packages/effects/... |
```

**Step 3: Update STATE.md**

```
PHASE = PHASE_3_TEST_SPEC
LAST_CHECKPOINT = 0001_PHASE2_CHECKPOINT
```

**Step 4: Write checkpoint**

```markdown
# Checkpoint: Phase 2 — TOPIC_MAP
Topics identified: [N]
Files mapped: [N]
Next: PHASE_3_TEST_SPEC
```

**Step 5: Verify**

- `04_TOPIC_MAP.md` has a row for every in-scope Python file
- Topic index lists at least 8 distinct topics
- `01_STATE.md` shows `PHASE = PHASE_3_TEST_SPEC`

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase2): complete topic map"
```

---

### Task 4: Audit Phase 3 — TEST_SPEC (behavior extraction)

**Files:**
- Read: all test files under `packages/*/tests/`
- Write: `docs/investigation/05_TEST_SPEC.md`
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE3_CHECKPOINT.md`

**Context:** This is the most critical phase. Every test case becomes a `BHV-XXXX` behavior entry. Evidence hierarchy: tests > contracts > code > docs. Read every test file carefully.

The 4 packages have tests at these locations (verify exact paths from inventory):
- `packages/settings/tests/`
- `packages/core/tests/`
- `packages/effects/tests/`
- `packages/orchestrator/tests/`

**Step 1: Read framework rules and state**

Read in order:
1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/00_REQUIREMENTS.md`
3. `docs/investigation/01_STATE.md`
4. `/home/inumaki/Development/investigation-framework/audit-agent/05_TEST_SPEC.md` (for exact schema)

**Step 2: Read every test file in each package**

For every test function (`def test_*` or method in test class), create a BHV entry:

```markdown
## BHV-0001

**Title:** Settings file merges TOML project config over package defaults
**Publicity:** public
**Package:** settings
**Preconditions:** A package-level `defaults.toml` exists; a project-level `config.toml` exists
**Steps:**
  1. Load settings with `load_settings(project_config="config.toml")`
**Expected output:** Project config values override package defaults; missing keys fall back to defaults
**Errors/edge cases:** Missing project config file → uses package defaults only
**Evidence:** `packages/settings/tests/unit/test_config.py::test_project_overrides_defaults` (line N)
```

Assign sequential BHV IDs: BHV-0001, BHV-0002, ...

Classify each behavior:
- `public` — part of the user-facing CLI or package API
- `internal` — implementation detail, not part of public contract
- `deprecated` — marked for removal

**Step 3: Note any unknown behaviors**

If a test's purpose is unclear, add to `docs/investigation/09_UNKNOWNS.md`:
```markdown
## U-0001
Question: What does `test_foo_edge_case` test exactly? The assertion is unclear.
Status: open
Opened: iteration 0001
```

**Step 4: Update STATE.md**

```
PHASE = PHASE_4_BEHAVIOR_CATALOG
UNKNOWNS_OPEN = [N]
LAST_CHECKPOINT = 0001_PHASE3_CHECKPOINT
```

**Step 5: Write checkpoint**

```markdown
# Checkpoint: Phase 3 — TEST_SPEC
Behaviors extracted: [N]
Public: [N]
Internal: [N]
Unknowns opened: [N]
Test files read: [N]
Next: PHASE_4_BEHAVIOR_CATALOG
```

**Step 6: Verify**

- `05_TEST_SPEC.md` has a BHV entry for every test function found across all 4 packages
- Every BHV entry has: Title, Publicity, Evidence (with file + line)
- No test function is unaccounted for
- `01_STATE.md` shows `PHASE = PHASE_4_BEHAVIOR_CATALOG`

**Step 7: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase3): extract behavior catalog from test suite"
```

---

### Task 5: Audit Phase 4 — BEHAVIOR_CATALOG (classify and verify)

**Files:**
- Read: `docs/investigation/05_TEST_SPEC.md` + source files for unclear behaviors
- Write: `docs/investigation/05_TEST_SPEC.md` (update publicity classifications)
- Write: `docs/investigation/09_UNKNOWNS.md` (resolve any unknowns from phase 3)
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE4_CHECKPOINT.md`

**Context:** Review every behavior from TEST_SPEC. Cross-check publicity classification against the actual source code (not just the test). An `internal` behavior tested via a public API should be reclassified. Resolve phase-3 unknowns by reading the relevant source.

**Step 1: Read framework rules and state**

1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/01_STATE.md`
3. `docs/investigation/05_TEST_SPEC.md`
4. `docs/investigation/09_UNKNOWNS.md`

**Step 2: Review each BHV classification**

For each `BHV-XXXX` entry:
- Read the corresponding test and source function
- Confirm `public` / `internal` / `deprecated` is correct
- Correct any misclassifications in place
- If still unclear → update `09_UNKNOWNS.md` entry, mark `status: blocked`

**Step 3: Update STATE.md**

```
PHASE = PHASE_5_DOC_CLAIMS
UNKNOWNS_OPEN = [N]  # update after resolving
LAST_CHECKPOINT = 0001_PHASE4_CHECKPOINT
```

**Step 4: Write checkpoint**

```markdown
# Checkpoint: Phase 4 — BEHAVIOR_CATALOG
Behaviors reviewed: [N]
Reclassified: [N]
Unknowns resolved: [N]
Unknowns remaining: [N]
Next: PHASE_5_DOC_CLAIMS
```

**Step 5: Verify**

- Every BHV has a confirmed publicity classification
- All phase-3 unknowns are either resolved or escalated with a clear question
- `01_STATE.md` shows `PHASE = PHASE_5_DOC_CLAIMS`

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase4): classify and verify behavior catalog"
```

---

### Task 6: Audit Phase 5 — DOC_CLAIMS (analyze existing documentation)

**Files:**
- Read: `README.md`, `DEVELOPMENT.md`, `packages/*/README.md`
- Write: `docs/investigation/06_DOC_CLAIMS.md`
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE5_CHECKPOINT.md`

**Context:** Every atomic claim in the existing documentation becomes a `DOC-XXXX` entry. Atomic means one factual assertion per entry. Evidence status: `verified` (claim matches test/code), `unverified` (no evidence found), `contradicted` (evidence contradicts claim).

**Step 1: Read framework rules and existing docs**

1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/01_STATE.md`
3. `/home/inumaki/Development/investigation-framework/audit-agent/06_DOC_CLAIMS.md` (for exact schema)
4. All doc files listed in `00_REQUIREMENTS.md`

**Step 2: Extract claims from each doc file**

For every factual sentence in the documentation, create a DOC entry:

```markdown
## DOC-0001

**Text:** "The wallpaper-core CLI accepts a --dry-run flag that previews commands without executing them."
**Source:** `README.md:45-46`
**Category:** reference
**Evidence status:** verified
**Evidence pointers:** BHV-0012 (`packages/core/tests/test_cli.py::test_dry_run_flag`)
```

Categories: `how-to`, `reference`, `concept`, `contract`, `troubleshooting`

**Step 3: Update STATE.md**

```
PHASE = PHASE_6_TRACEABILITY
LAST_CHECKPOINT = 0001_PHASE5_CHECKPOINT
```

**Step 4: Write checkpoint**

```markdown
# Checkpoint: Phase 5 — DOC_CLAIMS
Doc files analyzed: [N]
Claims extracted: [N]
Verified: [N]
Unverified: [N]
Contradicted: [N]
Next: PHASE_6_TRACEABILITY
```

**Step 5: Verify**

- `06_DOC_CLAIMS.md` has a DOC entry for every factual claim in README and package READMEs
- Every DOC entry has an evidence status with reasoning
- `01_STATE.md` shows `PHASE = PHASE_6_TRACEABILITY`

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase5): catalog existing documentation claims"
```

---

### Task 7: Audit Phase 6 — TRACEABILITY

**Files:**
- Read: `docs/investigation/05_TEST_SPEC.md`, `docs/investigation/06_DOC_CLAIMS.md`
- Write: `docs/investigation/07_TRACEABILITY.md`
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE6_CHECKPOINT.md`

**Context:** Build the bidirectional matrix. BHV → DOC tells us if each behavior is documented. DOC → BHV tells us if each claim has evidence. Every public behavior with no covering DOC claim is a coverage gap. Every DOC claim with no BHV backing is a suspect claim.

**Step 1: Read state**

1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/01_STATE.md`
3. `docs/investigation/05_TEST_SPEC.md`
4. `docs/investigation/06_DOC_CLAIMS.md`
5. `/home/inumaki/Development/investigation-framework/audit-agent/07_TRACEABILITY.md` (for schema)

**Step 2: Build BHV → DOC coverage table**

For every `BHV-XXXX` (public behaviors only):

```markdown
## BHV → Documentation coverage

| BHV ID | Title | Covered by DOC claims | Coverage status |
|---|---|---|---|
| BHV-0001 | Settings merges TOML project config over defaults | DOC-0003, DOC-0004 | covered |
| BHV-0015 | Batch processing runs effects in parallel | (none) | gap |
```

Coverage status: `covered`, `partial`, `gap`

**Step 3: Build DOC → BHV evidence table**

```markdown
## DOC → Evidence

| DOC ID | Claim summary | Evidence (BHV/test/code) | Evidence status |
|---|---|---|---|
| DOC-0001 | wallpaper-core accepts --dry-run | BHV-0012 | verified |
| DOC-0007 | Presets override composites | (none found) | unverified |
```

**Step 4: Update STATE.md**

```
PHASE = PHASE_7_REVIEW_FINDINGS
LAST_CHECKPOINT = 0001_PHASE6_CHECKPOINT
```

**Step 5: Write checkpoint**

```markdown
# Checkpoint: Phase 6 — TRACEABILITY
Public BHVs: [N]
Covered: [N]
Partial: [N]
Gaps: [N]
DOC claims verified: [N]
DOC claims unverified: [N]
Next: PHASE_7_REVIEW_FINDINGS
```

**Step 6: Verify**

- Every public BHV has a row in the BHV→DOC table
- Every DOC entry has a row in the DOC→BHV table
- `01_STATE.md` shows `PHASE = PHASE_7_REVIEW_FINDINGS`

**Step 7: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase6): build traceability matrix"
```

---

### Task 8: Audit Phase 7 — REVIEW_FINDINGS

**Files:**
- Read: `docs/investigation/07_TRACEABILITY.md`, `docs/investigation/05_TEST_SPEC.md`, `docs/investigation/06_DOC_CLAIMS.md`
- Write: `docs/investigation/08_FINDINGS.md`
- Write: `docs/investigation/01_STATE.md`
- Write: `docs/investigation/iterations/0001_PHASE7_CHECKPOINT.md`

**Context:** Convert gaps and contradictions into findings. Apply severity levels:
- **S0:** Existing doc claim that actively causes user failure (wrong flag, wrong command, broken example)
- **S1:** Public behavior entirely absent from documentation
- **S2:** Public behavior mentioned but incomplete (missing required option, unclear prerequisite)
- **S3:** Typo, formatting, style issue

**Step 1: Read state and traceability**

1. `/home/inumaki/Development/investigation-framework/audit-agent/00_RULES.md`
2. `docs/investigation/01_STATE.md`
3. `docs/investigation/07_TRACEABILITY.md`
4. `docs/investigation/06_DOC_CLAIMS.md`
5. `/home/inumaki/Development/investigation-framework/audit-agent/08_FINDINGS.md` (for schema)

**Step 2: Write findings from gaps**

Every `gap` row in BHV→DOC becomes at minimum an S1 finding. Every `contradicted` DOC entry becomes an S0 finding.

```markdown
## S0 — Critical

### F-0001
**Summary:** README example for `--output-dir` uses wrong flag syntax
**Location:** `README.md:72`
**Evidence:** BHV-0022 (`packages/core/tests/test_cli.py::test_output_dir_flag`) shows flag is `--out-dir`
**Proposed fix:** Update README:72 to use `--out-dir`

## S1 — Major

### F-0002
**Summary:** Batch processing parallelism behavior (BHV-0015) is not documented anywhere
**Location:** (missing from all docs)
**Evidence:** BHV-0015 (`packages/core/tests/test_batch.py::test_parallel_execution`)
**Proposed fix:** Add to reference docs: wallpaper-core batch mode runs effects in parallel
```

**Step 3: Update STATE.md with counts**

```
PHASE = PHASE_8_FINALIZE_INVESTIGATION
S0_COUNT = [N]
S1_COUNT = [N]
S2_COUNT = [N]
S3_COUNT = [N]
LAST_CHECKPOINT = 0001_PHASE7_CHECKPOINT
```

**Step 4: Write checkpoint**

```markdown
# Checkpoint: Phase 7 — REVIEW_FINDINGS
S0: [N]
S1: [N]
S2: [N]
S3: [N]
Next: PHASE_8_FINALIZE_INVESTIGATION
```

**Step 5: Verify**

- Every BHV coverage gap has a corresponding finding
- Every contradicted DOC claim has an S0 finding
- Severity is correctly applied (S0 only for claims that actively break user workflows)
- `01_STATE.md` shows `PHASE = PHASE_8_FINALIZE_INVESTIGATION`

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase7): complete findings review (S0=[N], S1=[N], S2=[N], S3=[N])"
```

---

### Task 9: Audit Phase 8 — FINALIZE

**Files:**
- Read: `docs/investigation/01_STATE.md`, `docs/investigation/08_FINDINGS.md`, `docs/investigation/09_UNKNOWNS.md`
- Write: `docs/investigation/10_METRICS.md`
- Write: `docs/investigation/11_NEXT_ACTIONS.md`
- Write: `docs/investigation/01_STATE.md` (set INVESTIGATION_STATUS)
- Write: `docs/investigation/iterations/0001_PHASE8_CHECKPOINT.md`

**Context:** Check acceptance thresholds from `00_REQUIREMENTS.md`:
- S0 must equal 0 to pass (any S0 = FAIL)
- S1 must be ≤ 3 to pass
- Open unknowns must be ≤ 5 to pass

If any threshold is violated, set `INVESTIGATION_STATUS = FAIL` and list what must be resolved before synthesis. If all pass, set `INVESTIGATION_STATUS = PASS`.

**Step 1: Read state and all counts**

1. `docs/investigation/01_STATE.md`
2. `docs/investigation/08_FINDINGS.md`
3. `docs/investigation/09_UNKNOWNS.md`
4. `docs/investigation/00_REQUIREMENTS.md`

**Step 2: Write 10_METRICS.md**

```markdown
# Investigation Metrics

ITERATION = 0001

## Counts
S0 = [N]
S1 = [N]
S2 = [N]
S3 = [N]
UNKNOWNS_OPEN = [N]

## Thresholds
S0_THRESHOLD = 0    → [PASS|FAIL]
S1_THRESHOLD = 3    → [PASS|FAIL]
UNKNOWNS_THRESHOLD = 5 → [PASS|FAIL]

## Public BHV coverage
Total public BHVs: [N]
Covered: [N]
Coverage %: [N]%

## INVESTIGATION_STATUS = [PASS|FAIL|BLOCKED]
```

**Step 3: Write 11_NEXT_ACTIONS.md**

If PASS:
```markdown
# Next Actions
1. Proceed to synthesis agent. Run Diátaxis profile.
2. S1 findings must be covered in synthesis output.
3. S2/S3 findings noted; address as S2/S3 improvements in docs.
```

If FAIL (S0 > 0):
```markdown
# Next Actions
BLOCKED: Must resolve S0 findings before synthesis.
1. Fix [F-XXXX]: [description] in [file:line]
Then re-run PHASE_7 and PHASE_8.
```

**Step 4: Update STATE.md**

```
INVESTIGATION_STATUS = [PASS|FAIL|BLOCKED]
LAST_CHECKPOINT = 0001_PHASE8_CHECKPOINT
```

**Step 5: Verify**

- `10_METRICS.md` has all counts populated
- `INVESTIGATION_STATUS` is set correctly (PASS only if all thresholds met)
- `11_NEXT_ACTIONS.md` has concrete next steps

**Step 6: Commit**

```bash
git add docs/investigation/
git commit -m "audit(phase8): finalize investigation (status=[PASS|FAIL])"
```

---

### Task 10: Findings gate — resolve S0 findings (if any)

**Skip this task if `INVESTIGATION_STATUS = PASS` in `docs/investigation/10_METRICS.md`.**

**Files:**
- Read: `docs/investigation/08_FINDINGS.md`
- Modify: source doc files where S0 findings point (e.g., `README.md`, `packages/*/README.md`)
- Write: `docs/investigation/08_FINDINGS.md` (mark resolved)
- Write: `docs/investigation/10_METRICS.md` (update S0 count)

**Step 1: Read every S0 finding**

Each S0 finding has a `Proposed fix`. Apply the fix directly to the referenced file and line.

**Step 2: Re-verify after each fix**

For each S0 fix, confirm the corrected claim now matches the evidence (test/code).

**Step 3: Mark resolved in findings**

Update each resolved S0 finding:
```markdown
**Status:** resolved — [description of fix applied]
```

**Step 4: Update metrics**

Decrement `S0` count in `10_METRICS.md`. If S0 = 0, set `INVESTIGATION_STATUS = PASS`.

**Step 5: Commit each fix separately**

```bash
git add [modified doc file] docs/investigation/08_FINDINGS.md docs/investigation/10_METRICS.md
git commit -m "fix(docs): resolve S0 finding F-XXXX — [summary]"
```

---

### Task 11: Synthesis — produce Diátaxis documentation

**Files:**
- Read: all `docs/investigation/` artifacts
- Read: `/home/inumaki/Development/investigation-framework/synthesis-agent/00_SYNTHESIS_RULES.md`
- Read: `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/` (all files)
- Create: `docs/tutorials/` (at least 1 .md file)
- Create: `docs/how-to/` (at least 1 .md file)
- Create: `docs/reference/` (at least 1 .md file)
- Create: `docs/explanation/` (at least 1 .md file)
- Write: `docs/investigation/02_SYNTHESIS_STATE.md`
- Write: `docs/investigation/03_DOC_PLAN.md`
- Write: `docs/investigation/04_CONFORMANCE.md`
- Write: `docs/investigation/iterations/0001_SYNTH_CHECKPOINT.md`

**Context:** You are the synthesis agent. Do not modify audit artifacts. Do not invent behaviors. Every claim in the output must cite a BHV ID from `05_TEST_SPEC.md`. Verification policy is `verified-only` — omit any behavior that is not `verified` in the traceability matrix.

**Step 1: Read synthesis rules and profile (mandatory order)**

1. `/home/inumaki/Development/investigation-framework/synthesis-agent/00_SYNTHESIS_RULES.md`
2. `docs/investigation/02_SYNTHESIS_STATE.md`
3. `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/00_PROFILE.md`
4. `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/01_STRUCTURE.md`
5. `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/02_MAPPING_RULES.md`
6. `/home/inumaki/Development/investigation-framework/synthesis-agent/profiles/diataxis/03_CONFORMANCE_CHECKS.md`

**Step 2: Read investigation artifacts**

7. `docs/investigation/05_TEST_SPEC.md` (source of truth for behaviors)
8. `docs/investigation/07_TRACEABILITY.md` (coverage map)
9. `docs/investigation/08_FINDINGS.md` (S1/S2 to address)
10. `docs/investigation/06_DOC_CLAIMS.md` (existing verified claims to reuse)

**Step 3: Write the DOC_PLAN**

Before writing any docs, plan which pages exist and which BHV IDs they cover:

```markdown
# docs/investigation/03_DOC_PLAN.md

## tutorials/getting-started.md
BHVs: BHV-0001, BHV-0002, BHV-0005
Goal: First-time walkthrough: install → process one image → batch run

## how-to/apply-effect.md
BHVs: BHV-0010, BHV-0011, BHV-0012
Goal: Apply a specific named effect to an image

## how-to/run-in-container.md
BHVs: BHV-0030, BHV-0031
Goal: Run wallpaper-process with Docker or Podman

## reference/cli.md
BHVs: [all public CLi-related BHVs]
Goal: All flags for wallpaper-core and wallpaper-process

## reference/config.md
BHVs: [all settings-related BHVs]
Goal: All configuration keys, types, defaults, precedence

## reference/effects.md
BHVs: [all effects/composite/preset BHVs]
Goal: All built-in effects, composites, presets

## explanation/architecture.md
BHVs: (no BHVs — conceptual)
Goal: Package structure, design decisions, contributor guide

## explanation/layered-config.md
BHVs: BHV-0001, BHV-0002, BHV-0003
Goal: Why 4-layer config, how precedence works

## explanation/host-vs-container.md
BHVs: BHV-0030, BHV-0031, BHV-0040
Goal: When to use host execution vs. container execution
```

**Step 4: Write each documentation page**

Follow the Diátaxis profile templates from `profiles/diataxis/`. Each page must:
- Cite BHV IDs inline: "(BHV-0012)"
- Use `verified-only` policy: only document behaviors with `verified` status in traceability
- Match the template structure exactly

**Tutorial template:**
```markdown
# Tutorial: [Title]
## Goal
## Prerequisites
## Steps
## Verification (BHV IDs: BHV-XXXX, ...)
```

**How-to template:**
```markdown
# How-to: [Task]
## Prerequisites
## Steps
## Verification (BHV IDs: BHV-XXXX, ...)
```

**Reference template:**
```markdown
# Reference
## CLI
## Config
## Verification
```

**Explanation template:**
```markdown
# Explanation
## Concepts
## Mental model
## Rationale
```

**Step 5: Write SYNTHESIS_STATE.md (update to RUNNING)**

```markdown
ITERATION = 0001
STATUS = RUNNING
LAST_CHECKPOINT = 0001_SYNTH_CHECKPOINT
```

**Step 6: Run conformance checks and write 04_CONFORMANCE.md**

Per `profiles/diataxis/03_CONFORMANCE_CHECKS.md`:
- [ ] `docs/tutorials/` exists with ≥ 1 .md file
- [ ] `docs/how-to/` exists with ≥ 1 .md file
- [ ] `docs/reference/` exists with ≥ 1 .md file
- [ ] `docs/explanation/` exists with ≥ 1 .md file
- [ ] Public BHV coverage ≥ 90%
- [ ] `verified-only` policy satisfied (no unverified claims)
- [ ] No S0 finding reproduced in output

```markdown
# docs/investigation/04_CONFORMANCE.md

OUTPUT_PROFILE = diataxis

Structure: PASS
Coverage: [N]/[N] public BHVs = [N]% → [PASS|FAIL]
Policy (verified-only): PASS
Safety (no S0 reproduced): PASS

SYNTHESIS_STATUS = [PASS|FAIL|BLOCKED]
```

**Step 7: Update SYNTHESIS_STATE to PASS**

```markdown
ITERATION = 0001
STATUS = PASS
LAST_CHECKPOINT = 0001_SYNTH_CHECKPOINT
```

**Step 8: Verify output**

- All 4 Diátaxis directories exist with at least 1 file each
- Every file cites at least one BHV ID
- `04_CONFORMANCE.md` shows `SYNTHESIS_STATUS = PASS`
- No page claims a behavior not in `05_TEST_SPEC.md`

**Step 9: Commit**

```bash
git add docs/
git commit -m "docs: generate Diataxis documentation from investigation (BHV coverage: [N]/[N])"
```

---

### Task 12: Final review commit

**Step 1: Verify complete output structure**

```
docs/
├── investigation/
│   ├── 00_REQUIREMENTS.md
│   ├── 01_STATE.md          (INVESTIGATION_STATUS = PASS)
│   ├── 02_SYNTHESIS_STATE.md (STATUS = PASS)
│   ├── 03_INVENTORY.md
│   ├── 04_TOPIC_MAP.md
│   ├── 05_TEST_SPEC.md
│   ├── 06_DOC_CLAIMS.md
│   ├── 07_TRACEABILITY.md
│   ├── 08_FINDINGS.md
│   ├── 09_UNKNOWNS.md
│   ├── 10_METRICS.md       (INVESTIGATION_STATUS = PASS)
│   ├── 11_NEXT_ACTIONS.md
│   ├── 03_DOC_PLAN.md
│   ├── 04_CONFORMANCE.md   (SYNTHESIS_STATUS = PASS)
│   └── iterations/
├── tutorials/
│   └── getting-started.md (at minimum)
├── how-to/
│   └── [task guides]
├── reference/
│   └── cli.md, config.md, effects.md (at minimum)
└── explanation/
    └── [concept pages]
```

**Step 2: Verify BHV coverage**

Check `docs/investigation/04_CONFORMANCE.md` shows coverage ≥ 90%.

**Step 3: Final commit if any uncommitted changes**

```bash
git status
git add docs/
git commit -m "docs: complete investigation-driven Diataxis documentation"
```
