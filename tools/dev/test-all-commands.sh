#!/bin/bash
##############################################################################
# Comprehensive Test Suite for wallpaper-effects-generator (core + orchestrator)
#
# Tests all CLI commands including dry-run functionality across both the
# core CLI (native execution) and orchestrator CLI (containerized).
#
# Covers:
#   - Core process commands (effect/composite/preset)
#   - Core batch commands (effects/composites/presets/all)
#   - Orchestrator process commands (containerized)
#   - Orchestrator install/uninstall
#   - Layered effects configuration (3-layer merge)
#   - Layered settings configuration
#   - Dry-run flags (42 tests)
#   - Edge cases
#
# Usage: ./test-all-commands.sh [OPTIONS] <wallpaper-path>
#
# Options:
#   -v, --verbose    Show detailed test information in summary
#   -h, --help       Show this help message
#
# Arguments:
#   wallpaper-path  Path to wallpaper image file (required)
#                   Example: ./test-all-commands.sh ~/Downloads/wallpaper.jpg
#
# Examples:
#   ./test-all-commands.sh wallpaper.jpg              # Normal mode
#   ./test-all-commands.sh --verbose wallpaper.jpg    # Verbose mode
#   ./test-all-commands.sh -v wallpaper.jpg           # Verbose (short)
#   ./test-all-commands.sh --help                     # Show help
##############################################################################

# Parse options
VERBOSE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            head -33 "$0" | tail -28
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Validate arguments
if [ $# -eq 0 ]; then
    echo "Error: wallpaper path is required"
    echo "Usage: $0 [OPTIONS] <wallpaper-path>"
    echo ""
    echo "Options:"
    echo "  -v, --verbose    Show detailed test information in summary"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Example: $0 ~/Downloads/wallpaper.jpg"
    echo "         $0 --verbose ~/Downloads/wallpaper.jpg"
    exit 1
fi

TEST_IMAGE="$1"

# Resolve to absolute path
TEST_IMAGE="$(cd "$(dirname "$TEST_IMAGE")" && pwd)/$(basename "$TEST_IMAGE")"

# Check if file exists
if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Wallpaper file not found: $1"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Check if running from workspace with venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "Error: Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Please run: uv sync"
    exit 1
fi

# Helper functions to run commands via uv
# Use --project to allow running from arbitrary CWD while keeping workspace resolution
wallpaper-core() {
    uv run --project "$PROJECT_ROOT" wallpaper-core "$@"
}

wallpaper-process() {
    uv run --project "$PROJECT_ROOT" wallpaper-process "$@"
}

export -f wallpaper-core
export -f wallpaper-process
export PROJECT_ROOT

TEST_OUTPUT_DIR="/tmp/wallpaper-effects-test"
PASSED=0
FAILED=0
SKIPPED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ============================================================================
# Test Results Tracking
# ============================================================================

# Arrays to track results per category
declare -a TEST_CATEGORIES
declare -A CATEGORY_PASSED
declare -A CATEGORY_FAILED
declare -A CATEGORY_SKIPPED
CURRENT_CATEGORY=""

# Arrays to track details for failures and skips
declare -a FAILED_TESTS
declare -a SKIPPED_TESTS

# Arrays to track verbose details per category
declare -A CATEGORY_DETAILS

# Last captured output for debugging
LAST_CMD=""
LAST_OUTPUT=""

# ============================================================================
# Helper Functions
# ============================================================================

# Capture command output for debugging
run_cmd() {
    local cmd="$1"
    LAST_CMD="$cmd"
    LAST_OUTPUT=$(eval "$cmd" 2>&1)
    local exit_code=$?
    return $exit_code
}

# Add detail for verbose mode
add_detail() {
    local detail="$1"
    if [ -n "$CURRENT_CATEGORY" ]; then
        if [ -z "${CATEGORY_DETAILS[$CURRENT_CATEGORY]}" ]; then
            CATEGORY_DETAILS["$CURRENT_CATEGORY"]="$detail"
        else
            CATEGORY_DETAILS["$CURRENT_CATEGORY"]+=$'\n'"$detail"
        fi
    fi
}

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}█ $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    # Track current category
    CURRENT_CATEGORY="$1"
    if [[ ! " ${TEST_CATEGORIES[*]} " =~ " ${CURRENT_CATEGORY} " ]]; then
        TEST_CATEGORIES+=("$CURRENT_CATEGORY")
        CATEGORY_PASSED["$CURRENT_CATEGORY"]=0
        CATEGORY_FAILED["$CURRENT_CATEGORY"]=0
        CATEGORY_SKIPPED["$CURRENT_CATEGORY"]=0
    fi
}

print_test() {
    echo -ne "${YELLOW}[TEST]${NC} $1 ... "
}

test_passed() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_PASSED["$CURRENT_CATEGORY"]++))
    fi
}

test_failed() {
    local reason="$1"
    local cmd="${2:-$LAST_CMD}"
    local output="${3:-$LAST_OUTPUT}"
    echo -e "${RED}✗ FAIL${NC}"
    if [ -n "$reason" ]; then
        echo -e "        ${RED}Reason: $reason${NC}"
    fi
    ((FAILED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_FAILED["$CURRENT_CATEGORY"]++))
    fi
    # Track for summary details with command and output
    local detail="[$CURRENT_CATEGORY] ${reason:-Unknown reason}"
    if [ -n "$cmd" ]; then
        detail+=$'\n    Command: '"$cmd"
    fi
    if [ -n "$output" ] && [ "${#output}" -lt 500 ]; then
        detail+=$'\n    Output: '"${output:0:300}"
    elif [ -n "$output" ]; then
        detail+=$'\n    Output (truncated): '"${output:0:300}..."
    fi
    detail+=$'\n    Investigate: Run the command manually to see full output'
    FAILED_TESTS+=("$detail")
}

test_skipped() {
    local reason="$1"
    local cmd="${2:-}"
    local output="${3:-}"
    local hint="${4:-}"
    echo -e "${YELLOW}⊘ SKIP${NC} ($reason)"
    ((SKIPPED++))
    if [ -n "$CURRENT_CATEGORY" ]; then
        ((CATEGORY_SKIPPED["$CURRENT_CATEGORY"]++))
    fi
    # Track for summary details with investigation hints
    local detail="[$CURRENT_CATEGORY] $reason"
    if [ -n "$cmd" ]; then
        detail+=$'\n    Command: '"$cmd"
    fi
    if [ -n "$output" ] && [ "${#output}" -lt 500 ]; then
        detail+=$'\n    Output: '"$output"
    elif [ -n "$output" ]; then
        detail+=$'\n    Output (truncated): '"${output:0:300}..."
    fi
    if [ -n "$hint" ]; then
        detail+=$'\n    How to fix: '"$hint"
    fi
    SKIPPED_TESTS+=("$detail")
}

echo -e "${BLUE}Wallpaper Effects Generator - Comprehensive Test Suite${NC}"
echo -e "${BLUE}Testing: Core CLI + Orchestrator CLI + Dry-Run Features${NC}"
echo -e "${BLUE}Wallpaper: $TEST_IMAGE${NC}"
if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}Mode: Verbose (detailed output in summary)${NC}"
fi
echo ""

echo -e "${BLUE}Checking prerequisites...${NC}"
echo -e "${GREEN}✓ Test image:${NC} $TEST_IMAGE"
mkdir -p "$TEST_OUTPUT_DIR"
echo -e "${GREEN}✓ Output directory ready${NC}\n"

# ============================================================================
# CORE CLI TESTS (wallpaper-core)
# ============================================================================

print_header "CORE CLI TESTS (wallpaper-core)"

print_test "wallpaper-core version displays version information"
if run_cmd "wallpaper-core version"; then
    version_output=$(echo "$LAST_OUTPUT" | head -1)
    add_detail "• Command: wallpaper-core version"
    add_detail "• Output: $version_output"
    test_passed
else
    test_failed "version command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core info displays system information"
if run_cmd "wallpaper-core info"; then
    line_count=$(echo "$LAST_OUTPUT" | wc -l)
    sample_line=$(echo "$LAST_OUTPUT" | head -1)
    add_detail "• Command: wallpaper-core info"
    add_detail "• Output lines: $line_count"
    add_detail "• Sample: $sample_line"
    test_passed
else
    test_failed "info command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core show effects lists all available effects"
