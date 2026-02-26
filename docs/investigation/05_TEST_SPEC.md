# TEST_SPEC — Behavior Catalog

<!-- Generated: iteration 0001, phase 3 -->
<!-- Updated: iteration 0001, phase 4 — publicity classifications verified -->
<!-- Total BHVs: 82 | Public: 38 | Internal: 44 -->

## Test execution

Command: `python -m pytest`
Run per-package: `make test-<package>` (e.g. `make test-settings`)
All packages: `make test-all`

---

## Behaviors

### Package: settings (BHV-0001 – BHV-0030)

## BHV-0001

- Title: FileLoader detects file format from extension (.toml, .yaml, .yml)
- Publicity: internal
- Package: settings
- Preconditions: A file path with a recognized extension exists on disk
- Steps:
  1. Call `FileLoader.detect_format(filepath)` with a path ending in `.toml`, `.yaml`, or `.yml`
- Expected output: Returns the string `"toml"` for `.toml` files; returns `"yaml"` for `.yaml` or `.yml` files
- Errors/edge cases: Raises `SettingsFileError("Unsupported file format")` for unsupported extensions (e.g., `.json`, `.ini`) and for files with no extension at all
- Evidence: `packages/settings/tests/test_loader.py::TestFormatDetection::test_detect_toml_format` (line 14), `::test_detect_yaml_format` (line 21), `::test_detect_yml_format` (line 28), `::test_detect_unsupported_format` (line 35), `::test_detect_no_extension` (line 43)

---

## BHV-0002

- Title: FileLoader loads TOML files into a plain Python dict
- Publicity: internal
- Package: settings
- Preconditions: A readable `.toml` file exists on disk
- Steps:
  1. Call `FileLoader.load(filepath)` where `filepath` points to a `.toml` file
- Expected output: Returns a `dict` whose keys and values reflect the parsed TOML structure, including nested tables, arrays of tables, and all scalar types (str, int, float, bool, list)
- Errors/edge cases: Returns `{}` for an empty file; raises `SettingsFileError("Failed to parse TOML file")` for invalid TOML syntax
- Evidence: `packages/settings/tests/test_loader.py::TestTOMLLoading::test_load_valid_toml` (line 78), `::test_load_empty_toml` (line 92), `::test_load_invalid_toml_syntax` (line 100), `::test_load_toml_with_nested_tables` (line 108)

---

## BHV-0003

- Title: FileLoader loads YAML files into a plain Python dict
- Publicity: internal
- Package: settings
- Preconditions: A readable `.yaml` or `.yml` file exists on disk
- Steps:
  1. Call `FileLoader.load(filepath)` where `filepath` points to a `.yaml` or `.yml` file
- Expected output: Returns a `dict` (or `None` / `{}` for empty files) whose structure reflects the YAML content; preserves all scalar types (str, int, float, bool, null, list, nested dict)
- Errors/edge cases: Returns `None` or `{}` for empty YAML; raises `SettingsFileError("Failed to parse YAML file")` for invalid YAML syntax
- Evidence: `packages/settings/tests/test_loader.py::TestYAMLLoading::test_load_valid_yaml` (line 158), `::test_load_yaml_with_yml_extension` (line 172), `::test_load_empty_yaml` (line 181), `::test_load_invalid_yaml_syntax` (line 189), `::test_load_yaml_with_complex_types` (line 197)

---

## BHV-0004

- Title: FileLoader raises SettingsFileError for file system problems
- Publicity: internal
- Package: settings
- Preconditions: The caller provides a path that is missing, is a directory, or is unreadable
- Steps:
  1. Call `FileLoader.load(filepath)` with a non-existent path, a directory path, or a path with no read permissions
- Expected output: No output; raises `SettingsFileError`
- Errors/edge cases:
  - Missing file: message matches `"File not found"`
  - Path is a directory: message matches `"is not a file"`
  - No read permission: message matches `"Failed to read file"`
  - Unsupported format: message matches `"Unsupported file format"`
- Evidence: `packages/settings/tests/test_loader.py::TestErrorHandling::test_load_nonexistent_file` (line 228), `::test_load_directory_instead_of_file` (line 235), `::test_load_unsupported_format` (line 243), `::test_load_unreadable_file` (line 251)

---

## BHV-0005

- Title: ConfigMerger deep-merges two dicts with later values winning
- Publicity: internal
- Package: settings
- Preconditions: None; operates on plain Python dicts
- Steps:
  1. Call `ConfigMerger.merge(base, override)` with any two dicts
- Expected output: Returns a new dict containing all keys from both inputs; for keys present in both, the `override` value wins; for nested dicts, the merge recurses (keys present only in `base` are preserved); the result is an independent copy
- Errors/edge cases: Empty dicts on either side are handled gracefully; merging empty dicts returns `{}`
- Evidence: `packages/settings/tests/test_merger.py::TestConfigMergerBasics::test_merge_empty_dicts` (line 9), `::test_merge_empty_base_with_override` (line 14), `::test_adding_new_keys` (line 24), `::TestConfigMergerDicts::test_recursively_merging_nested_dicts` (line 108), `::test_merging_deeply_nested_dicts` (line 115)

---

## BHV-0006

- Title: ConfigMerger replaces lists atomically, not element-wise
- Publicity: internal
- Package: settings
- Preconditions: None; operates on plain Python dicts
- Steps:
  1. Call `ConfigMerger.merge(base, override)` where both dicts contain the same key whose value is a list
- Expected output: The result contains the override's list verbatim; no element-level concatenation occurs
- Errors/edge cases: Replacing a list with an empty list produces `[]`; replacing an empty list with values produces the new list; lists of different lengths follow the same rule
- Evidence: `packages/settings/tests/test_merger.py::TestConfigMergerLists::test_replacing_list_atomically` (line 74), `::test_list_not_merged_element_wise` (line 95), `::test_replacing_empty_list_with_values` (line 81), `::test_replacing_list_with_empty_list` (line 88)

---

## BHV-0007

- Title: ConfigMerger never mutates its inputs and always returns an independent copy
- Publicity: internal
- Package: settings
- Preconditions: None
- Steps:
  1. Call `ConfigMerger.merge(base, override)`
  2. Modify the returned result or either input
