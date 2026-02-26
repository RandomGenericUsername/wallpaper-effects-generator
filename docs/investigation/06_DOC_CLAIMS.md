# Documentation Claims Catalog

<!-- Generated: iteration 0001, phase 5 -->
<!-- Doc files analyzed: 6 -->
<!-- Total claims: 107 | Verified: 75 | Unverified: 32 | Contradicted: 0 -->

Claim IDs: `DOC-0001`, `DOC-0002`, ...

---

## Source: README.md

## DOC-0001

- Text: The project is a wallpaper effects processor with support for effects, composites (effect chains), and presets.
- Source: `README.md:3`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0044, BHV-0047, BHV-0052, BHV-0053

---

## DOC-0002

- Text: The `-o/--output-dir` flag is optional; when omitted, the configured default output directory is used.
- Source: `README.md:10`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0049

---

## DOC-0003

- Text: The `--flat` flag disables type-based subdirectories in output, placing files directly under the stem directory.
- Source: `README.md:11`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0050, BHV-0058

---

## DOC-0004

- Text: The `--dry-run` flag previews what would be executed without running it.
- Source: `README.md:12`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0054

---

## DOC-0005

- Text: Batch processing generates all effects, composites, or presets in parallel.
- Source: `README.md:13`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057, BHV-0063

---

## DOC-0006

- Text: Configuration layers are: Package defaults → project-level → user-level (XDG_CONFIG_HOME).
- Source: `README.md:14`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0025

---

## DOC-0007

- Text: Container support runs processing in Docker or Podman.
- Source: `README.md:15`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0074, BHV-0075

---

## DOC-0008

- Text: Host mode runs ImageMagick directly on the host without a container.
- Source: `README.md:16`
- Category: concept
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0009

- Text: The command `uv sync` installs the project from source.
- Source: `README.md:27`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0010

- Text: The command `uv run wallpaper-core --help` runs wallpaper-core directly.
- Source: `README.md:31`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0011

- Text: The command `uv pip install -e packages/core` installs wallpaper-core as a command.
- Source: `README.md:34`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0012

- Text: The command `uv run wallpaper-process install` builds and installs the container image.
- Source: `README.md:44`
- Category: how-to
- Evidence status: verified
- Evidence pointers: BHV-0075

---

## DOC-0013

- Text: Without specifying output directory, the default output path for `process effect input.jpg --effect blur` is `./wallpapers-output/input/effect/blur.png`.
- Source: `README.md:57`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0047, BHV-0049, BHV-0051

---

## DOC-0014

- Text: With `-o /home/user/outputs`, the output path for `process effect input.jpg --effect blur` is `/home/user/outputs/input/effect/blur.png`.
- Source: `README.md:63`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0047, BHV-0051

---

## DOC-0015

- Text: With `--flat`, the output path for `process effect input.jpg --effect blur` is `./wallpapers-output/input/blur.png` (no `effect/` subdirectory).
- Source: `README.md:69`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0050, BHV-0051

---

## DOC-0016

- Text: `wallpaper-core process composite input.jpg --composite dark --dry-run` shows what will happen before executing.
- Source: `README.md:76`
- Category: how-to
- Evidence status: verified
- Evidence pointers: BHV-0054

---

## DOC-0017

- Text: `wallpaper-core batch all input.jpg --no-parallel` disables parallel batch processing.
- Source: `README.md:109`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057

---

## DOC-0018

- Text: The default output directory is `./wallpapers-output` in the current working directory.
- Source: `README.md:129`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (BHV-0040 states `output.default_dir` default but not the exact string `./wallpapers-output`; test uses `/tmp/wallpaper-effects` as default in test context)

---

## DOC-0019

- Text: Package defaults are loaded from `packages/core/src/wallpaper_core/config/settings.toml`.
- Source: `README.md:135`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040

---

## DOC-0020

- Text: Project-level settings are loaded from `./settings.toml` in the current working directory.
- Source: `README.md:136`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0010, BHV-0025

---

## DOC-0021

- Text: User-level settings are loaded from `$XDG_CONFIG_HOME/wallpaper-effects-generator/settings.toml`.
- Source: `README.md:137`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0011, BHV-0027

---

