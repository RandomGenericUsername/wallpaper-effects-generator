# Findings (Prioritized)

<!-- Generated: iteration 0001, phase 7 -->
<!-- S0: 3 | S1: 6 | S2: 12 | S3: 0 -->

---

## S0 — Critical

Critical findings represent doc claims that are actively wrong — wrong command syntax, wrong path, wrong value — that would cause a user to fail if they followed the documentation.

---

### F-0001

- Summary: `packages/orchestrator/README.md` documents positional command syntax for `wallpaper-process process effect/composite/preset` that does not exist. The actual CLI requires named flags (`--effect`, `--composite`, `--preset`, `-o`). A user who follows the documented syntax will receive a CLI error and cannot run any process command.
- Location: `packages/orchestrator/README.md:72-84`
- Evidence: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:54-70` (confirmed: `effect` is `typer.Option("--effect", ...)`, `output_dir` is `typer.Option("-o", "--output-dir", ...)`); BHV-0078 states "flag-based syntax matching wallpaper-core"; DOC-0100 claims positional syntax `wallpaper-process process effect input.jpg output.jpg blur`
- Proposed fix: Replace the three process command examples in `packages/orchestrator/README.md:72-84` with:
  ```bash
  # Apply single effect
  wallpaper-process process effect input.jpg --effect blur
  wallpaper-process process effect input.jpg --effect blur -o /path/to/output

  # Apply composite
  wallpaper-process process composite input.jpg --composite dark
  wallpaper-process process composite input.jpg --composite dark -o /path/to/output

  # Apply preset
  wallpaper-process process preset input.jpg --preset dark_vibrant
  wallpaper-process process preset input.jpg --preset dark_vibrant -o /path/to/output
  ```
- Status: resolved
- Resolution: Replaced all positional-syntax command examples in packages/orchestrator/README.md (Quick Start, Commands, and Architecture sections) with correct flag-based syntax using --effect, --composite, --preset, and -o flags.

---

### F-0002

- Summary: `packages/core/README.md` states the user settings path is `~/.config/wallpaper-effects/settings.toml`. The actual application name constant is `wallpaper-effects-generator`, making the correct path `~/.config/wallpaper-effects-generator/settings.toml`. A user following this path would look in the wrong directory and conclude their settings file is not being loaded when it is, or create a file at the wrong path that is silently ignored.
- Location: `packages/core/README.md:63`
- Evidence: `packages/settings/src/layered_settings/constants.py:7` (`APP_NAME = "wallpaper-effects-generator"`); `packages/settings/src/layered_settings/paths.py:32-36` (`USER_CONFIG_DIR = XDG_CONFIG_HOME / APP_NAME`, comment confirms `~/.config/wallpaper-effects-generator/`); BHV-0027 (XDG path uses `APP_NAME`); DOC-0028 (root README correctly uses `wallpaper-effects-generator`); DOC-0092 claims `wallpaper-effects` (wrong)
- Proposed fix: Change `packages/core/README.md:63` from:
  ```
  ~/.config/wallpaper-effects/settings.toml
  ```
  to:
  ```
  ~/.config/wallpaper-effects-generator/settings.toml
  ```
- Status: resolved
- Resolution: Replaced wallpaper-effects with wallpaper-effects-generator in both user settings path references in packages/core/README.md (Layer Priority list and settings format comment).

---

### F-0003

- Summary: Root `README.md` (DOC-0018, DOC-0023) claims the default output directory is `./wallpapers-output` in the current working directory. The actual package default in `packages/core/src/wallpaper_core/config/settings.toml` is `/tmp/wallpaper-effects`. A user who omits `-o` and expects output in `./wallpapers-output` will not find their files there.
- Location: `README.md:129` (DOC-0018), `README.md:157` (DOC-0023)
- Evidence: `packages/core/src/wallpaper_core/config/settings.toml:12` (`default_dir = "/tmp/wallpaper-effects"`); DOC-0018 claims `./wallpapers-output`; DOC-0023 claims default is `./wallpapers-output`; tests (BHV-0049 preconditions) note default is `/tmp/wallpaper-effects`
- Proposed fix: Update `README.md:129` and `README.md:157` to replace `./wallpapers-output` with `/tmp/wallpaper-effects`. Also update any example output paths (e.g., DOC-0013 shows `./wallpapers-output/input/effect/blur.png`) that use `./wallpapers-output` as the default, since the true default output base is `/tmp/wallpaper-effects`.
- Status: resolved
- Resolution: Replaced all occurrences of ./wallpapers-output with /tmp/wallpaper-effects in README.md, including the default_dir description, the "Default value" note, example output paths, output structure diagrams, and the Basic Workflow ls example.

---

## S1 — Major

Major findings represent public user-facing behaviors that have no documentation at all.

---

### F-0004

- Summary: The `wallpaper-core info` command (and its orchestrator equivalent `wallpaper-process info`) is undocumented. Users have no way to discover this diagnostic command which displays current settings and effects count.
- Location: No documentation exists for this command
- Evidence: BHV-0045 (`wallpaper-core info` exists, tested in `packages/core/tests/test_cli.py::TestInfoCommand`, exit 0, shows "Core Settings" and effects count); the `wallpaper-process info` delegate is confirmed in `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:613-618`; neither `README.md` nor `packages/core/README.md` nor `packages/orchestrator/README.md` documents this command
- Proposed fix: Add `info` command to the CLI reference section of `README.md` and `packages/core/README.md` / `packages/orchestrator/README.md`. Document: displays current core settings (verbosity, parallel, output dir, backend binary) and the count of available effects/composites/presets.

---

### F-0005

- Summary: The `wallpaper-core version` command (and its orchestrator equivalent `wallpaper-process version`) is undocumented. Users cannot discover how to check the installed version.
- Location: No documentation exists for this command
- Evidence: BHV-0046 (`wallpaper-core version` tested in `packages/core/tests/test_cli.py::TestMainCLI::test_version`, exit 0, output contains "wallpaper-effects"); `wallpaper-process version` confirmed in `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:621-626`; command is absent from all doc files
- Proposed fix: Add `version` command to the CLI reference in `README.md` and per-package READMEs. Document that it prints the version string (e.g., `wallpaper-effects vX.Y.Z`).

---

### F-0006

- Summary: Per-effect CLI parameter overrides (e.g., `--blur 0x10`) are completely undocumented. This is a key user-facing feature: users can pass effect-specific flags to override default parameter values at the command line.
- Location: No documentation exists for per-effect CLI parameters
- Evidence: BHV-0048 (`wallpaper-core process effect <input> -e blur --blur 0x10` tested in `packages/core/tests/test_cli.py::TestProcessCommands::test_process_effect_with_params`; the override is substituted for `$BLUR` in the effect command); no mention of per-effect parameters anywhere in `README.md` or any package README
- Proposed fix: Add a section to `README.md` and `packages/core/README.md` explaining that effects expose named CLI flags corresponding to their configurable parameters. Show a concrete example: `wallpaper-core process effect input.jpg -e blur --blur 0x10`.

---

### F-0007

- Summary: `wallpaper-process install --dry-run` and `wallpaper-process uninstall --dry-run` are undocumented. Users cannot discover that they can preview container image build/removal commands before executing them.
- Location: No documentation exists for install/uninstall dry-run
- Evidence: BHV-0077 (tested in `packages/orchestrator/tests/test_cli_dry_run.py::TestInstallDryRun` and `::TestUninstallDryRun`; `install --dry-run` shows build command with Dockerfile, `uninstall --dry-run` shows rmi command; neither docker command is executed); `--dry-run` is mentioned only for `process` commands in existing docs
- Proposed fix: Add `--dry-run` flag documentation to the `wallpaper-process install` and `wallpaper-process uninstall` command descriptions in `packages/orchestrator/README.md` and `README.md`.

---

### F-0008

- Summary: `wallpaper-process process <effect|composite|preset> --dry-run` is completely undocumented for the orchestrator. Users cannot discover that they can preview both the host Docker/Podman command AND the inner ImageMagick command without spawning a container.
- Location: No documentation exists for orchestrator process dry-run
- Evidence: BHV-0079 (tested in `packages/orchestrator/tests/test_cli_dry_run.py::TestProcessEffectContainerDryRun`, `::TestProcessCompositeContainerDryRun`, `::TestProcessPresetContainerDryRun`; output contains both the host `docker run ...` command and the inner `magick ...` command; no container is spawned); `--dry-run` for `wallpaper-core process` is documented (DOC-0004, DOC-0016, DOC-0032) but its orchestrator equivalent is absent
- Proposed fix: Add a `--dry-run` section to the process commands documentation in `packages/orchestrator/README.md`, noting that it shows both the host container command (with volume mounts) and the inner ImageMagick command that will be executed inside the container.

---

### F-0009

- Summary: The fact that `wallpaper-orchestrator` configures layered settings with three namespaces (`core`, `effects`, `orchestrator`) at startup — and that users can place orchestrator-specific config under `[orchestrator.container]` in any settings file — is not documented at a conceptual level for users trying to understand where to put their config.
- Location: `packages/orchestrator/README.md` (no startup config section)
- Evidence: BHV-0068 (tested in `packages/orchestrator/tests/test_integration.py::test_unified_config_loads_all_schemas` and `test_cli_bootstrap.py::test_cli_configures_layered_settings`; `configure(UnifiedConfig, app_name="wallpaper-effects")` called at import; unified config has `.core`, `.effects`, `.orchestrator` namespaces); DOC-0104 mentions `[orchestrator.container]` section but there is no explanation that orchestrator reads the same layered settings files as core, with orchestrator-specific config under the `orchestrator` namespace
- Proposed fix: Add a configuration section to `packages/orchestrator/README.md` explaining that `wallpaper-orchestrator` reads the same layered settings files as `wallpaper-core` (package defaults, `./settings.toml`, `~/.config/wallpaper-effects-generator/settings.toml`) and adds an `[orchestrator]` namespace for container settings.

---

## S2 — Moderate

Moderate findings represent behaviors that are partially documented, public API that is undocumented for developers, or unverified claims that are plausibly wrong or ambiguous.

---

### F-0010

- Summary: BHV-0039 (partial): `wallpaper-core` CLI overrides applied at highest priority are documented conceptually (DOC-0006, DOC-0073) but the specific flags that translate to config overrides (how `-q`/`-v`/`-vv` map to the `core.output.verbosity` setting, or how `--no-parallel` maps to `core.execution.parallel`) are not documented as config-layer overrides.
- Location: `README.md` (config layers section), `packages/core/README.md`
- Evidence: BHV-0039 (tested: CLI flags merge as highest-priority layer over package defaults); DOC-0006 and DOC-0073 mention "CLI arguments" as the top layer but do not explain which flags are overrides vs. standalone flags
- Proposed fix: Add a note to the configuration layers documentation clarifying which CLI flags function as config overrides (e.g., `--no-parallel` overrides `core.execution.parallel`, verbosity flags override `core.output.verbosity`).

---

### F-0011

- Summary: BHV-0043 (partial): The `effects.yaml` path for the user layer is documented inconsistently. `packages/core/README.md:104-107` states user effects are at `~/.config/wallpaper-effects/effects.yaml`, while `packages/effects/README.md:15` correctly states `~/.config/wallpaper-effects-generator/effects.yaml`. The actual path (from `paths.py`) is `~/.config/wallpaper-effects-generator/effects.yaml`.
- Location: `packages/core/README.md:104-107` (DOC-0089)
- Evidence: `packages/settings/src/layered_settings/paths.py:38-39` (`USER_EFFECTS_FILE = USER_CONFIG_DIR / EFFECTS_FILENAME` where `USER_CONFIG_DIR = XDG_CONFIG_HOME / APP_NAME` and `APP_NAME = "wallpaper-effects-generator"`); DOC-0095 (packages/effects/README.md) correctly uses `wallpaper-effects-generator`; DOC-0089 (packages/core/README.md) uses `wallpaper-effects` (wrong)
- Proposed fix: Update `packages/core/README.md:104-107` to use `~/.config/wallpaper-effects-generator/effects.yaml` for the user effects path. Also verify and update the package effects path (`packages/core/effects/effects.yaml` vs. `packages/core/src/wallpaper_core/config/effects.yaml`).

---

### F-0012

- Summary: BHV-0059 (partial): `wallpaper-core batch --dry-run` is only partially documented. DOC-0004 mentions `--dry-run` for process commands; it is verified for batch (BHV-0059) but no documentation explicitly describes batch dry-run behavior (listing all planned commands for every effect/composite/preset in the batch).
- Location: `README.md` (batch section)
- Evidence: BHV-0059 (tested: `wallpaper-core batch all input.jpg --dry-run` lists all planned commands; covered only by DOC-0004 which is a general statement about `--dry-run`)
- Proposed fix: Add an explicit example to the batch command documentation showing `wallpaper-core batch all input.jpg --dry-run` and describe that it lists the planned commands for all batch items without executing them.

---

### F-0013

- Summary: BHV-0078 (partial): BHV-0078 partially covers DOC-0100 but the process command documentation in `packages/orchestrator/README.md` is simultaneously wrong (S0-F-0001 above) AND missing the `-o/--output-dir` flag, `--flat`, and `--dry-run` options that are available to process commands in the orchestrator.
- Location: `packages/orchestrator/README.md:68-84`
- Evidence: `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:54-76` (confirmed: `--flat`, `--dry-run`, `-o/--output-dir` flags exist on all process subcommands); none of these flags appear in the current orchestrator README process section
- Proposed fix: After fixing S0-F-0001, extend the process command examples to show `--flat` and `--dry-run` flags alongside the corrected flag syntax.

---

### F-0014

- Summary: BHV-0081 (partial): `wallpaper-orchestrator batch` delegates to the core batch engine and runs on the host (not in the container), but this distinction is not documented. Users may incorrectly assume batch runs in the container.
- Location: `packages/orchestrator/README.md` (batch section absent)
- Evidence: BHV-0081 (tested: orchestrator batch delegates to core batch engine; covered only by DOC-0005 which does not specify host vs. container execution context); `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py:564-568` (batch help text: "Batch generate effects (runs on host)")
- Proposed fix: Add a note in the orchestrator documentation clarifying that `wallpaper-process batch` runs on the host (like `wallpaper-core batch`) and does not invoke the container for batch operations.

---

### F-0015

- Summary: BHV-0082 (partial): Orchestrator-specific CLI overrides for layered settings (e.g., passing config overrides on the command line to the orchestrator) are not documented. DOC-0006 covers the general layers concept but not orchestrator-specific override syntax.
- Location: `packages/orchestrator/README.md`
- Evidence: BHV-0082 (tested: `wallpaper-orchestrator layered settings supports CLI overrides`; covered only by DOC-0006 which is a general concept claim)
- Proposed fix: Add a note to the orchestrator configuration section that CLI config overrides work the same way as for `wallpaper-core`, using dotted-path notation.

---

### F-0016

- Summary: BHV-0028 (gap, developer API): The application constants `APP_NAME`, `SETTINGS_FILENAME`, and `EFFECTS_FILENAME` are public exports of `layered_settings.constants` but are not documented in `packages/settings/README.md`. Downstream package authors who extend the library need to know these constants.
- Location: `packages/settings/README.md`
- Evidence: BHV-0028 (`packages/settings/tests/test_constants.py::test_app_name_constant`, `::test_settings_filename_constant`, `::test_effects_filename_constant`; constants are in a public module); no corresponding DOC claim
- Proposed fix: Add a constants reference section to `packages/settings/README.md` listing `APP_NAME`, `SETTINGS_FILENAME`, and `EFFECTS_FILENAME` with their values and purpose.

---

### F-0017

- Summary: BHV-0029 (gap, developer API): `DryRunBase` — the base class for implementing dry-run display — is a public API of `layered_settings` but is completely undocumented. Downstream packages (core, orchestrator) subclass it; library users who want custom dry-run renderers cannot discover this API.
- Location: `packages/settings/README.md`
- Evidence: BHV-0029 (`packages/settings/tests/test_dry_run.py::TestDryRunBaseRendering`; `DryRunBase` is public, subclassed by `CoreDryRun` and `OrchestratorDryRun`); no DOC claim covers this class
- Proposed fix: Add a `DryRunBase` API reference section to `packages/settings/README.md` documenting the available render methods (`render_header`, `render_field`, `render_command`, `render_validation`, `render_table`, `render_commands_list`).

---

### F-0018

- Summary: BHV-0030 (gap, developer API): `ValidationCheck` dataclass is a public API used to represent check results in dry-run output but is undocumented.
- Location: `packages/settings/README.md`
- Evidence: BHV-0030 (`packages/settings/tests/test_dry_run.py::TestValidationCheck`; `ValidationCheck(name, passed, detail="")` is public); no DOC claim covers this type
- Proposed fix: Add `ValidationCheck` to the dry-run API documentation in `packages/settings/README.md`, noting its fields: `name` (str), `passed` (bool), `detail` (str, optional, default `""`).

---

### F-0019

- Summary: BHV-0031 (gap, developer API): `effects.configure()` from `layered_effects` is a public setup function that must be called at startup before `load_effects()`, analogous to `configure()` in `layered_settings`. It is not documented in `packages/effects/README.md`.
- Location: `packages/effects/README.md`
- Evidence: BHV-0031 (`packages/effects/tests/test_api.py::test_configure_stores_settings`; signature: `configure(package_effects_file, project_root=None, user_effects_file=None)`); `packages/effects/README.md` documents `load_effects()` (DOC-0094) but not `configure()`
- Proposed fix: Add a `configure()` reference to `packages/effects/README.md` documenting the function signature, when it must be called, which parameters are required vs. optional, and that calling it again clears the `load_effects()` cache.

---

### F-0020

- Summary: BHV-0035 (gap, developer API): The `layered_effects` error hierarchy (`EffectsError`, `EffectsLoadError`, `EffectsValidationError`) is public API used for error handling but is not documented in `packages/effects/README.md`.
- Location: `packages/effects/README.md`
- Evidence: BHV-0035 (`packages/effects/tests/test_errors.py`; `EffectsLoadError` has `file_path` and `reason`; `EffectsValidationError` has `message` and `layer`; all catchable as `EffectsError`); no DOC claim references this error hierarchy
- Proposed fix: Add an error reference section to `packages/effects/README.md` documenting `EffectsError` (base), `EffectsLoadError` (attributes: `file_path`, `reason`), and `EffectsValidationError` (attributes: `message`, `layer`), mirroring the style of the `layered_settings` error documentation.

---

### F-0021

- Summary: BHV-0032 (partial): `effects.load_effects()` is documented conceptually (DOC-0094) but the function signature, return type, and caching semantics (that it caches and returns the same instance on repeat calls, cleared by `configure()`) are not documented.
- Location: `packages/effects/README.md`
- Evidence: BHV-0032 (`packages/effects/tests/test_api.py`; `load_effects()` returns `EffectsConfig`; result is cached; `configure()` clears cache); DOC-0094 describes the package at a conceptual level only
- Proposed fix: Add an API reference for `load_effects()` to `packages/effects/README.md` documenting the return type (`EffectsConfig`), caching behavior (cached after first call, cleared by `configure()`), and that it raises `EffectsLoadError` or `EffectsValidationError` on failure.

---

## S3 — Minor

No S3 findings identified in this investigation pass. All observed issues rose to S2 or higher. The existing verified documentation (75 of 107 claims) is generally well-written with consistent style.

---