- Expected output: Modifications to the result do not affect `base` or `override`; modifications to `base` or `override` after the call do not affect the result
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_merger.py::TestConfigMergerImmutability::test_does_not_mutate_base` (line 178), `::test_does_not_mutate_override` (line 188), `::test_result_is_independent_copy` (line 198), `::test_modifying_base_after_merge` (line 209)

---

## BHV-0008

- Title: LayerSource is an immutable record describing a single config file layer
- Publicity: internal
- Package: settings
- Preconditions: None
- Steps:
  1. Construct `LayerSource(name=..., filepath=..., namespace=..., is_namespaced=...)`
  2. Attempt to reassign a field
- Expected output: Construction succeeds and all four fields are readable; attempting to reassign any field raises `AttributeError` (frozen dataclass)
- Errors/edge cases: `filepath` must be a `Path` object, not a string
- Evidence: `packages/settings/tests/test_layers.py::TestLayerSource::test_creates_layer_source_with_all_fields` (line 28), `::test_layer_source_is_immutable` (line 54), `::test_stores_path_object` (line 65)

---

## BHV-0009

- Title: LayerDiscovery discovers package default layers from SchemaRegistry
- Publicity: internal
- Package: settings
- Preconditions: One or more namespaces have been registered in `SchemaRegistry`
- Steps:
  1. Register schemas via `SchemaRegistry.register()`
  2. Call `LayerDiscovery.discover_layers()`
- Expected output: Returns one `LayerSource` per registered namespace whose `defaults_file` exists; each such layer has `is_namespaced=False` and `namespace` set to the registered namespace name
- Errors/edge cases: Skips entries whose `defaults_file` path does not exist on disk; returns `[]` when registry is empty and no files exist
- Evidence: `packages/settings/tests/test_layers.py::TestLayerDiscovery::test_discover_layers_returns_package_defaults_from_registry` (line 93), `::test_discover_layers_skips_nonexistent_package_defaults` (line 125), `::test_discover_layers_with_no_registry_and_no_files` (line 87)

---

## BHV-0010

- Title: LayerDiscovery includes the project-root settings.toml when it exists
- Publicity: internal
- Package: settings
- Preconditions: A file named `settings.toml` exists in the current working directory
- Steps:
  1. Call `LayerDiscovery.discover_layers()`
- Expected output: Returns a `LayerSource` named `"project-root"` with `is_namespaced=True` and `namespace=""` pointing to `<cwd>/settings.toml`
- Errors/edge cases: When `settings.toml` is absent from the cwd, no project-root layer is included
- Evidence: `packages/settings/tests/test_layers.py::TestLayerDiscovery::test_discover_layers_includes_project_root_when_exists` (line 143), `::test_discover_layers_skips_project_root_when_missing` (line 160)

---

## BHV-0011

- Title: LayerDiscovery includes the user config layer from the XDG config directory
- Publicity: internal
- Package: settings
- Preconditions: A file exists at `~/.config/<app_name>/settings.toml`
- Steps:
  1. Call `LayerDiscovery.discover_layers(app_name="<app_name>")`
- Expected output: Returns a `LayerSource` named `"user-config"` with `is_namespaced=True` and `namespace=""` pointing to that file; uses `"layered-settings"` as the default `app_name` when none is provided
- Errors/edge cases: When the user config file is absent, no user-config layer is included
- Evidence: `packages/settings/tests/test_layers.py::TestLayerDiscovery::test_discover_layers_includes_user_config_when_exists` (line 168), `::test_discover_layers_skips_user_config_when_missing` (line 185), `::test_discover_layers_uses_default_app_name` (line 193), `::test_discover_layers_respects_explicit_app_name` (line 209)

---

## BHV-0012

- Title: LayerDiscovery returns layers in priority order: package defaults → project → user
- Publicity: internal
- Package: settings
- Preconditions: Multiple layer types are present
- Steps:
  1. Register schemas and ensure all files exist
  2. Call `LayerDiscovery.discover_layers(app_name=...)`
- Expected output: All package-defaults layers appear before the project-root layer, which appears before the user-config layer; index order in the returned list determines merge priority (first = lowest priority)
- Errors/edge cases: Absent files are silently omitted; layer count equals the number of present files
- Evidence: `packages/settings/tests/test_layers.py::TestLayerDiscovery::test_discover_layers_returns_correct_priority_order` (line 224), `::test_discover_layers_with_mixed_existence` (line 254), `::TestLayerDiscoveryIntegration::test_discover_full_application_layers` (line 292)

---

## BHV-0013

- Title: ConfigBuilder.build() merges layers in order and returns a validated Pydantic model
- Publicity: internal
- Package: settings
- Preconditions: A Pydantic `BaseModel` subclass is available as `root_model`; a list of `LayerSource` objects may be provided
- Steps:
  1. Call `ConfigBuilder.build(root_model=..., layers=[...], cli_overrides=...)`
- Expected output: Returns an instance of `root_model` whose field values reflect the deep-merged result of all layers (later layers win); Pydantic field defaults fill any gaps; data types are preserved (bool, int, float, str, list)
- Errors/edge cases: An empty layers list returns the model with Pydantic defaults; raises `SettingsValidationError` when the merged dict fails Pydantic validation
- Evidence: `packages/settings/tests/test_builder.py::TestConfigBuilderBasics::test_build_with_empty_layers` (line 39), `::test_build_returns_validated_instance` (line 52), `::TestLayerMerging::test_build_merges_layers_in_order` (line 201), `::test_build_deep_merges_nested_values` (line 258), `::TestIntegration::test_build_preserves_data_types` (line 711)

---

## BHV-0014

- Title: ConfigBuilder handles flat-format (non-namespaced) layers by wrapping them in the namespace key
- Publicity: internal
- Package: settings
- Preconditions: A `LayerSource` has `is_namespaced=False` and a non-empty `namespace`
- Steps:
  1. Create a `LayerSource` with `namespace="core"`, `is_namespaced=False`, pointing to a flat TOML/YAML file
  2. Call `ConfigBuilder.build(root_model=..., layers=[layer])`
- Expected output: The file's top-level keys are treated as belonging to the `"core"` namespace, so `root_model.core.<key>` reflects the file values
- Errors/edge cases: Multiple flat layers for different namespaces are each wrapped independently before merging
- Evidence: `packages/settings/tests/test_builder.py::TestFlatFormatLoading::test_build_with_flat_format_layer` (line 67), `::test_build_with_multiple_flat_layers` (line 95)

---

## BHV-0015

- Title: ConfigBuilder handles namespaced layers without modification
- Publicity: internal
- Package: settings
- Preconditions: A `LayerSource` has `is_namespaced=True`
- Steps:
  1. Create a `LayerSource` with `is_namespaced=True`, pointing to a file with top-level namespace keys (e.g., `[core]`, `[effects]`)
  2. Call `ConfigBuilder.build(root_model=..., layers=[layer])`
- Expected output: The file's top-level keys map directly to `root_model` fields; partial namespaced files (defining only some namespaces) are also accepted
- Errors/edge cases: None beyond standard Pydantic validation
- Evidence: `packages/settings/tests/test_builder.py::TestNamespacedFormatLoading::test_build_with_namespaced_layer` (line 140), `::test_build_with_partial_namespaced_layer` (line 170)

---

## BHV-0016

- Title: ConfigBuilder applies CLI overrides via dotted-path keys at highest priority
- Publicity: internal
- Package: settings
- Preconditions: `cli_overrides` is a dict using dotted-path notation (e.g., `{"core.workers": 16}`)
- Steps:
  1. Call `ConfigBuilder.build(root_model=..., layers=[...], cli_overrides={"ns.key": value})`
- Expected output: CLI values override all layer values for the same dotted path; multi-segment paths (e.g., `"core.timeout"`) create or overwrite intermediate dict keys; `None` or `{}` are both treated as "no overrides"
- Errors/edge cases: Intermediate dicts that do not yet exist in the merged data are created automatically
- Evidence: `packages/settings/tests/test_builder.py::TestCLIOverrides::test_build_applies_cli_overrides` (line 348), `::test_build_applies_deep_cli_overrides` (line 379), `::test_build_cli_overrides_take_highest_priority` (line 397), `::test_build_creates_intermediate_dicts_for_cli_overrides` (line 426), `::test_build_with_none_cli_overrides` (line 441), `::test_build_with_empty_cli_overrides` (line 464)

---

## BHV-0017

- Title: ConfigBuilder raises SettingsValidationError when merged data fails Pydantic validation
- Publicity: internal
- Package: settings
- Preconditions: A layer or CLI override supplies a value that violates the `root_model` schema
- Steps:
  1. Provide a config file with an invalid field value (e.g., string where int expected)
  2. Call `ConfigBuilder.build()`
- Expected output: Raises `SettingsValidationError`; the error's `config_name` attribute equals the model class name; the message contains the model name and Pydantic error details
- Errors/edge cases: Missing required fields also raise `SettingsValidationError`
- Evidence: `packages/settings/tests/test_builder.py::TestValidation::test_build_raises_settings_validation_error_on_invalid_data` (line 521), `::test_build_validation_error_includes_details` (line 548), `::test_build_handles_missing_required_fields` (line 575)

---

## BHV-0018

- Title: SchemaEntry is an immutable record storing namespace, model type, and defaults file path
- Publicity: internal
- Package: settings
- Preconditions: None
- Steps:
  1. Construct `SchemaEntry(namespace=..., model=..., defaults_file=...)`
  2. Attempt to reassign any field
- Expected output: Construction succeeds; `entry.model` is the class itself (not an instance); attempting to reassign any field raises `AttributeError` (frozen dataclass)
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_registry.py::TestSchemaEntry::test_creates_entry_with_all_fields` (line 27), `::test_entry_is_immutable` (line 38), `::test_stores_model_type_not_instance` (line 48)

---

## BHV-0019

- Title: SchemaRegistry.register() maps a namespace to a Pydantic model and defaults file
- Publicity: public
- Package: settings
- Preconditions: The namespace has not already been registered
- Steps:
  1. Call `SchemaRegistry.register(namespace="core", model=MyModel, defaults_file=Path(...))`
- Expected output: The namespace is stored in the class-level registry; `SchemaRegistry.get("core")` returns a `SchemaEntry` with the correct model and path
- Errors/edge cases: Registering the same namespace twice raises `SettingsRegistryError` containing the namespace name and `"already registered"` in the reason; the original registration remains intact after a failed duplicate attempt
- Evidence: `packages/settings/tests/test_registry.py::TestSchemaRegistry::test_register_creates_new_entry` (line 71), `::test_register_with_different_namespaces` (line 86), `::test_register_duplicate_namespace_raises_error` (line 107), `::TestRegistryIntegration::test_prevents_accidental_duplicate_registration` (line 294)

---

## BHV-0020

- Title: SchemaRegistry.get(), all_namespaces(), and all_entries() query the registry
- Publicity: public
- Package: settings
- Preconditions: Zero or more namespaces have been registered
- Steps:
  1. Call `SchemaRegistry.get("namespace")` to retrieve one entry
  2. Call `SchemaRegistry.all_namespaces()` to list all registered namespace strings
  3. Call `SchemaRegistry.all_entries()` to retrieve all `SchemaEntry` objects
