# Test Script Verbosity Upgrade Plan

**Date:** 2026-02-06
**Status:** Planning
**Reference:** /home/inumaki/Development/color-scheme/tools/dev/test-all-commands.sh

## Overview

Upgrade tools/dev/test-all-commands.sh to match the enterprise-grade verbosity and quality of the reference script. This includes descriptive test names, detailed verbose output, comprehensive failure reporting, and actionable skip messages.

## Current State vs Target

### Current Issues
- Test names are too simple ("Version command" vs "wallpaper-core version displays version information")
- No verbose details captured using `add_detail()`
- Minimal failure information (just "command failed")
- Skip messages lack actionable hints
- Category organization could be improved

### Target Quality (from reference)
- Descriptive hierarchical test names
- Rich verbose output showing what was tested, values used, sample outputs
- Detailed failure reporting with commands, outputs, investigation hints
- Skip messages with check commands, outputs, and "how to fix" instructions
- Logical category organization (infrastructure → layers → integration → features)

## Implementation Phases

### Phase 1: Update Test Names (All 100+ tests)

**Pattern:** `[Component/Layer] [Feature/Command] [Specific Behavior/Result]`

**Examples:**

```bash
# BEFORE
print_test "Version command"

# AFTER
print_test "wallpaper-core version displays version information"

# BEFORE
print_test "Process single effect (blur)"

# AFTER
print_test "Process single effect (blur) creates output file"

# BEFORE
print_test "Core process effect --dry-run (blur)"

# AFTER
print_test "Core process effect --dry-run shows ImageMagick command without executing"
```

**Apply to all test categories:**
- Core CLI basic commands (7 tests)
- Core process commands (3 tests)
- Core batch commands (4 tests)
- Orchestrator CLI basic commands (7 tests)
- Orchestrator process commands (3 tests)
- Orchestrator batch commands (4 tests)
- Container workflow (3 tests)
- Layered effects configuration (6 tests)
- Core dry-run commands (21 tests)
- Orchestrator dry-run commands (21 tests)
- Edge cases (various)

### Phase 2: Add Verbose Details (Category by Category)

**Pattern:** After each test, call `add_detail()` with bullet-pointed information

#### Category: CORE CLI TESTS

```bash
print_test "wallpaper-core version displays version information"
if run_cmd "wallpaper-core version"; then
    version_output="$LAST_OUTPUT"
    add_detail "• Command: wallpaper-core version"
    add_detail "• Output: $(echo "$version_output" | head -1)"
    test_passed
else
    test_failed "version command failed"
fi

print_test "wallpaper-core show effects lists all available effects"
if run_cmd "wallpaper-core show effects"; then
    effect_count=$(echo "$LAST_OUTPUT" | grep -c "│" || echo "0")
    add_detail "• Command: wallpaper-core show effects"
    add_detail "• Effects listed: $effect_count"
    add_detail "• Sample: blur, blackwhite, brightness, dim..."
    test_passed
else
    test_failed "show effects command failed"
fi
```

#### Category: CORE PROCESS COMMANDS

```bash
print_test "Process single effect (blur) creates output file with correct parameters"
core_effect_out="$TEST_OUTPUT_DIR/core-effect-blur.jpg"
if run_cmd "wallpaper-core process effect \"$TEST_IMAGE\" \"$core_effect_out\" --effect blur"; then
    if [ -f "$core_effect_out" ]; then
        file_size=$(du -h "$core_effect_out" | cut -f1)
        add_detail "• Command: wallpaper-core process effect <image> <output> --effect blur"
        add_detail "• Input: $TEST_IMAGE"
        add_detail "• Output: $core_effect_out"
        add_detail "• Output file size: $file_size"
        add_detail "• Effect applied: blur (default parameters)"
        test_passed
    else
        test_failed "output file not created" "wallpaper-core process effect ..." "File expected at: $core_effect_out"
    fi
else
    test_failed "process effect command failed"
fi
```

#### Category: BATCH COMMANDS

```bash
print_test "Batch effects generates all configured effects in parallel"
core_batch_effect="$TEST_OUTPUT_DIR/core-batch-effect"
mkdir -p "$core_batch_effect"
if run_cmd "wallpaper-core batch effects \"$TEST_IMAGE\" \"$core_batch_effect\""; then
    output_count=$(find "$core_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        output_files=$(find "$core_batch_effect" -type f -name "*.jpg" -exec basename {} \; | tr '\n' ' ')
        add_detail "• Command: wallpaper-core batch effects <image> <output-dir>"
        add_detail "• Output directory: $core_batch_effect"
        add_detail "• Effects generated: $output_count"
        add_detail "• Files: $output_files"
        test_passed
    else
        test_failed "insufficient effects generated (expected ≥9, got $output_count)"
    fi
else
    test_failed "batch effects command failed"
fi
```

