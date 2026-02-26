# Checkpoint: Phase 4 — BEHAVIOR_CATALOG

Iteration: 0001
BHVs reviewed: 82
Reclassified: 2
Unknowns resolved: 4
Unknowns remaining: 0
Next: PHASE_5_DOC_CLAIMS

---

## Reclassified entries

### BHV-0026 — Settings error hierarchy (`public` → `internal`)

Reason: `SettingsFileError`, `SettingsRegistryError`, `SettingsValidationError`, and `SettingsError` are
defined in `layered_settings.errors` and are NOT exported in `layered_settings.__all__`. External
callers import them via `from layered_settings.errors import ...` (submodule path), not from the
package's top-level public API. The error classes are internal implementation details; they are
raised by the public `get_config()` / `configure()` functions but are not themselves part of the
published surface.

Evidence: `packages/settings/src/layered_settings/__init__.py` — `__all__` does not include any
error class. Only `configure`, `get_config`, `SchemaRegistry`, constants, paths, `DryRunBase`, and
`ValidationCheck` are exported.

### BHV-0082 — Orchestrator layered settings CLI overrides (`internal` → `public`)

Reason: The behavior is exercised entirely through `get_config(overrides={...})`, which IS in
`layered_settings.__all__` and is the documented public API for applying CLI-level overrides.
The fact that the test operates against `UnifiedConfig` (an orchestrator-specific model) does not
make the behavior internal — the override mechanism itself is public.

Evidence: `packages/settings/src/layered_settings/__init__.py` line 82 — `get_config` is in
`__all__`; `packages/orchestrator/tests/test_integration.py::test_config_merges_cli_overrides`.

---

## Unknowns resolved

### U-0001 — `loader._load_yaml_file()` contract

Status: resolved. The method has a leading underscore, is not in `layered_effects.__all__`, and is a
private YAML-reading helper invoked only by `load_and_merge()`. Tests exercise it directly for unit
isolation. No public contract implications.

### U-0002 — `test_console_progress.py` coverage

Status: resolved. File fully read. Tests cover `BatchProgress` edge cases (advance before start,
double start/stop, zero total, context manager). `BatchProgress` is not exported in
`wallpaper_core.__all__`. All behaviors are internal. No new public BHVs needed.

### U-0003 — `test_cli_dry_run.py` lines 200–543

Status: resolved. Read in full. All sub-cases (unknown preset/effect/composite in dry-run, podman
userns flag, invalid reference handling) are already captured as error cases under BHV-0079.
No new BHVs required.

### U-0004 — `test_cli_process.py` lines 200–680

Status: resolved. Read in full. Composite/preset process error cases (missing image, execution
failure, runtime error) are all sub-cases of BHV-0078's documented error variants. No new
BHVs required.

---

## Publicity audit summary by package

### settings (BHV-0001 – BHV-0030)

| BHV | Title (abbreviated) | Publicity | Verified |
|-----|---------------------|-----------|---------|
| 0001 | FileLoader.detect_format | internal | correct — FileLoader not in __all__ |
| 0002 | FileLoader loads TOML | internal | correct |
| 0003 | FileLoader loads YAML | internal | correct |
| 0004 | FileLoader raises SettingsFileError | internal | correct |
| 0005 | ConfigMerger.merge | internal | correct — ConfigMerger not in __all__ |
| 0006 | ConfigMerger replaces lists | internal | correct |
| 0007 | ConfigMerger immutability | internal | correct |
| 0008 | LayerSource immutable record | internal | correct — LayerSource not in __all__ |
| 0009 | LayerDiscovery discovers package defaults | internal | correct — LayerDiscovery not in __all__ |
| 0010 | LayerDiscovery project-root layer | internal | correct |
| 0011 | LayerDiscovery user config layer | internal | correct |
| 0012 | LayerDiscovery priority order | internal | correct |
| 0013 | ConfigBuilder.build() merges layers | internal | correct — ConfigBuilder not in __all__ |
| 0014 | ConfigBuilder flat-format layers | internal | correct |
| 0015 | ConfigBuilder namespaced layers | internal | correct |
| 0016 | ConfigBuilder CLI overrides | internal | correct |
| 0017 | ConfigBuilder raises SettingsValidationError | internal | correct |
| 0018 | SchemaEntry immutable record | internal | correct — SchemaEntry not in __all__ |
| 0019 | SchemaRegistry.register() | public | correct — SchemaRegistry in __all__ |
| 0020 | SchemaRegistry query methods | public | correct |
| 0021 | SchemaRegistry.clear() | internal | correct — test-only utility |
| 0022 | configure() | public | correct — configure in __all__ |
| 0023 | get_config() | public | correct — get_config in __all__ |
| 0024 | get_config(overrides=...) | public | correct |
| 0025 | Four-layer priority order end-to-end | public | correct |
| 0026 | Settings error hierarchy | internal | RECLASSIFIED from public |
| 0027 | XDG path constants and helpers | public | correct — all in __all__ |
| 0028 | APP_NAME, SETTINGS_FILENAME, EFFECTS_FILENAME | public | correct — in __all__ |
| 0029 | DryRunBase rendering | public | correct — DryRunBase in __all__ |
| 0030 | ValidationCheck dataclass | public | correct — ValidationCheck in __all__ |