- Expected output: `get()` returns `None` for unregistered namespaces and the correct `SchemaEntry` otherwise; `all_namespaces()` and `all_entries()` return `[]` when empty; all operations work as class methods (no instance required)
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_registry.py::TestSchemaRegistry::test_get_returns_none_for_unregistered_namespace` (line 127), `::test_get_returns_correct_entry` (line 132), `::test_all_namespaces_returns_empty_list_when_empty` (line 153), `::test_all_entries_returns_all_schema_entries` (line 173), `::test_registry_uses_class_level_storage` (line 221)

---

## BHV-0021

- Title: SchemaRegistry.clear() removes all registrations and permits re-registration
- Publicity: internal
- Package: settings
- Preconditions: One or more namespaces have been registered
- Steps:
  1. Call `SchemaRegistry.clear()`
- Expected output: `get()`, `all_namespaces()`, and `all_entries()` all return empty results; previously duplicate namespaces can be registered again without error
- Errors/edge cases: Calling `clear()` on an already-empty registry is a no-op
- Evidence: `packages/settings/tests/test_registry.py::TestSchemaRegistry::test_clear_removes_all_registrations` (line 193), `::test_clear_allows_re_registration` (line 210)

---

## BHV-0022

- Title: configure() stores the root model and app name and clears the config cache
- Publicity: public
- Package: settings
- Preconditions: None; may be called before or after `SchemaRegistry.register()`
- Steps:
  1. Call `configure(root_model=AppConfig, app_name="myapp")`
- Expected output: The system records the model class and app name; any previously cached `get_config()` result is discarded; the function returns `None` and does not raise
- Errors/edge cases: Calling `configure()` again (reconfiguration) also clears the cache; calling without any prior `SchemaRegistry.register()` calls is valid
- Evidence: `packages/settings/tests/test_integration.py::TestConfigureFunction::test_configure_stores_root_model_and_app_name` (line 43), `::test_configure_clears_cache` (line 61), `::TestErrorHandling::test_configure_without_registration_works` (line 344)

---

## BHV-0023

- Title: get_config() discovers layers, merges them, and returns a validated config instance
- Publicity: public
- Package: settings
- Preconditions: `configure()` has been called
- Steps:
  1. Call `get_config()` (no arguments) to get the base configuration
- Expected output: Returns a validated instance of the `root_model` with values sourced from all discovered layers (package defaults → project root → user config); subsequent calls without arguments return the same cached instance (`is` identity)
- Errors/edge cases: Raises `RuntimeError` (message contains `"configure() must be called"`) if `configure()` has not been called; raises `SettingsError` on validation failure
- Evidence: `packages/settings/tests/test_integration.py::TestGetConfigFunction::test_get_config_raises_if_not_configured` (line 86), `::test_get_config_returns_validated_instance` (line 103), `::test_get_config_caches_result` (line 121), `::TestFullWorkflow::test_full_workflow_with_package_defaults` (line 181)

---

## BHV-0024

- Title: get_config(overrides=...) applies dotted-path CLI overrides without polluting the cache
- Publicity: public
- Package: settings
- Preconditions: `configure()` has been called
- Steps:
  1. Call `get_config(overrides={"core.workers": 16})`
- Expected output: Returns a fresh instance with override values applied at highest priority; this call does not update the internal cache; subsequent no-argument `get_config()` calls still return the cached pre-override result
- Errors/edge cases: Each call with different overrides produces an independent instance
- Evidence: `packages/settings/tests/test_integration.py::TestGetConfigFunction::test_get_config_with_overrides_does_not_cache` (line 138), `::test_get_config_overrides_do_not_affect_cache` (line 157), `::TestFullWorkflow::test_full_workflow_with_cli_overrides` (line 284)

---

## BHV-0025

- Title: Full four-layer priority order is enforced end-to-end through the public API
- Publicity: public
- Package: settings
- Preconditions: Package defaults, project settings.toml, user config, and CLI overrides are all present
- Steps:
  1. Register package defaults via `SchemaRegistry.register()`
  2. Create `settings.toml` files at project root and user config dir
  3. Call `configure()` then `get_config(overrides={...})`
- Expected output: CLI overrides win over user config, which wins over project settings, which wins over package defaults; each layer only overrides the specific keys it defines
- Errors/edge cases: None beyond standard validation
- Evidence: `packages/settings/tests/test_integration.py::TestFullWorkflow::test_layer_priority_order` (line 302), `::test_full_workflow_with_project_settings` (line 219), `::test_full_workflow_with_user_config` (line 253), `::TestIntegration::test_build_realistic_multi_layer_scenario` (line 595)

---

## BHV-0026

- Title: Settings error hierarchy: SettingsFileError, SettingsRegistryError, and SettingsValidationError all extend SettingsError
- Publicity: internal
- Package: settings
- Preconditions: None
- Steps:
  1. Raise any of the specific error types
  2. Catch as `SettingsError` or `Exception`
- Expected output: Each specific error is catchable as `SettingsError`; each formats its message as `"Error loading <path>: <reason>"`, `"Registry error for namespace '<ns>': <reason>"`, or `"Validation error for '<name>': <reason>"` respectively
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_errors.py::TestSettingsError::test_inherits_from_exception` (line 16), `::TestSettingsFileError::test_formats_message_correctly` (line 41), `::TestSettingsRegistryError::test_formats_message_correctly` (line 72), `::TestSettingsValidationError::test_formats_message_correctly` (line 111), `::TestErrorHierarchy::test_all_errors_can_be_caught_by_base_class` (line 155)

---

## BHV-0027

- Title: XDG path constants and helper functions provide canonical file locations
- Publicity: public
- Package: settings
- Preconditions: None; module-level constants are evaluated at import time
- Steps:
  1. Import `XDG_CONFIG_HOME`, `USER_CONFIG_DIR`, `USER_SETTINGS_FILE`, `USER_EFFECTS_FILE`
  2. Call `get_project_settings_file(project_root)` or `get_project_effects_file(project_root)`
- Expected output: `XDG_CONFIG_HOME` is a `Path` defaulting to `~/.config`; `USER_CONFIG_DIR` equals `XDG_CONFIG_HOME / APP_NAME`; `USER_SETTINGS_FILE` equals `USER_CONFIG_DIR / "settings.toml"`; `USER_EFFECTS_FILE` equals `USER_CONFIG_DIR / "effects.yaml"`; project helpers return `<root>/settings.toml` and `<root>/effects.yaml`
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_paths.py::TestXdgConfigHome::test_xdg_config_home_default` (line 9), `::TestUserPaths::test_user_config_dir` (line 20), `::test_user_settings_file` (line 27), `::test_user_effects_file` (line 34), `::TestProjectPaths::test_get_project_settings_file` (line 45), `::test_get_project_effects_file` (line 53)

---

## BHV-0028

- Title: Application constants APP_NAME, SETTINGS_FILENAME, and EFFECTS_FILENAME are defined
- Publicity: public
- Package: settings
- Preconditions: None
- Steps:
  1. Import constants from `layered_settings.constants`
- Expected output: `APP_NAME` is a non-empty string; `SETTINGS_FILENAME == "settings.toml"`; `EFFECTS_FILENAME == "effects.yaml"`
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_constants.py::test_app_name_constant` (line 4), `::test_settings_filename_constant` (line 12), `::test_effects_filename_constant` (line 19)

---

## BHV-0029

- Title: DryRunBase renders headers, fields, commands, validation results, tables, and command lists
- Publicity: public
- Package: settings
- Preconditions: A `DryRunBase` instance is constructed with a Rich `Console`
- Steps:
  1. Call any of: `render_header(title)`, `render_field(label, value)`, `render_command(label, cmd)`, `render_validation(checks)`, `render_table(title, columns, rows)`, `render_commands_list(commands)`
