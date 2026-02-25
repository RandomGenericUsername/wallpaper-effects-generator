# Investigation-Driven Diátaxis Documentation Design

**Date:** 2026-02-25
**Status:** Approved
**Supersedes:** 2026-02-24 Diátaxis and MkDocs plans (deleted)

## Goal

Produce Diátaxis-structured documentation for `wallpaper-effects-generator` using the
investigation framework. All documented behaviors must be grounded in evidence from the
test suite, source code, or contracts — no invention, no guessing.

## Scope

- **Audience:** End users (CLI consumers) and contributors (developers)
- **Output format:** Diátaxis (Tutorials / How-to / Reference / Explanation)
- **Starting point:** Fresh — reset all investigation state
- **Verification policy:** `verified-only` (default)

## Architecture

```
wallpaper-effects-generator/          ← source under investigation
│
│   [Phase 1: Audit Agent]
│   Follows investigation-framework/audit-agent/ instructions
│   Reads: packages/, tests/, CLIs, configs, existing docs
│
├── docs/investigation/               ← audit artifacts (intermediate, committed)
│   ├── 03_INVENTORY.md
│   ├── 04_TOPIC_MAP.md
│   ├── 05_TEST_SPEC.md               ← BHV-XXXX behavior IDs with test citations
│   ├── 06_DOC_CLAIMS.md
│   ├── 07_TRACEABILITY.md
│   ├── 08_FINDINGS.md
│   ├── 09_UNKNOWNS.md
│   └── 10_METRICS.md
│
│   [Phase 2: Synthesis Agent]
│   Follows investigation-framework/synthesis-agent/ + Diátaxis profile
│
└── docs/
    ├── tutorials/                    ← learning-oriented
    ├── how-to/                       ← task-oriented
    ├── reference/                    ← information-oriented
    └── explanation/                  ← understanding-oriented (incl. contributor)
```

## Audit Phase Components

The audit agent runs 8 phases in sequence. Each phase produces one artifact:

| Phase | Artifact | Content |
|-------|----------|---------|
| INVENTORY | `03_INVENTORY.md` | Every file in scope with role and package |
| TOPIC_MAP | `04_TOPIC_MAP.md` | Thematic groupings: config, CLI, effects, containers, dev workflow |
| TEST_SPEC | `05_TEST_SPEC.md` | All tested behaviors with `BHV-XXXX` IDs, test file + line |
| DOC_CLAIMS | `06_DOC_CLAIMS.md` | Existing documentation claims with severity if wrong or missing |
| TRACEABILITY | `07_TRACEABILITY.md` | Each claim mapped to evidence (test / code / contract) |
| FINDINGS | `08_FINDINGS.md` | Gaps (S0–S3): behaviors tested but undocumented |
| UNKNOWNS | `09_UNKNOWNS.md` | Open questions that could not be resolved |
| METRICS | `10_METRICS.md` | BHV coverage statistics and audit status |

**Evidence hierarchy (non-negotiable):** tests > contracts > code > docs

**Severity levels:**

- S0 — Incorrect documentation that causes user failure → blocks synthesis
- S1 — Core public behavior with no documentation → must be covered in synthesis
- S2 — Ambiguity, missing edge cases → noted, does not block
- S3 — Typos, style → noted, does not block

## Synthesis Phase Output

The synthesis agent maps BHV-XXXX behaviors to Diátaxis document types:

| Type | Content from this project |
|------|--------------------------|
| **Tutorials** | Guided first-time walkthrough: install → process one image → batch run |
| **How-to guides** | Apply specific effects, use presets, run in containers, override config layers, dry-run |
| **Reference** | All `wallpaper-core` and `wallpaper-process` CLI flags, all config keys, all built-in effects / composites / presets, settings precedence table |
| **Explanation** | Layered config rationale, effect chaining model, host vs. container design, monorepo package structure, contributor dev workflow |

Each page cites `BHV-XXXX` IDs linking back to `05_TEST_SPEC.md`.
Contributor documentation lives under `docs/explanation/` and `docs/contributing/`.

## Execution Flow

```
1. RESET
   Clear docs/investigation/
   Set audit state: PHASE_1_INVENTORY, iteration 0001

2. AUDIT (runs to completion across iterations)
   All 4 packages in scope: settings, core, effects, orchestrator
   Stall detection: terminates if no progress on S0/S1/unknowns for 2 iterations

3. FINDINGS GATE
   S0 findings → must be resolved before synthesis begins
   S1 findings → must be covered in synthesis output

4. SYNTHESIS (runs to completion)
   Reads all 8 audit artifacts
   Applies Diátaxis profile mapping rules from investigation-framework/synthesis-agent/
   Writes docs/ pages with BHV citations
   Runs conformance checks: structure, coverage, policy, safety

5. COMMIT
   Commit docs/investigation/ artifacts and docs/ pages together
   Commit message includes BHV coverage count
```

## Packages in Scope

| Package | Responsibility |
|---------|---------------|
| `packages/settings` | Layered TOML/YAML configuration, 4-level precedence |
| `packages/core` | Local ImageMagick execution, `wallpaper-core` CLI |
| `packages/effects` | Effect / composite / preset definitions in YAML |
| `packages/orchestrator` | Container execution, `wallpaper-process` CLI |

Test suite: ~43 test files, 95% coverage minimum enforced in CI.
