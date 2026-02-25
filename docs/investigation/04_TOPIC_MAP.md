# Topic Map (Repo-wide)

<!-- Populated during PHASE_2_TOPIC_MAP, iteration 0001 -->

## File summaries

| File | Primary topics | Secondary topics | Key entities |
|---|---|---|---|
| README.md | CLI, host-execution, container-execution | effects, composites, presets, dry-run, configuration | wallpaper-core, wallpaper-process, `--dry-run`, `--flat` |
| DEVELOPMENT.md | development-workflow | CI, testing, packaging | `make dev`, `make pipeline`, `make test-all`, bandit |
| CHANGELOG.md | development-workflow | — | version history |
| Makefile | development-workflow, CI | testing, packaging | `make test-all`, `make smoke-test`, `make pipeline`, `make push` |
| pyproject.toml | packaging | configuration | uv workspace, ruff, mypy |
| settings.toml | configuration, settings-precedence | — | `[core]`, `[orchestrator]` namespaced TOML |
| uv.lock | packaging | — | dependency lockfile |
| .gitignore | development-workflow | — | wallpapers-output/ |
| .gitattributes | development-workflow | — | binary markers |
| .pre-commit-config.yaml | development-workflow, CI | — | ruff, mypy, pre-commit hooks |
| .python-version | development-workflow | — | Python 3.12 pin |
| .github/pull_request_template.md | development-workflow | — | PR description template |
| .github/workflows/ci-core.yml | CI | testing, packaging | lint, security, test matrix (ubuntu+macos, py3.12+3.13), bandit, coverage 95% |
| .github/workflows/ci-effects.yml | CI | testing | lint, security, test matrix |
| .github/workflows/ci-orchestrator.yml | CI | testing | lint, security, test matrix |
| .github/workflows/ci-settings.yml | CI | testing | lint, security, test matrix |
| .github/workflows/smoke-test.yml | CI, testing | container-execution, host-execution | `run-smoke-tests.sh`, Docker, ImageMagick |
| docs/MIGRATION.md | development-workflow | — | migration guide |
| docs/SMOKE_TESTS_CHANGES_SUMMARY.md | testing | — | smoke test change summary |
| docs/SMOKE_TESTS_MIGRATION_GUIDE.md | testing | development-workflow | smoke test migration guide |
| tests/smoke/README.md | testing | host-execution, container-execution | smoke test documentation |
| tests/smoke/run-smoke-tests.sh | testing, host-execution, container-execution | dry-run, effects, composites, presets, batch-processing | 42 dry-run tests, core + orchestrator CLI, layered config |
| packages/core/README.md | CLI, host-execution | effects, composites, presets, dry-run | wallpaper-core, process/batch/show subcommands |
| packages/core/pyproject.toml | packaging | configuration | wallpaper-core deps (typer, pydantic, rich, layered-settings, layered-effects) |
| packages/core/MANIFEST.in | packaging | effects | effects.yaml inclusion |
| packages/core/.gitignore | development-workflow | — | wallpapers-output/ |
| packages/core/uv.lock | packaging | — | dependency lockfile |
| packages/core/effects/effects.yaml | effects, composites, presets | configuration | top-level copy of canonical effects definition (identical to src copy) |
| packages/core/src/wallpaper_core/__init__.py | configuration, effects | CLI | `CoreSettings`, `EffectsConfig`, `Effect`, `ParameterType`, v0.3.0 |
| packages/core/src/wallpaper_core/py.typed | packaging | — | PEP 561 marker |
| packages/core/src/wallpaper_core/dry_run.py | dry-run | error-handling, effects | `CoreDryRun`, `validate_core()`, `render_process()`, `render_batch()` |
| packages/core/src/wallpaper_core/cli/__init__.py | CLI | — | CLI subpackage init |
| packages/core/src/wallpaper_core/cli/main.py | CLI, configuration, effects | dry-run, error-handling | `wallpaper-core` Typer app, `configure()`, `load_effects()`, `EffectsLoadError`, `EffectsValidationError`, `version`, `info` |
| packages/core/src/wallpaper_core/cli/batch.py | CLI, batch-processing | effects, composites, presets, dry-run, parallelism | `batch_effects`, `batch_composites`, `batch_presets`, `batch_all`, `--parallel/--sequential`, `--flat`, `--dry-run` |
| packages/core/src/wallpaper_core/cli/process.py | CLI, host-execution | effects, composites, presets, dry-run | `apply_effect`, `apply_composite`, `apply_preset`, `_resolve_command`, `_resolve_chain_commands` |
| packages/core/src/wallpaper_core/cli/show.py | CLI, effects | composites, presets | `show_effects`, `show_composites`, `show_presets`, `show_all`, Rich tables |
| packages/core/src/wallpaper_core/cli/path_utils.py | CLI, host-execution | effects, composites, presets | `resolve_output_path()`, `flat`, `explicit_output`, `ItemType` |
| packages/core/src/wallpaper_core/config/__init__.py | configuration | — | config subpackage init |
| packages/core/src/wallpaper_core/config/schema.py | configuration | host-execution, parallelism | `CoreSettings`, `ExecutionSettings`, `OutputSettings`, `ProcessingSettings`, `BackendSettings`, `Verbosity`, `ItemType` |
| packages/core/src/wallpaper_core/config/settings.toml | configuration, settings-precedence | — | package defaults: parallel=true, strict=true, max_workers=0, verbosity=1, default_dir=/tmp/wallpaper-effects |
| packages/core/src/wallpaper_core/console/__init__.py | CLI | — | console subpackage init |
| packages/core/src/wallpaper_core/console/output.py | CLI | dry-run | `RichOutput`, verbosity levels (QUIET/NORMAL/VERBOSE/DEBUG), Rich console |
| packages/core/src/wallpaper_core/console/progress.py | CLI, batch-processing | parallelism | `BatchProgress`, Rich progress bar, context manager |
| packages/core/src/wallpaper_core/effects/__init__.py | effects | configuration | `get_package_effects_file()`, re-exports effects schema |
| packages/core/src/wallpaper_core/effects/schema.py | effects, composites, presets | configuration | `ParameterType`, `ParameterDefinition`, `Effect`, `ChainStep`, `CompositeEffect`, `Preset`, `EffectsConfig` |
| packages/core/src/wallpaper_core/effects/effects.yaml | effects, composites, presets | configuration | 9 effects (blur, blackwhite, negate, brightness, contrast, saturation, sepia, vignette, color_overlay), 4 composites, 7 presets |
| packages/core/src/wallpaper_core/engine/__init__.py | host-execution | — | engine subpackage init |
| packages/core/src/wallpaper_core/engine/batch.py | batch-processing, parallelism | effects, composites, presets, error-handling | `BatchGenerator`, `BatchResult`, `ThreadPoolExecutor`, `generate_all`, `_process_parallel`, `_process_sequential` |
| packages/core/src/wallpaper_core/engine/chain.py | effects, composites | host-execution, error-handling | `ChainExecutor`, `execute_chain()`, temp files, `_get_params_with_defaults()` |
| packages/core/src/wallpaper_core/engine/executor.py | host-execution | effects, error-handling | `CommandExecutor`, `ExecutionResult`, `subprocess.run`, ImageMagick v6/v7 auto-detection |
| packages/core/tests/conftest.py | testing | effects, configuration | core test fixtures |
| packages/core/tests/test_cli.py | testing, CLI | effects, composites, presets | CLI integration tests |
| packages/core/tests/test_cli_bootstrap.py | testing, CLI | configuration | CLI init/bootstrap tests |
| packages/core/tests/test_cli_dry_run.py | testing, CLI, dry-run | effects, composites, presets | dry-run CLI tests |
| packages/core/tests/test_cli_effects_loading.py | testing, CLI | effects | effects YAML loading via CLI |
| packages/core/tests/test_config_defaults.py | testing, configuration | settings-precedence | config defaults tests |
| packages/core/tests/test_config_schema.py | testing, configuration | — | config schema validation tests |
| packages/core/tests/test_console_output.py | testing, CLI | — | console output formatting tests |
| packages/core/tests/test_console_progress.py | testing, CLI, batch-processing | — | progress bar tests |
| packages/core/tests/test_dry_run.py | testing, dry-run | — | CoreDryRun unit tests |
| packages/core/tests/test_effects_integration.py | testing, effects | composites, presets | effects pipeline integration tests |
| packages/core/tests/test_effects_schema.py | testing, effects | — | effects schema validation tests |
| packages/core/tests/test_engine_batch.py | testing, batch-processing | parallelism, effects | batch engine tests |
| packages/core/tests/test_engine_chain.py | testing, effects, composites | host-execution | chain executor tests |
| packages/core/tests/test_engine_executor.py | testing, host-execution | effects | ImageMagick executor tests |
| packages/core/tests/test_integration.py | testing, host-execution | effects, composites, presets | end-to-end core tests |
| packages/core/tests/test_path_resolution.py | testing, CLI | host-execution | path resolution tests |
| packages/core/tests/test_schema_registration.py | testing, configuration | — | schema registration tests |
| packages/effects/README.md | effects, configuration | settings-precedence | layered-effects package docs |
| packages/effects/CHANGELOG.md | development-workflow | effects | layered-effects changelog |
| packages/effects/pyproject.toml | packaging | effects | layered-effects deps |
| packages/effects/uv.lock | packaging | — | dependency lockfile |
| packages/effects/src/layered_effects/__init__.py | effects, configuration | settings-precedence | `configure()`, `load_effects()`, 3-layer discovery (package/project/user), caching, `EffectsLoadError`, `EffectsValidationError` |
| packages/effects/src/layered_effects/py.typed | packaging | — | PEP 561 marker |
| packages/effects/src/layered_effects/errors.py | error-handling, effects | — | `EffectsError`, `EffectsLoadError`, `EffectsValidationError` |
| packages/effects/src/layered_effects/loader.py | effects, configuration | settings-precedence, error-handling | `EffectsLoader`, `discover_layers()`, `load_and_merge()`, YAML deep merge via `ConfigMerger` |
| packages/effects/tests/conftest.py | testing | effects | layered-effects test fixtures |
| packages/effects/tests/test_api.py | testing, effects | configuration | public API surface tests |
| packages/effects/tests/test_errors.py | testing, error-handling | effects | error type tests |
| packages/effects/tests/test_integration.py | testing, effects | settings-precedence | layered-effects integration tests |
| packages/effects/tests/test_loader.py | testing, effects | configuration | YAML loader tests |
| packages/orchestrator/README.md | CLI, container-execution | effects, composites, presets, dry-run | wallpaper-process, install/uninstall, Docker/Podman |
| packages/orchestrator/pyproject.toml | packaging | container-execution | wallpaper-orchestrator deps |
| packages/orchestrator/docker/Dockerfile.imagemagick | container-execution | packaging | Alpine+ImageMagick image, non-root user `wallpaper` (UID 1000), ENTRYPOINT=wallpaper-core |
| packages/orchestrator/docker/.dockerignore | container-execution | — | Docker build context exclusions |
| packages/orchestrator/docker/README.md | container-execution | CLI | Docker usage docs |
| packages/orchestrator/src/wallpaper_orchestrator/__init__.py | configuration, container-execution | CLI | `OrchestratorSettings`, `ContainerSettings`, `UnifiedConfig`, `ContainerManager`, v0.1.0 |
| packages/orchestrator/src/wallpaper_orchestrator/py.typed | packaging | — | PEP 561 marker |
| packages/orchestrator/src/wallpaper_orchestrator/dry_run.py | dry-run, container-execution | error-handling | `OrchestratorDryRun`, `validate_container()`, `render_container_process()`, `render_install()`, `render_uninstall()` |
| packages/orchestrator/src/wallpaper_orchestrator/cli/__init__.py | CLI | — | orchestrator CLI subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/cli/main.py | CLI, container-execution | effects, composites, presets, dry-run, batch-processing | `wallpaper-process` Typer app, `process_effect`, `process_composite`, `process_preset`, install/uninstall, batch+show delegation |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/__init__.py | CLI | — | commands subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py | CLI, container-execution | dry-run, error-handling | `install()`, `docker/podman build`, `Dockerfile.imagemagick`, `--engine` flag |
| packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py | CLI, container-execution | dry-run, error-handling | `uninstall()`, `docker/podman rmi`, `--yes` flag |
| packages/orchestrator/src/wallpaper_orchestrator/config/__init__.py | configuration | — | orchestrator config subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/config/settings.py | configuration | container-execution | `OrchestratorSettings`, `ContainerSettings`, engine/image_name/image_registry validation |
| packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml | configuration, settings-precedence | container-execution | package defaults: engine=docker, image_name=wallpaper-effects:latest |
| packages/orchestrator/src/wallpaper_orchestrator/config/unified.py | configuration | container-execution, effects | `UnifiedConfig` (core + effects + orchestrator namespaces), `_load_effects_defaults()` |
| packages/orchestrator/src/wallpaper_orchestrator/container/__init__.py | container-execution | — | container subpackage init |
| packages/orchestrator/src/wallpaper_orchestrator/container/manager.py | container-execution | error-handling, host-execution | `ContainerManager`, `run_process()`, `is_image_available()`, volume mounts, `--userns=keep-id` for podman |
| packages/orchestrator/tests/conftest.py | testing | container-execution | orchestrator test fixtures |
| packages/orchestrator/tests/test_cli_bootstrap.py | testing, CLI | container-execution | orchestrator CLI bootstrap tests |
| packages/orchestrator/tests/test_cli_dry_run.py | testing, CLI, dry-run | container-execution | orchestrator dry-run tests |
| packages/orchestrator/tests/test_cli_install.py | testing, CLI | container-execution | install command tests |
| packages/orchestrator/tests/test_cli_integration.py | testing, CLI | container-execution | orchestrator CLI integration tests |
| packages/orchestrator/tests/test_cli_process.py | testing, CLI, container-execution | effects, composites, presets | process command tests |
| packages/orchestrator/tests/test_cli_uninstall.py | testing, CLI | container-execution | uninstall command tests |
| packages/orchestrator/tests/test_config_settings.py | testing, configuration | container-execution | orchestrator settings loading tests |
| packages/orchestrator/tests/test_config_unified.py | testing, configuration | effects, container-execution | unified config merge tests |
| packages/orchestrator/tests/test_container_execution.py | testing, container-execution | — | container execution behavior tests |
| packages/orchestrator/tests/test_container_manager.py | testing, container-execution | error-handling | ContainerManager lifecycle tests |
| packages/orchestrator/tests/test_dry_run.py | testing, dry-run | container-execution | orchestrator dry_run unit tests |
| packages/orchestrator/tests/test_integration.py | testing, container-execution | CLI | orchestrator end-to-end integration tests |
| packages/settings/README.md | configuration, settings-precedence | — | layered-settings package docs |
| packages/settings/pyproject.toml | packaging | configuration | layered-settings deps |
| packages/settings/examples/README.md | configuration, settings-precedence | development-workflow | layered-settings examples docs |
| packages/settings/examples/app_defaults.toml | configuration | settings-precedence | example defaults TOML (database, server, logging sections) |
| packages/settings/examples/basic_usage.py | configuration, settings-precedence | development-workflow | `SchemaRegistry.register()`, `configure()`, `get_config()`, CLI overrides demo |
| packages/settings/examples/layer_priority.py | configuration, settings-precedence | development-workflow | 4-layer priority demo (package to project to user to CLI), `XDG_CONFIG_HOME` |
| packages/settings/src/layered_settings/__init__.py | configuration, settings-precedence | dry-run | `configure()`, `get_config()`, caching, overrides, `SchemaRegistry`, `DryRunBase`, XDG paths, 4-layer discovery |
| packages/settings/src/layered_settings/py.typed | packaging | — | PEP 561 marker |
| packages/settings/src/layered_settings/builder.py | configuration, settings-precedence | error-handling | `ConfigBuilder.build()`, flat-to-namespaced wrapping, `_apply_overrides()`, dotted-path overrides |
| packages/settings/src/layered_settings/constants.py | configuration | — | `APP_NAME`, `SETTINGS_FILENAME`, `EFFECTS_FILENAME` |
| packages/settings/src/layered_settings/dry_run.py | dry-run | — | `DryRunBase`, `ValidationCheck`, Rich render helpers (header/field/command/table) |
| packages/settings/src/layered_settings/errors.py | error-handling, configuration | — | `SettingsError`, `SettingsFileError`, `SettingsRegistryError`, `SettingsValidationError` |
| packages/settings/src/layered_settings/layers.py | configuration, settings-precedence | — | `LayerSource`, `LayerDiscovery.discover_layers()`, 3-layer discovery (package/project/user) |
| packages/settings/src/layered_settings/loader.py | configuration | error-handling | `FileLoader`, TOML+YAML format detection and loading, `SettingsFileError` |
| packages/settings/src/layered_settings/merger.py | configuration, settings-precedence | — | `ConfigMerger.merge()`, deep dict merge (dicts merged recursively, lists replaced atomically) |
| packages/settings/src/layered_settings/paths.py | configuration, settings-precedence | — | `XDG_CONFIG_HOME`, `USER_CONFIG_DIR`, `USER_SETTINGS_FILE`, `USER_EFFECTS_FILE`, `get_project_settings_file()`, `get_project_effects_file()` |
| packages/settings/src/layered_settings/registry.py | configuration | — | `SchemaRegistry`, `SchemaEntry`, `register()`, `get()`, `all_entries()`, `clear()` |
| packages/settings/tests/__init__.py | testing | — | settings tests init |
| packages/settings/tests/test_builder.py | testing, configuration | settings-precedence | builder tests |
| packages/settings/tests/test_constants.py | testing, configuration | — | constants tests |
| packages/settings/tests/test_dry_run.py | testing, dry-run | — | DryRunBase tests |
| packages/settings/tests/test_errors.py | testing, error-handling | — | error type tests |
| packages/settings/tests/test_integration.py | testing, configuration | settings-precedence | layered-settings end-to-end tests |
| packages/settings/tests/test_layers.py | testing, configuration | settings-precedence | layer discovery tests |
| packages/settings/tests/test_loader.py | testing, configuration | error-handling | file loader tests |
| packages/settings/tests/test_merger.py | testing, configuration | settings-precedence | deep merge logic tests |
| packages/settings/tests/test_paths.py | testing, configuration | — | XDG path resolution tests |
| packages/settings/tests/test_registry.py | testing, configuration | — | schema registry tests |