- Expected output: Each method writes formatted text to the console including the provided values; `render_header` includes both `"Dry Run"` and the title; numbered list is rendered for `render_commands_list`
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_dry_run.py::TestDryRunBaseRendering::test_render_header` (line 44), `::test_render_field` (line 51), `::test_render_command` (line 58), `::test_render_validation_passed` (line 65), `::test_render_validation_failed` (line 76), `::test_render_table` (line 88), `::test_render_commands_list` (line 102)

---

## BHV-0030

- Title: ValidationCheck is a dataclass holding a check name, pass/fail status, and optional detail
- Publicity: public
- Package: settings
- Preconditions: None
- Steps:
  1. Construct `ValidationCheck(name=..., passed=True/False)` or with an optional `detail` string
- Expected output: `check.passed` and `check.name` reflect the arguments; `check.detail` defaults to `""`; failed checks carry the detail message
- Errors/edge cases: None
- Evidence: `packages/settings/tests/test_dry_run.py::TestValidationCheck::test_passed_check` (line 27), `::test_failed_check_with_detail` (line 33)

---

### Package: effects (BHV-0031 – BHV-0036)

## BHV-0031

- Title: effects.configure() stores paths and clears the cached EffectsConfig
- Publicity: public
- Package: effects
- Preconditions: None
- Steps:
  1. Call `configure(package_effects_file=Path(...), project_root=..., user_effects_file=...)`
- Expected output: The module stores the provided paths; any previously cached `load_effects()` result is discarded; the function returns `None` and does not raise
- Errors/edge cases: `project_root` and `user_effects_file` are optional; recalling `configure()` clears the cache
- Evidence: `packages/effects/tests/test_api.py::test_configure_stores_settings` (line 8)

---

## BHV-0032

- Title: effects.load_effects() loads and merges all effects layers into a validated EffectsConfig
- Publicity: public
- Package: effects
- Preconditions: `configure()` has been called with a valid `package_effects_file`
- Steps:
  1. Call `load_effects()`
- Expected output: Returns an `EffectsConfig` instance with `version`, `effects`, `parameter_types`, `composites`, and `presets` attributes; subsequent calls return the same cached instance (`is` identity)
- Errors/edge cases: Raises `RuntimeError` (matching `"configure.*must be called"`) if called before `configure()`; raises `EffectsValidationError` when merged YAML fails schema validation
- Evidence: `packages/effects/tests/test_api.py::test_load_effects_without_configure_raises` (line 22), `::test_load_effects_returns_effects_config` (line 33), `::test_load_effects_caches_result` (line 61), `::test_load_effects_raises_on_validation_error` (line 82)

---

## BHV-0033

- Title: EffectsLoader discovers layer files in package → project → user priority order
- Publicity: internal
- Package: effects
- Preconditions: An `EffectsLoader` is constructed with at least a `package_effects_file`
- Steps:
  1. Instantiate `EffectsLoader(package_effects_file=..., project_root=..., user_effects_file=...)`
  2. Call `loader.discover_layers()`
- Expected output: Returns a list of `Path` objects; `layers[0]` is always the package file; project effects.yaml (`<project_root>/effects.yaml`) appears second if present; user effects file appears last if present
- Errors/edge cases: Optional layers (`project_root`, `user_effects_file`) are simply omitted when absent
- Evidence: `packages/effects/tests/test_loader.py::TestEffectsLoader::test_discovers_package_layer` (line 11), `::test_discovers_project_layer` (line 21), `::test_discovers_user_layer` (line 42), `::test_layer_priority_order` (line 58)

---

## BHV-0034

- Title: EffectsLoader deep-merges effects dicts across layers so later layers override earlier ones
- Publicity: internal
- Package: effects
- Preconditions: Two or more effects YAML files exist
- Steps:
  1. Instantiate `EffectsLoader` with multiple layer paths
  2. Call `loader.load_and_merge()`
- Expected output: Returns a merged dict; effects defined in a later layer replace the same-keyed effect from an earlier layer; effects defined only in earlier layers are preserved; the package layer's `version` is the canonical version (not overridden by later layers); `load_and_merge()` raises `EffectsLoadError` if the package layer does not exist
- Errors/edge cases: Missing package file raises `EffectsLoadError`; invalid YAML in any file raises `EffectsLoadError`
- Evidence: `packages/effects/tests/test_loader.py::TestEffectsLoaderMerge::test_merges_effects_from_layers` (line 113), `::test_uses_package_version` (line 160), `::test_works_with_only_package_layer` (line 179), `::test_raises_when_no_package_layer` (line 189), `::test_raises_on_invalid_yaml` (line 96)

---

## BHV-0035

- Title: Effects error hierarchy: EffectsLoadError and EffectsValidationError extend EffectsError
- Publicity: public
- Package: effects
- Preconditions: None
- Steps:
  1. Construct error instances with their required arguments
- Expected output: `EffectsError` is a plain `Exception` subclass accepting a message string; `EffectsLoadError` accepts `file_path` and `reason`, and includes both in its string representation; `EffectsValidationError` accepts `message` and `layer`, and includes both in its string representation; all are catchable as `EffectsError`
- Errors/edge cases: None
- Evidence: `packages/effects/tests/test_errors.py::test_effects_error_base` (line 4), `::test_effects_load_error` (line 14), `::test_effects_validation_error` (line 28)

---

## BHV-0036

- Title: End-to-end three-layer effects merge produces correct EffectsConfig
- Publicity: public
- Package: effects
- Preconditions: Package, project, and user effects.yaml files are available
- Steps:
  1. Call `configure(package_effects_file=..., project_root=..., user_effects_file=...)`
  2. Call `load_effects()`
- Expected output: Returns `EffectsConfig` where: effects overridden in project layer reflect project descriptions/commands; effects present only in the package layer are inherited; effects added by project or user layers appear in the result; `parameter_types` from the package layer are preserved; users can fully replace a package effect by defining the same key in their layer
- Errors/edge cases: None
- Evidence: `packages/effects/tests/test_integration.py::test_full_stack_three_layers` (line 9), `::test_user_can_override_package_effect` (line 91), `::test_works_with_real_effects_yaml` (line 125)

---

### Package: core (BHV-0037 – BHV-0066)

## BHV-0037

- Title: wallpaper-core CLI app is a valid Typer application with help, process, batch, and show subcommands
- Publicity: public
- Package: core
- Preconditions: wallpaper-core package is installed
- Steps:
  1. Invoke `wallpaper-core --help`
- Expected output: Exit code 0; help text mentions `process`, `batch`, and `show` subcommands; `configuration` appears in output
- Errors/edge cases: Not applicable for bootstrap
- Evidence: `packages/core/tests/test_cli_bootstrap.py::test_cli_app_exists` (line 10), `::test_cli_help_works` (line 17), `packages/core/tests/test_cli.py::TestMainCLI::test_help` (line 21)

---

## BHV-0038

- Title: wallpaper-core configures layered settings on startup and exposes core/effects namespaces
- Publicity: public
- Package: core
- Preconditions: wallpaper-core package is installed; may or may not have user config files
- Steps:
  1. Import the CLI app or invoke any command
- Expected output: `layered_settings` is configured with `core` namespace; `get_config()` returns an object with `.core` and `.effects` attributes
- Errors/edge cases: If config files are missing, configuration may raise but the import itself succeeds
- Evidence: `packages/core/tests/test_cli_bootstrap.py::test_cli_configures_layered_settings` (line 24), `packages/core/tests/test_integration.py::test_config_loads_from_package_defaults` (line 10)

---

## BHV-0039

- Title: wallpaper-core layered settings merges CLI overrides onto package defaults
- Publicity: public
- Package: core
- Preconditions: wallpaper-core is configured with `CoreOnlyConfig`
- Steps:
  1. Call `configure(CoreOnlyConfig, app_name="wallpaper-effects")`
  2. Call `get_config(overrides={"core.execution.parallel": False, "core.execution.max_workers": 4})`
- Expected output: `config.core.execution.parallel` is `False`; `config.core.execution.max_workers` is `4`; unoverridden defaults (e.g., `backend.binary`) remain at package defaults
- Errors/edge cases: Passing unknown namespace keys has undefined behaviour
- Evidence: `packages/core/tests/test_integration.py::test_config_merges_cli_overrides` (line 23)

---

## BHV-0040

- Title: wallpaper-core package settings.toml provides correct default execution, output, and backend values
- Publicity: internal
- Package: core
- Preconditions: Package is installed; `settings.toml` exists inside `wallpaper_core/config/`
- Steps:
  1. Read `settings.toml` and parse into `CoreSettings`
- Expected output: `execution.parallel=True`, `execution.strict=True`, `execution.max_workers=0`, `output.verbosity=1` (NORMAL), `backend.binary="magick"`; file uses flat (non-namespaced) TOML sections
- Errors/edge cases: Missing or malformed file causes an uncaught error at schema registration time
- Evidence: `packages/core/tests/test_config_defaults.py::test_settings_toml_validates_against_schema` (line 28), `::test_settings_toml_uses_flat_format` (line 44), `::test_settings_toml_exists` (line 9)

---

## BHV-0041

- Title: wallpaper-core CoreSettings validates and normalises nested sub-settings via Pydantic
- Publicity: internal
- Package: core
- Preconditions: None
- Steps:
  1. Instantiate `CoreSettings` with a dict or keyword arguments
- Expected output: Nested `ExecutionSettings`, `OutputSettings`, `BackendSettings`, `ProcessingSettings` sub-objects are accessible; integer verbosity values coerce to `Verbosity` enum; `default_dir` strings coerce to `Path`; `max_workers` must be >= 0
- Errors/edge cases: `max_workers=-1` raises `ValidationError`; `CoreSettings(execution={"max_workers": -5})` raises `ValidationError` mentioning `max_workers`
- Evidence: `packages/core/tests/test_config_schema.py::test_core_settings_from_dict` (line 151), `::test_execution_settings_validation` (line 50), `::test_output_settings_default_dir_default_value` (line 79), `::test_core_settings_nested_validation` (line 165)

---

## BHV-0042

- Title: wallpaper-core loads the package effects.yaml via `get_package_effects_file()` and it passes schema validation
- Publicity: internal
- Package: core
- Preconditions: Package is installed
- Steps:
  1. Call `get_package_effects_file()`
  2. Load the returned YAML path with `load_effects()`
- Expected output: Returns an existing `Path` whose name is `effects.yaml` and which lives under `wallpaper_core`; the file contains `version: "1.0"`, `effects`, and `parameter_types` keys
- Errors/edge cases: Non-existent path causes `EffectsLoadError`
- Evidence: `packages/core/tests/test_effects_integration.py::TestPackageEffects::test_get_package_effects_file_returns_valid_path` (line 9), `::test_package_effects_file_is_valid_yaml` (line 19)

---

## BHV-0043

- Title: wallpaper-core layered-effects merges package, project, and user layers; later layers override earlier ones
- Publicity: public
- Package: core
- Preconditions: `layered_effects.configure()` has been called with at least a package effects file
- Steps:
  1. Call `configure(package_effects_file=..., project_root=..., user_effects_file=...)`
  2. Call `load_effects()`
- Expected output:
  - Package effects are always present (e.g., `blur`, `brightness`, `blackwhite-blur`)
  - Project-level effects extend the set (additive merge)
  - User-level effects override package definitions (e.g., changed description and command)
  - `parameter_types` from all layers are merged
- Errors/edge cases: Invalid YAML at any layer raises `EffectsLoadError`; effects with missing required fields raise `EffectsValidationError` mentioning the offending field
- Evidence: `packages/core/tests/test_effects_integration.py::TestLayeredEffectsConfiguration::test_loads_package_defaults_only` (line 41), `::test_project_effects_extend_package` (line 56), `::test_user_effects_override_package` (line 82), `::TestErrorHandling::test_invalid_yaml_raises_load_error` (line 142), `::test_validation_error_shows_helpful_message` (line 159)

---

## BHV-0044

- Title: wallpaper-core `show effects|composites|presets|all` displays available effects configuration
- Publicity: public
- Package: core
- Preconditions: effects.yaml is loadable; `wallpaper-core` CLI is installed
- Steps:
  1. Invoke `wallpaper-core show effects` (or `composites`, `presets`, `all`)
- Expected output: Exit code 0; output contains at least `blur` and `brightness` for effects; `blackwhite-blur` for composites; `dark_blur` for presets
- Errors/edge cases: Invalid user effects file causes exit code 1 with "Failed to load" message; `EffectsValidationError` or `EffectsError` during load causes exit code 1
- Evidence: `packages/core/tests/test_cli_effects_loading.py::test_cli_shows_package_effects` (line 10), `::test_cli_shows_composites` (line 18), `::test_cli_shows_presets` (line 25), `::test_cli_error_on_invalid_user_effects` (line 32), `packages/core/tests/test_cli.py::TestShowCommands::test_show_all` (line 49)

---

## BHV-0045

- Title: wallpaper-core `info` command displays core settings and effects count
- Publicity: public
- Package: core
- Preconditions: wallpaper-core CLI is installed
- Steps:
  1. Invoke `wallpaper-core info`
- Expected output: Exit code 0; output contains "Core Settings" and effects-related information
- Errors/edge cases: None documented
- Evidence: `packages/core/tests/test_cli.py::TestInfoCommand::test_info_shows_settings` (line 609), `::test_info_shows_effects_count` (line 616), `packages/core/tests/test_cli_bootstrap.py::test_cli_info_command_exists` (line 42)

---

## BHV-0046

- Title: wallpaper-core `version` command prints version string
- Publicity: public
- Package: core
- Preconditions: wallpaper-core CLI is installed
- Steps:
  1. Invoke `wallpaper-core version`
- Expected output: Exit code 0; output contains "wallpaper-effects"
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_cli.py::TestMainCLI::test_version` (line 15)

