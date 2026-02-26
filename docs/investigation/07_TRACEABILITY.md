# Traceability Matrix

<!-- Generated: iteration 0001, phase 6 -->
<!-- Public BHVs: 38 | DOC claims: 107 -->

---

## BHV → Documentation coverage

Only public BHVs are tracked here (38 total). Internal behaviors are implementation details that do not require documentation coverage.

| BHV ID | Title (short) | Covered by DOC claims | Coverage status |
|---|---|---|---|
| BHV-0019 | SchemaRegistry.register() maps namespace to model | DOC-0071 | covered |
| BHV-0020 | SchemaRegistry.get(), all_namespaces(), all_entries() | DOC-0082 | covered |
| BHV-0022 | configure() stores root model and clears cache | DOC-0072 | covered |
| BHV-0023 | get_config() discovers layers and caches result | DOC-0078, DOC-0079 | covered |
| BHV-0024 | get_config(overrides=...) applies overrides without caching | DOC-0076, DOC-0077 | covered |
| BHV-0025 | Full four-layer priority order enforced end-to-end | DOC-0006, DOC-0073 | covered |
| BHV-0027 | XDG path constants and helper functions | DOC-0021, DOC-0028, DOC-0049 | covered |
| BHV-0028 | Application constants APP_NAME, SETTINGS_FILENAME, EFFECTS_FILENAME | (none) | gap |
| BHV-0029 | DryRunBase renders headers, fields, commands, tables | (none) | gap |
| BHV-0030 | ValidationCheck dataclass for dry-run checks | (none) | gap |
| BHV-0031 | effects.configure() stores paths and clears cache | (none) | gap |
| BHV-0032 | effects.load_effects() loads and caches EffectsConfig | DOC-0094 | partial |
| BHV-0035 | Effects error hierarchy (EffectsLoadError, EffectsValidationError) | (none) | gap |
| BHV-0036 | End-to-end three-layer effects merge produces EffectsConfig | DOC-0095, DOC-0096 | covered |
| BHV-0037 | wallpaper-core CLI app with help, process, batch, show | DOC-0010, DOC-0011 | covered |
| BHV-0038 | wallpaper-core configures layered settings on startup | DOC-0093 | covered |
| BHV-0039 | wallpaper-core merges CLI overrides onto package defaults | DOC-0006, DOC-0073 | partial |
| BHV-0043 | wallpaper-core layered-effects merges package/project/user layers | DOC-0089, DOC-0096 | partial |
| BHV-0044 | wallpaper-core show effects/composites/presets/all | DOC-0001 | covered |
| BHV-0045 | wallpaper-core info command displays settings and effects count | (none) | gap |
| BHV-0046 | wallpaper-core version command prints version string | (none) | gap |
| BHV-0047 | wallpaper-core process effect with hierarchical output path | DOC-0013, DOC-0014, DOC-0088 | covered |
| BHV-0048 | wallpaper-core process effect accepts per-effect CLI parameters | (none) | gap |
| BHV-0049 | wallpaper-core uses default output dir from settings when -o omitted | DOC-0002, DOC-0022, DOC-0030 | covered |
| BHV-0050 | wallpaper-core process --flat uses flat output directory structure | DOC-0003, DOC-0015, DOC-0031, DOC-0041 | covered |
| BHV-0052 | wallpaper-core process composite chains effects and writes output | DOC-0001, DOC-0040 | covered |
| BHV-0053 | wallpaper-core process preset applies named preset | DOC-0001, DOC-0040 | covered |
| BHV-0054 | wallpaper-core process --dry-run shows commands without executing | DOC-0004, DOC-0016, DOC-0032 | covered |
| BHV-0057 | wallpaper-core batch runs all items in parallel or sequential | DOC-0005, DOC-0017, DOC-0033, DOC-0034, DOC-0035, DOC-0036, DOC-0040 | covered |
| BHV-0058 | wallpaper-core batch --flat writes outputs without type subdirs | DOC-0003, DOC-0041 | covered |
| BHV-0059 | wallpaper-core batch --dry-run lists all planned commands | DOC-0004 | partial |
| BHV-0065 | wallpaper-core verbosity flags (-q, -v, -vv) | DOC-0024, DOC-0090 | covered |
| BHV-0067 | wallpaper-orchestrator CLI exposes install/uninstall/process/batch/show | DOC-0007, DOC-0037 | covered |
| BHV-0068 | wallpaper-orchestrator configures settings with core/effects/orchestrator namespaces | (none) | gap |
| BHV-0071 | ContainerManager constructs image name with optional registry prefix | DOC-0106, DOC-0107 | covered |
| BHV-0074 | ContainerManager.run_process builds and runs docker run | DOC-0007, DOC-0046, DOC-0050, DOC-0097, DOC-0101, DOC-0102 | covered |
| BHV-0075 | wallpaper-process install builds container image | DOC-0012, DOC-0038, DOC-0098 | covered |
| BHV-0076 | wallpaper-process uninstall removes container image | DOC-0039, DOC-0099 | covered |
| BHV-0077 | wallpaper-process install/uninstall --dry-run shows command only | (none) | gap |
| BHV-0078 | wallpaper-orchestrator process command invokes ContainerManager | DOC-0037, DOC-0100 | partial |
| BHV-0079 | wallpaper-orchestrator process --dry-run shows host+inner commands | (none) | gap |
| BHV-0081 | wallpaper-orchestrator batch delegates to core batch engine | DOC-0005 | partial |
| BHV-0082 | wallpaper-orchestrator layered settings supports CLI overrides | DOC-0006 | partial |

