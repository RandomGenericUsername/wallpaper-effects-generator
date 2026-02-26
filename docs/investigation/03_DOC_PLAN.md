# Documentation Plan

<!-- Iteration 0001 — Synthesis phase -->
<!-- Profile: diataxis | Policy: verified-only -->
<!-- Public BHVs total: 38 -->

OUTPUT_DIR = docs/

---

## Pages and BHV coverage

### tutorials/

| File | Title | BHV IDs covered |
|---|---|---|
| `tutorials/getting-started.md` | Getting Started | BHV-0037, BHV-0038, BHV-0047, BHV-0049, BHV-0044, BHV-0045, BHV-0046 |

### how-to/

| File | Title | BHV IDs covered |
|---|---|---|
| `how-to/apply-single-effect.md` | Apply a Single Effect | BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0054 |
| `how-to/apply-composite.md` | Apply a Composite Effect | BHV-0052, BHV-0049, BHV-0050, BHV-0054 |
| `how-to/apply-preset.md` | Apply a Preset | BHV-0053, BHV-0049, BHV-0050, BHV-0054 |
| `how-to/batch-process.md` | Batch-Process Images | BHV-0057, BHV-0058, BHV-0059 |
| `how-to/run-in-container.md` | Run Effects in a Container | BHV-0067, BHV-0074, BHV-0078, BHV-0079, BHV-0081 |
| `how-to/install-container.md` | Install/Uninstall the Container Image | BHV-0075, BHV-0076, BHV-0077 |
| `how-to/override-config.md` | Override Configuration via CLI | BHV-0039, BHV-0065, BHV-0082 |
| `how-to/dry-run.md` | Preview Commands Without Executing (Dry Run) | BHV-0054, BHV-0059, BHV-0077, BHV-0079 |

### reference/

| File | Title | BHV IDs covered |
|---|---|---|
| `reference/cli-core.md` | wallpaper-core CLI Reference | BHV-0037, BHV-0038, BHV-0039, BHV-0043, BHV-0044, BHV-0045, BHV-0046, BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0052, BHV-0053, BHV-0054, BHV-0057, BHV-0058, BHV-0059, BHV-0065 |
| `reference/cli-orchestrator.md` | wallpaper-process CLI Reference | BHV-0067, BHV-0068, BHV-0071, BHV-0074, BHV-0075, BHV-0076, BHV-0077, BHV-0078, BHV-0079, BHV-0081, BHV-0082 |
| `reference/config.md` | Configuration Reference | BHV-0022, BHV-0023, BHV-0024, BHV-0025, BHV-0027, BHV-0028 |
| `reference/effects.md` | Built-in Effects, Composites, and Presets | BHV-0031, BHV-0032, BHV-0035, BHV-0036, BHV-0043 |

### explanation/

| File | Title | BHV IDs covered |
|---|---|---|
| `explanation/architecture.md` | Project Architecture | (conceptual — no BHV citations required) |
| `explanation/layered-config.md` | How Layered Configuration Works | BHV-0019, BHV-0020, BHV-0022, BHV-0023, BHV-0024, BHV-0025 |
| `explanation/host-vs-container.md` | Host Mode vs Container Mode | BHV-0074, BHV-0075 |
| `explanation/contributing.md` | Contributing and Development Workflow | (conceptual) |

---

## S1 findings coverage

| Finding | Page that covers it |
|---|---|
| F-0004 (info command undocumented) | `reference/cli-core.md`, `reference/cli-orchestrator.md` |
| F-0005 (version command undocumented) | `reference/cli-core.md`, `reference/cli-orchestrator.md` |
| F-0006 (per-effect CLI parameters undocumented) | `reference/cli-core.md`, `how-to/apply-single-effect.md`, `reference/effects.md` |
| F-0007 (install/uninstall --dry-run undocumented) | `how-to/install-container.md`, `how-to/dry-run.md`, `reference/cli-orchestrator.md` |
| F-0008 (orchestrator process --dry-run undocumented) | `how-to/dry-run.md`, `reference/cli-orchestrator.md` |
| F-0009 (orchestrator unified config namespace undocumented) | `explanation/layered-config.md`, `reference/config.md` |

---

## Coverage summary

Target: 38 public BHVs at >= 90% (>= 35 BHVs).

BHVs covered across all pages: BHV-0019, BHV-0020, BHV-0022, BHV-0023, BHV-0024, BHV-0025,
BHV-0027, BHV-0028, BHV-0031, BHV-0032, BHV-0035, BHV-0036, BHV-0037, BHV-0038, BHV-0039,
BHV-0043, BHV-0044, BHV-0045, BHV-0046, BHV-0047, BHV-0048, BHV-0049, BHV-0050, BHV-0052,
BHV-0053, BHV-0054, BHV-0057, BHV-0058, BHV-0059, BHV-0065, BHV-0067, BHV-0068, BHV-0071,
BHV-0074, BHV-0075, BHV-0076, BHV-0077, BHV-0078, BHV-0079, BHV-0081, BHV-0082

Coverage: 38/38 public BHVs = 100%