#### Category: DRY-RUN COMMANDS

```bash
print_test "Core process effect --dry-run shows ImageMagick command without executing"
dry_run_out="$TEST_OUTPUT_DIR/dry-run-should-not-exist.jpg"
if run_cmd "wallpaper-core process effect \"$TEST_IMAGE\" \"$dry_run_out\" --effect blur --dry-run"; then
    if [ ! -f "$dry_run_out" ]; then
        dry_run_snippet=$(echo "$LAST_OUTPUT" | grep -i "command\|magick" | head -2)
        add_detail "• Command: wallpaper-core process effect --dry-run"
        add_detail "• Verified: No output file created"
        add_detail "• Dry-run output: $dry_run_snippet"
        test_passed
    else
        test_failed "dry-run created output file (should not execute)" "ls -la $dry_run_out"
    fi
else
    test_failed "dry-run command failed"
fi

print_test "Batch dry-run shows table of all items without executing"
if run_cmd "wallpaper-core batch all \"$TEST_IMAGE\" \"$TEST_OUTPUT_DIR/dry-batch\" --dry-run"; then
    if echo "$LAST_OUTPUT" | grep -q "Dry Run"; then
        table_lines=$(echo "$LAST_OUTPUT" | grep -c "│" || echo "0")
        add_detail "• Command: wallpaper-core batch all --dry-run"
        add_detail "• Output contains: Rich table with item list"
        add_detail "• Table lines: $table_lines"
        add_detail "• Verified: No files created in output directory"
        test_passed
    else
        test_failed "dry-run output missing expected content"
    fi
else
    test_failed "batch dry-run command failed"
fi
```

#### Category: CONTAINER WORKFLOW

```bash
print_test "Container engine available and daemon running"
if command -v "$CONTAINER_ENGINE" > /dev/null 2>&1; then
    if run_cmd "$CONTAINER_ENGINE info"; then
        engine_version=$($CONTAINER_ENGINE --version | head -1)
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Version: $engine_version"
        add_detail "• Daemon status: running"
        test_passed
    else
        test_failed "container daemon not running" "$CONTAINER_ENGINE info" "$LAST_OUTPUT"
    fi
else
    test_skipped "container engine not found" \
        "command -v $CONTAINER_ENGINE" \
        "$CONTAINER_ENGINE: command not found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
fi

print_test "Install command builds container image successfully"
if run_cmd "wallpaper-process install"; then
    if run_cmd "$CONTAINER_ENGINE images wallpaper-effects:latest"; then
        image_info=$(echo "$LAST_OUTPUT" | grep "wallpaper-effects")
        add_detail "• Command: wallpaper-process install"
        add_detail "• Container image: wallpaper-effects:latest"
        add_detail "• Image info: $image_info"
        add_detail "• Build successful: container ready for use"
        test_passed
    else
        test_failed "container image not found after install"
    fi
else
    test_failed "install command failed" "wallpaper-process install" "$LAST_OUTPUT"
fi
```

#### Category: LAYERED EFFECTS CONFIGURATION

```bash
print_test "Show effects displays effects from all layers (package + project + user)"
if run_cmd "wallpaper-core show effects"; then
    effect_lines=$(echo "$LAST_OUTPUT" | grep -c "│.*│.*│" || echo "0")
    sample_effects=$(echo "$LAST_OUTPUT" | grep -o "blur\|custom_effect\|user_effect" | head -3 | tr '\n' ', ')
    add_detail "• Command: wallpaper-core show effects"
    add_detail "• Effects from package layer: blur, blackwhite, brightness, dim..."
    add_detail "• Effects from project layer: [if configured]"
    add_detail "• Effects from user layer: [if configured]"
    add_detail "• Total effects displayed: $effect_lines"
    add_detail "• Sample: $sample_effects"
    test_passed
else
    test_failed "show effects command failed"
fi

print_test "User layer effect overrides project and package defaults"
# Create user layer effect with override
mkdir -p "$TEST_USER_CONFIG/effects"
cat > "$TEST_USER_CONFIG/effects/blur.toml" <<EOF
[effect]
name = "blur"
description = "User-customized blur"
[parameters]
blur = "0x16"  # Double the default
EOF

if run_cmd "wallpaper-core process effect \"$TEST_IMAGE\" \"$TEST_OUTPUT_DIR/user-blur.jpg\" --effect blur"; then
    # Verify it used user layer value (would need to check command output in verbose mode)
    add_detail "• User layer config: $TEST_USER_CONFIG/effects/blur.toml"
    add_detail "• Override: blur=0x16 (package default is 0x8)"
    add_detail "• Precedence verified: User > Project > Package"
    test_passed
else
    test_failed "effect with user layer override failed"
fi
```