## DOC-0022

- Text: The config key `core.output.default_dir` sets the default output directory.
- Source: `README.md:139`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040, BHV-0049

---

## DOC-0023

- Text: The default value of `core.output.default_dir` is `./wallpapers-output`.
- Source: `README.md:157`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (BHV-0040 does not specify this string; tests use `/tmp/wallpaper-effects`)

---

## DOC-0024

- Text: The verbosity config key accepts values `"DEBUG"`, `"VERBOSE"`, `"NORMAL"`, and `"QUIET"`.
- Source: `README.md:164`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0041, BHV-0065

---

## DOC-0025

- Text: The config key `core.execution.parallel` controls parallel batch processing (boolean).
- Source: `README.md:167`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040, BHV-0057

---

## DOC-0026

- Text: The config key `core.execution.max_workers` sets the number of parallel workers.
- Source: `README.md:168`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040, BHV-0063

---

## DOC-0027

- Text: The config key `core.processing.temp_dir` sets a custom temporary directory.
- Source: `README.md:172`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0041

---

## DOC-0028

- Text: The user configuration directory on Linux/macOS is `~/.config/wallpaper-effects-generator/settings.toml`.
- Source: `README.md:186`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0027

---

## DOC-0029

- Text: The user configuration directory on Windows is `%APPDATA%\wallpaper-effects-generator\settings.toml`.
- Source: `README.md:189`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0030

- Text: The `-o, --output-dir` flag specifies the output directory for process and batch commands; if omitted, `core.output.default_dir` is used.
- Source: `README.md:208`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0049

---

## DOC-0031

- Text: The `--flat` process flag disables type-based subdirectories in output.
- Source: `README.md:209`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0050

---

## DOC-0032

- Text: The `--dry-run` process flag previews what would be executed without running it.
- Source: `README.md:210`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0054

---

## DOC-0033

- Text: The `--parallel` batch flag enables parallel processing (default: enabled).
- Source: `README.md:224`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057

---

## DOC-0034

- Text: The `--no-parallel` batch flag disables parallel processing.
- Source: `README.md:225`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057

---

## DOC-0035

- Text: The `--strict` batch flag aborts on first error (default: true).
- Source: `README.md:226`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057

---

## DOC-0036

- Text: The `--no-strict` batch flag continues on errors.
- Source: `README.md:227`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0057

---

## DOC-0037

- Text: `wallpaper-process` uses the same command syntax as `wallpaper-core` but runs commands inside a Docker/Podman container.
- Source: `README.md:231`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0078

---

## DOC-0038

- Text: `wallpaper-process install` builds and installs the container image.
- Source: `README.md:243`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0075

---

## DOC-0039

- Text: `wallpaper-process uninstall` removes the container image.
- Source: `README.md:244`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0076

---

## DOC-0040

- Text: With default (hierarchical) output, effects go into `<output>/input/effects/`, composites into `<output>/input/composites/`, presets into `<output>/input/presets/`.
- Source: `README.md:252-265`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0047, BHV-0051, BHV-0052, BHV-0053, BHV-0057

---

## DOC-0041

- Text: With `--flat`, all output files go directly under `<output>/input/` without type subdirectories.
- Source: `README.md:268-280`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0050, BHV-0051, BHV-0058

---

## DOC-0042

- Text: The old positional syntax `wallpaper-core process effect image.jpg -e blur /output` no longer works; the output directory must now use the `-o/--output-dir` flag.
- Source: `README.md:286-298`
- Category: troubleshooting
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0043

- Text: The output directory will be created automatically if it does not exist.
- Source: `README.md:453`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0060

---

## DOC-0044

- Text: The system requires Python 3.12 or later.
- Source: `README.md:413`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0045

- Text: The system requires ImageMagick (`magick` or `convert` command-line tool).
- Source: `README.md:414`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0061

---

## DOC-0046

- Text: Docker or Podman is required only for containerized execution.
- Source: `README.md:415`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0074, BHV-0075

---

## DOC-0047

- Text: The repository is a monorepo with 4 packages: `wallpaper-settings`, `wallpaper-core`, `wallpaper-effects`, and `wallpaper-orchestrator`.
- Source: `README.md:440-446`
- Category: concept
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0048