---

## BHV-0047

- Title: wallpaper-core `process effect` applies a single ImageMagick effect and writes output in hierarchical directory structure
- Publicity: public
- Package: core
- Preconditions: Input image file exists; effect name exists in loaded effects config; ImageMagick (`magick`) is on PATH
- Steps:
  1. Invoke `wallpaper-core process effect <input> --effect <name> -o <output_dir>`
- Expected output: Exit code 0; output file created at `<output_dir>/<stem>/effects/<effect_name>.<ext>`
- Errors/edge cases: Missing input file exits non-zero; unknown effect name exits non-zero; executor failure exits code 1; `EffectsValidationError` or `EffectsError` exits code 1
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_effect_with_output_dir_creates_subdirectory` (line 59), `::test_process_effect_unknown` (line 138), `::test_process_effect_missing_input` (line 157), `::TestExecutorFailures::test_apply_effect_executor_failure` (line 890)

---

## BHV-0048

- Title: wallpaper-core `process effect` accepts per-effect CLI parameters (e.g., `--blur 0x10`)
- Publicity: public
- Package: core
- Preconditions: Input image exists; named effect has corresponding CLI flags defined in effects config
- Steps:
  1. Invoke `wallpaper-core process effect <input> -e blur --blur 0x10 -o <output_dir>`
- Expected output: Exit code 0; output file created; the effect command is run with the overridden parameter value substituted for `$BLUR`
- Errors/edge cases: Unknown flags are rejected by Typer
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_effect_with_params` (line 115)

---

## BHV-0049

- Title: wallpaper-core `process effect|composite|preset` uses default output directory from settings when `-o` is omitted
- Publicity: public
- Package: core
- Preconditions: Input image exists; `output.default_dir` is set in settings (default `/tmp/wallpaper-effects`)
- Steps:
  1. Invoke `wallpaper-core process effect <input> --effect blur` (no `-o` flag)
- Expected output: Exit code 0; output written to `<default_dir>/<stem>/effects/blur.<ext>` (or `composites/` or `presets/` for the respective commands)
- Errors/edge cases: If default dir cannot be created, the executor fails
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_effect_without_output_uses_default` (line 80), `::test_process_composite_without_output_uses_default` (line 198), `::test_process_preset_without_output_uses_default` (line 301)

---

## BHV-0050

- Title: wallpaper-core `process effect|composite|preset --flat` uses flat output directory structure
- Publicity: public
- Package: core
- Preconditions: Input image exists; named effect/composite/preset exists
- Steps:
  1. Invoke `wallpaper-core process effect <input> --effect blur -o <output_dir> --flat`
- Expected output: Exit code 0; output at `<output_dir>/<stem>/<name>.<ext>` (no `effects/` subdirectory level); same pattern for composites and presets
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_effect_with_flat_flag` (line 93), `::test_process_composite_with_flat_flag` (line 221), `::test_process_preset_with_flat_flag` (line 315)

---

## BHV-0051

- Title: wallpaper-core output path resolution: hierarchical vs flat, preserving input extension
- Publicity: internal
- Package: core
- Preconditions: `resolve_output_path()` is called with `output_dir`, `input_file`, `item_name`, `item_type`, and `flat` flag
- Steps:
  1. Call `resolve_output_path(output_dir, input_file, item_name, item_type, flat=False)`
- Expected output:
  - Hierarchical: `<output_dir>/<stem>/<type_plural>/<name>.<ext>` (e.g., `effects/`, `composites/`, `presets/`)
  - Flat: `<output_dir>/<stem>/<name>.<ext>`
  - Extension defaults to `.png` when input has none; otherwise preserves input extension
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_path_resolution.py::test_resolve_output_path_effect_not_flat` (line 9), `::test_resolve_output_path_effect_flat` (line 21), `::test_resolve_output_path_no_extension_defaults_png` (line 57), `::test_resolve_output_path_preserves_extension` (line 69)

---

## BHV-0052

- Title: wallpaper-core `process composite` chains multiple effects and writes output
- Publicity: public
- Package: core
- Preconditions: Input image exists; named composite exists in effects config; ImageMagick is on PATH
- Steps:
  1. Invoke `wallpaper-core process composite <input> --composite <name> -o <output_dir>`
- Expected output: Exit code 0; output file created at `<output_dir>/<stem>/composites/<name>.<ext>`
- Errors/edge cases: Unknown composite name exits non-zero; missing input exits non-zero; chain executor failure exits code 1
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_composite_with_output_dir` (line 175), `::test_process_composite_unknown` (line 243), `::test_process_composite_missing_input` (line 262), `::TestExecutorFailures::test_apply_composite_executor_failure` (line 918)

---

## BHV-0053

- Title: wallpaper-core `process preset` applies a named preset (either effect-based or composite-based) and writes output
- Publicity: public
- Package: core
- Preconditions: Input image exists; preset name exists; preset references a valid effect or composite
- Steps:
  1. Invoke `wallpaper-core process preset <input> --preset <name> -o <output_dir>`
- Expected output: Exit code 0; output at `<output_dir>/<stem>/presets/<name>.<ext>`; dry-run output includes "Would apply preset: <name>"
- Errors/edge cases: Unknown preset exits non-zero; missing input exits non-zero; executor failure exits code 1
- Evidence: `packages/core/tests/test_cli.py::TestProcessCommands::test_process_preset_with_output_dir` (line 280), `::test_process_preset_missing_input` (line 364), `::test_process_preset_unknown` (line 382), `::test_process_preset_dry_run` (line 337)

---

## BHV-0054

- Title: wallpaper-core `process effect|composite|preset --dry-run` shows planned command(s) without executing
- Publicity: public
- Package: core
- Preconditions: Input image exists (or not — dry-run runs regardless); effect/composite/preset name provided
- Steps:
  1. Invoke any `process` subcommand with `--dry-run`
- Expected output:
  - Exit code 0 even when input or item name is invalid
  - Output includes "Dry Run" header and "Would apply effect/composite/preset: <name>"
  - Output shows the `magick` command that would be run
  - Validation section appears (unless `-q` flag suppresses it) with checks (input file found, magick found, item found, output directory status)
  - No output file is created
  - Unknown names produce "not found" or "cannot resolve" messages in output; exit code is still 0
- Errors/edge cases: Quiet mode (`-q`) shows only the magick command, not the validation section; unknown effects/composites/presets yield warnings, not failures
- Evidence: `packages/core/tests/test_cli_dry_run.py::TestProcessEffectDryRun::test_dry_run_shows_command` (line 11), `::test_dry_run_no_file_created` (line 29), `::test_dry_run_shows_validation` (line 46), `::test_dry_run_missing_input_shows_warning` (line 64), `::test_dry_run_unknown_effect_shows_warning` (line 81), `::test_dry_run_quiet_shows_only_command` (line 98), `packages/core/tests/test_cli.py::TestDryRunErrorCases::test_process_effect_dry_run` (line 780), `::test_dry_run_unknown_composite` (line 732)

---

## BHV-0055

- Title: wallpaper-core `CoreDryRun` validates input file, magick availability, item existence in config, and output directory status
- Publicity: internal
- Package: core
- Preconditions: `CoreDryRun` is instantiated with a Rich `Console`
- Steps:
  1. Call `dry_run.validate_core(input_path=..., item_name=..., item_type=..., config=..., output_path=...)`