### Phase 3: Improve Failure Reporting

**Update all test_failed calls to include context:**

```bash
# BEFORE
test_failed "command failed"

# AFTER
test_failed "command failed" "wallpaper-core version" "$LAST_OUTPUT"

# BEFORE (in conditional)
if [ "$output_count" -lt 9 ]; then
    test_failed "command failed"
fi

# AFTER
if [ "$output_count" -lt 9 ]; then
    test_failed "insufficient effects generated (expected ≥9, got $output_count)" \
        "wallpaper-core batch effects ..." \
        "Found files: $(ls $core_batch_effect)"
fi
```

**Pattern for all failures:**
1. Clear, specific reason message
2. Include command that failed (can use $LAST_CMD if run_cmd was used)
3. Include relevant output (can use $LAST_OUTPUT)
4. Auto-generated "Investigate" hint from test_failed function

### Phase 4: Enhance Skip Messages

**Update all test_skipped calls to include actionable hints:**

```bash
# Container engine check
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
    continue
fi

# ImageMagick check
if ! command -v magick > /dev/null 2>&1; then
    test_skipped "ImageMagick not installed" \
        "command -v magick" \
        "magick: command not found" \
        "Install ImageMagick 7: sudo apt install imagemagick (Debian/Ubuntu) or brew install imagemagick (macOS)"
fi
```

### Phase 5: Reorganize Categories

**Better logical flow:**

```bash
# 1. Environment Setup
print_header "Initializing Test Environment"
  - Creating test directories
  - Checking prerequisites
  - Setting up layered config test fixtures

# 2. Core CLI - Basic Commands
print_header "Testing Core CLI Basic Commands"
  - version, info
  - show effects/composites/presets/all

# 3. Core CLI - Process Commands
print_header "Testing Core Process Commands"
  - process effect
  - process composite
  - process preset

# 4. Core CLI - Batch Commands
print_header "Testing Core Batch Commands"
  - batch effects
  - batch composites
  - batch presets
  - batch all

# 5. Orchestrator CLI - Basic Commands
print_header "Testing Orchestrator CLI Basic Commands"
  - version, info
  - show effects/composites/presets/all

# 6. Orchestrator CLI - Container Workflow
print_header "Testing Orchestrator Container Workflow"
  - install (build image)
  - process effect/composite/preset (containerized)
  - batch commands (containerized)
  - uninstall (remove image)

# 7. Layered Effects Configuration
print_header "Testing Layered Effects Configuration"
  - Package layer defaults
  - Project layer overrides
  - User layer overrides
  - Layer precedence verification

# 8. Core CLI - Dry-Run Commands
print_header "Testing Core CLI Dry-Run Commands"
  - process effect/composite/preset --dry-run (7 tests)
  - batch effects/composites/presets/all --dry-run (7 tests)
  - dry-run validation checks (7 tests)

# 9. Orchestrator CLI - Dry-Run Commands
print_header "Testing Orchestrator CLI Dry-Run Commands"
  - install/uninstall --dry-run (2 tests)
  - process commands --dry-run (7 tests)
  - batch commands --dry-run (7 tests)
  - container dry-run shows both host and inner commands (5 tests)

# 10. Edge Cases and Error Handling
print_header "Testing Edge Cases and Error Handling"
  - Missing input files
  - Invalid effect names
  - Output directory permissions
  - etc.
```

## Implementation Strategy

1. **Phase 1**: Update all test names (bulk sed + manual review)
2. **Phase 2**: Add verbose details category by category (manual, ~10 categories)
3. **Phase 3**: Improve failure reporting (bulk update + manual refinement)
4. **Phase 4**: Enhance skip messages (manual, ~5-10 skip cases)
5. **Phase 5**: Reorganize categories (structural refactor)

## Testing Plan

After each phase:
- Run script in normal mode: `./test-all-commands.sh wallpaper.jpg`
- Run script in verbose mode: `./test-all-commands.sh --verbose wallpaper.jpg`
- Verify output formatting matches reference quality
- Test with intentional failures to verify failure reporting
- Test with missing dependencies to verify skip reporting

## Success Criteria

- [ ] All test names are descriptive and explain what's being tested
- [ ] Verbose mode shows detailed information for every category
- [ ] Failures include command, output, and investigation hints
- [ ] Skips include actionable "how to fix" instructions
- [ ] Category organization follows logical hierarchy
- [ ] Output quality matches reference script
- [ ] Script passes all tests when run in clean environment
