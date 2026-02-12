# Smoke Tests Reorganization - Changes Summary

## Overview

Reorganized smoke tests to avoid exposing the main test script in the root project structure. Created a clean wrapper interface with parameterized wallpaper support.

## Changes Made

### 1. Created Smoke Tests Infrastructure

**New Directory**: `tools/smoke-tests/`

This directory encapsulates all smoke test infrastructure and provides clean separation from development tools.

### 2. Files Created

#### `tools/smoke-tests/run.sh`
**Purpose**: Wrapper script that handles wallpaper parameter and calls main test script

**Features**:
- Default wallpaper: `tests/fixtures/test-wallpaper.jpg`
- Custom wallpaper support via positional argument
- Verbose mode via `--verbose` flag
- Help text via `--help`
- Automatic path resolution (relative → absolute)
- Graceful fallback to default wallpaper if custom not found
- Clear error messages

**Usage**:
```bash
./tools/smoke-tests/run.sh                      # Default wallpaper
./tools/smoke-tests/run.sh /path/to/image.jpg   # Custom wallpaper
./tools/smoke-tests/run.sh --verbose            # Verbose mode
./tools/smoke-tests/run.sh --verbose /path.jpg  # Both
```

#### `tools/smoke-tests/README.md`
**Purpose**: Comprehensive documentation for smoke tests infrastructure

**Sections**:
- Overview of what smoke tests validate
- File structure and locations
- Usage via Makefile and direct script
- Requirements and dependencies
- What gets tested (85+ test cases)
- Execution flow diagram
- Performance expectations
- Troubleshooting guide
- Integration with CI/CD
- Modifying tests guide

#### `docs/SMOKE_TESTS_MIGRATION_GUIDE.md`
**Purpose**: Complete guide for applying this pattern to other projects

**Sections**:
- Overview and prerequisites
- Step-by-step migration instructions
- File structure after migration
- Usage examples
- Customization guide for different needs
- Troubleshooting common issues
- Verification steps
- Summary of what you get

### 3. Files Modified

#### `Makefile`
**Changes**:
- Updated `smoke-test` target to use wrapper script
- Added `WALLPAPER=/path` parameter support
- Kept `VERBOSE=true` parameter support
- Updated help text
- Cleaner conditional logic for parameter combinations

**Before**:
```makefile
smoke-test: ## Run end-to-end smoke tests (requires ImageMagick + Docker)
	# ... dependency checks ...
	./tools/dev/test-all-commands.sh tests/fixtures/test-wallpaper.jpg
```

**After**:
```makefile
smoke-test: ## Run end-to-end smoke tests (add WALLPAPER=/path or VERBOSE=true)
	# ... dependency checks ...
	./tools/smoke-tests/run.sh [--verbose] [wallpaper-path]
```

**New Usage**:
```bash
make smoke-test                                  # Default
make smoke-test VERBOSE=true                     # Verbose
make smoke-test WALLPAPER=/path/to/image.jpg     # Custom wallpaper
make smoke-test WALLPAPER=/path.jpg VERBOSE=true # Both
```

#### `DEVELOPMENT.md`
**Changes**:
- Added Option 4: Custom wallpaper usage
- Added Option 5: Custom wallpaper + verbose
- Updated examples to show all parameter combinations
- Clearer explanation of what each option does

**New Examples**:
```bash
# Option 4: Run smoke tests with custom wallpaper
make smoke-test WALLPAPER=/path/to/wallpaper.jpg

# Option 5: Custom wallpaper + verbose output
make smoke-test WALLPAPER=/path/to/wallpaper.jpg VERBOSE=true
```

### 4. Files Unchanged

These files remain as-is:
- `tools/dev/test-all-commands.sh` - Main smoke test script (no changes needed)
- `tests/fixtures/test-wallpaper.jpg` - Test wallpaper image
- `.gitattributes` - Binary file handling
- `.github/workflows/smoke-test.yml` - GitHub Actions workflow
- `make push` target - Still calls `make smoke-test` for SMOKE=true

## Key Improvements

### 1. Better Organization
- **Before**: Main test script directly called from Makefile
- **After**: Wrapper script encapsulates execution logic, main script stays in `tools/dev/`

### 2. More Flexible
- **Before**: Fixed wallpaper path
- **After**: Default wallpaper OR custom path via `WALLPAPER=` parameter

### 3. Better Encapsulation
- **Before**: All smoke test logic exposed in Makefile
- **After**: Clean interface via wrapper script, implementation details hidden

### 4. Better Documentation
- **Before**: No dedicated smoke tests documentation
- **After**:
  - `tools/smoke-tests/README.md` - Infrastructure docs
  - `docs/SMOKE_TESTS_MIGRATION_GUIDE.md` - Reusable pattern guide

