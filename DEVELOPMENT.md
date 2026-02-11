# Development Pipeline Guide

This guide explains how to use the development pipeline for the wallpaper-effects-generator project.

## Quick Start

### First Time Setup
```bash
make dev
```
This installs all development dependencies and pre-commit hooks.

### Before Committing
```bash
make pipeline
```
This runs the complete validation pipeline (linting, security, tests) just like GitHub Actions will.

---

## Common Workflows

### 🎨 Format Your Code
```bash
make format
```
Auto-formats all code in all packages using Black, isort, and Ruff.

**For a specific package:**
```bash
make format-settings      # or format-core, format-effects, format-orchestrator
```

### 🔍 Check Code Quality
```bash
make lint
```
Checks for formatting issues, linting problems, and type errors in all packages.

**For a specific package:**
```bash
make lint-settings
```

### ✅ Run Tests
```bash
make test-all
```
Runs all tests with coverage reporting.

**For a specific package:**
```bash
make test-settings        # or test-core, test-effects, test-orchestrator
```

### 🔒 Security Check
```bash
make security
```
Runs Bandit security scanner on all packages.

### 🚀 Full Pipeline (Local CI)
```bash
make pipeline
```
Runs the complete pipeline that simulates GitHub Actions:
1. Linting on all packages
2. Security scans
3. Tests with coverage validation

---

## Understanding Error Messages

### When `make format` or `make lint` fails

The Makefile now provides **clear guidance** on what to do:

```
Linting settings package...
Black formatting needed. Run: make format-settings
make: *** [Makefile:66: lint-settings] Error 1
```

**This means:** Run `make format-settings` to fix the formatting issues.

### Common Issues & Solutions

| Error | Solution |
|-------|----------|
| `Black formatting needed` | `make format-<package>` |
| `Ruff found issues` | `make format-<package>` |
| `Import sorting needed` | `make format-<package>` |
| `Type errors found` | Fix manually or ask for help |
| `Security issues detected` | Review with `make security-<package>` |

---

## Pre-commit Hooks

Pre-commit hooks run **automatically** before every commit to catch issues early.

### Install Hooks
```bash
pre-commit install
```

### Run Manually
```bash
pre-commit run --all-files
```

### Hooks Included
- **File checks:** Trailing whitespace, EOF, YAML/JSON/TOML syntax
- **Python formatting:** Black, isort
- **Linting:** Ruff
- **Type checking:** mypy
- **Security:** Bandit
- **Large files:** Detects files >1MB

---

## Development Environment

### Install Dependencies
```bash
make install-deps          # Install all dev dependencies
make install-settings      # Install specific package
make install-core
make install-effects
make install-orchestrator
```

### Clean Build Artifacts
```bash
make clean
```
Removes `__pycache__`, `.pytest_cache`, `.mypy_cache`, build artifacts, etc.

---

## GitHub Actions

Workflows are automatically triggered on push/PR:

### Workflows
- `ci-core.yml` - Runs when core package changes
- `ci-settings.yml` - Runs when settings package changes
- `ci-effects.yml` - Runs when effects package changes
- `ci-orchestrator.yml` - Runs when orchestrator package changes

### What They Do
Each workflow:
1. **Lints** - Runs ruff, black, isort, mypy
2. **Security** - Runs Bandit and uploads report
3. **Tests** - Runs on ubuntu + macos with Python 3.12 & 3.13
   - Reports coverage to Codecov
   - Enforces 95% coverage threshold

### Setup Codecov
Add `CODECOV_TOKEN` secret to GitHub repo settings for coverage reports.

### Running GitHub Actions Locally

Before pushing to GitHub, test the entire CI pipeline locally:

```bash
make push
```

This will:
1. Download the `act` tool (GitHub Actions CLI) if not already present
2. Run all GitHub Actions workflows in local Docker containers
3. Simulate the exact environment GitHub uses (Ubuntu, specific Python versions)
4. Report any issues before they reach the cloud

**Benefits of local testing:**
- Catch CI failures before pushing
- Faster feedback loop (minutes vs. GitHub Actions queuing)
- No failed builds in your commit history
- Safe testing of edge cases