### effects (BHV-0031 – BHV-0036)

| BHV | Title (abbreviated) | Publicity | Verified |
|-----|---------------------|-----------|---------|
| 0031 | effects.configure() | public | correct — configure in __all__ |
| 0032 | effects.load_effects() | public | correct — load_effects in __all__ |
| 0033 | EffectsLoader.discover_layers | internal | correct — EffectsLoader not in __all__ |
| 0034 | EffectsLoader.load_and_merge | internal | correct |
| 0035 | Effects error hierarchy | public | correct — EffectsError/LoadError/ValidationError in __all__ |
| 0036 | End-to-end three-layer merge | public | correct — exercises configure+load_effects public API |

### core (BHV-0037 – BHV-0066)

| BHV | Title (abbreviated) | Publicity | Verified |
|-----|---------------------|-----------|---------|
| 0037 | wallpaper-core CLI help/subcommands | public | correct — CLI command |
| 0038 | wallpaper-core configures settings on startup | public | correct — CLI behavior |
| 0039 | wallpaper-core merges CLI overrides | public | correct |
| 0040 | wallpaper-core package settings.toml defaults | internal | correct — internal config file test |
| 0041 | CoreSettings Pydantic validation | internal | correct — CoreSettings not directly in CLI |
| 0042 | wallpaper-core loads package effects.yaml | internal | correct — get_package_effects_file is internal |
| 0043 | wallpaper-core layered-effects three layers | public | correct — exercises public layered-effects API |
| 0044 | wallpaper-core `show effects/composites/presets/all` | public | correct — CLI command |
| 0045 | wallpaper-core `info` command | public | correct — CLI command |
| 0046 | wallpaper-core `version` command | public | correct — CLI command |
| 0047 | wallpaper-core `process effect` | public | correct — CLI command |
| 0048 | wallpaper-core `process effect` per-effect params | public | correct — CLI flag |
| 0049 | wallpaper-core `process` default output dir | public | correct — CLI behavior |
| 0050 | wallpaper-core `process --flat` | public | correct — CLI flag |
| 0051 | wallpaper-core resolve_output_path | internal | correct — not exported |
| 0052 | wallpaper-core `process composite` | public | correct — CLI command |
| 0053 | wallpaper-core `process preset` | public | correct — CLI command |
| 0054 | wallpaper-core `process --dry-run` | public | correct — CLI flag |
| 0055 | CoreDryRun.validate_core | internal | correct — CoreDryRun not in __all__ |
| 0056 | CoreDryRun.render_process/render_batch | internal | correct |
| 0057 | wallpaper-core `batch effects/composites/presets/all` | public | correct — CLI command |
| 0058 | wallpaper-core `batch --flat` | public | correct — CLI flag |
| 0059 | wallpaper-core `batch --dry-run` | public | correct — CLI flag |
| 0060 | CommandExecutor builds/runs magick commands | internal | correct — not in __all__ |
| 0061 | CommandExecutor.is_magick_available | internal | correct |
| 0062 | ChainExecutor.execute_chain | internal | correct |
| 0063 | BatchGenerator runs all items | internal | correct |
| 0064 | BatchGenerator._get_output_path | internal | correct |
| 0065 | verbosity flags (-q, -v, -vv) | public | correct — CLI flags |
| 0066 | effects schema models | internal | correct — schema models not individually in __all__ |

### orchestrator (BHV-0067 – BHV-0082)

| BHV | Title (abbreviated) | Publicity | Verified |
|-----|---------------------|-----------|---------|
| 0067 | wallpaper-orchestrator CLI commands | public | correct — CLI |
| 0068 | wallpaper-orchestrator configures settings | public | correct — CLI startup behavior |
| 0069 | UnifiedConfig frozen model | internal | correct — UnifiedConfig in __all__ but behavior is internal model detail |
| 0070 | ContainerSettings validation | internal | correct — validates internal Pydantic model |
| 0071 | ContainerManager.get_image_name | public | correct — ContainerManager in __all__ |
| 0072 | ContainerManager.build_volume_mounts | internal | correct — internal helper |
| 0073 | ContainerManager.is_image_available | internal | correct — internal check |
| 0074 | ContainerManager.run_process | public | correct — ContainerManager in __all__, run_process is primary method |
| 0075 | wallpaper-process install command | public | correct — CLI command |
| 0076 | wallpaper-process uninstall command | public | correct — CLI command |
| 0077 | install/uninstall --dry-run | public | correct — CLI flag |
| 0078 | wallpaper-process process effect/composite/preset | public | correct — CLI command |
| 0079 | wallpaper-process process --dry-run | public | correct — CLI flag |
| 0080 | OrchestratorDryRun validate/render | internal | correct — not in __all__ |
| 0081 | wallpaper-process batch | public | correct — CLI command |
| 0082 | orchestrator layered settings CLI overrides | public | RECLASSIFIED from internal |