- Expected output: Returns a list of `Check` objects; checks include input file existence, magick binary presence on PATH, whether the named item is found in config, and whether the output directory exists (with "would be created" detail when absent); each `Check` has a `passed` boolean
- Errors/edge cases: Unknown `item_type` produces a failing check named "found in config"
- Evidence: `packages/core/tests/test_dry_run.py::TestCoreValidation::test_validate_input_exists` (line 29), `::test_validate_magick_found` (line 42), `::test_validate_magick_missing` (line 50), `::test_validate_effect_not_found` (line 72), `::test_validate_output_dir_missing` (line 97), `::test_validate_unknown_item_type` (line 193)

---

## BHV-0056

- Title: wallpaper-core `CoreDryRun.render_process` and `render_batch` display process and batch summaries to console
- Publicity: internal
- Package: core
- Preconditions: `CoreDryRun` is instantiated; a Rich `Console` captures output
- Steps:
  1. Call `dry_run.render_process(item_name, item_type, input_path, output_path, params, resolved_command)` or `dry_run.render_batch(...)`
- Expected output:
  - `render_process` for an effect: shows item name, input/output paths, params, and the `magick` command
  - `render_process` for a composite: shows chain steps numbered (e.g. "1.", "step")
  - `render_batch`: produces a table with item names, types, and commands; item count is shown
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_dry_run.py::TestCoreRenderProcess::test_render_process_shows_effect` (line 110), `::test_render_process_composite_shows_chain` (line 140), `::TestCoreRenderBatch::test_render_batch_shows_table` (line 160)

---

## BHV-0057

- Title: wallpaper-core `batch effects|composites|presets|all` applies all configured items in parallel (default) or sequential mode
- Publicity: public
- Package: core
- Preconditions: Input image exists; effects config is loaded; ImageMagick is on PATH
- Steps:
  1. Invoke `wallpaper-core batch effects <input> -o <output_dir>` (or `composites`, `presets`, `all`)
  2. Optionally add `--sequential` to disable parallelism
- Expected output:
  - Exit code 0 (unless `--strict` and a failure occurred)
  - Output directory `<output_dir>/<stem>/effects/` (or `composites/` or `presets/`) contains one file per item
  - `batch all` produces all three subdirectories
  - `BatchResult.total` equals the count of items in config; `succeeded > 0`
- Errors/edge cases: Missing input exits non-zero; `--strict` with any failure exits code 1; without `--strict` failures are tolerated
- Evidence: `packages/core/tests/test_cli.py::TestBatchCommands::test_batch_effects` (line 463), `::test_batch_composites` (line 528), `::test_batch_presets` (line 543), `::test_batch_all` (line 497), `::test_batch_missing_input` (line 558), `packages/core/tests/test_engine_batch.py::TestBatchGenerator::test_parallel_execution` (line 144), `::test_sequential_execution` (line 205)

---

## BHV-0058

- Title: wallpaper-core `batch --flat` writes all outputs directly into output directory without type subdirectories
- Publicity: public
- Package: core
- Preconditions: Input image exists; effects/composites/presets are loaded
- Steps:
  1. Invoke `wallpaper-core batch effects <input> -o <output_dir> --flat`
- Expected output: Exit code 0; output files at `<output_dir>/<stem>/<name>.<ext>` (no `effects/` subdirectory)
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_cli.py::TestBatchCommands::test_batch_effects_flat` (line 481), `::test_batch_all_flat` (line 512), `packages/core/tests/test_engine_batch.py::TestBatchGenerator::test_generate_all_effects_flat` (line 74)

---

## BHV-0059

- Title: wallpaper-core `batch effects|composites|presets --dry-run` lists all planned commands in a table without executing
- Publicity: public
- Package: core
- Preconditions: Input image exists (or not — dry-run proceeds)
- Steps:
  1. Invoke `wallpaper-core batch effects <input> -o <output_dir> --dry-run`
- Expected output:
  - Exit code 0
  - Tabular output containing item names (e.g., `blur`, `blackwhite`) and their `magick` commands
  - Item count is shown (e.g., "9 items" or the digit)
  - No output directory or files are created
- Errors/edge cases: Quiet mode suppresses the validation section; `--flat` in dry-run also succeeds; verbose mode also succeeds
- Evidence: `packages/core/tests/test_cli_dry_run.py::TestBatchEffectsDryRun::test_dry_run_shows_table` (line 196), `::test_dry_run_no_files_created` (line 212), `::test_dry_run_shows_commands` (line 227), `::test_dry_run_shows_item_count` (line 241), `::TestBatchAllDryRun::test_dry_run_shows_all_types` (line 257)

---

## BHV-0060

- Title: wallpaper-core `CommandExecutor` builds and runs ImageMagick commands, substituting `$INPUT`, `$OUTPUT`, and parameter variables
- Publicity: internal
- Package: core
- Preconditions: A command template string with `$INPUT`, `$OUTPUT`, and optional `$PARAM_NAME` variables; input and output `Path` objects
- Steps:
  1. Instantiate `CommandExecutor(output=...)`
  2. Call `executor.execute(command_template, input_path, output_path, params={...})`
- Expected output:
  - Returns `ExecutionResult` with `success=True`, `return_code=0`, `duration >= 0`, and substituted parameter values in `result.command`
  - Output parent directory is created automatically if it does not exist
  - `stdout` and `stderr` from the subprocess are captured in the result
- Errors/edge cases: Non-zero subprocess exit code sets `success=False`; subprocess `RuntimeError` sets `success=False`, `return_code=-1`, error message in `stderr`
- Evidence: `packages/core/tests/test_engine_executor.py::TestCommandExecutor::test_execute_with_params` (line 91), `::test_execute_creates_output_dir` (line 115), `::test_execute_failure` (line 161), `::test_execute_with_exception` (line 285), `::test_execute_duration_recorded` (line 209)

---

## BHV-0061

- Title: wallpaper-core `CommandExecutor.is_magick_available()` checks for ImageMagick binary on PATH
- Publicity: internal
- Package: core
- Preconditions: None
- Steps:
  1. Call `executor.is_magick_available()`
- Expected output: Returns `True` when `shutil.which("magick")` returns a path; `False` when it returns `None`
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_engine_executor.py::TestCommandExecutor::test_is_magick_available_true` (line 56), `::test_is_magick_available_false` (line 63)

---

## BHV-0062

- Title: wallpaper-core `ChainExecutor` executes a sequence of effect steps, piping output of each step as input to the next
- Publicity: internal
- Package: core
- Preconditions: A `ChainExecutor` is constructed with an `EffectsConfig`; at least one chain step references a valid effect name
- Steps:
  1. Call `executor.execute_chain(chain=[ChainStep(effect="blur", params={...}), ...], input_path, output_path)`
- Expected output:
  - `ExecutionResult.success=True`; output file at `output_path`
  - `result.command` contains all effect names in the chain (e.g., both `blur` and `brightness`)
  - `result.duration >= 0`
  - Default parameter values are used when not overridden in the chain step
- Errors/edge cases: Empty chain returns `success=False` with "Empty chain" in `stderr`; unknown effect name returns `success=False` with "Unknown effect" in `stderr`; step failure (non-zero exit code) stops the chain and returns failure
- Evidence: `packages/core/tests/test_engine_chain.py::TestChainExecutor::test_execute_multi_step_chain` (line 53), `::test_execute_empty_chain` (line 19), `::test_execute_chain_unknown_effect` (line 77), `::test_execute_chain_step_failure` (line 96), `::test_execute_chain_uses_defaults` (line 113), `::test_chain_total_duration` (line 154)

---

## BHV-0063

- Title: wallpaper-core `BatchGenerator` runs all effects/composites/presets against an input image, collecting per-item results
- Publicity: internal
- Package: core
- Preconditions: `BatchGenerator` instantiated with `EffectsConfig`; input image exists
- Steps:
  1. Call `generator.generate_all_effects(input_path, output_dir, flat=False)`
- Expected output:
  - Returns `BatchResult` with `total` equal to number of effects in config, `succeeded > 0`
  - `BatchResult.success` is `True` only when `failed == 0`
  - Same API for `generate_all_composites()`, `generate_all_presets()`, and `generate_all()` (which processes all three types)
- Errors/edge cases: `parallel=True` (default) and `parallel=False` are both supported; `max_workers` limits thread pool; `strict=True` (default) means `BatchResult.success=False` on any failure
- Evidence: `packages/core/tests/test_engine_batch.py::TestBatchGenerator::test_generate_all_effects` (line 57), `::test_generate_all` (line 123), `::test_parallel_execution` (line 144), `::test_sequential_execution` (line 205), `::test_generate_all_with_max_workers` (line 266), `::TestBatchResult::test_success_all_passed` (line 13), `::test_success_some_failed` (line 24)

---

## BHV-0064

- Title: wallpaper-core `BatchGenerator._get_output_path` produces correct hierarchical or flat output paths keyed by `ItemType`
- Publicity: internal
- Package: core
- Preconditions: `BatchGenerator` is instantiated
- Steps:
  1. Call `generator._get_output_path(base_dir, name, ItemType.EFFECT, input_file, flat=False)`
- Expected output:
  - Hierarchical: `base_dir/effects/<name><ext>`, `base_dir/composites/<name><ext>`, `base_dir/presets/<name><ext>` for the respective `ItemType` values
  - Flat: `base_dir/<name><ext>` regardless of `ItemType`
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_engine_batch.py::TestBatchGenerator::test_get_output_path_uses_itemtype_enum` (line 287)

