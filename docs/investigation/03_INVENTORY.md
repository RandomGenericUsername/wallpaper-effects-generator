# Repo Inventory (Deterministic)

<!-- Populated during PHASE_1_INVENTORY, iteration 0001 -->

## Status values
- `in-scope`
- `ignored` (must cite `.auditignore` pattern)
- `binary`
- `too-large`
- `unknown`

## Files
| Path | Type | Status | Role/Notes |
|------|------|--------|------------|
| README.md | Markdown doc | in-scope | Top-level project overview and usage guide |
| DEVELOPMENT.md | Markdown doc | in-scope | Developer setup, contribution, and workflow guide |
| CHANGELOG.md | Markdown doc | in-scope | Project-level changelog |
| Makefile | Build config | in-scope | Root Makefile: dev install, test-all, per-package test targets |
| pyproject.toml | Project config | in-scope | Root project configuration (workspace, linting, formatting) |
| settings.toml | Config data | in-scope | Project-level layered settings demo/defaults file |
| uv.lock | Lockfile | in-scope | Root uv dependency lockfile (reproducible installs) |
| .gitignore | VCS config | in-scope | Root gitignore rules |
| .gitattributes | VCS config | in-scope | Git attributes (marks image types as binary) |
| .pre-commit-config.yaml | CI/lint config | in-scope | Pre-commit hooks configuration (ruff, mypy, etc.) |
| .python-version | Tooling config | in-scope | Pinned Python version (3.12) for pyenv/uv |
| .github/pull_request_template.md | GitHub config | in-scope | PR description template |
| .github/workflows/ci-core.yml | CI config | in-scope | GitHub Actions CI pipeline for wallpaper-core package |
| .github/workflows/ci-effects.yml | CI config | in-scope | GitHub Actions CI pipeline for layered-effects package |
| .github/workflows/ci-orchestrator.yml | CI config | in-scope | GitHub Actions CI pipeline for wallpaper-orchestrator package |
| .github/workflows/ci-settings.yml | CI config | in-scope | GitHub Actions CI pipeline for layered-settings package |
| .github/workflows/smoke-test.yml | CI config | in-scope | GitHub Actions workflow for end-to-end smoke tests |
| docs/MIGRATION.md | Markdown doc | in-scope | Migration guide for project changes |
| docs/SMOKE_TESTS_CHANGES_SUMMARY.md | Markdown doc | in-scope | Summary of smoke test changes/updates |
| docs/SMOKE_TESTS_MIGRATION_GUIDE.md | Markdown doc | in-scope | Guide for migrating smoke tests |
| tests/fixtures/test-wallpaper.jpg | Image binary | ignored | Test fixture image; matches *.jpg ignore pattern |
| tests/smoke/README.md | Markdown doc | in-scope | Documentation for smoke test suite |
| tests/smoke/run-smoke-tests.sh | Shell script | in-scope | Bash script that runs comprehensive end-to-end smoke tests |
| packages/core/README.md | Markdown doc | in-scope | wallpaper-core package user-facing documentation |
| packages/core/pyproject.toml | Project config | in-scope | wallpaper-core package configuration and dependencies |
| packages/core/MANIFEST.in | Build config | in-scope | Includes effects/effects.yaml in core package distribution |
| packages/core/.gitignore | VCS config | in-scope | Package-level gitignore (wallpapers-output/) |
| packages/core/uv.lock | Lockfile | in-scope | wallpaper-core package-level uv dependency lockfile |
| packages/core/effects/effects.yaml | YAML data | in-scope | Canonical effects definition file (top-level copy; identical to src copy) |
| packages/core/src/wallpaper_core/__init__.py | Python source | in-scope | wallpaper-core package public API entrypoint |
| packages/core/src/wallpaper_core/py.typed | Typing marker | in-scope | PEP 561 py.typed marker enabling type checking for downstream consumers |
| packages/core/src/wallpaper_core/dry_run.py | Python source | in-scope | Dry-run mode support for wallpaper-core (no-op execution) |
| packages/core/src/wallpaper_core/cli/__init__.py | Python source | in-scope | wallpaper-core CLI subpackage init |
| packages/core/src/wallpaper_core/cli/main.py | Python source | in-scope | wallpaper-core CLI entrypoint (Click app, `wallpaper-core` command) |
| packages/core/src/wallpaper_core/cli/batch.py | Python source | in-scope | CLI batch subcommand for processing multiple wallpapers |
| packages/core/src/wallpaper_core/cli/process.py | Python source | in-scope | CLI process subcommand for single wallpaper processing |
| packages/core/src/wallpaper_core/cli/show.py | Python source | in-scope | CLI show subcommand for displaying effects/config |
| packages/core/src/wallpaper_core/cli/path_utils.py | Python source | in-scope | CLI path resolution utilities |
| packages/core/src/wallpaper_core/config/__init__.py | Python source | in-scope | wallpaper-core config subpackage init |
| packages/core/src/wallpaper_core/config/schema.py | Python source | in-scope | Configuration schema definition for wallpaper-core |
| packages/core/src/wallpaper_core/config/settings.toml | Config data | in-scope | Package-default settings for wallpaper-core (flat format) |
| packages/core/src/wallpaper_core/console/__init__.py | Python source | in-scope | wallpaper-core console subpackage init |
| packages/core/src/wallpaper_core/console/output.py | Python source | in-scope | Console output formatting utilities |
| packages/core/src/wallpaper_core/console/progress.py | Python source | in-scope | Console progress reporting (progress bars, spinners) |
| packages/core/src/wallpaper_core/effects/__init__.py | Python source | in-scope | wallpaper-core effects subpackage init |
| packages/core/src/wallpaper_core/effects/schema.py | Python source | in-scope | Schema/validation for effects definitions within core |
| packages/core/src/wallpaper_core/effects/effects.yaml | YAML data | in-scope | Bundled effects definition file (packaged with wallpaper-core) |
| packages/core/src/wallpaper_core/engine/__init__.py | Python source | in-scope | wallpaper-core engine subpackage init |
| packages/core/src/wallpaper_core/engine/batch.py | Python source | in-scope | Batch processing engine logic |
| packages/core/src/wallpaper_core/engine/chain.py | Python source | in-scope | Effect chain execution logic |
| packages/core/src/wallpaper_core/engine/executor.py | Python source | in-scope | Low-level command executor (invokes ImageMagick) |
| packages/core/tests/conftest.py | Python test | in-scope | Pytest fixtures and configuration for wallpaper-core tests |
| packages/core/tests/test_cli.py | Python test | in-scope | Integration/CLI tests for wallpaper-core CLI commands |
| packages/core/tests/test_cli_bootstrap.py | Python test | in-scope | Tests for CLI bootstrap and initialization |
| packages/core/tests/test_cli_dry_run.py | Python test | in-scope | Tests for CLI dry-run mode in wallpaper-core |
| packages/core/tests/test_cli_effects_loading.py | Python test | in-scope | Tests for effects YAML loading via CLI |
| packages/core/tests/test_config_defaults.py | Python test | in-scope | Tests for wallpaper-core config default values |
| packages/core/tests/test_config_schema.py | Python test | in-scope | Tests for wallpaper-core config schema validation |
| packages/core/tests/test_console_output.py | Python test | in-scope | Tests for console output formatting |
| packages/core/tests/test_console_progress.py | Python test | in-scope | Tests for console progress reporting |
| packages/core/tests/test_dry_run.py | Python test | in-scope | Unit tests for wallpaper-core dry_run module |
| packages/core/tests/test_effects_integration.py | Python test | in-scope | Integration tests for effects pipeline in wallpaper-core |
| packages/core/tests/test_effects_schema.py | Python test | in-scope | Tests for effects schema validation |
| packages/core/tests/test_engine_batch.py | Python test | in-scope | Tests for batch processing engine |
| packages/core/tests/test_engine_chain.py | Python test | in-scope | Tests for effect chain engine |
| packages/core/tests/test_engine_executor.py | Python test | in-scope | Tests for the low-level ImageMagick executor |
| packages/core/tests/test_integration.py | Python test | in-scope | End-to-end integration tests for wallpaper-core |
| packages/core/tests/test_path_resolution.py | Python test | in-scope | Tests for CLI path resolution utilities |
| packages/core/tests/test_schema_registration.py | Python test | in-scope | Tests for schema registration within wallpaper-core |
| packages/effects/README.md | Markdown doc | in-scope | layered-effects package user-facing documentation |
| packages/effects/CHANGELOG.md | Markdown doc | in-scope | layered-effects package changelog |
| packages/effects/pyproject.toml | Project config | in-scope | layered-effects package configuration and dependencies |
| packages/effects/uv.lock | Lockfile | in-scope | layered-effects package-level uv dependency lockfile |
| packages/effects/src/layered_effects/__init__.py | Python source | in-scope | layered-effects package public API entrypoint |
| packages/effects/src/layered_effects/py.typed | Typing marker | in-scope | PEP 561 py.typed marker for layered-effects |
| packages/effects/src/layered_effects/errors.py | Python source | in-scope | Custom exception types for layered-effects |
| packages/effects/src/layered_effects/loader.py | Python source | in-scope | Effects YAML loader (reads and parses effects definitions) |
| packages/effects/tests/conftest.py | Python test | in-scope | Pytest fixtures and configuration for layered-effects tests |
| packages/effects/tests/test_api.py | Python test | in-scope | Tests for layered-effects public API surface |
| packages/effects/tests/test_errors.py | Python test | in-scope | Tests for layered-effects error/exception types |
| packages/effects/tests/test_integration.py | Python test | in-scope | Integration tests for layered-effects |
| packages/effects/tests/test_loader.py | Python test | in-scope | Tests for effects YAML loader |
| packages/orchestrator/README.md | Markdown doc | in-scope | wallpaper-orchestrator package user-facing documentation |
| packages/orchestrator/pyproject.toml | Project config | in-scope | wallpaper-orchestrator package configuration and dependencies |
| packages/orchestrator/docker/Dockerfile.imagemagick | Dockerfile | in-scope | Dockerfile for ImageMagick container used by orchestrator |
| packages/orchestrator/docker/.dockerignore | Docker config | in-scope | Dockerignore rules for orchestrator Docker build context |
| packages/orchestrator/docker/README.md | Markdown doc | in-scope | Documentation for Docker/container usage with orchestrator |
| packages/orchestrator/src/wallpaper_orchestrator/__init__.py | Python source | in-scope | wallpaper-orchestrator package public API entrypoint |
| packages/orchestrator/src/wallpaper_orchestrator/py.typed | Typing marker | in-scope | PEP 561 py.typed marker for wallpaper-orchestrator |
| packages/orchestrator/src/wallpaper_orchestrator/dry_run.py | Python source | in-scope | Dry-run mode support for wallpaper-orchestrator |
| packages/orchestrator/src/wallpaper_orchestrator/cli/__init__.py | Python source | in-scope | wallpaper-orchestrator CLI subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/cli/main.py | Python source | in-scope | wallpaper-orchestrator CLI entrypoint (`wallpaper-process` command) |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/__init__.py | Python source | in-scope | wallpaper-orchestrator CLI commands subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py | Python source | in-scope | CLI install subcommand for orchestrator (systemd service install) |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py | Python source | in-scope | CLI uninstall subcommand for orchestrator (systemd service removal) |
| packages/orchestrator/src/wallpaper_orchestrator/config/__init__.py | Python source | in-scope | wallpaper-orchestrator config subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/config/settings.py | Python source | in-scope | Settings loading/access for wallpaper-orchestrator |
| packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml | Config data | in-scope | Package-default settings for wallpaper-orchestrator (flat format) |
| packages/orchestrator/src/wallpaper_orchestrator/config/unified.py | Python source | in-scope | Unified config merging for orchestrator (combines all config sources) |
| packages/orchestrator/src/wallpaper_orchestrator/container/__init__.py | Python source | in-scope | wallpaper-orchestrator container subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/container/manager.py | Python source | in-scope | Container lifecycle manager (start/stop/run ImageMagick container) |
| packages/orchestrator/tests/conftest.py | Python test | in-scope | Pytest fixtures and configuration for wallpaper-orchestrator tests |
| packages/orchestrator/tests/test_cli_bootstrap.py | Python test | in-scope | Tests for orchestrator CLI bootstrap/initialization |
| packages/orchestrator/tests/test_cli_dry_run.py | Python test | in-scope | Tests for orchestrator CLI dry-run mode |
| packages/orchestrator/tests/test_cli_install.py | Python test | in-scope | Tests for orchestrator CLI install subcommand |
| packages/orchestrator/tests/test_cli_integration.py | Python test | in-scope | Integration tests for orchestrator CLI end-to-end |
| packages/orchestrator/tests/test_cli_process.py | Python test | in-scope | Tests for orchestrator CLI process subcommand |
| packages/orchestrator/tests/test_cli_uninstall.py | Python test | in-scope | Tests for orchestrator CLI uninstall subcommand |
| packages/orchestrator/tests/test_config_settings.py | Python test | in-scope | Tests for orchestrator settings loading |
| packages/orchestrator/tests/test_config_unified.py | Python test | in-scope | Tests for orchestrator unified config merging |
| packages/orchestrator/tests/test_container_execution.py | Python test | in-scope | Tests for container execution behavior |
| packages/orchestrator/tests/test_container_manager.py | Python test | in-scope | Tests for container lifecycle manager |
| packages/orchestrator/tests/test_dry_run.py | Python test | in-scope | Unit tests for orchestrator dry_run module |
| packages/orchestrator/tests/test_integration.py | Python test | in-scope | End-to-end integration tests for wallpaper-orchestrator |
| packages/settings/README.md | Markdown doc | in-scope | layered-settings package user-facing documentation |
| packages/settings/pyproject.toml | Project config | in-scope | layered-settings package configuration and dependencies |
| packages/settings/examples/README.md | Markdown doc | in-scope | Documentation for layered-settings usage examples |
| packages/settings/examples/app_defaults.toml | Config data | in-scope | Example app defaults TOML file for layered-settings demo |
| packages/settings/examples/basic_usage.py | Python source | in-scope | Example script demonstrating basic layered-settings usage |
| packages/settings/examples/layer_priority.py | Python source | in-scope | Example script demonstrating layer priority/override behavior |
| packages/settings/src/layered_settings/__init__.py | Python source | in-scope | layered-settings package public API entrypoint |
| packages/settings/src/layered_settings/py.typed | Typing marker | in-scope | PEP 561 py.typed marker for layered-settings |
| packages/settings/src/layered_settings/builder.py | Python source | in-scope | Settings builder (fluent API for constructing layered config) |
| packages/settings/src/layered_settings/constants.py | Python source | in-scope | Shared constants for layered-settings (env var names, defaults) |
| packages/settings/src/layered_settings/dry_run.py | Python source | in-scope | Dry-run mode support for layered-settings |
| packages/settings/src/layered_settings/errors.py | Python source | in-scope | Custom exception types for layered-settings |
| packages/settings/src/layered_settings/layers.py | Python source | in-scope | Layer definitions and priority ordering for settings |
| packages/settings/src/layered_settings/loader.py | Python source | in-scope | Settings file loader (reads TOML files per layer) |
| packages/settings/src/layered_settings/merger.py | Python source | in-scope | Settings merger (deep merges layers in priority order) |
| packages/settings/src/layered_settings/paths.py | Python source | in-scope | Path resolution for settings files (XDG dirs, etc.) |
| packages/settings/src/layered_settings/registry.py | Python source | in-scope | Schema registry for settings validation |
| packages/settings/tests/__init__.py | Python test | in-scope | Settings tests package init |
| packages/settings/tests/test_builder.py | Python test | in-scope | Tests for settings builder API |
| packages/settings/tests/test_constants.py | Python test | in-scope | Tests for layered-settings constants |
| packages/settings/tests/test_dry_run.py | Python test | in-scope | Tests for layered-settings dry_run module |
| packages/settings/tests/test_errors.py | Python test | in-scope | Tests for layered-settings error/exception types |
| packages/settings/tests/test_integration.py | Python test | in-scope | Integration tests for layered-settings end-to-end |
| packages/settings/tests/test_layers.py | Python test | in-scope | Tests for layer definitions and priority ordering |
| packages/settings/tests/test_loader.py | Python test | in-scope | Tests for settings file loader |
| packages/settings/tests/test_merger.py | Python test | in-scope | Tests for settings merger (deep merge logic) |
| packages/settings/tests/test_paths.py | Python test | in-scope | Tests for settings path resolution |
| packages/settings/tests/test_registry.py | Python test | in-scope | Tests for settings schema registry |
