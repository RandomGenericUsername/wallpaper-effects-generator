# Investigation: Parameter Types Bug in Layered Effects

**Date Started:** 2026-02-09
**Date Completed:** 2026-02-09
**Status:** ✅ COMPLETE - ROOT CAUSE IDENTIFIED
**Issue:** Validation errors when merging parameter_types across layers

## Symptom
Test failure: "LAYERED EFFECTS - PARAMETER TYPES ACROSS LAYERS"
Error: `Field required` for parameters using `type_ref`

## Investigation Guidelines

1. **NO ASSUMPTIONS**: Every claim must be backed by code/test evidence
2. **Document everything**: Record findings, code locations, logic flow
3. **Verify each step**: Run tests, check outputs, confirm behavior
4. **Track progress**: Update this document after each investigation step

## Investigation Loop

1. Read this document (guidelines, plan, progress)
2. Execute next investigation step
3. Document findings with evidence
4. Update progress
5. Repeat

## Current Hypothesis
**UNVERIFIED**: Parameter types from different layers are not being merged correctly

## Evidence Required
- [ ] How are parameter_types defined in each layer?
- [ ] How does the merge process work?
- [ ] Where does validation happen?
- [ ] What is the expected behavior?
- [ ] What is the actual behavior?

---

## Investigation Plan

### Phase 1: Understand the Test Setup
- [ ] Document exact config files created by test
- [ ] Document expected behavior per test code
- [ ] Identify what the test is checking

### Phase 2: Understand Parameter Types System
- [ ] Find parameter_types schema definition
- [ ] Find parameter reference (`type_ref`) schema
- [ ] Document how type_ref is supposed to work

### Phase 3: Trace the Merge Process
- [ ] Find where layers are loaded
- [ ] Find where layers are merged
- [ ] Verify parameter_types are included in merge
- [ ] Check merge order (package → project → user)

### Phase 4: Trace the Validation Process
- [ ] Find where validation happens
- [ ] Verify what validation checks
- [ ] Determine if type_ref resolution happens before validation
- [ ] Check if parameter_types context is available during validation

### Phase 5: Identify Root Cause
- [ ] Compare expected vs actual behavior
- [ ] Pinpoint exact code location of bug
- [ ] Verify with minimal reproduction

---

## Progress Log

### Session 1: Initial Setup
- Created investigation framework
- Next: Phase 1 - Understand test setup

---

## ✅ INVESTIGATION COMPLETE

### Root Cause Identified

**Bug:** Test script uses invalid field name `type_ref` instead of `type`

**Locations:**
- Line 1062: `type_ref: user_strength` → should be `type: user_strength`
- Line 1074: `type_ref: blur_geometry` → should be `type: blur_geometry`

### Evidence Summary

1. **Schema (schema.py:40):** Defines field as `type` (required)
2. **Package usage (effects.yaml):** All effects use `type:` not `type_ref:`
3. **Codebase search:** `type_ref` appears nowhere in source code
4. **Validation error:** Pydantic requires `type` field, test provides `type_ref`

### Verification Steps Taken

✅ Read schema definition
✅ Searched entire codebase for `type_ref`
✅ Checked package layer usage
✅ Examined test configuration
✅ Traced error message to schema requirement
✅ Confirmed logical chain of causation

### Fix Required

**File:** `tools/dev/test-all-commands.sh`
**Changes:** Replace `type_ref:` with `type:` on lines 1062 and 1074

**Verification:** Run test suite after fix to confirm test passes

---

## No Assumptions Made

Every conclusion is backed by code evidence:
- Schema: packages/core/src/wallpaper_core/effects/schema.py
- Usage: packages/core/src/wallpaper_core/effects/effects.yaml
- Test: tools/dev/test-all-commands.sh
- Error: Actual command output from test run

**Investigation Method:** Evidence-based, systematic, no speculation