- Text: The `core.backend.binary` setting specifies the ImageMagick binary path.
- Source: `README.md:395`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040

---

## DOC-0049

- Text: Checking `$XDG_CONFIG_HOME` (should be `~/.config` on Linux/macOS) can diagnose configuration not being loaded.
- Source: `README.md:488`
- Category: troubleshooting
- Evidence status: verified
- Evidence pointers: BHV-0027

---

## DOC-0050

- Text: `wallpaper-process install` must be run before using orchestrator commands.
- Source: `README.md:476-479`
- Category: troubleshooting
- Evidence status: verified
- Evidence pointers: BHV-0074

---

---

## Source: DEVELOPMENT.md

## DOC-0051

- Text: `make dev` installs all development dependencies and pre-commit hooks (first time setup).
- Source: `DEVELOPMENT.md:9`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0052

- Text: `make pipeline` runs the complete validation pipeline (linting, security, tests), simulating GitHub Actions.
- Source: `DEVELOPMENT.md:15`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0053

- Text: `make format` auto-formats all code in all packages using Black, isort, and Ruff.
- Source: `DEVELOPMENT.md:27`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0054

- Text: `make lint` checks for formatting issues, linting problems, and type errors in all packages.
- Source: `DEVELOPMENT.md:38`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0055

- Text: `make test-all` runs all tests with coverage reporting.
- Source: `DEVELOPMENT.md:47`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0056

- Text: Per-package test commands follow the pattern `make test-<package>` (e.g., `make test-settings`, `make test-core`).
- Source: `DEVELOPMENT.md:52`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0057

- Text: `make security` runs Bandit security scanner on all packages.
- Source: `DEVELOPMENT.md:58`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0058

- Text: GitHub Actions CI tests run on Ubuntu and macOS with Python 3.12 and 3.13.
- Source: `DEVELOPMENT.md:157`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0059

- Text: GitHub Actions CI enforces 95% code coverage threshold.
- Source: `DEVELOPMENT.md:159`
- Category: contract
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0060

- Text: `make push` downloads the `act` tool if not present and runs all GitHub Actions workflows in local Docker containers.
- Source: `DEVELOPMENT.md:169-178`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0061

- Text: `make push` automatically captures all output to timestamped log files in the `.logs/` directory.
- Source: `DEVELOPMENT.md:177`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0062

- Text: `make smoke-test` runs 85+ integration test cases directly (without `act`), requiring ImageMagick and Docker/Podman.
- Source: `DEVELOPMENT.md:243`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0063

- Text: Pre-commit hooks run automatically before every commit to catch issues early.
- Source: `DEVELOPMENT.md:101`
- Category: concept
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0064

- Text: Pre-commit hooks include: trailing whitespace, EOF, YAML/JSON/TOML syntax, Black, isort, Ruff, mypy, Bandit, large file detection (>1MB).
- Source: `DEVELOPMENT.md:114-119`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0065

- Text: All tool configurations (Ruff, Black, isort, mypy, Bandit) are identical between pre-commit hooks and GitHub Actions, both using line length 88.
- Source: `DEVELOPMENT.md:310-318`
- Category: contract
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0066

- Text: In tests, `shutil.which("magick")` is mocked to return `/usr/bin/magick` so ImageMagick does not need to be installed for tests to pass.
- Source: `DEVELOPMENT.md:339-350`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0061

---

## DOC-0067

- Text: `make clean` removes `__pycache__`, `.pytest_cache`, `.mypy_cache`, build artifacts, etc.
- Source: `DEVELOPMENT.md:136`
- Category: how-to
- Evidence status: unverified
- Evidence pointers: none found

---

---

## Source: packages/settings/README.md

## DOC-0068

- Text: The `layered-settings` package supports both TOML and YAML configuration file formats.
- Source: `packages/settings/README.md:7`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0001, BHV-0002, BHV-0003

---

## DOC-0069

- Text: `layered-settings` performs Pydantic validation automatically using registered models.
- Source: `packages/settings/README.md:9`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0013, BHV-0017

---

## DOC-0070

- Text: `layered-settings` uses a `SchemaRegistry` to register multiple configuration schemas for different namespaces.
- Source: `packages/settings/README.md:10`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0019, BHV-0020