---

## BHV-0065

- Title: wallpaper-core verbosity flags (`-q`, `-v`, `-vv`) control output detail level
- Publicity: public
- Package: core
- Preconditions: wallpaper-core CLI is installed
- Steps:
  1. Invoke any command with `-q` (quiet), `-v` (verbose), or `-vv` (debug) global flag
- Expected output:
  - All verbosity levels exit code 0
  - Quiet mode: dry-run shows only the magick command, no Validation section
  - Verbose/debug: additional details in output
  - `RichOutput` suppresses output below its configured verbosity threshold; errors are always shown regardless of level
- Errors/edge cases: None
- Evidence: `packages/core/tests/test_cli.py::TestVerbosityFlags::test_quiet_flag` (line 626), `::test_verbose_flag` (line 631), `::test_debug_flag` (line 636), `packages/core/tests/test_cli_dry_run.py::TestProcessEffectDryRun::test_dry_run_quiet_shows_only_command` (line 98), `packages/core/tests/test_console_output.py::TestRichOutputVerbosity::test_error_always_shown` (line 72)

---

## BHV-0066

- Title: wallpaper-core effects schema models (`Effect`, `CompositeEffect`, `Preset`, `EffectsConfig`) parse from YAML-derived dicts
- Publicity: internal
- Package: core
- Preconditions: None
- Steps:
  1. Construct schema objects directly from Python dicts matching YAML structure
- Expected output:
  - `Effect` validates `description`, `command`, and optional `parameters` dict
  - `CompositeEffect` validates `description` and `chain` list of `ChainStep` objects (each with `effect` and optional `params`)
  - `Preset` validates `description` and either `composite` or `effect` reference with optional `params`
  - `EffectsConfig` composes all above with `version` and optional `parameter_types`
  - Minimal config (version + empty dicts) is valid
- Errors/edge cases: Missing `command` in an `Effect` is a validation error
- Evidence: `packages/core/tests/test_effects_schema.py::TestEffect::test_effect_with_parameters` (line 146), `::TestChainStep::test_chain_step_with_params` (line 195), `::TestPreset::test_preset_with_composite` (line 255), `::TestEffectsConfig::test_complete_config` (line 292), `::test_minimal_config` (line 339)

---

### Package: orchestrator (BHV-0067 – BHV-0082)

## BHV-0067

- Title: wallpaper-orchestrator CLI app exposes `install`, `uninstall`, `process`, `batch`, `show`, `info`, and `version` commands
- Publicity: public
- Package: orchestrator
- Preconditions: wallpaper-orchestrator package is installed
- Steps:
  1. Invoke `wallpaper-process --help`
- Expected output: Exit code 0; `install` and `uninstall` are listed; `process` and `info` are present; `version` command exists and prints "wallpaper-orchestrator"
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_cli_bootstrap.py::test_cli_app_exists` (line 11), `::test_cli_has_install_command` (line 23), `::test_cli_has_uninstall_command` (line 30), `packages/orchestrator/tests/test_cli_integration.py::TestCLIBasics::test_cli_has_core_commands` (line 16), `::test_cli_version_command` (line 43), `packages/orchestrator/tests/test_integration.py::test_cli_commands_registered` (line 64)

---

## BHV-0068

- Title: wallpaper-orchestrator configures layered settings with core, effects, and orchestrator namespaces on startup
- Publicity: public
- Package: orchestrator
- Preconditions: wallpaper-orchestrator package is installed
- Steps:
  1. Call `configure(UnifiedConfig, app_name="wallpaper-effects")`
  2. Call `get_config()`
- Expected output: Config has `.core`, `.effects`, and `.orchestrator` namespaces; `core.execution.parallel=True`, `effects.version="1.0"`, `orchestrator.container.engine="docker"`
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_integration.py::test_unified_config_loads_all_schemas` (line 8), `packages/orchestrator/tests/test_cli_bootstrap.py::test_cli_configures_layered_settings` (line 37)

---

## BHV-0069

- Title: wallpaper-orchestrator `UnifiedConfig` composes `CoreSettings`, `EffectsConfig`, and `OrchestratorSettings` as a frozen model
- Publicity: internal
- Package: orchestrator
- Preconditions: None
- Steps:
  1. Instantiate `UnifiedConfig()` or `UnifiedConfig(**data)`
- Expected output: All three sub-settings accessible at `.core`, `.effects`, `.orchestrator`; model is frozen (mutating `.core` raises `ValidationError`); `engine` defaults to `"docker"`, `image_name` defaults to `"wallpaper-effects:latest"`
- Errors/edge cases: Attempting to assign after construction raises `ValidationError`
- Evidence: `packages/orchestrator/tests/test_config_unified.py::test_unified_config_defaults` (line 11), `::test_unified_config_is_frozen` (line 64), `::test_unified_config_from_dict` (line 47)

---

## BHV-0070

- Title: wallpaper-orchestrator `ContainerSettings` validates engine (only `docker` or `podman`) and normalises trailing slash in registry
- Publicity: internal
- Package: orchestrator
- Preconditions: None
- Steps:
  1. Instantiate `ContainerSettings(engine=..., image_registry=...)`
- Expected output: `engine="docker"` or `engine="podman"` accepted; invalid engine raises `ValidationError` with "Invalid container engine"; trailing slash on `image_registry` is stripped; `None` registry stays `None`
- Errors/edge cases: `ContainerSettings(engine="invalid")` raises `ValidationError`
- Evidence: `packages/orchestrator/tests/test_config_settings.py::test_container_settings_validates_engine` (line 20), `::test_container_settings_normalizes_registry` (line 36), `::test_container_settings_normalizes_empty_registry` (line 45)

---

## BHV-0071

- Title: wallpaper-orchestrator `ContainerManager` constructs the container image name, incorporating optional registry prefix
- Publicity: public
- Package: orchestrator
- Preconditions: `ContainerManager` instantiated with a `UnifiedConfig`
- Steps:
  1. Call `manager.get_image_name()`
- Expected output: Without registry: `"wallpaper-effects:latest"`; with registry `"ghcr.io/user"`: `"ghcr.io/user/wallpaper-effects:latest"`
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_container_manager.py::test_get_image_name_without_registry` (line 30), `::test_get_image_name_with_registry` (line 36), `packages/orchestrator/tests/test_integration.py::test_container_manager_with_registry` (line 54)

---

## BHV-0072

- Title: wallpaper-orchestrator `ContainerManager.build_volume_mounts` produces read-only input and read-write output mount specs
- Publicity: internal
- Package: orchestrator
- Preconditions: Input image file exists; output directory exists
- Steps:
  1. Call `manager.build_volume_mounts(input_image, output_dir)`
- Expected output: Returns a list of exactly 2 mount spec strings; input mount is `<host_path>:/input/<filename>:ro`; output mount is `<output_dir>:/output:rw`
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_container_manager.py::test_build_volume_mounts` (line 47)

---

## BHV-0073

- Title: wallpaper-orchestrator `ContainerManager.is_image_available()` checks whether the container image exists locally via `docker inspect`
- Publicity: internal
- Package: orchestrator
- Preconditions: Container engine CLI is accessible (or mocked)
- Steps:
  1. Call `manager.is_image_available()`
- Expected output: Returns `True` when `docker inspect <image>` exits 0; `False` when exit code is non-zero; `False` on `SubprocessError`; `False` on `FileNotFoundError` (engine not on PATH)
- Errors/edge cases: Engine not installed causes `FileNotFoundError` → returns `False` (does not raise)
- Evidence: `packages/orchestrator/tests/test_container_manager.py::test_is_image_available_true` (line 62), `::test_is_image_available_false` (line 75), `::test_is_image_available_subprocess_error` (line 85), `::test_is_image_available_file_not_found` (line 99)

---

## BHV-0074

- Title: wallpaper-orchestrator `ContainerManager.run_process` builds and runs `docker run` with correct volume mounts, image, and inner `wallpaper-core process` command
- Publicity: public
- Package: orchestrator
- Preconditions: Container image is locally available; input file exists; output directory exists (or can be created)
- Steps:
  1. Call `manager.run_process(command_type="effect", command_name="blur", input_path=..., output_dir=...)`
- Expected output:
  - Calls `docker run --rm -v <input>:/input/<file>:ro -v <output>:/output:rw wallpaper-effects:latest process effect /input/<file> --effect blur -o /output`
  - Input and output host paths are absolute
  - Returns the subprocess result with the container's exit code
  - Output directory is created automatically if absent
  - Works with `podman` engine when configured
  - Additional args (e.g., `--intensity 5`) are appended to the inner command
- Errors/edge cases: Missing container image raises `RuntimeError` mentioning "Container image not found" and suggesting `wallpaper-process install`; missing input raises `FileNotFoundError`; `PermissionError` creating output dir raises `PermissionError` with "Cannot create output directory"; invalid `command_type` raises `ValueError`; empty `command_name` raises `ValueError`
- Evidence: `packages/orchestrator/tests/test_container_execution.py::test_run_process_effect_builds_correct_command` (line 24), `::test_run_process_validates_image_exists` (line 83), `::test_run_process_validates_input_exists` (line 106), `::test_run_process_creates_output_directory` (line 125), `::test_run_process_uses_absolute_paths` (line 152), `::test_run_process_returns_container_exit_code` (line 183), `::test_run_process_with_podman_engine` (line 208), `::test_run_process_with_additional_args` (line 234), `packages/orchestrator/tests/test_container_manager.py::test_run_process_invalid_command_type` (line 109), `::test_run_process_empty_command_name` (line 126), `::test_run_process_permission_error` (line 143)