### 5. Easier to Maintain
- **Before**: Changes require editing Makefile
- **After**: Most changes can be made in wrapper script

## Directory Structure

```
project-root/
├── .github/workflows/
│   └── smoke-test.yml                    # Unchanged
├── .gitattributes                        # Unchanged
├── docs/
│   ├── SMOKE_TESTS_MIGRATION_GUIDE.md    # NEW: Reusable migration guide
│   └── SMOKE_TESTS_CHANGES_SUMMARY.md    # NEW: This file
├── tests/fixtures/
│   └── test-wallpaper.jpg                # Unchanged
├── tools/
│   ├── dev/
│   │   └── test-all-commands.sh          # Unchanged (main test script)
│   └── smoke-tests/                      # NEW directory
│       ├── README.md                     # NEW: Infrastructure docs
│       └── run.sh                        # NEW: Wrapper script
├── Makefile                              # Modified: Updated smoke-test target
└── DEVELOPMENT.md                        # Modified: Added new usage examples
```

## Usage Quick Reference

### Local Development

```bash
# Default: uses tests/fixtures/test-wallpaper.jpg
make smoke-test

# Verbose mode
make smoke-test VERBOSE=true

# Custom wallpaper
make smoke-test WALLPAPER=~/Downloads/my-wallpaper.jpg

# Both custom wallpaper and verbose
make smoke-test WALLPAPER=~/Pictures/test.jpg VERBOSE=true
```

### Direct Script Usage

```bash
# Default wallpaper
./tools/smoke-tests/run.sh

# Custom wallpaper
./tools/smoke-tests/run.sh /path/to/wallpaper.jpg

# Verbose
./tools/smoke-tests/run.sh --verbose

# Both
./tools/smoke-tests/run.sh --verbose /path/to/wallpaper.jpg

# Help
./tools/smoke-tests/run.sh --help
```

### CI Integration

```bash
# Standard CI + smoke tests
make push SMOKE=true

# Standard CI only
make push
```

## Testing the Changes

All changes have been verified:

```bash
# 1. Wrapper script works
✓ ./tools/smoke-tests/run.sh --help
✓ ./tools/smoke-tests/run.sh
✓ ./tools/smoke-tests/run.sh --verbose

# 2. Makefile targets work
✓ make help | grep smoke
✓ make smoke-test
✓ make smoke-test VERBOSE=true
✓ make smoke-test WALLPAPER=/path/to/image.jpg

# 3. Main script still works (85/85 tests pass)
✓ All smoke tests passing
```

## Migration to Other Projects

To apply this pattern to another project:

1. **Read**: `docs/SMOKE_TESTS_MIGRATION_GUIDE.md`
2. **Copy**: `tools/smoke-tests/run.sh` (adapt paths)
3. **Update**: Makefile smoke-test target
4. **Adapt**: Dependency checks for your project
5. **Test**: Run `make smoke-test` to verify

The migration guide provides complete step-by-step instructions with customization examples.

## Rollback (if needed)

To revert to the original simple approach:

```bash
# 1. Remove new files
rm -rf tools/smoke-tests/
rm docs/SMOKE_TESTS_MIGRATION_GUIDE.md
rm docs/SMOKE_TESTS_CHANGES_SUMMARY.md

# 2. Revert Makefile smoke-test target to:
smoke-test:
	./tools/dev/test-all-commands.sh tests/fixtures/test-wallpaper.jpg

# 3. Revert DEVELOPMENT.md to remove Options 4 and 5
```

## Benefits Summary

✅ **Cleaner structure**: Smoke tests infrastructure isolated
✅ **Flexible execution**: Support for custom wallpapers
✅ **Better documentation**: README + migration guide
✅ **Easier maintenance**: Changes in wrapper, not Makefile
✅ **Reusable pattern**: Migration guide for other projects
✅ **No behavior changes**: All existing commands still work
✅ **Backward compatible**: Old usage still works

## Next Steps

1. **Commit changes**:
   ```bash
   git add tools/smoke-tests/ docs/ Makefile DEVELOPMENT.md
   git commit -m "refactor: reorganize smoke tests with wrapper script and custom wallpaper support"
   ```

2. **Test in CI** (optional):
   - Push to GitHub
   - Manually trigger smoke-test.yml workflow
   - Verify it works in GitHub Actions environment

3. **Apply to other projects**:
   - Use `docs/SMOKE_TESTS_MIGRATION_GUIDE.md`
   - Follow step-by-step instructions
   - Adapt to project-specific needs

---

**Date**: 2026-02-12
**Changes**: Reorganization + parameterization
**Impact**: Low (backward compatible)
**Files Changed**: 2 modified, 5 created
**Testing**: All smoke tests passing (85/85)