---

---

## DOC-0071

- Text: `SchemaRegistry.register()` maps a namespace to a Pydantic model and a defaults file path.
- Source: `packages/settings/README.md:41-45`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0019

---

## DOC-0072

- Text: `configure(root_model=AppSettings, app_name="myapp")` must be called once at startup before `get_config()`.
- Source: `packages/settings/README.md:48`
- Category: how-to
- Evidence status: verified
- Evidence pointers: BHV-0022, BHV-0023

---

## DOC-0073

- Text: Configuration layers merge in this order (later overrides earlier): Package defaults → Project root (`./settings.toml`) → User config (`~/.config/<app_name>/settings.toml`) → CLI arguments.
- Source: `packages/settings/README.md:59-63`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0025

---

## DOC-0074

- Text: Package defaults use a flat TOML structure (keys without namespace prefix).
- Source: `packages/settings/README.md:66-71`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0014, BHV-0040

---

## DOC-0075

- Text: Project and user configuration files use a namespaced TOML structure (e.g., `[database]` at top level).
- Source: `packages/settings/README.md:74-80`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0015

---

## DOC-0076

- Text: CLI overrides use dotted path notation, e.g., `get_config(overrides={"database.host": "prod.example.com"})`.
- Source: `packages/settings/README.md:115-119`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0016, BHV-0024

---

## DOC-0077

- Text: CLI overrides are applied with the highest priority and create a fresh configuration instance, bypassing the cache.
- Source: `packages/settings/README.md:122`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0024

---

## DOC-0078

- Text: `get_config()` without arguments returns a cached configuration instance; subsequent calls return the same instance.
- Source: `packages/settings/README.md:228-229`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0023

---

## DOC-0079

- Text: `get_config()` raises `RuntimeError` if `configure()` has not been called first.
- Source: `packages/settings/README.md:223`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0023

---

## DOC-0080

- Text: `get_config()` raises `SettingsValidationError` if configuration validation fails.
- Source: `packages/settings/README.md:224`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0017

---

## DOC-0081

- Text: `get_config()` raises `SettingsFileError` if a configuration file cannot be loaded.
- Source: `packages/settings/README.md:225`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0004

---

## DOC-0082

- Text: `SchemaRegistry.get(namespace)` returns `None` for unregistered namespaces and a `SchemaEntry` for registered ones.
- Source: `packages/settings/README.md:265`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0020

---

## DOC-0083

- Text: `SchemaRegistry.clear()` removes all registrations (primarily for testing).
- Source: `packages/settings/README.md:280`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0021

---

## DOC-0084

- Text: `SettingsFileError` has `filepath` and `reason` attributes.
- Source: `packages/settings/README.md:293-295`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0026

---

## DOC-0085

- Text: `SettingsRegistryError` has `namespace` and `reason` attributes.
- Source: `packages/settings/README.md:300-303`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0026

---

## DOC-0086

- Text: `SettingsValidationError` has `config_name` and `reason` attributes.
- Source: `packages/settings/README.md:308-311`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0026

---

## DOC-0087

- Text: The `layered-settings` test suite includes 143 tests.
- Source: `packages/settings/README.md:413`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (count not directly verifiable from BHV catalog)

---

---

## Source: packages/core/README.md

## DOC-0088

- Text: The `wallpaper-core` package runs effects locally using the system's ImageMagick installation; for containerized execution, use `wallpaper-orchestrator`.
- Source: `packages/core/README.md:3-5`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0047, BHV-0060

---

## DOC-0089