### Workflow: Fast Testing → Local CI → Push to Cloud

```bash
# 1. Make your changes
vim packages/core/src/wallpaper_core/something.py

# 2. Format and lint locally
make format-core
make lint-core

# 3. Test locally
make test-core

# 4. Run full local pipeline
make pipeline

# 5. Run GitHub Actions locally (final check)
make push

# 6. Push to GitHub if all passes
git push origin master
```

---

## Configuration Standardization

### Pre-commit Hooks vs GitHub Actions

All tools are **configured identically** in both environments:

| Tool | Config | Pre-commit | GitHub Actions |
|------|--------|-----------|-----------------|
| Ruff | Line length | `--line-length=88` | `--line-length=88` |
| Black | Line length | `--line-length=88` | `--line-length=88` |
| isort | Profile & length | `--profile black --line-length 88` | `--profile black --line-length 88` |
| mypy | Strict mode | `config in pyproject.toml` | `config in pyproject.toml` |
| Bandit | Security scan | `config in pyproject.toml` | `config in pyproject.toml` |

**Key Points:**
- Configuration is centralized in `pyproject.toml`
- Pre-commit hooks enforce the same rules as GitHub Actions
- No surprises: if it passes locally, it passes in the cloud

### Special Handling: External Dependencies

Some validation checks require external tools that may not be available everywhere:

**Example: ImageMagick (magick) Binary**

The `wallpaper_core/dry_run.py` module performs pre-flight validation checks using `shutil.which("magick")`.

**How we handle it:**
- **Local development:** Not required for tests (mocked)
- **GitHub Actions:** Not required (mocked via test fixtures)
- **Integration tests:** Use subprocess mocking to simulate ImageMagick without installation

The mock is configured in:
```python
# packages/core/tests/conftest.py
@pytest.fixture(autouse=True)
def mock_subprocess_for_integration_tests():
    """Mock subprocess.run and shutil.which for all tests"""
    def mock_which(cmd):
        if cmd == "magick":
            return "/usr/bin/magick"  # Fake path for validation checks
        return None

    with patch("shutil.which", side_effect=mock_which):
        yield
```

This ensures:
- Tests don't require ImageMagick to be installed
- Validation checks pass without external dependencies
- CI/CD pipeline is isolated and reproducible

---

## Tools Overview

| Tool | Purpose | Run Via |
|------|---------|---------|
| **Ruff** | Fast linting | `make lint` |
| **Black** | Code formatting | `make format` |
| **isort** | Import sorting | `make format` |
| **mypy** | Type checking | `make lint` |
| **Bandit** | Security scanning | `make security` |
| **pytest** | Unit testing | `make test-all` |
| **pre-commit** | Git hooks | `pre-commit run` |

---

## Typical Development Workflow

```bash
# 1. Make your changes
vim packages/core/src/wallpaper_core/something.py

# 2. Format code
make format-core

# 3. Check quality
make lint-core

# 4. Run tests
make test-core

# 5. Commit (pre-commit hooks run automatically)
git add packages/core/
git commit -m "feat: describe your changes"

# 6. Before final push, validate full pipeline
make pipeline
```

---

## Troubleshooting

### "Pre-commit hook failed"
This is **good** - it caught an issue before committing. Fix it and try again:
```bash
make format
git add .
git commit -m "your message"
```

### "Tests fail but pass locally"
Run with the same settings:
```bash
cd packages/core
uv run pytest -n auto --cov=src
```

### "Coverage below 95%"
Add more test cases or check coverage report:
```bash
make test-core
# or
cd packages/core && uv run coverage report --skip-covered
```

### "MyPy errors"
Type checking is strict. Either:
1. Fix the type issues
2. Add type hints
3. Use `# type: ignore` as last resort (not recommended)

---

## Configuration Files

- **pyproject.toml** - Tool configuration (Black, isort, Ruff), dependencies
- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- **.github/workflows/** - GitHub Actions workflows
- **Makefile** - Development commands

---

## Need Help?

```bash
make help
```

This shows all available make targets and their descriptions.
