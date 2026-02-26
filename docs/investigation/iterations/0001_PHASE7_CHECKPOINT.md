# Checkpoint: Phase 7 — REVIEW_FINDINGS

Iteration: 0001
S0: 3
S1: 6
S2: 12
S3: 0
Next: PHASE_8_FINALIZE_INVESTIGATION

## S0 summary

- F-0001: `packages/orchestrator/README.md:72-84` documents positional process command syntax that does not exist. Actual CLI requires `--effect`/`--composite`/`--preset` named flags and `-o` for output. User following docs will get a CLI error.
- F-0002: `packages/core/README.md:63` states user settings path as `~/.config/wallpaper-effects/settings.toml`. Actual path (from `constants.py`: `APP_NAME = "wallpaper-effects-generator"`) is `~/.config/wallpaper-effects-generator/settings.toml`. User who follows this path cannot configure the application.
- F-0003: `README.md:129,157` claims default output directory is `./wallpapers-output`. Actual default in `packages/core/src/wallpaper_core/config/settings.toml` is `/tmp/wallpaper-effects`. User who omits `-o` will not find output where documented.

## S1 summary

- F-0004: `wallpaper-core info` and `wallpaper-process info` commands are undocumented.
- F-0005: `wallpaper-core version` and `wallpaper-process version` commands are undocumented.
- F-0006: Per-effect CLI parameter overrides (e.g., `--blur 0x10`) are undocumented.
- F-0007: `wallpaper-process install/uninstall --dry-run` is undocumented.
- F-0008: `wallpaper-process process <effect|composite|preset> --dry-run` is undocumented.
- F-0009: Orchestrator unified config namespace layout (`core`/`effects`/`orchestrator`) is undocumented at a user-facing level.

## S2 summary

- F-0010: CLI-to-config-layer mapping for wallpaper-core flags not documented (BHV-0039 partial).
- F-0011: User effects.yaml path inconsistency in `packages/core/README.md:104` (BHV-0043 partial; `wallpaper-effects` vs `wallpaper-effects-generator`).
- F-0012: Batch `--dry-run` not explicitly documented as showing all planned commands (BHV-0059 partial).
- F-0013: Orchestrator process command `--flat` and `-o` flags not documented alongside corrected syntax (BHV-0078 partial).
- F-0014: `wallpaper-process batch` runs on host, not in container — distinction undocumented (BHV-0081 partial).
- F-0015: Orchestrator CLI config overrides not documented (BHV-0082 partial).
- F-0016: `APP_NAME`, `SETTINGS_FILENAME`, `EFFECTS_FILENAME` constants undocumented in settings README (BHV-0028 gap, developer API).
- F-0017: `DryRunBase` class undocumented in settings README (BHV-0029 gap, developer API).
- F-0018: `ValidationCheck` dataclass undocumented in settings README (BHV-0030 gap, developer API).
- F-0019: `effects.configure()` function undocumented in effects README (BHV-0031 gap, developer API).
- F-0020: Effects error hierarchy undocumented in effects README (BHV-0035 gap, developer API).
- F-0021: `load_effects()` caching semantics undocumented (BHV-0032 partial).

## Evidence notes

- S0 claims verified by reading source files directly:
  - `packages/settings/src/layered_settings/constants.py` (APP_NAME value)
  - `packages/settings/src/layered_settings/paths.py` (XDG path construction)
  - `packages/orchestrator/src/wallpaper_orchestrator/cli/main.py` (actual CLI parameter definitions)
  - `packages/core/src/wallpaper_core/config/settings.toml` (actual default_dir value)
