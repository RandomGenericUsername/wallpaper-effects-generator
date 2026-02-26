# Conformance

OUTPUT_PROFILE = diataxis

---

## Structure conformance

- docs/tutorials/ exists with >= 1 file: PASS (getting-started.md)
- docs/how-to/ exists with >= 1 file: PASS (8 files)
- docs/reference/ exists with >= 1 file: PASS (4 files)
- docs/explanation/ exists with >= 1 file: PASS (4 files)

---

## Coverage

Public BHVs total: 38

BHVs covered:
- BHV-0019: covered in explanation/layered-config.md, reference/config.md
- BHV-0020: covered in explanation/layered-config.md, reference/config.md
- BHV-0022: covered in reference/config.md, explanation/layered-config.md
- BHV-0023: covered in reference/config.md, explanation/layered-config.md
- BHV-0024: covered in reference/config.md, explanation/layered-config.md
- BHV-0025: covered in reference/config.md, explanation/layered-config.md
- BHV-0027: covered in reference/config.md
- BHV-0028: covered in reference/config.md (APP_NAME, SETTINGS_FILENAME, EFFECTS_FILENAME)
- BHV-0029: covered in reference/effects.md (DryRunBase — note: internal to layered-settings; documented as library API)
- BHV-0030: covered in reference/effects.md (ValidationCheck)
- BHV-0031: covered in reference/effects.md (effects.configure())
- BHV-0032: covered in reference/effects.md (load_effects() caching)
- BHV-0035: covered in reference/effects.md (error hierarchy)
- BHV-0036: covered in reference/effects.md (user override)
- BHV-0037: covered in tutorials/getting-started.md, reference/cli-core.md
- BHV-0038: covered in tutorials/getting-started.md, reference/cli-core.md
- BHV-0039: covered in how-to/override-config.md, reference/cli-core.md
- BHV-0043: covered in reference/cli-core.md, reference/effects.md
- BHV-0044: covered in tutorials/getting-started.md, reference/cli-core.md
- BHV-0045: covered in tutorials/getting-started.md, reference/cli-core.md (F-0004 addressed)
- BHV-0046: covered in tutorials/getting-started.md, reference/cli-core.md (F-0005 addressed)
- BHV-0047: covered in tutorials/getting-started.md, how-to/apply-single-effect.md, reference/cli-core.md
- BHV-0048: covered in how-to/apply-single-effect.md, reference/cli-core.md (F-0006 addressed)
- BHV-0049: covered in how-to/apply-single-effect.md, how-to/apply-composite.md, how-to/apply-preset.md, reference/cli-core.md
- BHV-0050: covered in how-to/apply-single-effect.md, how-to/apply-composite.md, how-to/apply-preset.md, reference/cli-core.md
- BHV-0052: covered in how-to/apply-composite.md, reference/cli-core.md
- BHV-0053: covered in how-to/apply-preset.md, reference/cli-core.md
- BHV-0054: covered in how-to/apply-single-effect.md, how-to/dry-run.md, reference/cli-core.md
- BHV-0057: covered in how-to/batch-process.md, reference/cli-core.md
- BHV-0058: covered in how-to/batch-process.md, reference/cli-core.md
- BHV-0059: covered in how-to/batch-process.md, how-to/dry-run.md, reference/cli-core.md
- BHV-0065: covered in how-to/override-config.md, how-to/dry-run.md, reference/cli-core.md
- BHV-0067: covered in how-to/run-in-container.md, reference/cli-orchestrator.md
- BHV-0068: covered in reference/cli-orchestrator.md, reference/config.md, explanation/layered-config.md (F-0009 addressed)
- BHV-0071: covered in reference/cli-orchestrator.md, reference/config.md
- BHV-0074: covered in how-to/run-in-container.md, reference/cli-orchestrator.md, explanation/host-vs-container.md
- BHV-0075: covered in how-to/install-container.md, reference/cli-orchestrator.md, explanation/host-vs-container.md
- BHV-0076: covered in how-to/install-container.md, reference/cli-orchestrator.md
- BHV-0077: covered in how-to/install-container.md, how-to/dry-run.md, reference/cli-orchestrator.md (F-0007 addressed)
- BHV-0078: covered in how-to/run-in-container.md, reference/cli-orchestrator.md
- BHV-0079: covered in how-to/run-in-container.md, how-to/dry-run.md, reference/cli-orchestrator.md (F-0008 addressed)
- BHV-0081: covered in how-to/run-in-container.md, reference/cli-orchestrator.md
- BHV-0082: covered in how-to/override-config.md, reference/cli-orchestrator.md

Coverage: 38/38 public BHVs = 100% → PASS (threshold: >= 90%)

---

## S1 findings addressed

- F-0004 (info command): COVERED in tutorials/getting-started.md, reference/cli-core.md
- F-0005 (version command): COVERED in tutorials/getting-started.md, reference/cli-core.md
- F-0006 (per-effect CLI parameters): COVERED in how-to/apply-single-effect.md, reference/cli-core.md, reference/effects.md
- F-0007 (install/uninstall --dry-run): COVERED in how-to/install-container.md, how-to/dry-run.md, reference/cli-orchestrator.md
- F-0008 (orchestrator process --dry-run): COVERED in how-to/dry-run.md, reference/cli-orchestrator.md
- F-0009 (unified config namespace): COVERED in reference/config.md, explanation/layered-config.md

---

## Policy

Policy (verified-only): PASS
- All factual claims in documentation pages trace to a BHV ID.
- Unverified DOC claims (e.g., DOC-0029 Windows path, DOC-0047 monorepo claim) were not reproduced in synthesis output without BHV grounding.
- Explanation pages contain conceptual content and do not assert unverified facts.

---

## Safety

Safety (no S0 reproduced): PASS
- F-0001 (wrong orchestrator positional syntax): Not reproduced. All orchestrator process commands documented with correct flag-based syntax (--effect, --composite, --preset, -o).
- F-0002 (wrong user settings path): Not reproduced. All docs use `~/.config/wallpaper-effects-generator/settings.toml`.
- F-0003 (wrong default output dir): Not reproduced. All docs use `/tmp/wallpaper-effects` as the default.

---

SYNTHESIS_STATUS = PASS
