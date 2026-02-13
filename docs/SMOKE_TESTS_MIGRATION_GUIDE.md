# Conditional Smoke Tests Integration - Migration Guide

This guide shows how to integrate conditional end-to-end smoke tests into any project with a similar development setup (uv workspace, GitHub Actions, Makefile-based workflow).

## Overview

This integration adds:
- **Conditional smoke tests** via `make push SMOKE=true`
- **Standalone smoke tests** via `make smoke-test`
- **Parameterized wallpaper** via `WALLPAPER=/path` flag
- **Verbose output** via `VERBOSE=true` flag
- **GitHub Actions workflow** for manual smoke test triggers
- **Hard-fail dependency checking** with clear installation instructions

## Prerequisites

Your project should have:
- **uv workspace** setup with `pyproject.toml`
- **Makefile** for development commands
- **GitHub Actions** workflows
- **act** for local CI simulation (optional but recommended)

## Migration Steps

### Step 1: Create Smoke Tests Infrastructure

#### 1.1 Create Directory Structure

```bash
# Create smoke tests directory
mkdir -p tests/smoke
mkdir -p tests/fixtures
```

#### 1.2 Add Test Wallpaper (or Test Asset)

```bash
# Copy your test asset
cp ~/Downloads/wallpaper.jpg tests/fixtures/test-wallpaper.jpg
```

#### 1.3 Configure Git Binary Handling

Create or append to `.gitattributes`:

```gitattributes
# Binary files
*.jpg binary
*.png binary
*.gif binary
*.jpeg binary

# Test fixtures
tests/fixtures/* binary
```

### Step 2: Move Your Test Script

Move your existing comprehensive test script to `tests/smoke/run-smoke-tests.sh`:

```bash
# Simply move your existing test script
mv tools/dev/test-all-commands.sh tests/smoke/run-smoke-tests.sh

# Or if you have a different location
mv path/to/your/test-script.sh tests/smoke/run-smoke-tests.sh

# Make sure it's executable
chmod +x tests/smoke/run-smoke-tests.sh
```

**Important**: Your test script should:
- Accept a wallpaper/test asset path as the first positional argument
- Support `--verbose` flag (optional but recommended)
- Support `--help` flag (optional but recommended)
- Use `tests/fixtures/test-wallpaper.jpg` as default if no argument provided

### Step 3: Add Makefile Target

Add to your `Makefile`:

```makefile
##@ Smoke Testing
smoke-test: ## Run end-to-end smoke tests (add WALLPAPER=/path or VERBOSE=true)
	@echo -e "$(BLUE)Running smoke tests...$(NC)"
	@# Check dependencies (adapt to your project's needs)
	@if ! command -v magick &> /dev/null; then \
		echo -e "$(RED)✗ ImageMagick (magick) not found$(NC)"; \
		echo -e "$(RED)  Install: sudo apt-get install imagemagick$(NC)"; \
		exit 1; \
	fi
	@if ! command -v docker &> /dev/null && ! command -v podman &> /dev/null; then \
		echo -e "$(RED)✗ Docker or Podman not found$(NC)"; \
		echo -e "$(RED)  Install Docker: https://docs.docker.com/get-docker/$(NC)"; \
		echo -e "$(RED)  Or Podman: sudo apt-get install podman$(NC)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)✓ Dependencies available$(NC)"
	@# Run smoke tests via wrapper script
	@if [ "$(VERBOSE)" = "true" ] && [ -n "$(WALLPAPER)" ]; then \
		./tests/smoke/run-smoke-tests.sh --verbose "$(WALLPAPER)"; \
	elif [ "$(VERBOSE)" = "true" ]; then \
		./tests/smoke/run-smoke-tests.sh --verbose; \
	elif [ -n "$(WALLPAPER)" ]; then \
		./tests/smoke/run-smoke-tests.sh "$(WALLPAPER)"; \
	else \
		./tests/smoke/run-smoke-tests.sh; \
	fi
	@echo -e "$(GREEN)✓ Smoke tests completed$(NC)"
```

**Important Adaptations:**
- Replace dependency checks (ImageMagick, Docker) with your project's actual dependencies
- Add/remove dependency checks as needed
- Keep the color variables (BLUE, GREEN, RED, NC) consistent with your Makefile

### Step 4: Integrate with `make push`

Modify your existing `push` target in `Makefile`:

```makefile
push: ## Run GitHub Actions workflows locally (add SMOKE=true for smoke tests)
	@echo -e "$(BLUE)Setting up GitHub Actions locally...$(NC)"
	@if [ ! -f ./bin/act ]; then \
		echo -e "$(BLUE)Downloading act (GitHub Actions CLI)...$(NC)"; \
		mkdir -p ./bin; \
		curl -sL https://github.com/nektos/act/releases/download/v0.2.65/act_Linux_x86_64.tar.gz -o /tmp/act.tar.gz; \
		tar -xzf /tmp/act.tar.gz -C ./bin; \
		rm /tmp/act.tar.gz; \
		echo -e "$(GREEN)✓ act installed to ./bin/act$(NC)"; \
	else \
		echo -e "$(GREEN)✓ act already available$(NC)"; \
	fi
	@echo -e ""
	@mkdir -p .logs
	@TIMESTAMP=$$(date +%Y%m%d-%H%M%S); \
	LOG_FILE=".logs/make-push-$$TIMESTAMP.log"; \
	if [ "$(SMOKE)" = "true" ]; then \
		echo -e "$(BLUE)Running GitHub Actions with SMOKE TESTS enabled...$(NC)"; \
		echo -e "$(BLUE)This includes standard CI + end-to-end smoke tests$(NC)"; \
		echo -e "$(BLUE)Logs will be saved to: $$LOG_FILE$(NC)"; \
		echo -e ""; \
		./bin/act push 2>&1 | tee "$$LOG_FILE"; \
		STANDARD_EXIT=$$?; \
		if [ $$STANDARD_EXIT -eq 0 ]; then \
			echo -e "" | tee -a "$$LOG_FILE"; \
			echo -e "$(BLUE)Standard CI passed. Running smoke tests...$(NC)" | tee -a "$$LOG_FILE"; \
			$(MAKE) smoke-test 2>&1 | tee -a "$$LOG_FILE"; \
			SMOKE_EXIT=$$?; \
			if [ $$SMOKE_EXIT -ne 0 ]; then \
				echo -e "$(RED)✗ Smoke tests failed$(NC)" | tee -a "$$LOG_FILE"; \
				EXIT_CODE=$$SMOKE_EXIT; \
			else \
				echo -e "$(GREEN)✓ Smoke tests passed$(NC)" | tee -a "$$LOG_FILE"; \
				EXIT_CODE=0; \
			fi; \
		else \
			echo -e "$(RED)✗ Standard CI failed, skipping smoke tests$(NC)" | tee -a "$$LOG_FILE"; \
			EXIT_CODE=$$STANDARD_EXIT; \
		fi; \
	else \
		echo -e "$(BLUE)Running standard GitHub Actions workflows...$(NC)"; \
		echo -e "$(BLUE)Logs will be saved to: $$LOG_FILE$(NC)"; \
		echo -e "$(BLUE)Tip: Add SMOKE=true to include smoke tests$(NC)"; \
		echo -e ""; \
		./bin/act push 2>&1 | tee "$$LOG_FILE"; \
		EXIT_CODE=$$?; \
	fi; \
	echo -e ""; \
	if [ $$EXIT_CODE -eq 0 ]; then \
		echo -e "$(GREEN)✓ GitHub Actions simulation complete$(NC)"; \
	else \
		echo -e "$(RED)✗ GitHub Actions simulation failed (exit code: $$EXIT_CODE)$(NC)"; \
	fi; \
	echo -e ""; \
	echo -e "$(GREEN)📋 Full logs saved to: $$LOG_FILE$(NC)"; \
	echo -e "$(GREEN)Review logs with: cat $$LOG_FILE$(NC)"; \
	echo -e "$(GREEN)Search logs with: grep 'PASSED\|FAILED' $$LOG_FILE$(NC)"; \
	echo -e ""; \
	exit $$EXIT_CODE
```

**Key Changes:**
- Added conditional check for `SMOKE=true` flag
- Runs standard CI first via `act push`
- If CI passes, runs `$(MAKE) smoke-test` directly (not via act)
- All output captured in single timestamped log file
- Sequential execution (CI → smoke tests)

### Step 5: Create GitHub Actions Workflow

Create `.github/workflows/smoke-test.yml`:

```yaml
name: Smoke Tests (Integration)

on:
  workflow_dispatch:
    inputs:
      verbose:
        description: 'Verbose test output'
        required: false
        default: false
        type: boolean

jobs:
  smoke-test:
    name: End-to-End Smoke Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync --dev --all-packages

      - name: Install ImageMagick
        run: |
          echo "📦 Installing ImageMagick..."
          apt-get update -qq 2>&1 | tail -5
          apt-get install -y -qq imagemagick 2>&1 | tail -5
          # Verify installation
          echo "Verifying ImageMagick installation..."
          if ! which magick; then
            echo "ERROR: magick command not found after installation"
            exit 1
          fi
          magick -version | head -1

      - name: Check Docker availability
        run: |
          if which docker > /dev/null 2>&1; then
            echo "✓ Docker is available"
          else
            echo "❌ Docker not available"
            echo "This test requires Docker to be available"
            exit 1
          fi

      - name: Verify test wallpaper exists
        run: |
          if [ ! -f "tests/fixtures/test-wallpaper.jpg" ]; then
            echo "❌ Test wallpaper not found at tests/fixtures/test-wallpaper.jpg"
            exit 1
          fi
          echo "✓ Test wallpaper found"

      - name: Run smoke tests (standard mode)
        if: inputs.verbose == false
        run: |
          cd ${{ github.workspace }}
          ./tests/smoke/run-smoke-tests.sh

      - name: Run smoke tests (verbose mode)
        if: inputs.verbose == true
        run: |
          cd ${{ github.workspace }}
          ./tests/smoke/run-smoke-tests.sh --verbose
```

**Important Adaptations:**
- Change `python-version` to match your project
- Modify dependency installation steps (ImageMagick, etc.)
- Adapt `uv sync` command if your project structure differs
- Change test wallpaper path if different

### Step 6: Update Documentation

Add to your `DEVELOPMENT.md`:

```markdown
### Running with End-to-End Smoke Tests

For comprehensive validation that includes real CLI command execution:

```bash
# Option 1: Run standard CI + smoke tests
make push SMOKE=true

# Option 2: Run smoke tests only (uses default wallpaper)
make smoke-test

# Option 3: Run smoke tests with verbose output
make smoke-test VERBOSE=true

# Option 4: Run smoke tests with custom wallpaper
make smoke-test WALLPAPER=/path/to/wallpaper.jpg

# Option 5: Custom wallpaper + verbose output
make smoke-test WALLPAPER=/path/to/wallpaper.jpg VERBOSE=true
```

#### What Each Command Does

**`make push SMOKE=true`** (Local CI simulation + real smoke tests):
1. Simulates GitHub Actions locally via `act` (lint, security, tests)
2. If CI passes, runs end-to-end smoke tests locally
3. All logs captured in single timestamped file in `.logs/`
4. Total time: ~5-8 minutes

**`make smoke-test`** (Direct smoke tests):
1. Checks dependencies (ImageMagick, Docker/Podman)
2. Runs 85+ integration test cases
3. Fast failure if dependencies missing
4. Time: ~2-5 minutes

**Tests Validated**:
- Core CLI commands with real processing
- Containerized execution
- Container image building
- Dry-run functionality
- Configuration layer merging
- Integration test cases

**Requirements**:
- ImageMagick (`magick` command) must be installed
- Docker or Podman must be available

**Troubleshooting**:

If you see "ImageMagick not found":
```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS
brew install imagemagick

# Fedora/RHEL
sudo dnf install ImageMagick
```

If you see "Docker not found":
```bash
# Install Docker: https://docs.docker.com/get-docker/
# Or use Podman instead
sudo apt-get install podman
```
```

## File Structure After Migration

```
project-root/
├── .github/
│   └── workflows/
│       └── smoke-test.yml          # New: GitHub Actions smoke test workflow
├── .gitattributes                  # New/Modified: Binary file handling
├── tests/
│   ├── fixtures/
│   │   └── test-wallpaper.jpg      # New: Test asset
│   └── smoke/                      # New directory
│       ├── README.md               # New: Smoke tests documentation
│       └── run-smoke-tests.sh      # Moved: Your main test script (from tools/dev/)
├── Makefile                        # Modified: Added smoke-test target, modified push
└── DEVELOPMENT.md                  # Modified: Added smoke tests documentation
```

## Usage Examples

After migration, you'll have these commands available:

```bash
# Run smoke tests with defaults
make smoke-test

# Run with verbose output
make smoke-test VERBOSE=true

# Run with custom wallpaper
make smoke-test WALLPAPER=/path/to/wallpaper.jpg

# Run both custom wallpaper and verbose
make smoke-test WALLPAPER=/path/to/wallpaper.jpg VERBOSE=true

# Run full CI + smoke tests
make push SMOKE=true

# Standard CI only (unchanged)
make push
```