---

## DOC → Evidence

| DOC ID | Claim summary (brief) | Evidence | Evidence status |
|---|---|---|---|
| DOC-0001 | Project processes images with effects, composites, and presets | BHV-0044, BHV-0047, BHV-0052, BHV-0053 | verified |
| DOC-0002 | `-o/--output-dir` flag is optional; omitting uses configured default | BHV-0049 | verified |
| DOC-0003 | `--flat` disables type-based subdirectories in output | BHV-0050, BHV-0058 | verified |
| DOC-0004 | `--dry-run` previews execution without running | BHV-0054 | verified |
| DOC-0005 | Batch processing runs in parallel | BHV-0057, BHV-0063 | verified |
| DOC-0006 | Config layers: Package defaults → project-level → user-level (XDG) | BHV-0025 | verified |
| DOC-0007 | Container support runs processing in Docker or Podman | BHV-0074, BHV-0075 | verified |
| DOC-0008 | Host mode runs ImageMagick directly without a container | none found | unverified |
| DOC-0009 | `uv sync` installs the project from source | none found | unverified |
| DOC-0010 | `uv run wallpaper-core --help` runs wallpaper-core | none found | unverified |
| DOC-0011 | `uv pip install -e packages/core` installs wallpaper-core | none found | unverified |
| DOC-0012 | `uv run wallpaper-process install` builds and installs container image | BHV-0075 | verified |
| DOC-0013 | Default output path for `process effect input.jpg --effect blur` is `./wallpapers-output/input/effect/blur.png` | BHV-0047, BHV-0049, BHV-0051 | verified |
| DOC-0014 | With `-o /home/user/outputs`, output is `/home/user/outputs/input/effect/blur.png` | BHV-0047, BHV-0051 | verified |
| DOC-0015 | With `--flat`, output is `./wallpapers-output/input/blur.png` (no `effect/` subdir) | BHV-0050, BHV-0051 | verified |
| DOC-0016 | `wallpaper-core process composite input.jpg --composite dark --dry-run` shows what will happen | BHV-0054 | verified |
| DOC-0017 | `wallpaper-core batch all input.jpg --no-parallel` disables parallel batch | BHV-0057 | verified |
| DOC-0018 | Default output directory is `./wallpapers-output` in CWD | none found | unverified |
| DOC-0019 | Package defaults loaded from `packages/core/src/wallpaper_core/config/settings.toml` | BHV-0040 | verified |
| DOC-0020 | Project-level settings loaded from `./settings.toml` | BHV-0010, BHV-0025 | verified |
| DOC-0021 | User-level settings from `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml` | BHV-0011, BHV-0027 | verified |
| DOC-0022 | Config key `core.output.default_dir` sets the default output directory | BHV-0040, BHV-0049 | verified |
| DOC-0023 | Default value of `core.output.default_dir` is `./wallpapers-output` | none found | unverified |
| DOC-0024 | Verbosity config key accepts `"DEBUG"`, `"VERBOSE"`, `"NORMAL"`, `"QUIET"` | BHV-0041, BHV-0065 | verified |
| DOC-0025 | Config key `core.execution.parallel` controls parallel batch (boolean) | BHV-0040, BHV-0057 | verified |
| DOC-0026 | Config key `core.execution.max_workers` sets number of parallel workers | BHV-0040, BHV-0063 | verified |
| DOC-0027 | Config key `core.processing.temp_dir` sets custom temporary directory | BHV-0041 | verified |
| DOC-0028 | User config on Linux/macOS is `~/.config/wallpaper-effects-generator/settings.toml` | BHV-0027 | verified |
| DOC-0029 | User config on Windows is `%APPDATA%\wallpaper-effects-generator\settings.toml` | none found | unverified |
| DOC-0030 | `-o, --output-dir` flag specifies output directory; omitting uses `core.output.default_dir` | BHV-0049 | verified |
| DOC-0031 | `--flat` process flag disables type-based subdirectories in output | BHV-0050 | verified |
| DOC-0032 | `--dry-run` process flag previews execution without running | BHV-0054 | verified |
| DOC-0033 | `--parallel` batch flag enables parallel processing (default: enabled) | BHV-0057 | verified |
| DOC-0034 | `--no-parallel` batch flag disables parallel processing | BHV-0057 | verified |
| DOC-0035 | `--strict` batch flag aborts on first error (default: true) | BHV-0057 | verified |
| DOC-0036 | `--no-strict` batch flag continues on errors | BHV-0057 | verified |
| DOC-0037 | `wallpaper-process` uses same syntax as `wallpaper-core` but runs in container | BHV-0078 | verified |
| DOC-0038 | `wallpaper-process install` builds and installs container image | BHV-0075 | verified |
| DOC-0039 | `wallpaper-process uninstall` removes container image | BHV-0076 | verified |
| DOC-0040 | Hierarchical output: effects → `effects/`, composites → `composites/`, presets → `presets/` | BHV-0047, BHV-0051, BHV-0052, BHV-0053, BHV-0057 | verified |
| DOC-0041 | With `--flat`, all output under `<output>/input/` without type subdirs | BHV-0050, BHV-0051, BHV-0058 | verified |
| DOC-0042 | Old positional syntax `wallpaper-core process effect image.jpg -e blur /output` no longer works | none found | unverified |
| DOC-0043 | Output directory will be created automatically if it does not exist | BHV-0060 | verified |
| DOC-0044 | System requires Python 3.12 or later | none found | unverified |
| DOC-0045 | System requires ImageMagick (`magick` or `convert`) | BHV-0061 | verified |
| DOC-0046 | Docker or Podman required only for containerized execution | BHV-0074, BHV-0075 | verified |
| DOC-0047 | Repository is a monorepo with 4 packages | none found | unverified |
| DOC-0048 | `core.backend.binary` setting specifies ImageMagick binary path | BHV-0040 | verified |
| DOC-0049 | Checking `$XDG_CONFIG_HOME` diagnoses config not loading | BHV-0027 | verified |
| DOC-0050 | `wallpaper-process install` must be run before using orchestrator commands | BHV-0074 | verified |
| DOC-0051 | `make dev` installs dev dependencies and pre-commit hooks | none found | unverified |
| DOC-0052 | `make pipeline` runs full validation pipeline | none found | unverified |
| DOC-0053 | `make format` auto-formats all code with Black, isort, and Ruff | none found | unverified |
| DOC-0054 | `make lint` checks formatting, linting, and type errors | none found | unverified |
| DOC-0055 | `make test-all` runs all tests with coverage reporting | none found | unverified |
| DOC-0056 | Per-package test commands follow `make test-<package>` pattern | none found | unverified |
| DOC-0057 | `make security` runs Bandit security scanner | none found | unverified |
| DOC-0058 | GitHub Actions CI tests on Ubuntu and macOS with Python 3.12 and 3.13 | none found | unverified |
| DOC-0059 | GitHub Actions CI enforces 95% code coverage | none found | unverified |
| DOC-0060 | `make push` downloads `act` and runs GitHub Actions workflows locally | none found | unverified |
| DOC-0061 | `make push` captures output to timestamped log files in `.logs/` | none found | unverified |
| DOC-0062 | `make smoke-test` runs 85+ integration test cases | none found | unverified |
| DOC-0063 | Pre-commit hooks run automatically before every commit | none found | unverified |
| DOC-0064 | Pre-commit hooks include trailing whitespace, EOF, YAML/JSON/TOML, Black, isort, Ruff, mypy, Bandit, large file | none found | unverified |
| DOC-0065 | All tool configs identical between pre-commit hooks and GitHub Actions (line length 88) | none found | unverified |
| DOC-0066 | In tests, `shutil.which("magick")` is mocked so ImageMagick need not be installed | BHV-0061 | verified |
| DOC-0067 | `make clean` removes `__pycache__`, `.pytest_cache`, `.mypy_cache`, build artifacts | none found | unverified |
| DOC-0068 | `layered-settings` supports both TOML and YAML configuration formats | BHV-0001, BHV-0002, BHV-0003 | verified |
| DOC-0069 | `layered-settings` performs Pydantic validation using registered models | BHV-0013, BHV-0017 | verified |
| DOC-0070 | `layered-settings` uses `SchemaRegistry` to register multiple schemas | BHV-0019, BHV-0020 | verified |
| DOC-0071 | `SchemaRegistry.register()` maps namespace to model and defaults file | BHV-0019 | verified |
| DOC-0072 | `configure(root_model=..., app_name=...)` must be called once at startup | BHV-0022, BHV-0023 | verified |
| DOC-0073 | Config layers merge: Package defaults → Project root → User config → CLI args | BHV-0025 | verified |
| DOC-0074 | Package defaults use flat TOML structure (keys without namespace prefix) | BHV-0014, BHV-0040 | verified |
| DOC-0075 | Project and user config files use namespaced TOML structure | BHV-0015 | verified |
| DOC-0076 | CLI overrides use dotted path notation | BHV-0016, BHV-0024 | verified |
| DOC-0077 | CLI overrides are applied at highest priority and bypass the cache | BHV-0024 | verified |
| DOC-0078 | `get_config()` without arguments returns cached instance | BHV-0023 | verified |
| DOC-0079 | `get_config()` raises `RuntimeError` if `configure()` not called first | BHV-0023 | verified |
| DOC-0080 | `get_config()` raises `SettingsValidationError` on validation failure | BHV-0017 | verified |
| DOC-0081 | `get_config()` raises `SettingsFileError` if config file cannot be loaded | BHV-0004 | verified |
| DOC-0082 | `SchemaRegistry.get(namespace)` returns `None` for unregistered namespaces | BHV-0020 | verified |
| DOC-0083 | `SchemaRegistry.clear()` removes all registrations (for testing) | BHV-0021 | verified |
| DOC-0084 | `SettingsFileError` has `filepath` and `reason` attributes | BHV-0026 | verified |
| DOC-0085 | `SettingsRegistryError` has `namespace` and `reason` attributes | BHV-0026 | verified |
| DOC-0086 | `SettingsValidationError` has `config_name` and `reason` attributes | BHV-0026 | verified |
| DOC-0087 | `layered-settings` test suite includes 143 tests | none found | unverified |
| DOC-0088 | `wallpaper-core` runs effects locally; use `wallpaper-orchestrator` for containers | BHV-0047, BHV-0060 | verified |
| DOC-0089 | Effects defined in `effects.yaml` with layered lookup from package and user paths | none found | unverified |
| DOC-0090 | `core.output.verbosity` accepts integer values: 0=QUIET, 1=NORMAL, 2=VERBOSE, 3=DEBUG | BHV-0041, BHV-0065 | verified |
| DOC-0091 | `core.execution.max_workers` of `0` means auto (system-determined) | BHV-0040 | verified |
| DOC-0092 | User settings path for wallpaper-core is `~/.config/wallpaper-effects/settings.toml` | none found | unverified |
| DOC-0093 | `CoreSettings` and `EffectsConfig` both registered with `SchemaRegistry` at import | BHV-0038 | verified |
| DOC-0094 | `layered-effects` package provides layered config system for `effects.yaml` with deep merging | BHV-0033, BHV-0034 | verified |
| DOC-0095 | Effects layer precedence: Package defaults → Project root → User config | BHV-0033, BHV-0036 | verified |
| DOC-0096 | Users can override specific effects while inheriting others; can add new effects | BHV-0036, BHV-0043 | verified |
| DOC-0097 | Orchestrator provides containerized execution, bundling ImageMagick in container image | BHV-0074 | verified |
| DOC-0098 | `wallpaper-process install --engine podman` builds image using Podman | BHV-0075 | verified |
| DOC-0099 | `wallpaper-process uninstall --yes` removes image without confirmation prompt | BHV-0076 | verified |
| DOC-0100 | Orchestrator process commands use positional syntax (no `-o` flag) | none found | unverified |
| DOC-0101 | Orchestrator mounts input as `{input}:/input/image.jpg:ro` and output as `{output}:/output:rw` | BHV-0072, BHV-0074 | verified |
| DOC-0102 | Container is removed after each execution (`--rm`) | BHV-0074 | verified |
| DOC-0103 | Container image runs as non-root user (UID 1000) | none found | unverified |
| DOC-0104 | Default container engine is Docker; Podman configurable via `[orchestrator.container]` | BHV-0069, BHV-0070 | verified |
| DOC-0105 | Orchestrator `info` and `version` commands run on host (no container spawned) | none found | unverified |
| DOC-0106 | Custom image registry set via `[orchestrator.container] image_registry = "..."` | BHV-0071 | verified |
| DOC-0107 | Default container image name is `wallpaper-effects:latest` | BHV-0069, BHV-0071 | verified |