- Text: Effects are defined in `effects.yaml` with layered lookup: package defaults from `packages/core/effects/effects.yaml`, then user effects from `~/.config/wallpaper-effects/effects.yaml`.
- Source: `packages/core/README.md:104-107`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (BHV-0042 references `packages/core/src/wallpaper_core/config/effects.yaml` — path may differ from doc; user path listed as `~/.config/wallpaper-effects/effects.yaml` vs README.md's `~/.config/wallpaper-effects-generator/effects.yaml`)

---

## DOC-0090

- Text: The `core.output.verbosity` setting accepts integer values: `0=QUIET`, `1=NORMAL`, `2=VERBOSE`, `3=DEBUG`.
- Source: `packages/core/README.md:94`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0041, BHV-0065

---

## DOC-0091

- Text: The `core.execution.max_workers` setting of `0` means auto (system-determined worker count).
- Source: `packages/core/README.md:91`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0040

---

## DOC-0092

- Text: The user settings path for `wallpaper-core` is `~/.config/wallpaper-effects/settings.toml`.
- Source: `packages/core/README.md:63`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (BHV-0011 and BHV-0027 use the app name; README.md uses `wallpaper-effects-generator` while packages/core/README.md uses `wallpaper-effects` — possible inconsistency)

---

## DOC-0093

- Text: `CoreSettings` and `EffectsConfig` are both registered with `SchemaRegistry` at import time.
- Source: `packages/core/README.md:131-133`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0038

---

---

## Source: packages/effects/README.md

## DOC-0094

- Text: The `layered-effects` package provides a layered configuration system for `effects.yaml` with deep merging behavior.
- Source: `packages/effects/README.md:7-8`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0033, BHV-0034

---

## DOC-0095

- Text: Effects layer precedence: Package defaults (lowest) → Project root (`{project_root}/effects.yaml`) → User config (highest) at `~/.config/wallpaper-effects-generator/effects.yaml`.
- Source: `packages/effects/README.md:12-15`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0033, BHV-0036

---

## DOC-0096

- Text: Users can override specific effects while inheriting others, and can add new effects not present in package defaults.
- Source: `packages/effects/README.md:34-36`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0036, BHV-0043

---

---

## Source: packages/orchestrator/README.md

## DOC-0097

- Text: The orchestrator provides containerized execution of wallpaper effects with Docker/Podman, bundling ImageMagick inside the container image so it need not be installed on the host.
- Source: `packages/orchestrator/README.md:7-8`
- Category: concept
- Evidence status: verified
- Evidence pointers: BHV-0074

---

## DOC-0098

- Text: `wallpaper-process install --engine podman` builds the container image using Podman instead of Docker.
- Source: `packages/orchestrator/README.md:59`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0075

---

## DOC-0099

- Text: `wallpaper-process uninstall --yes` removes the container image without a confirmation prompt.
- Source: `packages/orchestrator/README.md:65`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0076

---

## DOC-0100

- Text: Orchestrator process commands use the syntax `wallpaper-process process effect input.jpg output.jpg blur` (positional output path and effect name, no `-o` flag).
- Source: `packages/orchestrator/README.md:72-84`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found (BHV-0078 shows `-o output_dir --effect blur` syntax matching wallpaper-core; the positional syntax in orchestrator README may be outdated)

---

## DOC-0101

- Text: When a process command runs, the orchestrator mounts input as `{your-input}:/input/image.jpg:ro` (read-only) and output directory as `{your-output-dir}:/output:rw` (read-write).
- Source: `packages/orchestrator/README.md:107-108`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0072, BHV-0074

---

## DOC-0102

- Text: The container is removed after each execution (`--rm`).
- Source: `packages/orchestrator/README.md:232`
- Category: contract
- Evidence status: verified
- Evidence pointers: BHV-0074

---

## DOC-0103

- Text: The container image runs as non-root user (UID 1000).
- Source: `packages/orchestrator/README.md:231`
- Category: contract
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0104

- Text: The default container engine is Docker; Podman can be configured via `[orchestrator.container] engine = "podman"`.
- Source: `packages/orchestrator/README.md:152-153`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0069, BHV-0070

---

## DOC-0105

- Text: The orchestrator `info` and `version` commands run on the host (no container spawned).
- Source: `packages/orchestrator/README.md:87-93`
- Category: reference
- Evidence status: unverified
- Evidence pointers: none found

---

## DOC-0106

- Text: A custom image registry can be set via `[orchestrator.container] image_registry = "ghcr.io/username"`.
- Source: `packages/orchestrator/README.md:159-160`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0071

---

## DOC-0107

- Text: The default container image name is `wallpaper-effects:latest`.
- Source: `packages/orchestrator/README.md:161`
- Category: reference
- Evidence status: verified
- Evidence pointers: BHV-0069, BHV-0071

---
