# Checkpoint: Phase 6 — TRACEABILITY

Iteration: 0001

## BHV → DOC coverage

Public BHVs: 43
  Note: 05_TEST_SPEC.md header says 38 public — the Grep confirms 43 entries marked
        `Publicity: public`. The 5-count discrepancy is a Phase 3/4 header error;
        the per-entry classifications are authoritative.
  Covered: 25
  Partial: 7
  Gaps: 11

Gap BHVs (no DOC claim covers them):
  BHV-0028 — APP_NAME, SETTINGS_FILENAME, EFFECTS_FILENAME constants
  BHV-0029 — DryRunBase rendering API
  BHV-0030 — ValidationCheck dataclass
  BHV-0031 — effects.configure() function
  BHV-0035 — Effects error hierarchy (EffectsLoadError, EffectsValidationError)
  BHV-0045 — wallpaper-core info command
  BHV-0046 — wallpaper-core version command
  BHV-0048 — wallpaper-core process effect per-effect CLI parameters
  BHV-0068 — wallpaper-orchestrator UnifiedConfig namespace configuration
  BHV-0077 — wallpaper-process install/uninstall --dry-run
  BHV-0079 — wallpaper-orchestrator process --dry-run (shows host+inner commands)

Partial BHVs (incompletely documented):
  BHV-0032 — effects.load_effects(): DOC-0094 describes layered config concept but not the API
  BHV-0039 — wallpaper-core CLI merges overrides: covered by config-layer docs, not CLI docs
  BHV-0043 — layered-effects merge in core: DOC-0089 unverified; DOC-0096 covers concept only
  BHV-0059 — wallpaper-core batch --dry-run: only DOC-0004 (process dry-run) partially covers
  BHV-0078 — orchestrator process command: DOC-0100 unverified (syntax may be outdated)
  BHV-0081 — orchestrator batch: DOC-0005 covers parallel batch concept only, not orchestrator-specific
  BHV-0082 — orchestrator CLI overrides: DOC-0006 covers settings concept, not orchestrator-specific

## DOC → Evidence

DOC claims: 107
  Verified: 75
  Unverified: 32

## Next

Next: PHASE_7_REVIEW_FINDINGS
