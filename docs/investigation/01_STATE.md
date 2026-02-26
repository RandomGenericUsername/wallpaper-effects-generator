# Investigation State

## Iteration
- Current iteration: 0001
- Phase: PHASE_8_FINALIZE_INVESTIGATION

## Progress
Completed:
- PHASE_1_INVENTORY (iteration 0001): Full file inventory, 141 in-scope files, 1 ignored.
- PHASE_2_TOPIC_MAP (iteration 0001): Topic map covering all in-scope files (141 rows), 16 distinct topics identified.
- PHASE_3_TEST_SPEC (iteration 0001): 82 behaviors extracted from 43 test files across 4 packages.
- PHASE_4_BEHAVIOR_CATALOG (iteration 0001): Publicity classifications verified. 2 reclassified. 4 unknowns resolved.
- PHASE_5_DOC_CLAIMS (iteration 0001): 107 claims extracted from 6 doc files. Verified: 75. Unverified: 32. Contradicted: 0. Notable unverified: DOC-0089 (effects.yaml path discrepancy between docs), DOC-0092 (user config path inconsistency between core README and root README), DOC-0100 (orchestrator process syntax may be outdated — positional vs flag).
- PHASE_6_TRACEABILITY (iteration 0001): Full traceability matrix built. Public BHVs: 43 (note: header says 38 — 5 additional confirmed public during this phase). Covered: 25. Partial: 7. Gaps: 11. DOC claims: 107. Verified: 75. Unverified: 32. Gap BHVs include: BHV-0028 (APP_NAME constants undocumented), BHV-0029 (DryRunBase API undocumented), BHV-0030 (ValidationCheck undocumented), BHV-0031 (effects.configure() undocumented), BHV-0035 (Effects error hierarchy undocumented), BHV-0045 (info command undocumented), BHV-0046 (version command undocumented), BHV-0048 (per-effect CLI params undocumented), BHV-0068 (orchestrator namespace config undocumented), BHV-0077 (install/uninstall dry-run undocumented), BHV-0079 (orchestrator process dry-run undocumented).
- PHASE_7_REVIEW_FINDINGS (iteration 0001): All gaps and unverified claims classified. S0: 3 (F-0001 wrong command syntax in orchestrator README; F-0002 wrong user settings path in core README; F-0003 wrong default output directory in root README). S1: 6 (F-0004 info command undocumented; F-0005 version command undocumented; F-0006 per-effect CLI params undocumented; F-0007 install/uninstall dry-run undocumented; F-0008 orchestrator process dry-run undocumented; F-0009 orchestrator namespace config undocumented). S2: 12 (F-0010 through F-0021). S3: 0.

Current focus:
- Finalize investigation: compile metrics, document next actions, close the investigation loop.
