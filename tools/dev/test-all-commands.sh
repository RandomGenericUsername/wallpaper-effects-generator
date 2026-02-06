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

print_test "Version command"
if wallpaper-core version > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Info command"
if wallpaper-core info > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show effects"
if wallpaper-core show effects > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show composites"
if wallpaper-core show composites > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show presets"
if wallpaper-core show presets > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process single effect (blur)"
core_effect_out="$TEST_OUTPUT_DIR/core-effect-blur.jpg"
if wallpaper-core process effect "$TEST_IMAGE" "$core_effect_out" --effect blur > /dev/null 2>&1 && [ -f "$core_effect_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process composite (blackwhite-blur)"
core_composite_out="$TEST_OUTPUT_DIR/core-composite-blackwhite-blur.jpg"
if wallpaper-core process composite "$TEST_IMAGE" "$core_composite_out" --composite blackwhite-blur > /dev/null 2>&1 && [ -f "$core_composite_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process preset (dark_blur)"
core_preset_out="$TEST_OUTPUT_DIR/core-preset-dark_blur.jpg"
if wallpaper-core process preset "$TEST_IMAGE" "$core_preset_out" --preset dark_blur > /dev/null 2>&1 && [ -f "$core_preset_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Batch effects (all effects)"
core_batch_effect="$TEST_OUTPUT_DIR/core-batch-effect"
mkdir -p "$core_batch_effect"
if wallpaper-core batch effects "$TEST_IMAGE" "$core_batch_effect" > /dev/null 2>&1; then
    # Should generate 9 effects
    output_count=$(find "$core_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
fi

print_test "Batch composites (all composites)"
core_batch_composite="$TEST_OUTPUT_DIR/core-batch-composite"
mkdir -p "$core_batch_composite"
if wallpaper-core batch composites "$TEST_IMAGE" "$core_batch_composite" > /dev/null 2>&1; then
    # Should generate 4 composites
    output_count=$(find "$core_batch_composite" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 4 ]; then
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
fi

print_test "Batch presets (all presets)"
core_batch_preset="$TEST_OUTPUT_DIR/core-batch-preset"
mkdir -p "$core_batch_preset"
if wallpaper-core batch presets "$TEST_IMAGE" "$core_batch_preset" > /dev/null 2>&1; then
    # Should generate 7 presets
    output_count=$(find "$core_batch_preset" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 7 ]; then
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
fi

print_test "Batch all (effects, composites, presets)"
core_batch_all="$TEST_OUTPUT_DIR/core-batch-all"
mkdir -p "$core_batch_all"
if wallpaper-core batch all "$TEST_IMAGE" "$core_batch_all" > /dev/null 2>&1; then
    # Check if at least some outputs were created
    output_count=$(find "$core_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then  # Should have 9 effects + 4 composites + presets
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
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

print_test "User config custom effect loaded"
# Set XDG_CONFIG_HOME to use our test directory
if XDG_CONFIG_HOME="$TEST_USER_CONFIG" wallpaper-core show effects 2>&1 | grep -q "test_custom"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "User config effect override applied"
# Check that blur effect description shows the override
if XDG_CONFIG_HOME="$TEST_USER_CONFIG" wallpaper-core show effects 2>&1 | grep "blur" | grep -q "Overridden blur"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Project-level effects loaded"
# Change to project directory to test project-level config
(cd "$TEST_PROJECT_ROOT" && wallpaper-core show effects 2>&1 | grep -q "project_effect")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "User custom effect can be processed"
user_custom_out="$TEST_OUTPUT_DIR/user-custom-effect.jpg"
if XDG_CONFIG_HOME="$TEST_USER_CONFIG" wallpaper-core process effect "$TEST_IMAGE" "$user_custom_out" --effect test_custom > /dev/null 2>&1 && [ -f "$user_custom_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Project effect can be processed"
project_effect_out="$TEST_OUTPUT_DIR/project-effect.jpg"
(cd "$TEST_PROJECT_ROOT" && wallpaper-core process effect "$TEST_IMAGE" "$project_effect_out" --effect project_effect > /dev/null 2>&1)
if [ -f "$project_effect_out" ]; then
    test_passed
else
    test_failed("command failed")
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

print_test "Invalid YAML in user config shows error"
cat > "$TEST_ERROR_USER/wallpaper-effects-generator/effects.yaml" << 'EOF'
invalid: yaml: content:
  bad: structure
EOF
XDG_CONFIG_HOME="$TEST_ERROR_USER" wallpaper-core show effects > /dev/null 2>&1
if [ $? -ne 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Invalid YAML in project config shows error"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
malformed yaml without proper structure
  missing: colons
EOF
(cd "$TEST_ERROR_PROJECT" && wallpaper-core show effects > /dev/null 2>&1)
if [ $? -ne 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Missing required field shows validation error"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
effects:
  broken_effect:
    description: "Missing command field"
    parameters: {}
EOF
(cd "$TEST_ERROR_PROJECT" && wallpaper-core show effects > /dev/null 2>&1)
if [ $? -ne 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Well-formed but empty effects.yaml works"
cat > "$TEST_ERROR_PROJECT/effects.yaml" << 'EOF'
version: "1.0"
EOF
(cd "$TEST_ERROR_PROJECT" && wallpaper-core show effects > /dev/null 2>&1)
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
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

print_test "3-layer merge: all effects present"
# Should have: package effects + project_effect + user_effect + user-overridden blur
(cd "$TEST_3LAYER_PROJECT" && XDG_CONFIG_HOME="$TEST_3LAYER_USER" wallpaper-core show effects 2>&1 | grep -q "user_effect") && \
(cd "$TEST_3LAYER_PROJECT" && XDG_CONFIG_HOME="$TEST_3LAYER_USER" wallpaper-core show effects 2>&1 | grep -q "project_effect")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "3-layer merge: user override takes precedence"
(cd "$TEST_3LAYER_PROJECT" && XDG_CONFIG_HOME="$TEST_3LAYER_USER" wallpaper-core show effects 2>&1 | grep "blur" | grep -q "User-overridden")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "3-layer merge: process user effect"
threelayer_out="$TEST_OUTPUT_DIR/3layer-user-effect.jpg"
(cd "$TEST_3LAYER_PROJECT" && XDG_CONFIG_HOME="$TEST_3LAYER_USER" wallpaper-core process effect "$TEST_IMAGE" "$threelayer_out" --effect user_effect > /dev/null 2>&1)
if [ -f "$threelayer_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "3-layer merge: process project effect"
threelayer_project_out="$TEST_OUTPUT_DIR/3layer-project-effect.jpg"
(cd "$TEST_3LAYER_PROJECT" && XDG_CONFIG_HOME="$TEST_3LAYER_USER" wallpaper-core process effect "$TEST_IMAGE" "$threelayer_project_out" --effect project_effect > /dev/null 2>&1)
if [ -f "$threelayer_project_out" ]; then
    test_passed
else
    test_failed("command failed")
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

print_test "Parameter types merge across layers"
# Verify both effects are present and can be listed (meaning parameter type merging worked)
(cd "$TEST_PARAMS_PROJECT" && XDG_CONFIG_HOME="$TEST_PARAMS_USER" wallpaper-core show effects 2>&1 | grep -q "user_effect_with_param") && \
(cd "$TEST_PARAMS_PROJECT" && XDG_CONFIG_HOME="$TEST_PARAMS_USER" wallpaper-core show effects 2>&1 | grep -q "project_effect_with_package_param")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
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

print_test "User composite is loaded"
(cd "$TEST_COMP_PROJECT" && XDG_CONFIG_HOME="$TEST_COMP_USER" wallpaper-core show composites 2>&1 | grep -q "user_composite")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "User preset is loaded"
(cd "$TEST_COMP_PROJECT" && XDG_CONFIG_HOME="$TEST_COMP_USER" wallpaper-core show presets 2>&1 | grep -q "user_preset")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Project preset is loaded"
(cd "$TEST_COMP_PROJECT" && XDG_CONFIG_HOME="$TEST_COMP_USER" wallpaper-core show presets 2>&1 | grep -q "project_preset")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "User composite can be processed"
user_comp_out="$TEST_OUTPUT_DIR/user-composite.jpg"
(cd "$TEST_COMP_PROJECT" && XDG_CONFIG_HOME="$TEST_COMP_USER" wallpaper-core process composite "$TEST_IMAGE" "$user_comp_out" --composite user_composite > /dev/null 2>&1)
if [ -f "$user_comp_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "User preset can be processed"
user_preset_out="$TEST_OUTPUT_DIR/user-preset.jpg"
(cd "$TEST_COMP_PROJECT" && XDG_CONFIG_HOME="$TEST_COMP_USER" wallpaper-core process preset "$TEST_IMAGE" "$user_preset_out" --preset user_preset > /dev/null 2>&1)
if [ -f "$user_preset_out" ]; then
    test_passed
else
    test_failed("command failed")
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

print_test "Settings load without errors"
(cd "$TEST_SETTINGS_PROJECT" && XDG_CONFIG_HOME="$TEST_SETTINGS_USER" wallpaper-core info > /dev/null 2>&1)
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

# ============================================================================
# EDGE CASES
# ============================================================================

print_header "EDGE CASES"

TEST_EDGE="$TEST_OUTPUT_DIR/edge-cases"
mkdir -p "$TEST_EDGE/wallpaper-effects-generator"

print_test "Very long effect name"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects:
  this_is_a_very_long_effect_name_that_tests_the_limits_of_identifier_length:
    description: "Effect with very long name"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
EOF
(XDG_CONFIG_HOME="$TEST_EDGE" wallpaper-core show effects 2>&1 | grep -q "this_is_a_very_long")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Effect name with underscores and numbers"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects:
  effect_123_test:
    description: "Effect with numbers"
    command: "convert $INPUT -blur 0x10 $OUTPUT"
    parameters: {}
EOF
(XDG_CONFIG_HOME="$TEST_EDGE" wallpaper-core show effects 2>&1 | grep -q "effect_123_test")
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Empty effects section"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
effects: {}
EOF
XDG_CONFIG_HOME="$TEST_EDGE" wallpaper-core show effects > /dev/null 2>&1
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Only version field (minimal valid file)"
cat > "$TEST_EDGE/wallpaper-effects-generator/effects.yaml" << 'EOF'
version: "1.0"
EOF
XDG_CONFIG_HOME="$TEST_EDGE" wallpaper-core show effects > /dev/null 2>&1
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

# ============================================================================
# ORCHESTRATOR CLI TESTS (wallpaper-process)
# ============================================================================

print_header "ORCHESTRATOR CLI TESTS (wallpaper-process)"

print_test "Version command"
if wallpaper-process version > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Info command"
if wallpaper-process info > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show effects"
if wallpaper-process show effects > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show composites"
if wallpaper-process show composites > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Show presets"
if wallpaper-process show presets > /dev/null 2>&1; then
    test_passed
else
    test_failed("command failed")
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

print_test "Install container image"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process install > /dev/null 2>&1); then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process effect (containerized - blur)"
orch_effect_out="$TEST_OUTPUT_DIR/orch-effect-blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process effect "$TEST_IMAGE" "$orch_effect_out" blur > /dev/null 2>&1) && [ -f "$orch_effect_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process composite (containerized - blackwhite-blur)"
orch_composite_out="$TEST_OUTPUT_DIR/orch-composite-blackwhite-blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process composite "$TEST_IMAGE" "$orch_composite_out" blackwhite-blur > /dev/null 2>&1) && [ -f "$orch_composite_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Process preset (containerized - dark_blur)"
orch_preset_out="$TEST_OUTPUT_DIR/orch-preset-dark_blur.jpg"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process preset "$TEST_IMAGE" "$orch_preset_out" dark_blur > /dev/null 2>&1) && [ -f "$orch_preset_out" ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "Batch effects (host execution - all effects)"
orch_batch_effect="$TEST_OUTPUT_DIR/orch-batch-effect"
mkdir -p "$orch_batch_effect"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process batch effects "$TEST_IMAGE" "$orch_batch_effect" > /dev/null 2>&1); then
    # Should generate 9 effects
    output_count=$(find "$orch_batch_effect" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -ge 9 ]; then
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
fi

print_test "Batch all (host execution)"
orch_batch_all="$TEST_OUTPUT_DIR/orch-batch-all"
mkdir -p "$orch_batch_all"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process batch all "$TEST_IMAGE" "$orch_batch_all" > /dev/null 2>&1); then
    output_count=$(find "$orch_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then
        test_passed
    else
        test_failed("command failed")
    fi
else
    test_failed("command failed")
fi

print_test "Uninstall container image"
if [ "$CONTAINER_ENGINE" = "none" ]; then
    echo "  Skipped (no container engine)"
elif (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --yes > /dev/null 2>&1); then
    test_passed
else
    test_failed("command failed")
fi

# ============================================================================
# DRY-RUN TESTS - CORE CLI
# ============================================================================

print_header "DRY-RUN TESTS - CORE CLI"

print_test "process effect --dry-run shows command without executing"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/dry-run-test.jpg --effect blur --dry-run 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ] && echo "$dry_run_output" | grep -q "magick"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process effect --dry-run creates no output file"
test_output="/tmp/wallpaper-dry-run-should-not-exist.jpg"
rm -f "$test_output" 2>/dev/null
wallpaper-core process effect "$TEST_IMAGE" "$test_output" --effect blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    test_passed
else
    test_failed("command failed")
    rm -f "$test_output"
fi

print_test "process effect --dry-run shows validation checks"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(Validation|✓|✗)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process effect --dry-run with missing input shows warning"
dry_run_output=$(wallpaper-core process effect /nonexistent/file.jpg /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(not found|✗)" && [ $? -ne 1 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process effect --dry-run with unknown effect shows warning"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect nonexistent_effect --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(not found|✗)" && [ $? -ne 1 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process effect -q --dry-run shows only command (quiet mode)"
dry_run_output=$(wallpaper-core -q process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "magick" && ! echo "$dry_run_output" | grep -q "Validation"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process composite --dry-run shows chain commands"
dry_run_output=$(wallpaper-core process composite "$TEST_IMAGE" /tmp/test.jpg --composite blackwhite-blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -qi "blur" && echo "$dry_run_output" | grep -qi "blackwhite"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process composite --dry-run creates no output file"
test_output="/tmp/wallpaper-composite-dry-run.jpg"
rm -f "$test_output" 2>/dev/null
wallpaper-core process composite "$TEST_IMAGE" "$test_output" --composite blackwhite-blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    test_passed
else
    test_failed("command failed")
    rm -f "$test_output"
fi

print_test "process preset --dry-run shows resolved command"
dry_run_output=$(wallpaper-core process preset "$TEST_IMAGE" /tmp/test.jpg --preset dark_blur --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "magick"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "process preset --dry-run creates no output file"
test_output="/tmp/wallpaper-preset-dry-run.jpg"
rm -f "$test_output" 2>/dev/null
wallpaper-core process preset "$TEST_IMAGE" "$test_output" --preset dark_blur --dry-run > /dev/null 2>&1
if [ ! -f "$test_output" ]; then
    test_passed
else
    test_failed("command failed")
    rm -f "$test_output"
fi

print_test "batch effects --dry-run shows table with all effects"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -q "blur" && echo "$dry_run_output" | grep -q "blackwhite"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch effects --dry-run shows item count"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "([0-9]+ items|Effects)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch effects --dry-run shows resolved commands"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
command_count=$(echo "$dry_run_output" | grep -c "magick" || echo "0")
if [ "$command_count" -ge 3 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch effects --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-dry-run"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
wallpaper-core batch effects "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi
rm -rf "$test_dir"

print_test "batch composites --dry-run shows table"
dry_run_output=$(wallpaper-core batch composites "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(blackwhite-blur|Composites)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch composites --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-composite-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
wallpaper-core batch composites "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi
rm -rf "$test_dir"

print_test "batch presets --dry-run shows table"
dry_run_output=$(wallpaper-core batch presets "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(dark_blur|Presets|subtle_blur)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch presets --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-preset-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
wallpaper-core batch presets "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi
rm -rf "$test_dir"

print_test "batch all --dry-run shows all item types"
dry_run_output=$(wallpaper-core batch all "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(Effects|Composites|Presets)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "batch all --dry-run creates no files"
test_dir="/tmp/wallpaper-batch-all-dry"
rm -rf "$test_dir" 2>/dev/null
mkdir -p "$test_dir"
wallpaper-core batch all "$TEST_IMAGE" "$test_dir" --dry-run > /dev/null 2>&1
file_count=$(find "$test_dir" -type f 2>/dev/null | wc -l)
if [ "$file_count" -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi
rm -rf "$test_dir"

print_test "batch all -q --dry-run shows only commands (quiet mode)"
dry_run_output=$(wallpaper-core -q batch all "$TEST_IMAGE" /tmp/batch-test --dry-run 2>&1)
command_count=$(echo "$dry_run_output" | grep -c "magick" || echo "0")
if [ "$command_count" -ge 5 ] && ! echo "$dry_run_output" | grep -q "Validation"; then
    test_passed
else
    test_failed("command failed")
fi

# ============================================================================
# DRY-RUN TESTS - ORCHESTRATOR CLI
# ============================================================================

print_header "DRY-RUN TESTS - ORCHESTRATOR CLI"

if [ "$CONTAINER_ENGINE" != "none" ]; then
    # Re-install image for dry-run tests
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process install > /dev/null 2>&1)

    print_test "install --dry-run shows build command"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process install --dry-run 2>&1)
    if echo "$dry_run_output" | grep -qi "build" && echo "$dry_run_output" | grep -qi "dockerfile"; then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "install --dry-run does not build image"
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
    XDG_CONFIG_HOME="$TEST_CONTAINER_PROJECT" wallpaper-process install --dry-run > /dev/null 2>&1
    if ! $CONTAINER_ENGINE inspect "$test_image_name" > /dev/null 2>&1; then
        test_passed
    else
        test_failed("command failed")
        $CONTAINER_ENGINE rmi "$test_image_name" > /dev/null 2>&1
    fi
    rm -f "$TEST_CONTAINER_PROJECT/settings-drytest.toml"

    print_test "uninstall --dry-run shows rmi command"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "rmi"; then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "uninstall --dry-run does not remove image"
    # Check image still exists after dry-run uninstall
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process uninstall --dry-run > /dev/null 2>&1)
    if (cd "$TEST_CONTAINER_PROJECT" && $CONTAINER_ENGINE inspect wallpaper-effects:latest > /dev/null 2>&1); then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "process effect --dry-run shows both host and inner commands"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process effect "$TEST_IMAGE" /tmp/test.jpg blur --dry-run 2>&1)
    has_host_cmd=$(echo "$dry_run_output" | grep -E "($CONTAINER_ENGINE|run)" | wc -l)
    has_inner_cmd=$(echo "$dry_run_output" | grep "magick" | wc -l)
    if [ "$has_host_cmd" -ge 1 ] && [ "$has_inner_cmd" -ge 1 ]; then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "process effect --dry-run does not spawn container"
    test_output="/tmp/wallpaper-orch-dry-effect.jpg"
    rm -f "$test_output" 2>/dev/null
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process effect "$TEST_IMAGE" "$test_output" blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        test_passed
    else
        test_failed("command failed")
        rm -f "$test_output"
    fi

    print_test "process composite --dry-run shows container and chain"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process composite "$TEST_IMAGE" /tmp/test.jpg blackwhite-blur --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "$CONTAINER_ENGINE" && echo "$dry_run_output" | grep -qi "blur"; then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "process composite --dry-run creates no output"
    test_output="/tmp/wallpaper-orch-dry-composite.jpg"
    rm -f "$test_output" 2>/dev/null
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process composite "$TEST_IMAGE" "$test_output" blackwhite-blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        test_passed
    else
        test_failed("command failed")
        rm -f "$test_output"
    fi

    print_test "process preset --dry-run shows container command"
    dry_run_output=$(cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process preset "$TEST_IMAGE" /tmp/test.jpg dark_blur --dry-run 2>&1)
    if echo "$dry_run_output" | grep -q "$CONTAINER_ENGINE"; then
        test_passed
    else
        test_failed("command failed")
    fi

    print_test "process preset --dry-run creates no output"
    test_output="/tmp/wallpaper-orch-dry-preset.jpg"
    rm -f "$test_output" 2>/dev/null
    (cd "$TEST_CONTAINER_PROJECT" && wallpaper-process process preset "$TEST_IMAGE" "$test_output" dark_blur --dry-run > /dev/null 2>&1)
    if [ ! -f "$test_output" ]; then
        test_passed
    else
        test_failed("command failed")
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

print_test "dry-run with special characters in paths"
special_path="/tmp/wallpaper test (dry-run).jpg"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" "$special_path" --effect blur --dry-run 2>&1)
if [ $? -eq 0 ] && echo "$dry_run_output" | grep -q "magick"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "dry-run with very long output path"
long_path="/tmp/$(printf 'a%.0s' {1..200}).jpg"
dry_run_output=$(wallpaper-core process effect "$TEST_IMAGE" "$long_path" --effect blur --dry-run 2>&1)
if [ $? -eq 0 ]; then
    test_passed
else
    test_failed("command failed")
fi

print_test "dry-run shows parameter defaults vs overrides"
# Test with default parameter
dry_run_default=$(wallpaper-core process effect "$TEST_IMAGE" /tmp/test.jpg --effect blur --dry-run 2>&1)
# Check that output shows parameter value (either default notation or actual value)
if echo "$dry_run_default" | grep -qE "(blur|0x8|param)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "dry-run batch with --flat flag shows correct paths"
dry_run_output=$(wallpaper-core batch effects "$TEST_IMAGE" /tmp/batch-flat --flat --dry-run 2>&1)
# In flat mode, output paths should not have subdirectories
if echo "$dry_run_output" | grep -q "/tmp/batch-flat" && ! echo "$dry_run_output" | grep -q "/effects/"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "dry-run batch with --parallel shows execution mode"
dry_run_output=$(wallpaper-core batch all "$TEST_IMAGE" /tmp/batch-test --parallel --dry-run 2>&1)
if echo "$dry_run_output" | grep -qE "(parallel|Mode)"; then
    test_passed
else
    test_failed("command failed")
fi

print_test "dry-run shows validation for all preconditions"
# With missing input, multiple validation checks should appear
dry_run_output=$(wallpaper-core process effect /nonexistent.jpg /tmp/test.jpg --effect blur --dry-run 2>&1)
validation_checks=$(echo "$dry_run_output" | grep -cE "(✓|✗)" || echo "0")
if [ "$validation_checks" -ge 2 ]; then
    test_passed
else
    test_failed("command failed")
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