---

## BHV-0075

- Title: wallpaper-orchestrator `install` command builds the container image with `docker build` (or `podman build`)
- Publicity: public
- Package: orchestrator
- Preconditions: Dockerfile exists in the package; container engine is on PATH
- Steps:
  1. Invoke `wallpaper-process install` (optionally with `--engine podman`)
- Expected output: Calls `docker build` (or `podman build`) with the build command; exits code 0 on success
- Errors/edge cases: Build failure (non-zero exit from build) exits code 1; invalid engine exits code 1; `SubprocessError` exits code 1; unexpected exception exits code 1; Dockerfile not found exits code 1
- Evidence: `packages/orchestrator/tests/test_cli_install.py::test_install_default_engine` (line 14), `::test_install_with_podman` (line 35), `::test_install_build_failure` (line 51), `::test_install_invalid_engine` (line 65), `::test_install_subprocess_error` (line 73), `::test_install_dockerfile_not_found` (line 101)

---

## BHV-0076

- Title: wallpaper-orchestrator `uninstall` command removes the container image via `docker rmi` (or `podman rmi`), with optional confirmation prompt
- Publicity: public
- Package: orchestrator
- Preconditions: Container engine is on PATH
- Steps:
  1. Invoke `wallpaper-process uninstall` (prompts for confirmation) or `wallpaper-process uninstall --yes` (skips prompt)
- Expected output: Calls `docker rmi` (or `podman rmi`); exits code 0 on success; if image does not exist (`returncode=1`, stderr "no such image"), exits code 0 (already removed)
- Errors/edge cases: User cancels prompt → exits code 0 without running rmi; `returncode=1` with non-"no such image" stderr → exits code 1 (permission denied); `SubprocessError` exits code 1; unexpected exception exits code 1; invalid engine exits code 1; `--engine podman` uses `podman` binary
- Evidence: `packages/orchestrator/tests/test_cli_uninstall.py::test_uninstall_with_confirmation` (line 11), `::test_uninstall_cancelled` (line 32), `::test_uninstall_skip_confirmation` (line 46), `::test_uninstall_image_not_found` (line 60), `::test_uninstall_with_podman` (line 74), `::test_uninstall_removal_failure` (line 118), `::test_uninstall_invalid_engine_error` (line 133)

---

## BHV-0077

- Title: wallpaper-orchestrator `install --dry-run` and `uninstall --dry-run` display the build/remove command without executing
- Publicity: public
- Package: orchestrator
- Preconditions: wallpaper-orchestrator CLI is installed
- Steps:
  1. Invoke `wallpaper-process install --dry-run` or `wallpaper-process uninstall --dry-run`
- Expected output:
  - `install --dry-run`: exit 0; output contains "build" and "Dockerfile"; `docker build` is NOT called
  - `uninstall --dry-run`: exit 0; output contains "rmi"; `docker rmi` is NOT called
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_cli_dry_run.py::TestInstallDryRun::test_dry_run_shows_build_command` (line 13), `::test_dry_run_no_image_built` (line 19), `::TestUninstallDryRun::test_dry_run_shows_rmi_command` (line 30), `::test_dry_run_no_image_removed` (line 35)

---

## BHV-0078

- Title: wallpaper-orchestrator `process effect|composite|preset` invokes `ContainerManager.run_process` with correct command type, name, and flat flag
- Publicity: public
- Package: orchestrator
- Preconditions: Container image is available; input file exists; output directory provided or default used from settings
- Steps:
  1. Invoke `wallpaper-process process effect <input> -o <output_dir> --effect blur`
- Expected output:
  - Exit code 0
  - `run_process` is called with `command_type="effect"`, `command_name="blur"`, `flat=False`
  - With `--flat`, `flat=True` is passed
  - Without `-o`, default output dir from settings is used
  - Works for `composite` and `preset` command types identically
- Errors/edge cases: Container missing → `RuntimeError`; input missing → `FileNotFoundError`; `run_process` failure → exit code 1
- Evidence: `packages/orchestrator/tests/test_cli_process.py::test_process_effect_with_output_dir` (line 13), `::test_process_effect_without_output_dir` (line 54), `::test_process_effect_with_flat_flag` (line 90), `::test_process_composite_with_output_dir` (line 170), `::test_process_preset_with_output_dir` (line 316), `::test_process_effect_checks_image_available` (line 467), `::test_process_effect_handles_container_failure` (line 497)

---

## BHV-0079

- Title: wallpaper-orchestrator `process effect|composite|preset --dry-run` shows both the host container command and the inner ImageMagick command without spawning a container
- Publicity: public
- Package: orchestrator
- Preconditions: Container manager is accessible (image does not need to be present for dry-run output)
- Steps:
  1. Invoke `wallpaper-process process effect <input> --effect blur --dry-run`
- Expected output:
  - Exit code 0; no container spawned (`run_process` NOT called)
  - Output contains the host command (`docker run ...` or `podman run ...`)
  - Output contains the inner command (`magick ...`)
  - For `podman` engine, output contains podman-specific flags (e.g., `--userns`)
  - Unknown preset/effect names produce warning output; exit code is still 0
- Errors/edge cases: Unknown preset exits 0 with "cannot resolve" or similar; preset with invalid composite reference exits 0 with warning
- Evidence: `packages/orchestrator/tests/test_cli_dry_run.py::TestProcessEffectContainerDryRun::test_dry_run_shows_both_commands` (line 45), `::test_dry_run_no_container_spawned` (line 74), `::TestProcessCompositeContainerDryRun::test_dry_run_composite_with_podman` (line 130), `::TestProcessPresetContainerDryRun::test_dry_run_unknown_preset` (line 186)

---

## BHV-0080

- Title: wallpaper-orchestrator `OrchestratorDryRun` validates container engine availability and image existence; renders host + inner commands for display
- Publicity: internal
- Package: orchestrator
- Preconditions: `OrchestratorDryRun` is instantiated with a Rich `Console`
- Steps:
  1. Call `dry_run.validate_container(engine=..., image_name=...)`
  2. Call `dry_run.render_container_process(item_name, item_type, input_path, output_path, engine, image_name, host_command, inner_command)`
- Expected output:
  - `validate_container` returns checks including engine found/missing, image available/missing; SubprocessError or FileNotFoundError on image check → check fails (no exception raised)
  - `render_container_process` outputs both "Host" and "Inner" (or "Inside") command labels; both `podman`/`docker` and `magick` appear in output
  - `render_install` shows engine, image name, Dockerfile, and build command
  - `render_uninstall` shows engine and `rmi` command
- Errors/edge cases: `SubprocessError` or `FileNotFoundError` during image check → failing check, not raised exception
- Evidence: `packages/orchestrator/tests/test_dry_run.py::TestContainerValidation::test_validate_engine_found` (line 27), `::test_validate_engine_missing` (line 37), `::test_validate_image_subprocess_error` (line 71), `::TestContainerRenderProcess::test_render_container_process_shows_both_commands` (line 101), `::test_render_install` (line 121), `::test_render_uninstall` (line 134)

---

## BHV-0081

- Title: wallpaper-orchestrator `batch effects|composites|presets|all` delegates to core batch engine via CLI, supporting `--flat`, `--sequential`, and default output directory
- Publicity: public
- Package: orchestrator
- Preconditions: Input image exists; effects config is loaded; ImageMagick is on PATH (used inside container or directly in test)
- Steps:
  1. Invoke `wallpaper-process batch effects <input> -o <output_dir>` (or `composites`, `presets`, `all`)
  2. Optionally add `--flat`, `--sequential`
- Expected output:
  - Exit code 0
  - `batch effects` with `-o`: creates `<output_dir>/<stem>/effects/*.png`
  - `batch effects` without `-o`: uses `core.output.default_dir` from settings
  - `batch effects --flat`: flat structure with files directly in `output_dir/*.png`
  - `batch all`: creates all three type subdirectories
- Errors/edge cases: None documented beyond missing input
- Evidence: `packages/orchestrator/tests/test_cli_integration.py::TestBatchCommands::test_batch_effects_with_output_dir` (line 104), `::test_batch_effects_flat` (line 126), `::test_batch_composites_without_output_uses_default` (line 146), `::test_batch_all_flat` (line 254)

---

## BHV-0082

- Title: wallpaper-orchestrator layered settings supports CLI-level overrides across core and orchestrator namespaces
- Publicity: public
- Package: orchestrator
- Preconditions: `UnifiedConfig` is configured with `configure(UnifiedConfig, ...)`
- Steps:
  1. Call `get_config(overrides={"core.execution.parallel": False, "orchestrator.container.engine": "podman"})`
- Expected output: `config.core.execution.parallel` is `False`; `config.orchestrator.container.engine` is `"podman"`
- Errors/edge cases: None
- Evidence: `packages/orchestrator/tests/test_integration.py::test_config_merges_cli_overrides` (line 31)
