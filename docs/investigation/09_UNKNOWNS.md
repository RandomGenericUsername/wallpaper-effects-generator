# Unknowns Register

<!-- Populated during investigation phases -->

Unknown IDs: `U-0001`, `U-0002`, ...

Required fields:
- Question
- Status: open | resolved | blocked
- Opened in iteration
- Attempts
- Resolution evidence

---

## U-0001

- Question: `packages/effects/tests/test_loader.py::TestEffectsLoader::test_loads_single_file` (line 85) calls the private method `loader._load_yaml_file()` directly — is this private method part of any documented contract, or purely an internal implementation detail accessed only in tests?
- Status: resolved
- Opened: iteration 0001
- Attempts: Read test file and source — purpose still unclear; method name implies internal YAML loading helper but test exercises it directly
- Resolution evidence: Read `packages/effects/src/layered_effects/loader.py` — `_load_yaml_file()` is defined with a leading underscore (line 63), is not in `layered_effects.__all__`, and is not exported from the package. It is a private helper used internally by `load_and_merge()`. The test exercises it directly for unit testing convenience, but it is purely an internal implementation detail. BHV classification for `_load_yaml_file` tests remains `internal`.

---

## U-0002

- Question: `packages/core/tests/test_console_progress.py` — file not read in full; may cover progress bar / rich progress display behaviors not captured in the behavior catalog
- Status: resolved
- Opened: iteration 0001
- Attempts: File identified in inventory but not read during phase 3; behaviors may duplicate or extend BHV-0065 (verbosity flags)
- Resolution evidence: Read the full file. It tests `BatchProgress` (a context-manager wrapper around Rich's progress bar) via `TestBatchProgressEdgeCases`. Behaviors covered: `advance()` before/after start, `completed` property, `update_description()`, double `start()`/`stop()` guard, context-manager protocol, zero-total edge case. These are all internal implementation details of `wallpaper_core.console.progress.BatchProgress`, which is not exported in `wallpaper_core.__init__.__all__`. The behaviors are distinct from BHV-0065 (which is about CLI verbosity flags). No new public BHV needs to be added; if required, an internal BHV for `BatchProgress` edge cases could be appended. For the purposes of the behavior catalog, this is an internal helper and does not affect the public BHV count.

---

## U-0003

- Question: `packages/orchestrator/tests/test_cli_dry_run.py` lines 200–543 — partial read during phase 3; error cases for preset with unknown effect/composite reference, podman-specific preset dry-run, and invalid reference handling may constitute distinct behaviors beyond those captured in BHV-0079
- Status: resolved
- Opened: iteration 0001
- Attempts: Lines 200–543 not individually enumerated; covered at a high level by BHV-0079 but sub-cases not individually verified
- Resolution evidence: Read lines 200–542. The section contains `TestProcessPresetContainerDryRun` (unknown preset → exit 0 with "cannot resolve" / "unknown" in output; preset with unknown effect reference → exit 0; preset with unknown composite reference → exit 0) and `TestProcessEffectDryRunEdgeCases` (effect not found in config → exit 0 with "not found" in output), `TestProcessCompositeEdgeCases` (composite not found → exit 0), and `TestPodmanDryRun` (podman userns flag for effect and preset). All these are sub-cases of BHV-0079 (dry-run shows both commands, exits 0 for unknown items). They do not constitute separate BHVs: BHV-0079 already states "Unknown preset/effect names produce warning output; exit code is still 0" and "preset with invalid composite reference exits 0 with warning". No new BHVs required. The podman-specific userns flag is also already captured in BHV-0079's evidence reference to `TestProcessCompositeContainerDryRun::test_dry_run_composite_with_podman`.

---

## U-0004

- Question: `packages/orchestrator/tests/test_cli_process.py` lines 200–680 — partial read; composite/preset process error cases (missing image, execution failure, runtime error) are variants of BHV-0078 but were not individually captured; unclear whether they constitute additional distinct behaviors
- Status: resolved
- Opened: iteration 0001
- Attempts: Lines 200–680 not fully enumerated; treated as variants of BHV-0078 during phase 3
- Resolution evidence: Read lines 200–680 in full. Contents: `test_process_composite_without_output_dir` (uses default), `test_process_composite_with_flat_flag`, `test_process_composite_dry_run` (run_process NOT called), `test_process_preset_with_output_dir/without_output_dir/with_flat_flag/dry_run`, `test_process_effect_checks_image_available` (exit 1 + "Container image not found"), `test_process_effect_handles_container_failure` (exit 1 + "failed"), `test_process_composite_missing_image`, `test_process_composite_execution_failure`, `test_process_preset_missing_image`, `test_process_preset_execution_failure`, `test_process_effect_runtime_error` (RuntimeError → exit 1). All of these are sub-cases of BHV-0078 (process effect/composite/preset dispatches to ContainerManager, handles errors). BHV-0078's error cases section already states "Container missing → RuntimeError; input missing → FileNotFoundError; run_process failure → exit code 1". No new BHVs are required.