## Key Differences from Original

### What Changed from Initial Plan

**Original Plan:**
- `make push SMOKE=true` would run smoke tests via `act workflow_dispatch`
- Smoke tests would run in Docker container via act

**Final Implementation:**
- `make push SMOKE=true` runs CI via `act`, then runs smoke tests **directly** on host
- Avoids `act` container environment limitations (can't install ImageMagick properly)
- Works reliably because host has proper environment setup

### Why This Approach Works Better

1. **Environment Access**: Direct execution uses host environment (ImageMagick, Docker available)
2. **No Container Issues**: Avoids `act` Docker-in-Docker limitations
3. **Faster Execution**: No container build overhead
4. **Better Error Messages**: Real errors instead of container environment issues
5. **Works Locally and in CI**: Same tests run everywhere

## Customization Guide

### For Different Test Scripts

If your test script has different arguments:

1. **Adapt your test script** to accept standard arguments:
   - First positional argument: path to test asset
   - `--verbose` flag: enable verbose output
   - `--help` flag: show help message

2. **Or update Makefile** to pass arguments in your script's format:
   ```makefile
   # If your script uses --image flag instead
   ./tests/smoke/run-smoke-tests.sh --image "$(WALLPAPER)"
   ```

### For Different Dependencies

If your project needs different dependencies:

1. **Modify `Makefile` smoke-test target**:
   - Replace ImageMagick check with your dependency
   - Add additional checks as needed
   - Update installation instructions

2. **Example**: Check for Node.js instead:
   ```makefile
   @if ! command -v node &> /dev/null; then \
       echo -e "$(RED)✗ Node.js not found$(NC)"; \
       echo -e "$(RED)  Install: https://nodejs.org/$(NC)"; \
       exit 1; \
   fi
   ```

### For Different Asset Types

If you have different test assets (not images):

1. **Update paths** in:
   - `tests/smoke/run-smoke-tests.sh` (DEFAULT_WALLPAPER variable)
   - `Makefile` (smoke-test target comments)
   - `.gitattributes` (binary file patterns)

2. **Rename variables**:
   - `WALLPAPER` → `ASSET` or `INPUT_FILE`
   - `TEST_WALLPAPER` → `TEST_ASSET`

## Troubleshooting

### Script Not Found

If you get "Script not found":
- Verify script is at `tests/smoke/run-smoke-tests.sh`
- Check it's executable: `chmod +x tests/smoke/run-smoke-tests.sh`
- Check permissions: `ls -l tests/smoke/run-smoke-tests.sh`

### Dependency Check Fails

If dependency checks always fail:
- Run `which magick` (or your dependency) manually
- Verify command is in PATH
- Check if dependency is actually installed

### Makefile Syntax Errors

If you get syntax errors:
- Ensure tabs (not spaces) for indentation in Makefile
- Check that all `\` line continuations are correct
- Verify closing `fi` for all `if` statements

## Verification Steps

After migration, verify everything works:

```bash
# 1. Check help is updated
make help | grep smoke

# 2. Test wrapper script directly
./tests/smoke/run-smoke-tests.sh --help

# 3. Run smoke tests with defaults
make smoke-test

# 4. Test with verbose flag
make smoke-test VERBOSE=true

# 5. Test with custom wallpaper
make smoke-test WALLPAPER=/path/to/test.jpg

# 6. Verify GitHub Actions workflow is recognized
./bin/act --list | grep smoke

# 7. Test full CI + smoke tests (long-running)
make push SMOKE=true
```

## Summary

This migration adds:

✅ **Clean organization**: Test script in `tests/smoke/` with other test files
✅ **Flexible execution**: Default or custom wallpaper via `WALLPAPER=` flag
✅ **Verbose output**: Optional detailed test information
✅ **Hard-fail validation**: Clear error messages for missing dependencies
✅ **Conditional integration**: Opt-in smoke tests via `SMOKE=true`
✅ **GitHub Actions ready**: Manual workflow for CI environments
✅ **Single log file**: All output captured in timestamped `.logs/` files

All changes are modular and can be adapted to different project structures and requirements.

---

**Created**: 2026-02-12
**Project**: wallpaper-effects-generator
**Migration Complexity**: Moderate (2-3 hours for full integration)
**Compatibility**: Works with uv workspaces, GitHub Actions, Makefile-based workflows
