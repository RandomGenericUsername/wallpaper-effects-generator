# Checkpoint: Phase 5 — DOC_CLAIMS

Iteration: 0001
Doc files analyzed: 6
  - README.md
  - DEVELOPMENT.md
  - packages/settings/README.md
  - packages/core/README.md
  - packages/effects/README.md
  - packages/orchestrator/README.md

Claims extracted: 107
  Verified: 75
  Unverified: 32
  Contradicted: 0

## Notable findings

### Possible documentation inconsistencies flagged as unverified

- **DOC-0089**: `packages/core/README.md` lists the effects.yaml package path as
  `packages/core/effects/effects.yaml` and user path as `~/.config/wallpaper-effects/effects.yaml`.
  BHV-0042 references `packages/core/src/wallpaper_core/config/effects.yaml` (different path).
  The user path differs from the `wallpaper-effects-generator` app name used elsewhere.
  Marked unverified pending path verification.

- **DOC-0092**: `packages/core/README.md` states user settings at `~/.config/wallpaper-effects/settings.toml`
  while root `README.md` and `packages/settings/README.md` use `wallpaper-effects-generator`.
  Possible stale path — requires code-level verification.

- **DOC-0100**: `packages/orchestrator/README.md` shows process command syntax with positional
  output path (`wallpaper-process process effect input.jpg output.jpg blur`) while
  BHV-0078 shows named-flag syntax (`-o output_dir --effect blur`). May be outdated documentation.

- **DOC-0018 / DOC-0023**: Root README.md claims default output dir is `./wallpapers-output`;
  BHV-0040 notes test context uses `/tmp/wallpaper-effects`. The actual settings.toml default
  value needs verification.

### DEVELOPMENT.md claims
32 of the 50 unverified claims come from DEVELOPMENT.md, which describes CI/CD infrastructure
(GitHub Actions, Makefile targets, pre-commit hooks). These are plausible but have no
corresponding BHV behaviors since the test suite focuses on application code, not build tooling.

Next: PHASE_6_TRACEABILITY
