# Investigation Findings: Parameter Types Bug

**Status:** ✅ **ROOT CAUSE IDENTIFIED**
**Last Updated:** 2026-02-09

---

## EXECUTIVE SUMMARY

### Root Cause
**Test script uses invalid field name `type_ref` instead of `type`**

**Locations:**
- `tools/dev/test-all-commands.sh:1062` - `type_ref: user_strength`
- `tools/dev/test-all-commands.sh:1074` - `type_ref: blur_geometry`

**Fix Required:**
Change `type_ref:` to `type:` in both locations

**Evidence:**
1. Schema defines field as `type` (schema.py:40)
2. Package effects use `type` not `type_ref` (effects.yaml)
3. `type_ref` does not exist anywhere in codebase
4. Pydantic validation fails because `type` field is required

---

## Evidence Chain

### E1: Schema Definition (Source of Truth)

**File:** `packages/core/src/wallpaper_core/effects/schema.py`
**Lines:** 33-47

```python
class ParameterDefinition(BaseModel):
    """Parameter definition for an effect."""

    type: str = Field(description="Reference to a parameter_type name")
    cli_flag: str | None = Field(default=None)
    default: Any = Field(default=None)
    description: str | None = Field(default=None)
```

**Key Facts:**
- ✅ Field name is `type` (line 40)
- ✅ `type` is required (no default value, not Optional)
- ❌ No field named `type_ref` exists

### E2: Package Layer Usage (Actual Usage)

**File:** `packages/core/src/wallpaper_core/effects/effects.yaml`
**Example:**

```yaml
effects:
  blur:
    parameters:
      blur:
        type: blur_geometry    # Uses 'type'
        cli_flag: "--blur"
```

**Key Facts:**
- ✅ All effects use `type:` field
- ❌ Zero uses of `type_ref:` in codebase

**Verification:**
```bash
$ grep -r "type_ref" packages/*/src --include="*.py"
# No results

$ grep -r "type_ref" packages/*/src --include="*.yaml"
# No results
```

### E3: Test Configuration (The Bug)

**File:** `tools/dev/test-all-commands.sh`
**Lines:** 1062, 1074

```bash
# Line 1062 - User layer
parameters:
  user_strength:
    type_ref: user_strength    # ❌ WRONG - should be 'type'

# Line 1074 - Project layer
parameters:
  blur:
    type_ref: blur_geometry    # ❌ WRONG - should be 'type'
```

**Key Facts:**
- ❌ Uses `type_ref` (invalid field)
- ❌ Missing required `type` field
- ✅ Causes Pydantic validation error

### E4: Validation Error (Observed Behavior)

**Command:**
```bash
cd /tmp/wallpaper-effects-test/params-project && \
XDG_CONFIG_HOME=/tmp/wallpaper-effects-test/params-user \
wallpaper-core show effects
```

**Error:**
```
✗ Error: Effects configuration validation failed
✗ Error: Layer: merged
✗ Error: Problem: 2 validation errors for EffectsConfig
effects.project_effect_with_package_param.parameters.blur.type
  Field required
effects.user_effect_with_param.parameters.user_strength.type
  Field required
```

**Key Facts:**
- ✅ Error says `type` field is required
- ✅ Validation happens on merged layer
- ✅ Both parameters fail (user + project)
- ✅ Confirms schema requires `type` field

---

## Logical Chain

1. **Schema defines** `ParameterDefinition.type` as required field
2. **Package uses** `type:` correctly in all effects
3. **Test uses** `type_ref:` incorrectly
4. **Pydantic validates** against schema
5. **Validation fails** because `type` field is missing
6. **Error message** says "Field required: type"

**Conclusion:** Test has a typo/bug. Field should be `type` not `type_ref`.

---

## Fix Specification

**File:** `tools/dev/test-all-commands.sh`

**Line 1062:** Change from:
```yaml
parameters:
  user_strength:
    type_ref: user_strength
```

To:
```yaml
parameters:
  user_strength:
    type: user_strength
```

**Line 1074:** Change from:
```yaml
parameters:
  blur:
    type_ref: blur_geometry
```

To:
```yaml
parameters:
  blur:
    type: blur_geometry
```

---

## Verification Plan

After fix:
1. ✅ Run test: `./tools/dev/test-all-commands.sh ~/Downloads/wallpaper.jpg`
2. ✅ Verify "LAYERED EFFECTS - PARAMETER TYPES" test passes
3. ✅ Confirm no validation errors
4. ✅ Check effects can be listed from all layers

---

## Investigation Complete

**Time Invested:** 1 session
**Method:** Systematic evidence-based investigation
**Assumptions Made:** 0
**Evidence Collected:** 4 documents
**Root Cause:** Confirmed with code references
