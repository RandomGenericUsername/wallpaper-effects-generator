# Smoke Tests

End-to-end integration testing for the wallpaper-effects-generator project.

## Overview

This directory contains the infrastructure for running comprehensive smoke tests that validate the full CLI workflow including:

- Core CLI commands (version, info, show, process, batch)
- Orchestrator CLI commands with containerization
- Real image processing with ImageMagick
- Container image building with Docker/Podman
- Dry-run functionality validation
- Configuration layer merging
- 85+ integration test cases

## Files

- **run.sh** - Wrapper script for executing smoke tests with wallpaper parameter handling
- **../dev/test-all-commands.sh** - Main comprehensive smoke test script (85+ test cases)

## Usage

### Via Makefile (Recommended)

```bash
# Run smoke tests with default wallpaper
make smoke-test

# Run with custom wallpaper
make smoke-test WALLPAPER=/path/to/wallpaper.jpg

# Run with verbose output
make smoke-test VERBOSE=true

# Run with custom wallpaper and verbose output
make smoke-test WALLPAPER=/path/to/wallpaper.jpg VERBOSE=true
```

### Direct Script Execution

```bash
# Use default wallpaper from tests/fixtures/test-wallpaper.jpg
./tools/smoke-tests/run.sh

# Use custom wallpaper
./tools/smoke-tests/run.sh /path/to/wallpaper.jpg

# Verbose mode with default wallpaper
./tools/smoke-tests/run.sh --verbose

# Verbose mode with custom wallpaper
./tools/smoke-tests/run.sh --verbose /path/to/wallpaper.jpg

# Help
./tools/smoke-tests/run.sh --help
```

## Requirements

- **ImageMagick** (`magick` command)
  - Ubuntu/Debian: `sudo apt-get install imagemagick`
  - macOS: `brew install imagemagick`
  - Fedora/RHEL: `sudo dnf install ImageMagick`

- **Docker or Podman**
  - Docker: https://docs.docker.com/get-docker/
  - Podman: `sudo apt-get install podman` (Ubuntu/Debian)

- **Test Wallpaper**
  - Default location: `tests/fixtures/test-wallpaper.jpg`
  - Can provide custom wallpaper via WALLPAPER flag

## What Gets Tested

### Core CLI Tests (13 tests)
- Basic commands (version, info, show)
- Process commands (effect, composite, preset)
- Batch commands (effects, composites, presets, all)

### Orchestrator Tests (12 tests)
- Containerized execution
- Container installation/uninstallation
- Process and batch commands via container

### Configuration Tests (15 tests)
- Layered effects configuration (3-layer merge)
- Layered settings configuration
- Parameter type handling
- Composite and preset loading

### Dry-Run Tests (31 tests)
- Core CLI dry-run validation
- Orchestrator CLI dry-run validation
- Edge cases and special characters

### Edge Cases (10 tests)
- Long effect names
- Special characters in paths
- Empty configuration sections
- Parameter overrides

## Execution Flow

```
Dependency Check
  ├─ ImageMagick (magick)
  ├─ Docker or Podman
  └─ Test wallpaper

Initialize Environment
  ├─ Create temp directory
  └─ Set up configuration

Run Test Categories
  ├─ Core CLI Basic Commands
  ├─ Core Process Commands
  ├─ Core Batch Commands
  ├─ Orchestrator CLI Basic Commands
  ├─ Orchestrator Container Workflow
  ├─ Layered Effects Configuration
  ├─ Layered Settings Tests
  ├─ Core CLI Dry-Run Commands
  ├─ Orchestrator CLI Dry-Run Commands
  └─ Edge Cases and Error Handling

Generate Report
  ├─ Test summary
  ├─ Results by category
  ├─ Failed test details (if any)
  └─ Output location
```

## Performance

- **Expected Duration**: 2-5 minutes
- **Test Count**: 85+ test cases
- **Success Rate**: All tests should pass when dependencies are installed

## Troubleshooting

### "ImageMagick not found"
```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS
brew install imagemagick

# Fedora/RHEL
sudo dnf install ImageMagick
```

### "Docker not found"
```bash
# Install Docker
# Visit: https://docs.docker.com/get-docker/

# Or use Podman (Ubuntu/Debian)
sudo apt-get install podman
```

### "Test wallpaper not found"
Ensure one of the following:
- `tests/fixtures/test-wallpaper.jpg` exists in the project root
- Provide custom wallpaper: `make smoke-test WALLPAPER=/path/to/wallpaper.jpg`

### Tests fail with "magick: not found"
This means ImageMagick is not properly installed or not in PATH.
```bash
# Verify installation
which magick
magick -version

# If still not found, reinstall ImageMagick
```

## Integration with CI/CD

### Locally (Direct Execution)
```bash
make smoke-test                    # Quick test with defaults
make smoke-test VERBOSE=true       # Detailed output
```

### Before Pushing (Combined with CI Simulation)
```bash
make push SMOKE=true               # Run CI + smoke tests
```

### In GitHub Actions
The workflow in `.github/workflows/smoke-test.yml` runs when manually triggered:
- Has proper environment setup
- Automatic dependency installation
- Full Docker support

## Modifying Tests

The main test script (`tools/dev/test-all-commands.sh`) should not be modified for simple test runs. To add new tests:

1. Edit `tools/dev/test-all-commands.sh` directly
2. Follow the existing test pattern
3. Run `make smoke-test` to verify changes
4. Update documentation if adding new test categories

## File Locations

```
tools/
├── dev/
│   └── test-all-commands.sh      # Main test script (85+ tests)
└── smoke-tests/
    ├── README.md                  # This file
    └── run.sh                      # Wrapper script

tests/
└── fixtures/
    └── test-wallpaper.jpg         # Default test image (2.0M)

.github/workflows/
└── smoke-test.yml                 # GitHub Actions workflow
```

## See Also

- `DEVELOPMENT.md` - Development workflow guide
- `Makefile` - Make targets and build commands
- `.github/workflows/smoke-test.yml` - GitHub Actions workflow definition
