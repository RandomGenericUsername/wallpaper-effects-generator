#!/bin/bash
##############################################################################
# Comprehensive Test Suite for wallpaper-effects-generator (core + orchestrator)
#
# Tests both the core CLI (native execution) and orchestrator CLI (containerized)
# Usage: ./test-all-commands.sh <wallpaper-path>
#
# Arguments:
#   wallpaper-path  Path to wallpaper image file (required)
#                   Example: ./test-all-commands.sh ~/Downloads/wallpaper.jpg
##############################################################################

# Validate arguments
if [ $# -eq 0 ]; then
    echo "Error: wallpaper path is required"
    echo "Usage: $0 <wallpaper-path>"
    echo ""
    echo "Example: $0 ~/Downloads/wallpaper.jpg"
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

TEST_OUTPUT_DIR="/tmp/wallpaper-effects-test"
PASSED=0
FAILED=0

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

print_test() {
    echo -ne "  → $1 ... "
}

print_pass() {
    echo -e "${GREEN}✓${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗${NC}"
    ((FAILED++))
}

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
    print_pass
else
    print_fail
fi

print_test "Info command"
if wallpaper-core info > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show effects"
if wallpaper-core show effects > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show composites"
if wallpaper-core show composites > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show presets"
if wallpaper-core show presets > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Process single effect (blur)"
core_effect_out="$TEST_OUTPUT_DIR/core-effect-blur.jpg"
if wallpaper-core process effect "$TEST_IMAGE" "$core_effect_out" --effect blur > /dev/null 2>&1 && [ -f "$core_effect_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Process composite (blackwhite-blur)"
core_composite_out="$TEST_OUTPUT_DIR/core-composite-blackwhite-blur.jpg"
if wallpaper-core process composite "$TEST_IMAGE" "$core_composite_out" --composite blackwhite-blur > /dev/null 2>&1 && [ -f "$core_composite_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Process preset (dark_blur)"
core_preset_out="$TEST_OUTPUT_DIR/core-preset-dark_blur.jpg"
if wallpaper-core process preset "$TEST_IMAGE" "$core_preset_out" --preset dark_blur > /dev/null 2>&1 && [ -f "$core_preset_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Batch effects (blur, sepia)"
core_batch_effect="$TEST_OUTPUT_DIR/core-batch-effect"
mkdir -p "$core_batch_effect"
if wallpaper-core batch effects "$TEST_IMAGE" "$core_batch_effect" --effects blur,sepia > /dev/null 2>&1; then
    if [ -f "$core_batch_effect/$(basename "$TEST_IMAGE" .jpg)/effects/blur.jpg" ] && \
       [ -f "$core_batch_effect/$(basename "$TEST_IMAGE" .jpg)/effects/sepia.jpg" ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Batch composites (blackwhite-blur, blur-brightness80)"
core_batch_composite="$TEST_OUTPUT_DIR/core-batch-composite"
mkdir -p "$core_batch_composite"
if wallpaper-core batch composites "$TEST_IMAGE" "$core_batch_composite" --composites blackwhite-blur,blur-brightness80 > /dev/null 2>&1; then
    if [ -f "$core_batch_composite/$(basename "$TEST_IMAGE" .jpg)/composites/blackwhite-blur.jpg" ] && \
       [ -f "$core_batch_composite/$(basename "$TEST_IMAGE" .jpg)/composites/blur-brightness80.jpg" ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Batch presets (dark_blur, subtle_blur)"
core_batch_preset="$TEST_OUTPUT_DIR/core-batch-preset"
mkdir -p "$core_batch_preset"
if wallpaper-core batch presets "$TEST_IMAGE" "$core_batch_preset" --presets dark_blur,subtle_blur > /dev/null 2>&1; then
    if [ -f "$core_batch_preset/$(basename "$TEST_IMAGE" .jpg)/presets/dark_blur.jpg" ] && \
       [ -f "$core_batch_preset/$(basename "$TEST_IMAGE" .jpg)/presets/subtle_blur.jpg" ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Batch all (effects, composites, presets)"
core_batch_all="$TEST_OUTPUT_DIR/core-batch-all"
mkdir -p "$core_batch_all"
if wallpaper-core batch all "$TEST_IMAGE" "$core_batch_all" > /dev/null 2>&1; then
    # Check if at least some outputs were created
    output_count=$(find "$core_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then  # Should have 9 effects + 4 composites + presets
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

# ============================================================================
# ORCHESTRATOR CLI TESTS (wallpaper-process)
# ============================================================================

print_header "ORCHESTRATOR CLI TESTS (wallpaper-process)"

print_test "Version command"
if wallpaper-process version > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Info command"
if wallpaper-process info > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show effects"
if wallpaper-process show effects > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show composites"
if wallpaper-process show composites > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Show presets"
if wallpaper-process show presets > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

# ============================================================================
# CONTAINER MANAGEMENT TESTS
# ============================================================================

print_header "CONTAINER MANAGEMENT TESTS"

print_test "Install container image"
if wallpaper-process install > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

print_test "Process effect (containerized - blur)"
orch_effect_out="$TEST_OUTPUT_DIR/orch-effect-blur.jpg"
if wallpaper-process process effect "$TEST_IMAGE" "$orch_effect_out" blur > /dev/null 2>&1 && [ -f "$orch_effect_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Process composite (containerized - blackwhite-blur)"
orch_composite_out="$TEST_OUTPUT_DIR/orch-composite-blackwhite-blur.jpg"
if wallpaper-process process composite "$TEST_IMAGE" "$orch_composite_out" blackwhite-blur > /dev/null 2>&1 && [ -f "$orch_composite_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Process preset (containerized - dark_blur)"
orch_preset_out="$TEST_OUTPUT_DIR/orch-preset-dark_blur.jpg"
if wallpaper-process process preset "$TEST_IMAGE" "$orch_preset_out" dark_blur > /dev/null 2>&1 && [ -f "$orch_preset_out" ]; then
    print_pass
else
    print_fail
fi

print_test "Batch effects (host execution - blur, brightness)"
orch_batch_effect="$TEST_OUTPUT_DIR/orch-batch-effect"
mkdir -p "$orch_batch_effect"
if wallpaper-process batch effects "$TEST_IMAGE" "$orch_batch_effect" --effects blur,brightness > /dev/null 2>&1; then
    if [ -f "$orch_batch_effect/$(basename "$TEST_IMAGE" .jpg)/effects/blur.jpg" ] && \
       [ -f "$orch_batch_effect/$(basename "$TEST_IMAGE" .jpg)/effects/brightness.jpg" ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Batch all (host execution)"
orch_batch_all="$TEST_OUTPUT_DIR/orch-batch-all"
mkdir -p "$orch_batch_all"
if wallpaper-process batch all "$TEST_IMAGE" "$orch_batch_all" > /dev/null 2>&1; then
    output_count=$(find "$orch_batch_all" -type f -name "*.jpg" 2>/dev/null | wc -l)
    if [ "$output_count" -gt 15 ]; then
        print_pass
    else
        print_fail
    fi
else
    print_fail
fi

print_test "Uninstall container image"
if wallpaper-process uninstall --yes > /dev/null 2>&1; then
    print_pass
else
    print_fail
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_header "TEST SUMMARY"

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    PERCENT=$((PASSED * 100 / TOTAL))
else
    PERCENT=0
fi

echo -e "${GREEN}Passed:${NC}  $PASSED/$TOTAL (${PERCENT}%)"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:${NC}  $FAILED/$TOTAL"
fi

echo ""
echo "Test outputs: $TEST_OUTPUT_DIR"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}\n"
    exit 0
else
    echo -e "${RED}✗ $FAILED test(s) failed${NC}\n"
    exit 1
fi
