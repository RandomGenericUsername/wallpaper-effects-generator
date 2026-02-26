# Contributing and Development Workflow

An explanation of the development setup, tooling, and workflow for contributors to `wallpaper-effects-generator`.

---

## Setting up the development environment

After cloning the repository, run from the project root:

```bash
make dev
```

This installs all four packages in editable mode (with `uv`) and sets up the pre-commit hooks.

---

## Package layout

Each package in `packages/` is a standalone Python project with its own:

- `pyproject.toml` — dependencies and build config.
- `src/<package_name>/` — source code.
- `tests/` — test suite.
- `README.md` — package-level documentation.

The root `Makefile` provides convenience targets that operate across all packages.

---

## Running tests

Run all tests:

```bash
make test-all
```

Run tests for a single package:

```bash
make test-settings
make test-effects
make test-core
make test-orchestrator
```

In tests, `shutil.which("magick")` is mocked to return a known path so ImageMagick does not need to be installed on the test machine.

---

## Code quality

```bash
make format      # Auto-format with Black, isort, and Ruff
make lint        # Check formatting, linting, and type errors (mypy)
make security    # Run Bandit security scanner
make pipeline    # Run the full validation pipeline (format check + lint + security + tests)
```

All tools use line length 88. The same configuration is used in pre-commit hooks and in GitHub Actions CI.

---

## Pre-commit hooks

Pre-commit hooks run automatically before each commit. Hooks include:

- Trailing whitespace and EOF fixes
- YAML, JSON, and TOML syntax checks
- Black (formatting)
- isort (import ordering)
- Ruff (linting)
- mypy (type checking)
- Bandit (security)
- Large file detection (>1 MB)

To run hooks manually:

```bash
pre-commit run --all-files
```

---

## Local CI simulation

```bash
make push
```

This downloads the `act` tool (if not already present) and runs GitHub Actions workflows in local Docker containers, capturing output to `.logs/`.

For smoke testing without act:

```bash
make smoke-test
```

This requires ImageMagick and Docker/Podman to be installed on the host.

---

## Adding a new effect

1. Edit `packages/core/effects/effects.yaml` (or a project/user override file).
2. Add an entry under `effects:` with a `description` and `command` template.
3. Optionally add `parameters:` with `cli_flag`, `type`, `default`, and `description`.
4. Run `wallpaper-core show effects` to verify it appears.
5. Run `make test-core` to confirm tests pass.

---

## Adding a new composite or preset

Add entries under `composites:` or `presets:` in `effects.yaml`. Composites reference effect names in a `chain:` list. Presets reference either an `effect:` name (with optional `params:`) or a `composite:` name.

---

## Cleaning up build artifacts

```bash
make clean
```

Removes `__pycache__`, `.pytest_cache`, `.mypy_cache`, and build artifacts across all packages.
