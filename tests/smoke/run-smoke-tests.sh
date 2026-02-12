#!/bin/bash
##############################################################################
# Smoke Tests Runner
#
# Wrapper script for running the comprehensive smoke test suite.
# Handles wallpaper selection and test execution.
#
# Usage: ./tests/smoke/run-smoke-tests.sh [OPTIONS] [wallpaper-path]
#
# Options:
#   -v, --verbose    Show detailed test information in summary
#   -h, --help       Show this help message
#
# Arguments:
#   wallpaper-path  Path to wallpaper image file
#                   If not provided, uses default: tests/fixtures/test-wallpaper.jpg
#
##############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Default wallpaper
DEFAULT_WALLPAPER="$PROJECT_ROOT/tests/fixtures/test-wallpaper.jpg"
TEST_WALLPAPER="$DEFAULT_WALLPAPER"
VERBOSE=false

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            head -21 "$0" | tail -15
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            # This is the wallpaper path
            TEST_WALLPAPER="$1"
            shift
            ;;
    esac
done

# Resolve to absolute path
if [ -n "$TEST_WALLPAPER" ] && [ "$TEST_WALLPAPER" != "$DEFAULT_WALLPAPER" ]; then
    TEST_WALLPAPER="$(cd "$(dirname "$TEST_WALLPAPER")" && pwd)/$(basename "$TEST_WALLPAPER")"
fi

# Check if file exists
if [ ! -f "$TEST_WALLPAPER" ]; then
    echo "Error: Wallpaper file not found: $TEST_WALLPAPER"
    echo "Using default: $DEFAULT_WALLPAPER"
    TEST_WALLPAPER="$DEFAULT_WALLPAPER"
fi

# Check if default wallpaper exists
if [ ! -f "$TEST_WALLPAPER" ]; then
    echo "Error: Default wallpaper not found at: $TEST_WALLPAPER"
    echo "Please provide a wallpaper path or ensure tests/fixtures/test-wallpaper.jpg exists"
    exit 1
fi

# Call the main test script
MAIN_SCRIPT="$PROJECT_ROOT/tools/dev/test-all-commands.sh"

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: Main test script not found at: $MAIN_SCRIPT"
    exit 1
fi

# Pass arguments to the main script
if [ "$VERBOSE" = true ]; then
    "$MAIN_SCRIPT" --verbose "$TEST_WALLPAPER"
else
    "$MAIN_SCRIPT" "$TEST_WALLPAPER"
fi
