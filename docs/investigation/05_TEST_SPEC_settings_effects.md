# TEST_SPEC — settings and effects packages
# BHV range: BHV-0001 to BHV-0036
# Generated: iteration 0001, phase 3

---

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
- Publicity: public
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

# UNKNOWNS
# U-001: packages/effects/tests/test_loader.py::TestEffectsLoader::test_loads_single_file (line 85) — calls the private method `loader._load_yaml_file()` directly; it is unclear whether this private method is part of any documented contract or purely an internal implementation detail accessed only in tests

# SUMMARY
# Total BHVs: 36
# Public: 14  (BHV-0019, BHV-0020, BHV-0022, BHV-0023, BHV-0024, BHV-0025, BHV-0026, BHV-0027, BHV-0028, BHV-0029, BHV-0030, BHV-0031, BHV-0032, BHV-0035, BHV-0036)
# Internal: 22 (BHV-0001 through BHV-0018, BHV-0021, BHV-0033, BHV-0034)
# Last BHV ID used: BHV-0036