---

## Topic index

| Topic | Files |
|---|---|
| CLI | packages/core/src/wallpaper_core/cli/main.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/cli/process.py, packages/core/src/wallpaper_core/cli/show.py, packages/core/src/wallpaper_core/cli/path_utils.py, packages/core/src/wallpaper_core/console/output.py, packages/core/src/wallpaper_core/console/progress.py, packages/orchestrator/src/wallpaper_orchestrator/cli/main.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py, README.md, packages/core/README.md, packages/orchestrator/README.md |
| configuration | packages/core/src/wallpaper_core/config/schema.py, packages/core/src/wallpaper_core/config/settings.toml, packages/core/src/wallpaper_core/cli/main.py, packages/orchestrator/src/wallpaper_orchestrator/config/settings.py, packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml, packages/orchestrator/src/wallpaper_orchestrator/config/unified.py, packages/settings/src/layered_settings/__init__.py, packages/settings/src/layered_settings/builder.py, packages/settings/src/layered_settings/constants.py, packages/settings/src/layered_settings/layers.py, packages/settings/src/layered_settings/loader.py, packages/settings/src/layered_settings/merger.py, packages/settings/src/layered_settings/paths.py, packages/settings/src/layered_settings/registry.py, packages/settings/examples/basic_usage.py, packages/settings/examples/layer_priority.py, settings.toml |
| settings-precedence | packages/settings/src/layered_settings/__init__.py, packages/settings/src/layered_settings/builder.py, packages/settings/src/layered_settings/layers.py, packages/settings/src/layered_settings/merger.py, packages/settings/src/layered_settings/paths.py, packages/effects/src/layered_effects/__init__.py, packages/effects/src/layered_effects/loader.py, packages/settings/examples/basic_usage.py, packages/settings/examples/layer_priority.py, packages/core/src/wallpaper_core/config/settings.toml, packages/orchestrator/src/wallpaper_orchestrator/config/settings.toml |
| effects | packages/core/src/wallpaper_core/effects/schema.py, packages/core/src/wallpaper_core/effects/__init__.py, packages/core/src/wallpaper_core/effects/effects.yaml, packages/core/effects/effects.yaml, packages/effects/src/layered_effects/__init__.py, packages/effects/src/layered_effects/loader.py, packages/core/src/wallpaper_core/engine/chain.py, packages/core/src/wallpaper_core/engine/executor.py, packages/core/src/wallpaper_core/cli/process.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/cli/show.py |
| composites | packages/core/src/wallpaper_core/effects/schema.py, packages/core/src/wallpaper_core/effects/effects.yaml, packages/core/src/wallpaper_core/engine/chain.py, packages/core/src/wallpaper_core/cli/process.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/cli/show.py |
| presets | packages/core/src/wallpaper_core/effects/schema.py, packages/core/src/wallpaper_core/effects/effects.yaml, packages/core/src/wallpaper_core/cli/process.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/cli/show.py |
| dry-run | packages/core/src/wallpaper_core/dry_run.py, packages/orchestrator/src/wallpaper_orchestrator/dry_run.py, packages/settings/src/layered_settings/dry_run.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/cli/process.py, packages/orchestrator/src/wallpaper_orchestrator/cli/main.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py |
| host-execution | packages/core/src/wallpaper_core/engine/executor.py, packages/core/src/wallpaper_core/engine/chain.py, packages/core/src/wallpaper_core/engine/batch.py, packages/core/src/wallpaper_core/cli/process.py, packages/core/src/wallpaper_core/cli/path_utils.py, packages/core/src/wallpaper_core/config/schema.py |
| container-execution | packages/orchestrator/src/wallpaper_orchestrator/container/manager.py, packages/orchestrator/src/wallpaper_orchestrator/cli/main.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py, packages/orchestrator/src/wallpaper_orchestrator/cli/commands/uninstall.py, packages/orchestrator/src/wallpaper_orchestrator/dry_run.py, packages/orchestrator/docker/Dockerfile.imagemagick, .github/workflows/smoke-test.yml |
| batch-processing | packages/core/src/wallpaper_core/engine/batch.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/console/progress.py, packages/orchestrator/src/wallpaper_orchestrator/cli/main.py |
| parallelism | packages/core/src/wallpaper_core/engine/batch.py, packages/core/src/wallpaper_core/cli/batch.py, packages/core/src/wallpaper_core/config/schema.py |
| error-handling | packages/core/src/wallpaper_core/engine/executor.py, packages/core/src/wallpaper_core/engine/chain.py, packages/core/src/wallpaper_core/engine/batch.py, packages/effects/src/layered_effects/errors.py, packages/settings/src/layered_settings/errors.py, packages/orchestrator/src/wallpaper_orchestrator/container/manager.py, packages/core/src/wallpaper_core/cli/main.py |
| testing | packages/core/tests/conftest.py, packages/core/tests/test_cli.py, packages/core/tests/test_cli_bootstrap.py, packages/core/tests/test_cli_dry_run.py, packages/core/tests/test_cli_effects_loading.py, packages/core/tests/test_config_defaults.py, packages/core/tests/test_config_schema.py, packages/core/tests/test_console_output.py, packages/core/tests/test_console_progress.py, packages/core/tests/test_dry_run.py, packages/core/tests/test_effects_integration.py, packages/core/tests/test_effects_schema.py, packages/core/tests/test_engine_batch.py, packages/core/tests/test_engine_chain.py, packages/core/tests/test_engine_executor.py, packages/core/tests/test_integration.py, packages/core/tests/test_path_resolution.py, packages/core/tests/test_schema_registration.py, packages/effects/tests/conftest.py, packages/effects/tests/test_api.py, packages/effects/tests/test_errors.py, packages/effects/tests/test_integration.py, packages/effects/tests/test_loader.py, packages/orchestrator/tests/conftest.py, packages/orchestrator/tests/test_cli_bootstrap.py, packages/orchestrator/tests/test_cli_dry_run.py, packages/orchestrator/tests/test_cli_install.py, packages/orchestrator/tests/test_cli_integration.py, packages/orchestrator/tests/test_cli_process.py, packages/orchestrator/tests/test_cli_uninstall.py, packages/orchestrator/tests/test_config_settings.py, packages/orchestrator/tests/test_config_unified.py, packages/orchestrator/tests/test_container_execution.py, packages/orchestrator/tests/test_container_manager.py, packages/orchestrator/tests/test_dry_run.py, packages/orchestrator/tests/test_integration.py, packages/settings/tests/__init__.py, packages/settings/tests/test_builder.py, packages/settings/tests/test_constants.py, packages/settings/tests/test_dry_run.py, packages/settings/tests/test_errors.py, packages/settings/tests/test_integration.py, packages/settings/tests/test_layers.py, packages/settings/tests/test_loader.py, packages/settings/tests/test_merger.py, packages/settings/tests/test_paths.py, packages/settings/tests/test_registry.py, tests/smoke/run-smoke-tests.sh, tests/smoke/README.md |
| CI | .github/workflows/ci-core.yml, .github/workflows/ci-effects.yml, .github/workflows/ci-orchestrator.yml, .github/workflows/ci-settings.yml, .github/workflows/smoke-test.yml, .pre-commit-config.yaml, Makefile |
| packaging | packages/core/pyproject.toml, packages/effects/pyproject.toml, packages/orchestrator/pyproject.toml, packages/settings/pyproject.toml, pyproject.toml, packages/core/MANIFEST.in, packages/orchestrator/docker/Dockerfile.imagemagick |
| development-workflow | DEVELOPMENT.md, Makefile, .gitignore, .gitattributes, .pre-commit-config.yaml, .python-version, docs/MIGRATION.md, packages/settings/examples/basic_usage.py, packages/settings/examples/layer_priority.py |
