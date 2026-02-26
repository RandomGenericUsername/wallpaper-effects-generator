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
- Status: open
- Opened: iteration 0001
- Attempts: Read test file and source — purpose still unclear; method name implies internal YAML loading helper but test exercises it directly
- Resolution evidence: (none yet)

---

## U-0002

- Question: `packages/core/tests/test_console_progress.py` — file not read in full; may cover progress bar / rich progress display behaviors not captured in the behavior catalog
- Status: open
- Opened: iteration 0001
- Attempts: File identified in inventory but not read during phase 3; behaviors may duplicate or extend BHV-0065 (verbosity flags)
- Resolution evidence: (none yet)

---

## U-0003

- Question: `packages/orchestrator/tests/test_cli_dry_run.py` lines 200–543 — partial read during phase 3; error cases for preset with unknown effect/composite reference, podman-specific preset dry-run, and invalid reference handling may constitute distinct behaviors beyond those captured in BHV-0079
- Status: open
- Opened: iteration 0001
- Attempts: Lines 200–543 not individually enumerated; covered at a high level by BHV-0079 but sub-cases not individually verified
- Resolution evidence: (none yet)

---

## U-0004

- Question: `packages/orchestrator/tests/test_cli_process.py` lines 200–680 — partial read; composite/preset process error cases (missing image, execution failure, runtime error) are variants of BHV-0078 but were not individually captured; unclear whether they constitute additional distinct behaviors
- Status: open
- Opened: iteration 0001
- Attempts: Lines 200–680 not fully enumerated; treated as variants of BHV-0078 during phase 3
- Resolution evidence: (none yet)
