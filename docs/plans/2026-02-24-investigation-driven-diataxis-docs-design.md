# Design: Investigation-Driven Documentation

**Date:** 2026-02-24
**Status:** Superseded — profile changed to MkDocs (see implementation plan `2026-02-24-investigation-driven-mkdocs-docs.md`)

## Goal

Produce a complete Diátaxis documentation set for the wallpaper-effects-generator monorepo, grounded entirely in code analysis and test-suite evidence using the investigation framework.

## Approach

Full sequential execution of the investigation framework's two-phase pipeline:

1. **Audit agent** — 8 sequential phases that catalog the repo and extract test-backed behaviors.
2. **Synthesis agent** — Diátaxis profile that maps behaviors to documentation deliverables.

No content is invented. Every statement in output docs cites a `BHV-XXXX` behavior ID or test reference.

---

## Phase 1: Audit

All artifact files are saved to `docs/investigation/`.

| Phase | Artifact | Purpose |
|---|---|---|
| PHASE_1_INVENTORY | `03_INVENTORY.md` | Complete file registry classified by type |
| PHASE_2_TOPIC_MAP | `04_TOPIC_MAP.md` | Topic-to-file index (primary/secondary owners) |
| PHASE_3_TEST_SPEC | `05_TEST_SPEC.md` | All 566 tests cataloged; behaviors assigned `BHV-XXXX` IDs |
| PHASE_4_BEHAVIOR_CATALOG | `06_BEHAVIOR_CATALOG.md` | Per-behavior: preconditions, steps, expected output, error cases |
| PHASE_5_DOC_CLAIMS | (feeds PHASE_6) | Existing doc claims extracted from READMEs and CHANGELOG |
| PHASE_6_TRACEABILITY | `07_TRACEABILITY.md` | Every claim/behavior mapped to test, code, or contract evidence |
| PHASE_7_REVIEW_FINDINGS | `08_FINDINGS.md` | Discrepancies rated S0–S3 severity |
| PHASE_8_FINALIZE | `10_METRICS.md` | Pass/fail against completeness thresholds |

---

## Phase 2: Synthesis (Diátaxis Profile)

The synthesis agent reads investigation artifacts and produces:

```
docs/
├── investigation/           ← audit artifacts (preserved, not published)
│   ├── 03_INVENTORY.md
│   ├── 04_TOPIC_MAP.md
│   ├── 05_TEST_SPEC.md
│   ├── 06_BEHAVIOR_CATALOG.md
│   ├── 07_TRACEABILITY.md
│   ├── 08_FINDINGS.md
│   └── 10_METRICS.md
├── tutorials/
│   └── getting-started.md       ← task-oriented, first-run experience
├── how-to/
│   ├── apply-an-effect.md
│   ├── run-batch-processing.md
│   ├── use-container-mode.md
│   └── configure-output-directory.md
├── reference/
│   ├── cli.md                   ← all commands, flags, defaults
│   ├── effects-catalog.md       ← all effects, composites, presets
│   └── configuration.md         ← all config layers, keys, precedence
└── explanation/
    ├── architecture.md          ← 4-package design, data flow
    └── layered-config.md        ← rationale and mechanics of layered config
```

### Diátaxis Mapping Rules

| Behavior type | Diátaxis category |
|---|---|
| First-run / onboarding flows | tutorials/ |
| Goal-oriented task flows | how-to/ |
| CLI flags, config keys, effect names/params | reference/ |
| Architectural decisions, design rationale | explanation/ |

---

## Constraints

- Output replaces the existing `docs/` directory.
- Audit artifacts are preserved under `docs/investigation/` for traceability.
- Evidence hierarchy: Tests > Code contracts > Code references > Existing docs.
- The `plans/` subdirectory is excluded from replacement.