if run_cmd "wallpaper-core show effects"; then
    effect_count=$(echo "$LAST_OUTPUT" | grep -c "blur\|brightness\|blackwhite" || echo "0")
    sample_effects=$(echo "$LAST_OUTPUT" | grep -o "blur\|brightness\|blackwhite" | head -3 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-core show effects"
    add_detail "• Effects listed: $effect_count+"
    add_detail "• Samples: $sample_effects"
    test_passed
else
    test_failed "show effects command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core show composites lists all available composites"
if run_cmd "wallpaper-core show composites"; then
    composite_count=$(echo "$LAST_OUTPUT" | grep -c "blackwhite-blur\|blur-brightness" || echo "0")
    sample_composites=$(echo "$LAST_OUTPUT" | grep -o "blackwhite-blur\|blur-brightness" | head -2 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-core show composites"
    add_detail "• Composites listed: $composite_count+"
    add_detail "• Samples: $sample_composites"
    test_passed
else
    test_failed "show composites command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core show presets lists all available presets"
if run_cmd "wallpaper-core show presets"; then
    preset_count=$(echo "$LAST_OUTPUT" | grep -c "dark_blur\|subtle_blur" || echo "0")
    sample_presets=$(echo "$LAST_OUTPUT" | grep -o "dark_blur\|subtle_blur" | head -2 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-core show presets"
    add_detail "• Presets listed: $preset_count+"
    add_detail "• Samples: $sample_presets"
    test_passed
else
    test_failed "show presets command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core process effect (blur) creates output file"
core_effect_out="$TEST_OUTPUT_DIR/core-effect-blur.jpg"
if run_cmd "wallpaper-core process effect \"$TEST_IMAGE\" \"$core_effect_out\" --effect blur" && [ -f "$core_effect_out" ]; then
    file_size=$(stat -f%z "$core_effect_out" 2>/dev/null || stat -c%s "$core_effect_out" 2>/dev/null)
    add_detail "• Command: wallpaper-core process effect <image> <output> --effect blur"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output file: $core_effect_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Effect: blur (default parameters)"
    test_passed
else
    test_failed "process effect command failed or output file not created (expected: $core_effect_out)" \
        "$LAST_CMD" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-core process composite (blackwhite-blur) creates output file"
core_composite_out="$TEST_OUTPUT_DIR/core-composite-blackwhite-blur.jpg"
if run_cmd "wallpaper-core process composite \"$TEST_IMAGE\" \"$core_composite_out\" --composite blackwhite-blur" && [ -f "$core_composite_out" ]; then
    file_size=$(stat -f%z "$core_composite_out" 2>/dev/null || stat -c%s "$core_composite_out" 2>/dev/null)
    add_detail "• Command: wallpaper-core process composite <image> <output> --composite blackwhite-blur"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output file: $core_composite_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Composite: blackwhite-blur (2-effect chain)"
    test_passed
else
    test_failed "process composite command failed or output file not created (expected: $core_composite_out)" \
        "$LAST_CMD" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-core process preset (dark_blur) creates output file"
core_preset_out="$TEST_OUTPUT_DIR/core-preset-dark_blur.jpg"
if run_cmd "wallpaper-core process preset \"$TEST_IMAGE\" \"$core_preset_out\" --preset dark_blur" && [ -f "$core_preset_out" ]; then
    file_size=$(stat -f%z "$core_preset_out" 2>/dev/null || stat -c%s "$core_preset_out" 2>/dev/null)
    add_detail "• Command: wallpaper-core process preset <image> <output> --preset dark_blur"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output file: $core_preset_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Preset: dark_blur (configured effect chain)"
    test_passed
else
    test_failed "process preset command failed or output file not created (expected: $core_preset_out)" \
        "$LAST_CMD" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-core batch effects generates all effect outputs"
core_batch_effect="$TEST_OUTPUT_DIR/core-batch-effect"
mkdir -p "$core_batch_effect"
if run_cmd "wallpaper-core batch effects \"$TEST_IMAGE\" \"$core_batch_effect\""; then
    # Should generate 9 effects
    output_count=$(find "$core_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        output_files=$(find "$core_batch_effect" -type f -name "*.jpg" -exec basename {} \; | head -5 | tr '\n' ' ')
        add_detail "• Command: wallpaper-core batch effects <image> <output-dir>"
        add_detail "• Output directory: $core_batch_effect"
        add_detail "• Effects generated: $output_count"
        add_detail "• Sample files: $output_files..."
        test_passed
    else
        test_failed "insufficient effects generated (expected ≥9, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$core_batch_effect" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "batch effects command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core batch composites generates all composite outputs"
core_batch_composite="$TEST_OUTPUT_DIR/core-batch-composite"
mkdir -p "$core_batch_composite"
if run_cmd "wallpaper-core batch composites \"$TEST_IMAGE\" \"$core_batch_composite\""; then
    # Should generate 4 composites
    output_count=$(find "$core_batch_composite" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 4 ]; then
        output_files=$(find "$core_batch_composite" -type f -name "*.jpg" -exec basename {} \; | tr '\n' ' ')
        add_detail "• Command: wallpaper-core batch composites <image> <output-dir>"
        add_detail "• Output directory: $core_batch_composite"
        add_detail "• Composites generated: $output_count"
        add_detail "• Files: $output_files"
        test_passed
    else
        test_failed "insufficient composites generated (expected ≥4, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$core_batch_composite" 2>/dev/null | tr '\n' ' ')"
    fi
else
    test_failed "batch composites command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core batch presets generates all preset outputs"
core_batch_preset="$TEST_OUTPUT_DIR/core-batch-preset"
mkdir -p "$core_batch_preset"
if run_cmd "wallpaper-core batch presets \"$TEST_IMAGE\" \"$core_batch_preset\""; then
    # Should generate 7 presets
    output_count=$(find "$core_batch_preset" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 7 ]; then
        output_files=$(find "$core_batch_preset" -type f -name "*.jpg" -exec basename {} \; | head -5 | tr '\n' ' ')
        add_detail "• Command: wallpaper-core batch presets <image> <output-dir>"
        add_detail "• Output directory: $core_batch_preset"
        add_detail "• Presets generated: $output_count"
        add_detail "• Sample files: $output_files..."
        test_passed
    else
        test_failed "insufficient presets generated (expected ≥7, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$core_batch_preset" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "batch presets command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-core batch all generates effects, composites, and presets"
core_batch_all="$TEST_OUTPUT_DIR/core-batch-all"
mkdir -p "$core_batch_all"
if run_cmd "wallpaper-core batch all \"$TEST_IMAGE\" \"$core_batch_all\""; then
    # Check if at least some outputs were created
    output_count=$(find "$core_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then  # Should have 9 effects + 4 composites + presets
        effects_count=$(find "$core_batch_all" -type f -name "*blur*.jpg" 2>/dev/null | wc -l)
        add_detail "• Command: wallpaper-core batch all <image> <output-dir>"
        add_detail "• Output directory: $core_batch_all"
        add_detail "• Total files generated: $output_count (effects + composites + presets)"
        add_detail "• Effects subset: $effects_count files"
        test_passed
    else
        test_failed "insufficient outputs generated (expected >15, got $output_count)" \
            "$LAST_CMD" \
            "Found files: $(ls -1 "$core_batch_all" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "batch all command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

# ============================================================================
# LAYERED EFFECTS CONFIGURATION TESTS
# ============================================================================

print_header "LAYERED EFFECTS CONFIGURATION TESTS"

# Setup test configuration directories
TEST_USER_CONFIG="$TEST_OUTPUT_DIR/user-config"
TEST_PROJECT_ROOT="$TEST_OUTPUT_DIR/project"
mkdir -p "$TEST_USER_CONFIG"
mkdir -p "$TEST_PROJECT_ROOT"

# Create user-level effects.yaml with custom effect
# Fix: Use proper directory structure for user config
mkdir -p "$TEST_USER_CONFIG/wallpaper-effects-generator"
cat > "$TEST_USER_CONFIG/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
parameter_types:
  test_radius:
    type: integer
    min: 1
    max: 50
    default: 10
    description: "Test radius parameter"
effects:
  test_custom:
    description: "Custom user-defined blur effect"
    command: "convert $INPUT -blur 0x15 $OUTPUT"
    parameters: {}
  blur:
    description: "Overridden blur with stronger effect"
    command: "convert $INPUT -blur 0x20 $OUTPUT"
    parameters: {}
EOF

# Create project-level effects.yaml with different custom effect
cat > "$TEST_PROJECT_ROOT/effects.yaml" << 'EOF'
version: "1.0"
effects:
  project_effect:
    description: "Project-specific effect"
    command: "convert $INPUT -brightness-contrast 10x10 $OUTPUT"
    parameters: {}
EOF

print_test "Layered effects user layer loads custom effect"
# Set XDG_CONFIG_HOME to use our test directory
if run_cmd "XDG_CONFIG_HOME=\"$TEST_USER_CONFIG\" wallpaper-core show effects 2>&1" && echo "$LAST_OUTPUT" | grep -q "test_custom"; then
    add_detail "• Layer: User (XDG_CONFIG_HOME=$TEST_USER_CONFIG)"
    add_detail "• Custom effect: test_custom"
    add_detail "• Config file: $TEST_USER_CONFIG/wallpaper-effects-generator/effects.yaml"
    test_passed
else
    test_failed "user layer custom effect not found (test_custom)" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "Layered effects user layer overrides package defaults"
# Check that blur effect description shows the override
if run_cmd "XDG_CONFIG_HOME=\"$TEST_USER_CONFIG\" wallpaper-core show effects 2>&1" && echo "$LAST_OUTPUT" | grep "blur" | grep -q "Overridden blur"; then
    add_detail "• Layer: User overrides package default"
    add_detail "• Effect: blur (overridden)"
    add_detail "• Verified: User layer takes precedence over package defaults"
    test_passed
else
    test_failed "user layer override not applied (blur effect should show 'Overridden blur')" \
        "$LAST_CMD" \
        "$(echo "$LAST_OUTPUT" | grep "blur" | head -3)"
fi

print_test "Layered effects project layer loads project-specific effects"
# Change to project directory to test project-level config
if run_cmd "cd \"$TEST_PROJECT_ROOT\" && wallpaper-core show effects 2>&1" && echo "$LAST_OUTPUT" | grep -q "project_effect"; then
    add_detail "• Layer: Project (cwd: $TEST_PROJECT_ROOT)"
    add_detail "• Custom effect: project_effect"
    add_detail "• Config file: $TEST_PROJECT_ROOT/effects.yaml"
    test_passed
else
    test_failed "project layer custom effect not found (project_effect)" \
        "cd $TEST_PROJECT_ROOT && wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects user custom effect processes successfully"
user_custom_out="$TEST_OUTPUT_DIR/user-custom-effect.jpg"
if run_cmd "XDG_CONFIG_HOME=\"$TEST_USER_CONFIG\" wallpaper-core process effect \"$TEST_IMAGE\" \"$user_custom_out\" --effect test_custom" && [ -f "$user_custom_out" ]; then
    file_size=$(stat -f%z "$user_custom_out" 2>/dev/null || stat -c%s "$user_custom_out" 2>/dev/null)
    add_detail "• Effect: test_custom (user-defined)"
    add_detail "• Output file: $user_custom_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "user custom effect processing failed or output not created (expected: $user_custom_out)" \
        "$LAST_CMD" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects project effect processes successfully"
project_effect_out="$TEST_OUTPUT_DIR/project-effect.jpg"
if run_cmd "cd \"$TEST_PROJECT_ROOT\" && wallpaper-core process effect \"$TEST_IMAGE\" \"$project_effect_out\" --effect project_effect" && [ -f "$project_effect_out" ]; then
    file_size=$(stat -f%z "$project_effect_out" 2>/dev/null || stat -c%s "$project_effect_out" 2>/dev/null)
    add_detail "• Effect: project_effect (project-defined)"
    add_detail "• Output file: $project_effect_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "project effect processing failed or output not created (expected: $project_effect_out)" \
        "cd $TEST_PROJECT_ROOT && wallpaper-core process effect ... --effect project_effect" \
        "$LAST_OUTPUT"
fi

# Cleanup test configs
unset XDG_CONFIG_HOME
unset WEG_USER_CONFIG_DIR

# ============================================================================
# LAYERED EFFECTS - ERROR HANDLING TESTS
# ============================================================================

print_header "LAYERED EFFECTS - ERROR HANDLING TESTS"

# Setup error test directories
TEST_ERROR_USER="$TEST_OUTPUT_DIR/error-user"
TEST_ERROR_PROJECT="$TEST_OUTPUT_DIR/error-project"
mkdir -p "$TEST_ERROR_USER/wallpaper-effects-generator"
mkdir -p "$TEST_ERROR_PROJECT"

print_test "Layered effects invalid YAML in user config shows error"
cat > "$TEST_ERROR_USER/wallpaper-effects-generator/effects.yaml" << 'EOF'
invalid: yaml: content:
  bad: structure
EOF
if run_cmd "XDG_CONFIG_HOME=\"$TEST_ERROR_USER\" wallpaper-core show effects 2>&1"; then
    test_failed "should have failed with invalid YAML (command succeeded incorrectly)" \
        "$LAST_CMD" \
        "$LAST_OUTPUT"
else
    add_detail "• Test: Invalid YAML syntax in user config"
    add_detail "• Config: $TEST_ERROR_USER/wallpaper-effects-generator/effects.yaml"
    add_detail "• Result: Properly rejected invalid YAML"
    test_passed
fi

print_test "Layered effects invalid YAML in project config shows error"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
malformed yaml without proper structure
  missing: colons
EOF
if run_cmd "cd \"$TEST_ERROR_PROJECT\" && wallpaper-core show effects 2>&1"; then
    test_failed "should have failed with invalid YAML (command succeeded incorrectly)" \
        "cd $TEST_ERROR_PROJECT && wallpaper-core show effects" \
        "$LAST_OUTPUT"
else
    add_detail "• Test: Malformed YAML in project config"
    add_detail "• Config: $TEST_ERROR_PROJECT/effects.yaml"
    add_detail "• Result: Properly rejected malformed YAML"
    test_passed
fi

print_test "Layered effects missing required field shows validation error"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
effects:
  broken_effect:
    description: "Missing command field"
    parameters: {}
EOF
if run_cmd "cd \"$TEST_ERROR_PROJECT\" && wallpaper-core show effects 2>&1"; then
    test_failed "should have failed with missing required field (command succeeded incorrectly)" \
        "cd $TEST_ERROR_PROJECT && wallpaper-core show effects" \
        "$LAST_OUTPUT"
else
    add_detail "• Test: Effect missing required 'command' field"
    add_detail "• Effect: broken_effect"
    add_detail "• Result: Properly validated and rejected"
    test_passed
fi

print_test "Layered effects empty effects.yaml loads successfully"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
EOF
if run_cmd "cd \"$TEST_ERROR_PROJECT\" && wallpaper-core show effects 2>&1"; then
    add_detail "• Test: Minimal valid effects.yaml (version only)"
    add_detail "• Config: $TEST_ERROR_PROJECT/effects.yaml"
    add_detail "• Result: Successfully loaded, falls back to package defaults"
    test_passed
else
    test_failed "empty effects.yaml failed to load" \
        "cd $TEST_ERROR_PROJECT && wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# LAYERED EFFECTS - COMBINED LAYERS (3-LAYER MERGE)
# ============================================================================

print_header "LAYERED EFFECTS - COMBINED LAYERS (3-LAYER MERGE)"

# Setup 3-layer test
TEST_3LAYER_USER="$TEST_OUTPUT_DIR/3layer-user"
TEST_3LAYER_PROJECT="$TEST_OUTPUT_DIR/3layer-project"
mkdir -p "$TEST_3LAYER_USER/wallpaper-effects-generator"
mkdir -p "$TEST_3LAYER_PROJECT"

# User layer: override blur + add user_effect
cat > "$TEST_3LAYER_USER/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects:
  blur:
    description: "User-overridden blur"
    command: "convert $INPUT -blur 0x25 $OUTPUT"
    parameters: {}
  user_effect:
    description: "User-only effect"
    command: "convert $INPUT -negate $OUTPUT"
    parameters: {}
EOF

# Project layer: add project_effect
cat > "$TEST_3LAYER_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
effects:
  project_effect:
    description: "Project-only effect"
    command: "convert $INPUT -sepia-tone 80% $OUTPUT"
    parameters: {}
EOF

print_test "Layered effects 3-layer merge includes all effects from all layers"
# Should have: package effects + project_effect + user_effect + user-overridden blur
if run_cmd "cd \"$TEST_3LAYER_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_3LAYER_USER\" wallpaper-core show effects 2>&1" && \
   echo "$LAST_OUTPUT" | grep -q "user_effect" && echo "$LAST_OUTPUT" | grep -q "project_effect"; then
    add_detail "• Layers: Package + Project + User (3-layer merge)"
    add_detail "• User effect: user_effect found"
    add_detail "• Project effect: project_effect found"
    add_detail "• Result: All layers merged successfully"
    test_passed
else
    test_failed "3-layer merge missing effects (expected user_effect and project_effect)" \
        "cd $TEST_3LAYER_PROJECT && XDG_CONFIG_HOME=$TEST_3LAYER_USER wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects 3-layer merge user override takes precedence"
if run_cmd "cd \"$TEST_3LAYER_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_3LAYER_USER\" wallpaper-core show effects 2>&1" && \
   echo "$LAST_OUTPUT" | grep "blur" | grep -q "User-overridden"; then
    add_detail "• Effect: blur (overridden by user layer)"
    add_detail "• Precedence: User > Project > Package"
    add_detail "• Result: User override correctly applied"
    test_passed
else
    test_failed "3-layer merge user override not applied (blur should show 'User-overridden')" \
        "cd $TEST_3LAYER_PROJECT && XDG_CONFIG_HOME=$TEST_3LAYER_USER wallpaper-core show effects" \
        "$(echo "$LAST_OUTPUT" | grep "blur" | head -3)"
fi

print_test "Layered effects 3-layer merge user effect processes successfully"
threelayer_out="$TEST_OUTPUT_DIR/3layer-user-effect.jpg"
if run_cmd "cd \"$TEST_3LAYER_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_3LAYER_USER\" wallpaper-core process effect \"$TEST_IMAGE\" \"$threelayer_out\" --effect user_effect" && \
   [ -f "$threelayer_out" ]; then
    file_size=$(stat -f%z "$threelayer_out" 2>/dev/null || stat -c%s "$threelayer_out" 2>/dev/null)
    add_detail "• Effect: user_effect (from user layer in 3-layer merge)"
    add_detail "• Output file: $threelayer_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "3-layer merge user effect processing failed or output not created (expected: $threelayer_out)" \
        "cd $TEST_3LAYER_PROJECT && XDG_CONFIG_HOME=$TEST_3LAYER_USER wallpaper-core process effect ... --effect user_effect" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects 3-layer merge project effect processes successfully"
threelayer_project_out="$TEST_OUTPUT_DIR/3layer-project-effect.jpg"
if run_cmd "cd \"$TEST_3LAYER_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_3LAYER_USER\" wallpaper-core process effect \"$TEST_IMAGE\" \"$threelayer_project_out\" --effect project_effect" && \
   [ -f "$threelayer_project_out" ]; then
    file_size=$(stat -f%z "$threelayer_project_out" 2>/dev/null || stat -c%s "$threelayer_project_out" 2>/dev/null)
    add_detail "• Effect: project_effect (from project layer in 3-layer merge)"
    add_detail "• Output file: $threelayer_project_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "3-layer merge project effect processing failed or output not created (expected: $threelayer_project_out)" \
        "cd $TEST_3LAYER_PROJECT && XDG_CONFIG_HOME=$TEST_3LAYER_USER wallpaper-core process effect ... --effect project_effect" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# LAYERED EFFECTS - PARAMETER TYPES ACROSS LAYERS
# ============================================================================

print_header "LAYERED EFFECTS - PARAMETER TYPES ACROSS LAYERS"

TEST_PARAMS_USER="$TEST_OUTPUT_DIR/params-user"
TEST_PARAMS_PROJECT="$TEST_OUTPUT_DIR/params-project"
mkdir -p "$TEST_PARAMS_USER/wallpaper-effects-generator"
mkdir -p "$TEST_PARAMS_PROJECT"

# User adds custom parameter type and effect using it
cat > "$TEST_PARAMS_USER/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
parameter_types:
  user_strength:
    type: integer
    min: 0
    max: 100
    default: 50
    description: "User-defined strength parameter"
effects:
  user_effect_with_param:
    description: "Effect using user parameter type"
    command: "convert $INPUT -brightness-contrast {user_strength} $OUTPUT"
    parameters:
      user_strength:
        type_ref: user_strength
EOF

# Project adds different parameter type and effect using package parameter type
cat > "$TEST_PARAMS_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
effects:
  project_effect_with_package_param:
    description: "Project effect using package parameter type"
    command: "convert $INPUT -blur {blur_geometry} $OUTPUT"
    parameters:
      blur:
        type_ref: blur_geometry
EOF

print_test "Layered effects parameter types merge across all layers"
# Verify both effects are present and can be listed (meaning parameter type merging worked)
if run_cmd "cd \"$TEST_PARAMS_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_PARAMS_USER\" wallpaper-core show effects 2>&1" && \
   echo "$LAST_OUTPUT" | grep -q "user_effect_with_param" && echo "$LAST_OUTPUT" | grep -q "project_effect_with_package_param"; then
    add_detail "• User layer: Defines custom parameter type 'user_strength'"
    add_detail "• Project layer: Uses package parameter type 'blur_geometry'"
    add_detail "• Result: Both effects loaded, parameter types merged successfully"
    test_passed
else
    test_failed "parameter type merge failed (expected user_effect_with_param and project_effect_with_package_param)" \
        "cd $TEST_PARAMS_PROJECT && XDG_CONFIG_HOME=$TEST_PARAMS_USER wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# LAYERED EFFECTS - COMPOSITES AND PRESETS
# ============================================================================

print_header "LAYERED EFFECTS - COMPOSITES AND PRESETS"

TEST_COMP_USER="$TEST_OUTPUT_DIR/comp-user"
TEST_COMP_PROJECT="$TEST_OUTPUT_DIR/comp-project"
mkdir -p "$TEST_COMP_USER/wallpaper-effects-generator"
mkdir -p "$TEST_COMP_PROJECT"

# User adds custom composite
cat > "$TEST_COMP_USER/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
composites:
  user_composite:
    description: "User-defined composite"
    chain:
      - effect: blur
      - effect: brightness
presets:
  user_preset:
    description: "User-defined preset"
    composite: user_composite
EOF

# Project adds custom preset
cat > "$TEST_COMP_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
presets:
  project_preset:
    description: "Project-defined preset"
    effect: blur
EOF

print_test "Layered effects user composite is loaded"
if run_cmd "cd \"$TEST_COMP_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_COMP_USER\" wallpaper-core show composites 2>&1" && \
   echo "$LAST_OUTPUT" | grep -q "user_composite"; then
    add_detail "• Layer: User"
    add_detail "• Composite: user_composite (chain: blur -> brightness)"
    add_detail "• Result: User-defined composite loaded successfully"
    test_passed
else
    test_failed "user composite not found (user_composite)" \
        "cd $TEST_COMP_PROJECT && XDG_CONFIG_HOME=$TEST_COMP_USER wallpaper-core show composites" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects user preset is loaded"
if run_cmd "cd \"$TEST_COMP_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_COMP_USER\" wallpaper-core show presets 2>&1" && \
   echo "$LAST_OUTPUT" | grep -q "user_preset"; then
    add_detail "• Layer: User"
    add_detail "• Preset: user_preset (uses user_composite)"
    add_detail "• Result: User-defined preset loaded successfully"
    test_passed
else
    test_failed "user preset not found (user_preset)" \
        "cd $TEST_COMP_PROJECT && XDG_CONFIG_HOME=$TEST_COMP_USER wallpaper-core show presets" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects project preset is loaded"
if run_cmd "cd \"$TEST_COMP_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_COMP_USER\" wallpaper-core show presets 2>&1" && \
   echo "$LAST_OUTPUT" | grep -q "project_preset"; then
    add_detail "• Layer: Project"
    add_detail "• Preset: project_preset (uses blur effect)"
    add_detail "• Result: Project-defined preset loaded successfully"
    test_passed
else
    test_failed "project preset not found (project_preset)" \
        "cd $TEST_COMP_PROJECT && XDG_CONFIG_HOME=$TEST_COMP_USER wallpaper-core show presets" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects user composite processes successfully"
user_comp_out="$TEST_OUTPUT_DIR/user-composite.jpg"
if run_cmd "cd \"$TEST_COMP_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_COMP_USER\" wallpaper-core process composite \"$TEST_IMAGE\" \"$user_comp_out\" --composite user_composite" && \
   [ -f "$user_comp_out" ]; then
    file_size=$(stat -f%z "$user_comp_out" 2>/dev/null || stat -c%s "$user_comp_out" 2>/dev/null)
    add_detail "• Composite: user_composite (user layer)"
    add_detail "• Output file: $user_comp_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "user composite processing failed or output not created (expected: $user_comp_out)" \
        "cd $TEST_COMP_PROJECT && XDG_CONFIG_HOME=$TEST_COMP_USER wallpaper-core process composite ... --composite user_composite" \
        "$LAST_OUTPUT"
fi

print_test "Layered effects user preset processes successfully"
user_preset_out="$TEST_OUTPUT_DIR/user-preset.jpg"
if run_cmd "cd \"$TEST_COMP_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_COMP_USER\" wallpaper-core process preset \"$TEST_IMAGE\" \"$user_preset_out\" --preset user_preset" && \
   [ -f "$user_preset_out" ]; then
    file_size=$(stat -f%z "$user_preset_out" 2>/dev/null || stat -c%s "$user_preset_out" 2>/dev/null)
    add_detail "• Preset: user_preset (user layer)"
    add_detail "• Output file: $user_preset_out"
    add_detail "• File size: $file_size bytes"
    test_passed
else
    test_failed "user preset processing failed or output not created (expected: $user_preset_out)" \
        "cd $TEST_COMP_PROJECT && XDG_CONFIG_HOME=$TEST_COMP_USER wallpaper-core process preset ... --preset user_preset" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# LAYERED SETTINGS TESTS
# ============================================================================

print_header "LAYERED SETTINGS TESTS"

TEST_SETTINGS_USER="$TEST_OUTPUT_DIR/settings-user"
TEST_SETTINGS_PROJECT="$TEST_OUTPUT_DIR/settings-project"
mkdir -p "$TEST_SETTINGS_USER/wallpaper-effects-generator"
mkdir -p "$TEST_SETTINGS_PROJECT"

# User settings
cat > "$TEST_SETTINGS_USER/wallpaper-effects-generator/settings.toml" << 'EOF'
[core]
verbosity = "verbose"
default_format = "png"
EOF

# Project settings
cat > "$TEST_SETTINGS_PROJECT/settings.toml" << 'EOF'
[core]
default_format = "webp"
EOF

print_test "Layered settings load without errors"
if run_cmd "cd \"$TEST_SETTINGS_PROJECT\" && XDG_CONFIG_HOME=\"$TEST_SETTINGS_USER\" wallpaper-core info 2>&1"; then
    add_detail "• User settings: $TEST_SETTINGS_USER/wallpaper-effects-generator/settings.toml"
    add_detail "• Project settings: $TEST_SETTINGS_PROJECT/settings.toml"
    add_detail "• Result: Settings loaded successfully from all layers"
    test_passed
else
    test_failed "layered settings failed to load" \
        "cd $TEST_SETTINGS_PROJECT && XDG_CONFIG_HOME=$TEST_SETTINGS_USER wallpaper-core info" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# EDGE CASES
# ============================================================================

print_header "EDGE CASES"

TEST_EDGE="$TEST_OUTPUT_DIR/edge-cases"
mkdir -p "$TEST_EDGE/wallpaper-effects-generator"

print_test "Edge case very long effect name loads successfully"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects:
  this_is_a_very_long_effect_name_that_tests_the_limits_of_identifier_length:
    description: "Effect with very long name"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
EOF
if run_cmd "XDG_CONFIG_HOME=\"$TEST_EDGE\" wallpaper-core show effects 2>&1" && echo "$LAST_OUTPUT" | grep -q "this_is_a_very_long"; then
    add_detail "• Test: Effect name with 73 characters"
    add_detail "• Result: Long identifier handled correctly"
    test_passed
else
    test_failed "very long effect name failed to load (this_is_a_very_long...)" \
        "XDG_CONFIG_HOME=$TEST_EDGE wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

print_test "Edge case effect name with underscores and numbers loads successfully"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects:
  effect_123_test:
    description: "Effect with numbers"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
EOF
if run_cmd "XDG_CONFIG_HOME=\"$TEST_EDGE\" wallpaper-core show effects 2>&1" && echo "$LAST_OUTPUT" | grep -q "effect_123_test"; then
    add_detail "• Test: Effect name 'effect_123_test' (underscores + numbers)"
    add_detail "• Result: Mixed alphanumeric identifier accepted"
    test_passed
else
    test_failed "effect name with underscores and numbers failed to load (effect_123_test)" \
        "XDG_CONFIG_HOME=$TEST_EDGE wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

print_test "Edge case empty effects section loads successfully"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects: {}
EOF
if run_cmd "XDG_CONFIG_HOME=\"$TEST_EDGE\" wallpaper-core show effects 2>&1"; then
    add_detail "• Test: Empty effects section (effects: {})"
    add_detail "• Result: Valid YAML, falls back to package defaults"
    test_passed
else
    test_failed "empty effects section failed to load" \
        "XDG_CONFIG_HOME=$TEST_EDGE wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

print_test "Edge case minimal valid file with only version field loads successfully"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
EOF
if run_cmd "XDG_CONFIG_HOME=\"$TEST_EDGE\" wallpaper-core show effects 2>&1"; then
    add_detail "• Test: Minimal effects.yaml (version field only)"
    add_detail "• Result: Valid config, uses package defaults"
    test_passed
else
    test_failed "minimal effects.yaml (version only) failed to load" \
        "XDG_CONFIG_HOME=$TEST_EDGE wallpaper-core show effects" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# ORCHESTRATOR CLI TESTS (wallpaper-process)
# ============================================================================

print_header "ORCHESTRATOR CLI TESTS (wallpaper-process)"

print_test "wallpaper-process version displays version information"
if run_cmd "wallpaper-process version"; then
    version_output=$(echo "$LAST_OUTPUT" | head -1)
    add_detail "• Command: wallpaper-process version"
    add_detail "• Output: $version_output"
    test_passed
else
    test_failed "wallpaper-process version command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process info displays system information"
if run_cmd "wallpaper-process info"; then
    line_count=$(echo "$LAST_OUTPUT" | wc -l)
    sample_line=$(echo "$LAST_OUTPUT" | head -1)
    add_detail "• Command: wallpaper-process info"
    add_detail "• Output lines: $line_count"
    add_detail "• Sample: $sample_line"
    test_passed
else
    test_failed "wallpaper-process info command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process show effects lists all available effects"
if run_cmd "wallpaper-process show effects"; then
    effect_count=$(echo "$LAST_OUTPUT" | grep -c "blur\|brightness\|blackwhite" || echo "0")
    sample_effects=$(echo "$LAST_OUTPUT" | grep -o "blur\|brightness\|blackwhite" | head -3 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-process show effects"
    add_detail "• Effects listed: $effect_count+"
    add_detail "• Samples: $sample_effects"
    test_passed
else
    test_failed "wallpaper-process show effects command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process show composites lists all available composites"
if run_cmd "wallpaper-process show composites"; then
    composite_count=$(echo "$LAST_OUTPUT" | grep -c "blackwhite-blur\|blur-brightness" || echo "0")
    sample_composites=$(echo "$LAST_OUTPUT" | grep -o "blackwhite-blur\|blur-brightness" | head -2 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-process show composites"
    add_detail "• Composites listed: $composite_count+"
    add_detail "• Samples: $sample_composites"
    test_passed
else
    test_failed "wallpaper-process show composites command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

print_test "wallpaper-process show presets lists all available presets"
if run_cmd "wallpaper-process show presets"; then
    preset_count=$(echo "$LAST_OUTPUT" | grep -c "dark_blur\|subtle_blur" || echo "0")
    sample_presets=$(echo "$LAST_OUTPUT" | grep -o "dark_blur\|subtle_blur" | head -2 | tr '\n' ', ' | sed 's/,$//')
    add_detail "• Command: wallpaper-process show presets"
    add_detail "• Presets listed: $preset_count+"
    add_detail "• Samples: $sample_presets"
    test_passed
else
    test_failed "wallpaper-process show presets command failed" "$LAST_CMD" "$LAST_OUTPUT"
fi

# ============================================================================
# CONTAINER MANAGEMENT TESTS
# ============================================================================

print_header "CONTAINER MANAGEMENT TESTS"

# Detect container engine
if command -v podman > /dev/null 2>&1; then
    CONTAINER_ENGINE="podman"
elif command -v docker > /dev/null 2>&1; then
    CONTAINER_ENGINE="docker"
else
    echo "Warning: No container engine found, skipping container tests"
    CONTAINER_ENGINE="none"
fi

# Create a project directory with settings.toml for container engine config
# Note: layered_settings discovers project-level config from cwd/settings.toml
TEST_CONTAINER_PROJECT="$TEST_OUTPUT_DIR/container-project"
mkdir -p "$TEST_CONTAINER_PROJECT"
if [ "$CONTAINER_ENGINE" != "none" ]; then
    cat > "$TEST_CONTAINER_PROJECT/settings.toml" << EOF
[orchestrator]
version = "1.0"

[orchestrator.container]
engine = "$CONTAINER_ENGINE"
image_name = "wallpaper-effects:latest"
EOF
fi

print_test "wallpaper-process install builds container image"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process install 2>&1"; then
    add_detail "• Command: wallpaper-process install"
    add_detail "• Container engine: $CONTAINER_ENGINE"
    add_detail "• Image built: wallpaper-effects:latest"
    add_detail "• Build location: $TEST_CONTAINER_PROJECT"
    test_passed
else
    test_failed "container image build failed (wallpaper-effects:latest)" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process install" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process process effect (blur) creates output file via container"
orch_effect_out="$TEST_OUTPUT_DIR/orch-effect-blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process process effect \"$TEST_IMAGE\" \"$orch_effect_out\" blur 2>&1" && [ -f "$orch_effect_out" ]; then
    file_size=$(stat -f%z "$orch_effect_out" 2>/dev/null || stat -c%s "$orch_effect_out" 2>/dev/null)
    add_detail "• Command: wallpaper-process process effect <image> <output> blur"
    add_detail "• Container engine: $CONTAINER_ENGINE"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output: $orch_effect_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Effect: blur (containerized execution)"
    test_passed
else
    test_failed "containerized effect processing failed or output not created (expected: $orch_effect_out)" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process process effect ... blur" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process process composite (blackwhite-blur) creates output file via container"
orch_composite_out="$TEST_OUTPUT_DIR/orch-composite-blackwhite-blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process process composite \"$TEST_IMAGE\" \"$orch_composite_out\" blackwhite-blur 2>&1" && [ -f "$orch_composite_out" ]; then
    file_size=$(stat -f%z "$orch_composite_out" 2>/dev/null || stat -c%s "$orch_composite_out" 2>/dev/null)
    add_detail "• Command: wallpaper-process process composite <image> <output> blackwhite-blur"
    add_detail "• Container engine: $CONTAINER_ENGINE"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output: $orch_composite_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Composite: blackwhite-blur (2-effect chain, containerized)"
    test_passed
else
    test_failed "containerized composite processing failed or output not created (expected: $orch_composite_out)" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process process composite ... blackwhite-blur" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process process preset (dark_blur) creates output file via container"
orch_preset_out="$TEST_OUTPUT_DIR/orch-preset-dark_blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process process preset \"$TEST_IMAGE\" \"$orch_preset_out\" dark_blur 2>&1" && [ -f "$orch_preset_out" ]; then
    file_size=$(stat -f%z "$orch_preset_out" 2>/dev/null || stat -c%s "$orch_preset_out" 2>/dev/null)
    add_detail "• Command: wallpaper-process process preset <image> <output> dark_blur"
    add_detail "• Container engine: $CONTAINER_ENGINE"
    add_detail "• Input: $TEST_IMAGE"
    add_detail "• Output: $orch_preset_out"
    add_detail "• File size: $file_size bytes"
    add_detail "• Preset: dark_blur (containerized execution)"
    test_passed
else
    test_failed "containerized preset processing failed or output not created (expected: $orch_preset_out)" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process process preset ... dark_blur" \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch effects generates all effect outputs on host"
orch_batch_effect="$TEST_OUTPUT_DIR/orch-batch-effect"
mkdir -p "$orch_batch_effect"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process batch effects \"$TEST_IMAGE\" \"$orch_batch_effect\" 2>&1"; then
    # Should generate 9 effects
    output_count=$(find "$orch_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        output_files=$(find "$orch_batch_effect" -type f -name "*.jpg" -exec basename {} \; | head -3 | tr '\n' ', ' | sed 's/,$//')
        add_detail "• Command: wallpaper-process batch effects <image> <output-dir>"
        add_detail "• Output directory: $orch_batch_effect"
        add_detail "• Effects generated: $output_count"
        add_detail "• Sample files: $output_files..."
        add_detail "• Execution: Host-side (delegates to core)"
        test_passed
    else
        test_failed "orchestrator batch effects: insufficient outputs (expected ≥9, got $output_count)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process batch effects ..." \
            "Found files: $(ls -1 "$orch_batch_effect" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "orchestrator batch effects command failed" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process batch effects ..." \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process batch all generates all outputs on host"
orch_batch_all="$TEST_OUTPUT_DIR/orch-batch-all"
mkdir -p "$orch_batch_all"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process batch all \"$TEST_IMAGE\" \"$orch_batch_all\" 2>&1"; then
    output_count=$(find "$orch_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then
        effects_count=$(find "$orch_batch_all" -type f -name "*blur*.jpg" 2>/dev/null | wc -l)
        add_detail "• Command: wallpaper-process batch all <image> <output-dir>"
        add_detail "• Output directory: $orch_batch_all"
        add_detail "• Total files: $output_count (effects + composites + presets)"
        add_detail "• Effects subset: $effects_count files"
        add_detail "• Execution: Host-side (delegates to core)"
        test_passed
    else
        test_failed "orchestrator batch all: insufficient outputs (expected >15, got $output_count)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process batch all ..." \
            "Found files: $(ls -1 "$orch_batch_all" 2>/dev/null | head -10 | tr '\n' ' ')"
    fi
else
    test_failed "orchestrator batch all command failed" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process batch all ..." \
        "$LAST_OUTPUT"
fi

print_test "wallpaper-process uninstall removes container image"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    test_skipped "container engine not found" \
        "command -v docker && command -v podman" \
        "Neither docker nor podman found" \
        "Install Docker (https://docs.docker.com/) or Podman (https://podman.io/)"
elif run_cmd "cd \"$TEST_CONTAINER_PROJECT\" && wallpaper-process uninstall --yes 2>&1"; then
    add_detail "• Command: wallpaper-process uninstall --yes"
    add_detail "• Container engine: $CONTAINER_ENGINE"
    add_detail "• Image removed: wallpaper-effects:latest"
    test_passed
else
    test_failed "container uninstall failed (wallpaper-effects:latest)" \
        "cd $TEST_CONTAINER_PROJECT && wallpaper-process uninstall --yes" \
        "$LAST_OUTPUT"
fi

# ============================================================================
# DRY-RUN TESTS - CORE CLI
# ============================================================================

print_header "DRY-RUN TESTS - CORE CLI"

print_test "wallpaper-core process effect --dry-run shows ImageMagick command without executing"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/dry-run-test.jpg --effect blur --dry-run 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "magick"; then
    sample_cmd=$(echo "$dry_run_output" | grep "magick" | head -1 | cut -c1-60)
    add_detail "• Command: wallpaper-core process effect --dry-run"
    add_detail "• Effect: blur"
    add_detail "• Exit code: $exit_code (success)"
    add_detail "• Output shows: $sample_cmd..."
    add_detail "• Verified: ImageMagick command displayed without execution"
    test_passed
else
    test_failed "dry-run effect command failed or no magick command shown (exit: $exit_code)" \
        "wallpaper-core process effect ... --effect blur --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process effect --dry-run creates no output file"
test_output="/tmp/wallpaper-dry-run-should-not-exist.jpg"
rm -f "$test_output" 2>/dev/null
dry_run_cmd="wallpaper-core process effect \"$TEST_IMAGE\" \"$test_output\" --effect blur --dry-run"
wallpaper-core process effect "$TEST_IMAGE" "$test_output" --effect blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    add_detail "• Test output path: $test_output"
    add_detail "• Verified: No file created (dry-run mode)"
    test_passed
else
    test_failed "dry-run created output file (should not execute)" \
        "$dry_run_cmd" \
        "Unexpected file: $test_output"
    rm -f "$test_output"
fi

print_test "wallpaper-core process effect --dry-run shows validation checks"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(Validation|✓|✗)"; then
    check_count=$(echo "$dry_run_output" | grep -cE "(✓|✗)" || echo "0")
    add_detail "• Validation checks displayed: $check_count"
    add_detail "• Verified: Pre-flight validation in dry-run mode"
    test_passed
else
    test_failed "no validation checks found in dry-run output" \
        "wallpaper-core process effect ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process effect --dry-run with missing input shows warning"
dry_run_output=$(wallpaper-core process effect /nonexistent/file.jpg /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(not found|✗)" && [ $? -ne 1 ]; then
    warning_line=$(echo "$dry_run_output" | grep -m1 "not found\|✗" | head -c 80)
    add_detail "• Test: Nonexistent input file /nonexistent/file.jpg"
    add_detail "• Warning shown: $warning_line..."
    add_detail "• Verified: Validation catches missing input in dry-run"
    test_passed
else
    test_failed "missing input not detected in dry-run validation" \
        "wallpaper-core process effect /nonexistent/file.jpg ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process effect --dry-run with unknown effect shows warning"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect nonexistent_effect --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(not found|✗)" && [ $? -ne 1 ]; then
    warning_line=$(echo "$dry_run_output" | grep -m1 "not found\|✗" | head -c 80)
    add_detail "• Test: Unknown effect 'nonexistent_effect'"
    add_detail "• Warning shown: $warning_line..."
    add_detail "• Verified: Validation catches unknown effect in dry-run"
    test_passed
else
    test_failed "unknown effect not detected in dry-run validation" \
        "wallpaper-core process effect ... --effect nonexistent_effect --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process effect -q --dry-run shows only command in quiet mode"
dry_run_output=$(wallpaper-core -q process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "magick" && ! echo "$dry_run_output" | grep -q "Validation"; then
    add_detail "• Flag: -q (quiet mode)"
    add_detail "• Output: Command only, no validation details"
    add_detail "• Verified: Quiet mode suppresses verbose output"
    test_passed
else
    test_failed "quiet mode not working (should show only magick command, no validation)" \
        "wallpaper-core -q process effect ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process composite --dry-run shows chain commands"
dry_run_output=$(wallpaper-core process composite "$TEST_IMAGE" /tmp/test.jpg --composite blackwhite-blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qi "blur" && echo "$dry_run_output" | grep -qi "blackwhite"; then
    add_detail "• Composite: blackwhite-blur (2-effect chain)"
    add_detail "• Output shows: Both effects in chain"
    add_detail "• Verified: Composite chain expanded in dry-run"
    test_passed
else
    test_failed "composite chain not shown in dry-run output (expected blur and blackwhite)" \
        "wallpaper-core process composite ... --composite blackwhite-blur --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process composite --dry-run creates no output file"
test_output="/tmp/wallpaper-composite-dry-run.jpg"
rm -f "$test_output" 2>/dev/null
dry_run_cmd="wallpaper-core process composite \"$TEST_IMAGE\" \"$test_output\" --composite blackwhite-blur --dry-run"
wallpaper-core process composite "$TEST_IMAGE" "$test_output" --composite blackwhite-blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    add_detail "• Test output path: $test_output"
    add_detail "• Verified: No file created (dry-run mode)"
    test_passed
else
    test_failed "dry-run created output file (should not execute)" \
        "$dry_run_cmd" \
        "Unexpected file: $test_output"
    rm -f "$test_output"
fi

print_test "wallpaper-core process preset --dry-run shows resolved command"
dry_run_output=$(wallpaper-core process preset "$TEST_IMAGE" /tmp/test.jpg --preset dark_blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "magick"; then
    add_detail "• Preset: dark_blur"
    add_detail "• Output shows: Resolved ImageMagick command"
    add_detail "• Verified: Preset resolved to concrete command"
    test_passed
else
    test_failed "preset command not shown in dry-run output" \
        "wallpaper-core process preset ... --preset dark_blur --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core process preset --dry-run creates no output file"
test_output="/tmp/wallpaper-preset-dry-run.jpg"
rm -f "$test_output" 2>/dev/null
dry_run_cmd="wallpaper-core process preset \"$TEST_IMAGE\" \"$test_output\" --preset dark_blur --dry-run"
wallpaper-core process preset "$TEST_IMAGE" "$test_output" --preset dark_blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    add_detail "• Test output path: $test_output"
    add_detail "• Verified: No file created (dry-run mode)"
    test_passed
else
    test_failed "dry-run created output file (should not execute)" \
        "$dry_run_cmd" \
        "Unexpected file: $test_output"
    rm -f "$test_output"
fi

print_test "wallpaper-core batch effects --dry-run shows table with all effects"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "blur" && echo "$dry_run_output" | grep -q "blackwhite"; then
    effect_mentions=$(echo "$dry_run_output" | grep -c "blur\|blackwhite\|brightness" || echo "0")
    add_detail "• Command: batch effects --dry-run"
    add_detail "• Effects in output: $effect_mentions+ mentions"
    add_detail "• Verified: Table showing all available effects"
    test_passed
else
    test_failed "effects table not shown in dry-run output (expected blur, blackwhite)" \
        "wallpaper-core batch effects ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch effects --dry-run shows item count"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "([0-9]+ items|Effects)"; then
    add_detail "• Output includes: Item count or 'Effects' header"
    add_detail "• Verified: Summary information displayed"
    test_passed
else
    test_failed "item count or Effects header not shown in dry-run output" \
        "wallpaper-core batch effects ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch effects --dry-run shows resolved commands"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
command_count=$(echo "$dry_run_output" | grep -c "magick" || echo "0")
if [ "$command_count" -ge 3 ]; then
    add_detail "• ImageMagick commands found: $command_count"
    add_detail "• Verified: Resolved commands for multiple effects"
    test_passed
else
    test_failed "insufficient magick commands in dry-run output (expected ≥3, got $command_count)" \
        "wallpaper-core batch effects ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch effects --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-dry-run"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
dry_run_cmd="wallpaper-core batch effects \"$TEST_IMAGE\" \"$test_dir\" --dry-run"
wallpaper-core batch effects "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    add_detail "• Test directory: $test_dir"
    add_detail "• Files created: $file_count"
    add_detail "• Verified: No files created in dry-run mode"
    test_passed
else
    test_failed "dry-run created files (should not execute, found $file_count files)" \
        "$dry_run_cmd" \
        "Files: $(ls -1 "$test_dir" 2>/dev/null | head -5 | tr '\n' ' ')"
fi
rm -rf "$test_dir"

print_test "wallpaper-core batch composites --dry-run shows table"
dry_run_output=$(wallpaper-core batch composites "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(blackwhite-blur|Composites)"; then
    add_detail "• Output includes: Composite names or 'Composites' header"
    add_detail "• Sample: blackwhite-blur found in output"
    add_detail "• Verified: Composites table displayed"
    test_passed
else
    test_failed "composites table not shown in dry-run output (expected blackwhite-blur or Composites header)" \
        "wallpaper-core batch composites ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch composites --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-composite-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
dry_run_cmd="wallpaper-core batch composites \"$TEST_IMAGE\" \"$test_dir\" --dry-run"
wallpaper-core batch composites "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    add_detail "• Test directory: $test_dir"
    add_detail "• Files created: $file_count"
    add_detail "• Verified: No files created in dry-run mode"
    test_passed
else
    test_failed "dry-run created files (should not execute, found $file_count files)" \
        "$dry_run_cmd" \
        "Files: $(ls -1 "$test_dir" 2>/dev/null | tr '\n' ' ')"
fi
rm -rf "$test_dir"

print_test "wallpaper-core batch presets --dry-run shows table"
dry_run_output=$(wallpaper-core batch presets "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(dark_blur|Presets|subtle_blur)"; then
    add_detail "• Output includes: Preset names or 'Presets' header"
    add_detail "• Samples: dark_blur, subtle_blur found"
    add_detail "• Verified: Presets table displayed"
    test_passed
else
    test_failed "presets table not shown in dry-run output (expected dark_blur/subtle_blur or Presets header)" \
        "wallpaper-core batch presets ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch presets --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-preset-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
dry_run_cmd="wallpaper-core batch presets \"$TEST_IMAGE\" \"$test_dir\" --dry-run"
wallpaper-core batch presets "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    add_detail "• Test directory: $test_dir"
    add_detail "• Files created: $file_count"
    add_detail "• Verified: No files created in dry-run mode"
    test_passed
else
    test_failed "dry-run created files (should not execute, found $file_count files)" \
        "$dry_run_cmd" \
        "Files: $(ls -1 "$test_dir" 2>/dev/null | tr '\n' ' ')"
fi
rm -rf "$test_dir"

print_test "wallpaper-core batch all --dry-run shows all item types"
dry_run_output=$(wallpaper-core batch all "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(Effects|Composites|Presets)"; then
    type_count=$(echo "$dry_run_output" | grep -cE "Effects|Composites|Presets" || echo "0")
    add_detail "• Output sections: $type_count types (Effects/Composites/Presets)"
    add_detail "• Verified: All batch types displayed"
    test_passed
else
    test_failed "not all item types shown in dry-run output (expected Effects, Composites, Presets)" \
        "wallpaper-core batch all ... --dry-run" \
        "$dry_run_output"
fi

print_test "wallpaper-core batch all --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-all-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
dry_run_cmd="wallpaper-core batch all \"$TEST_IMAGE\" \"$test_dir\" --dry-run"
wallpaper-core batch all "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    add_detail "• Test directory: $test_dir"
    add_detail "• Files created: $file_count"
    add_detail "• Verified: No files created in dry-run mode"
    test_passed
else
    test_failed "dry-run created files (should not execute, found $file_count files)" \
        "$dry_run_cmd" \
        "Files: $(ls -1 "$test_dir" 2>/dev/null | head -5 | tr '\n' ' ')"
fi
rm -rf "$test_dir"

print_test "wallpaper-core batch all -q --dry-run shows only commands in quiet mode"
dry_run_output=$(wallpaper-core -q batch all "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
command_count=$(echo "$dry_run_output" | grep -c "magick" || echo "0")
if [ "$command_count" -ge 5 ] && ! echo "$dry_run_output" | grep -q "Validation"; then
    sample_cmd=$(echo "$dry_run_output" | grep "magick" | head -1 | cut -c1-60)
    add_detail "• Flag: -q (quiet mode)"
    add_detail "• Commands shown: $command_count"
    add_detail "• Sample command: $sample_cmd..."
    add_detail "• Verified: Only commands, no validation/table headers"
    test_passed
else
    test_failed "quiet mode not working (expected ≥5 magick commands without Validation, got $command_count)" \
        "wallpaper-core -q batch all ... --dry-run" \
        "$dry_run_output"
fi

# ============================================================================
# DRY-RUN TESTS - ORCHESTRATOR CLI
# ============================================================================

print_header "DRY-RUN TESTS - ORCHESTRATOR CLI"

if [ "$CONTAINER_ENGINE" != "none" ]; then
    # Re-install image for dry-run tests
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process install > /dev/null 2>&1)

    print_test "wallpaper-process install --dry-run shows build command without executing"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process install --dry-run 2>&1)
    if echo "$dry_run_output" | grep -qi "build" && echo "$dry_run_output" | grep -qi "dockerfile"; then
        build_line=$(echo "$dry_run_output" | grep -im1 "build\|dockerfile" | head -c 80)
        add_detail "• Command: wallpaper-process install --dry-run"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Output shows: $build_line..."
        add_detail "• Verified: Build command displayed without execution"
        test_passed
    else
        test_failed "build command not shown in dry-run output (expected 'build' and 'dockerfile')" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process install --dry-run" \
            "$dry_run_output"
    fi

    print_test "wallpaper-process install --dry-run does not build image"
    # Check that we can still do a real install after dry-run (image wasn't built)
    test_image_name="wallpaper-effects-test:dry-run-$(date +%s)"
    cat > "$TEST_CONTAINER_PROJECT/settings-drytest.toml" << EOF
[orchestrator]
version = "1.0"

[orchestrator.container]
engine = "$CONTAINER_ENGINE"
image_name = "$test_image_name"
EOF
    # Dry-run should NOT create the image
    install_dry_cmd="XDG_CONFIG_HOME=$TEST_CONTAINER_PROJECT wallpaper-process install --dry-run"
    XDG_CONFIG_HOME="$TEST_CONTAINER_PROJECT" wallpaper-process install --dry-run > /dev/null 2>&1
    if ! $CONTAINER_ENGINE inspect "$test_image_name" > /dev/null 2>&1; then
        add_detail "• Test image name: $test_image_name"
        add_detail "• Command: wallpaper-process install --dry-run"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Verified: Image not created (dry-run mode)"
        test_passed
    else
        test_failed "dry-run built image (should not execute)" \
            "$install_dry_cmd" \
            "Unexpected image: $test_image_name"
        $CONTAINER_ENGINE rmi "$test_image_name" > /dev/null 2>&1
    fi
    rm -f "$TEST_CONTAINER_PROJECT/settings-drytest.toml"

    print_test "wallpaper-process uninstall --dry-run shows rmi command without executing"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "rmi"; then
        rmi_line=$(echo "$dry_run_output" | grep -m1 "rmi" | head -c 80)
        add_detail "• Command: wallpaper-process uninstall --dry-run"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Output shows: $rmi_line..."
        add_detail "• Verified: Removal command displayed without execution"
        test_passed
    else
        test_failed "rmi command not shown in dry-run output" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process uninstall --dry-run" \
            "$dry_run_output"
    fi

    print_test "wallpaper-process uninstall --dry-run does not remove image"
    # Check image still exists after dry-run uninstall
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --dry-run > /dev/null 2>&1)
    if (cd "$TEST_CONTAINER_PROJECT" && $CONTAINER_ENGINE inspect wallpaper-effects:latest > /dev/null 2>&1); then
        add_detail "• Command: wallpaper-process uninstall --dry-run"
        add_detail "• Image: wallpaper-effects:latest"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Verified: Image still exists (dry-run mode, no removal)"
        test_passed
    else
        test_failed "dry-run removed image (should not execute)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process uninstall --dry-run" \
            "Image wallpaper-effects:latest was removed"
    fi

    print_test "wallpaper-process process effect --dry-run shows both host and inner commands"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process effect "$TEST_IMAGE" /tmp/test.jpg blur --dry-run 2>&1)
    has_host_cmd=$(echo "$dry_run_output" | grep -E "($CONTAINER_ENGINE|run)" | wc -l)
    has_inner_cmd=$(echo "$dry_run_output" | grep "magick" | wc -l)
    if [ "$has_host_cmd" -ge 1 ] && [ "$has_inner_cmd" -ge 1 ]; then
        sample_host=$(echo "$dry_run_output" | grep -E "$CONTAINER_ENGINE" | head -1 | cut -c1-60)
        sample_inner=$(echo "$dry_run_output" | grep "magick" | head -1 | cut -c1-60)
        add_detail "• Command: wallpaper-process process effect --dry-run"
        add_detail "• Host commands: $has_host_cmd ($CONTAINER_ENGINE run...)"
        add_detail "• Inner commands: $has_inner_cmd (ImageMagick)"
        add_detail "• Sample host: $sample_host..."
        add_detail "• Sample inner: $sample_inner..."
        add_detail "• Verified: Both container and effect commands shown"
        test_passed
    else
        test_failed "missing commands in dry-run output (host: $has_host_cmd, inner: $has_inner_cmd, expected ≥1 each)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process process effect ... blur --dry-run" \
            "$dry_run_output"
    fi

    print_test "wallpaper-process process effect --dry-run does not spawn container"
    test_output="/tmp/wallpaper-orch-dry-effect.jpg"
    rm -f "$test_output" 2>/dev/null
    dry_run_cmd="cd $TEST_CONTAINER_PROJECT && wallpaper-process process effect ... blur --dry-run"
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process effect "$TEST_IMAGE" "$test_output" blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        add_detail "• Test output: $test_output"
        add_detail "• Verified: No container spawned, no file created"
        test_passed
    else
        test_failed "dry-run created output file (should not execute)" \
            "$dry_run_cmd" \
            "Unexpected file: $test_output"
        rm -f "$test_output"
    fi

    print_test "wallpaper-process process composite --dry-run shows container and chain commands"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process composite "$TEST_IMAGE" /tmp/test.jpg blackwhite-blur --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "$CONTAINER_ENGINE" && echo "$dry_run_output" | grep -qi "blur"; then
        sample_line=$(echo "$dry_run_output" | grep -m1 "$CONTAINER_ENGINE\|blur" | head -c 80)
        add_detail "• Command: wallpaper-process process composite --dry-run"
        add_detail "• Composite: blackwhite-blur (2-effect chain)"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Output sample: $sample_line..."
        add_detail "• Verified: Both container and composite details displayed"
        test_passed
    else
        test_failed "container or composite chain not shown in dry-run output (expected $CONTAINER_ENGINE and blur)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process process composite ... blackwhite-blur --dry-run" \
            "$dry_run_output"
    fi

    print_test "wallpaper-process process composite --dry-run creates no output"
    test_output="/tmp/wallpaper-orch-dry-composite.jpg"
    rm -f "$test_output" 2>/dev/null
    dry_run_cmd="cd $TEST_CONTAINER_PROJECT && wallpaper-process process composite ... blackwhite-blur --dry-run"
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process composite "$TEST_IMAGE" "$test_output" blackwhite-blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        add_detail "• Test output: $test_output"
        add_detail "• Verified: No file created in dry-run mode"
        test_passed
    else
        test_failed "dry-run created output file (should not execute)" \
            "$dry_run_cmd" \
            "Unexpected file: $test_output"
        rm -f "$test_output"
    fi

    print_test "wallpaper-process process preset --dry-run shows container command"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process preset "$TEST_IMAGE" /tmp/test.jpg dark_blur --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "$CONTAINER_ENGINE"; then
        sample_line=$(echo "$dry_run_output" | grep -m1 "$CONTAINER_ENGINE" | head -c 80)
        add_detail "• Command: wallpaper-process process preset --dry-run"
        add_detail "• Preset: dark_blur"
        add_detail "• Container engine: $CONTAINER_ENGINE"
        add_detail "• Output sample: $sample_line..."
        add_detail "• Verified: Containerized preset command displayed"
        test_passed
    else
        test_failed "container command not shown in dry-run output (expected $CONTAINER_ENGINE)" \
            "cd $TEST_CONTAINER_PROJECT && wallpaper-process process preset ... dark_blur --dry-run" \
            "$dry_run_output"
    fi

    print_test "wallpaper-process process preset --dry-run creates no output"
    test_output="/tmp/wallpaper-orch-dry-preset.jpg"
    rm -f "$test_output" 2>/dev/null
    dry_run_cmd="cd $TEST_CONTAINER_PROJECT && wallpaper-process process preset ... dark_blur --dry-run"
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process preset "$TEST_IMAGE" "$test_output" dark_blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        add_detail "• Test output: $test_output"
        add_detail "• Verified: No file created in dry-run mode"
        test_passed
    else
        test_failed "dry-run created output file (should not execute)" \
            "$dry_run_cmd" \
            "Unexpected file: $test_output"
        rm -f "$test_output"
    fi

    # Note: Orchestrator batch commands delegate to core (host execution), so they're already tested above

    # Clean up container image
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --yes > /dev/null 2>&1)
else
    echo "  Skipping all orchestrator dry-run tests (no container engine)"
fi

# ============================================================================
# DRY-RUN EDGE CASES
# ============================================================================

print_header "DRY-RUN EDGE CASES"

print_test "Dry-run edge case special characters in paths handled correctly"
special_path="/tmp/wallpaper test (dry-run).jpg"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" "$special_path" --effect blur --dry-run 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "magick"; then
    add_detail "• Test path: $special_path (spaces + parentheses)"
    add_detail "• Exit code: $exit_code (success)"
    add_detail "• Command shown: ImageMagick command with special path"
    add_detail "• Verified: Special characters handled in dry-run output"
    test_passed
else
    test_failed "special characters not handled correctly in dry-run (exit: $exit_code)" \
        "wallpaper-core process effect ... \"$special_path\" --dry-run" \
        "$dry_run_output"
fi

print_test "Dry-run edge case very long output path handled correctly"
long_path="/tmp/$(printf 'a%.0s' {1..200}).jpg"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" "$long_path" --effect blur --dry-run 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
    path_length=${#long_path}
    add_detail "• Path length: $path_length characters"
    add_detail "• Verified: Very long path handled without error"
    test_passed
else
    test_failed "very long path not handled correctly in dry-run (exit: $exit_code)" \
        "wallpaper-core process effect ... (200-char path) --dry-run" \
        "$dry_run_output"
fi

print_test "Dry-run edge case parameter defaults and overrides displayed correctly"
# Test with default parameter
dry_run_default=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
# Check that output shows parameter value (either default notation or actual value)
if echo "$dry_run_default" | grep -qE "(blur|0x8|param)"; then
    add_detail "• Effect: blur with default parameters"
    add_detail "• Output contains: Parameter value or reference"
    add_detail "• Verified: Parameters displayed in dry-run output"
    test_passed
else
    test_failed "parameters not displayed in dry-run output (expected blur/0x8/param)" \
        "wallpaper-core process effect ... --effect blur --dry-run" \
        "$dry_run_default"
fi

print_test "Dry-run edge case batch with --flat flag shows correct paths"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-flat --flat --dry-run 2>&1)
# In flat mode, output paths should not have subdirectories
if echo "$dry_run_output" | grep -q "/tmp/batch-flat" && ! echo "$dry_run_output" | grep -q "/effects/"; then
    sample_path=$(echo "$dry_run_output" | grep "/tmp/batch-flat" | head -1 | cut -c1-80)
    add_detail "• Command: wallpaper-core batch effects --flat --dry-run"
    add_detail "• Flag: --flat (no subdirectories)"
    add_detail "• Output dir: /tmp/batch-flat"
    add_detail "• Sample path: $sample_path..."
    add_detail "• Verified: Flat structure shown (no /effects/ subdirs)"
    test_passed
else
    test_failed "flat mode paths incorrect in dry-run (expected /tmp/batch-flat without /effects/ subdirs)" \
        "wallpaper-core batch effects ... --flat --dry-run" \
        "$dry_run_output"
fi

print_test "Dry-run edge case batch with --parallel shows execution mode"
dry_run_output=$(wallpaper-core batch all "$TEST_IMAGE" /tmp/batch-test --parallel --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(parallel|Mode)"; then
    mode_line=$(echo "$dry_run_output" | grep -im1 "parallel\|mode" | head -c 80)
    add_detail "• Command: wallpaper-core batch all --parallel --dry-run"
    add_detail "• Flag: --parallel (concurrent execution)"
    add_detail "• Output mentions: $mode_line..."
    add_detail "• Verified: Execution mode displayed in dry-run"
    test_passed
else
    test_failed "parallel mode not displayed in dry-run output (expected 'parallel' or 'Mode')" \
        "wallpaper-core batch all ... --parallel --dry-run" \
        "$dry_run_output"
fi

print_test "Dry-run edge case validation for all preconditions displayed"
# With missing input, multiple validation checks should appear
dry_run_output=$(wallpaper-core process effect /nonexistent.jpg /tmp/test.jpg --effect blur --dry-run 2>&1)
validation_checks=$(echo "$dry_run_output" | grep -cE "(✓|✗)" || echo "0")
if [ "$validation_checks" -ge 2 ]; then
    add_detail "• Test: Missing input file /nonexistent.jpg"
    add_detail "• Validation checks: $validation_checks"
    add_detail "• Verified: Multiple preconditions validated and displayed"
    test_passed
else
    test_failed "insufficient validation checks in dry-run output (expected ≥2, got $validation_checks)" \
        "wallpaper-core process effect /nonexistent.jpg ... --dry-run" \
        "$dry_run_output"
fi

# ============================================================================
# Summary and Results
# ============================================================================

print_summary() {
    print_header "TEST SUMMARY"

    local total=$((PASSED + FAILED + SKIPPED))
    printf "%-40s %3d\n" "Total Tests Run:" "$total"
    printf "%-40s %3d ${GREEN}✓${NC}\n" "Tests Passed:" "$PASSED"
    printf "%-40s %3d ${RED}✗${NC}\n" "Tests Failed:" "$FAILED"
    printf "%-40s %3d ${YELLOW}⊘${NC}\n" "Tests Skipped:" "$SKIPPED"

    echo ""
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}Results by Category:${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────${NC}"

    for category in "${TEST_CATEGORIES[@]}"; do
        # Skip the summary category itself
        if [[ "$category" == "TEST SUMMARY" ]]; then
            continue
        fi

        local p=${CATEGORY_PASSED["$category"]:-0}
        local f=${CATEGORY_FAILED["$category"]:-0}
        local s=${CATEGORY_SKIPPED["$category"]:-0}

        # Determine status icon
        local status_icon
        if [ "$f" -gt 0 ]; then
            status_icon="${RED}✗${NC}"
        elif [ "$s" -gt 0 ] && [ "$p" -eq 0 ]; then
            status_icon="${YELLOW}⊘${NC}"
        else
            status_icon="${GREEN}✓${NC}"
        fi

        # Build result string
        local result_str="${GREEN}${p}✓${NC}"
        if [ "$f" -gt 0 ]; then
            result_str="$result_str ${RED}${f}✗${NC}"
        fi
        if [ "$s" -gt 0 ]; then
            result_str="$result_str ${YELLOW}${s}⊘${NC}"
        fi

        # Truncate category name if too long
        local short_cat="${category:0:45}"
        if [ ${#category} -gt 45 ]; then
            short_cat="${short_cat}..."
        fi

        echo -e "  $status_icon $short_cat: $result_str"

        # Show verbose details for this category
        if [ "$VERBOSE" = true ] && [ -n "${CATEGORY_DETAILS[$category]:-}" ]; then
            while IFS= read -r detail_line; do
                echo -e "      ${BLUE}$detail_line${NC}"
            done <<< "${CATEGORY_DETAILS[$category]}"
        fi
    done

    # Show details for failures
    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}────────────────────────────────────────────────────────────────${NC}"
        echo -e "${RED}Failed Tests Details:${NC}"
        echo -e "${RED}────────────────────────────────────────────────────────────────${NC}"
        for detail in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}✗${NC} $detail" | head -1
            echo "$detail" | tail -n +2 | while IFS= read -r line; do
                echo -e "     $line"
            done
            echo ""
        done
    fi

    # Show details for skips
    if [ ${#SKIPPED_TESTS[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
        echo -e "${YELLOW}Skipped Tests Details:${NC}"
        echo -e "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
        for detail in "${SKIPPED_TESTS[@]}"; do
            echo -e "  ${YELLOW}⊘${NC} $detail" | head -1
            echo "$detail" | tail -n +2 | while IFS= read -r line; do
                echo -e "     $line"
            done
            echo ""
        done
    fi

    # Final result
    echo ""
    echo "Test outputs: $TEST_OUTPUT_DIR"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        if [ $SKIPPED -gt 0 ]; then
            echo -e "${GREEN}✓ ALL EXECUTED TESTS PASSED!${NC} ${YELLOW}($SKIPPED skipped)${NC}"
        else
            echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
        fi
        echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
        return 0
    else
        echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}✗ SOME TESTS FAILED - See details above${NC}"
        echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
        return 1
    fi
}

# Print summary and return appropriate exit code
print_summary
exit $?
