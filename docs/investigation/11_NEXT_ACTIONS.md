# Next Actions

STATUS: BLOCKED — Must resolve S0 findings before synthesis.

## Required before synthesis

### Fix F-0001 (S0): Orchestrator README wrong command syntax
File: `packages/orchestrator/README.md`
Problem: Documents positional syntax that does not exist in CLI.
Fix: Replace example commands with correct flag-based syntax matching BHV-0078.

### Fix F-0002 (S0): Core README wrong user settings path
File: `packages/core/README.md`
Problem: States `~/.config/wallpaper-effects/` but APP_NAME = "wallpaper-effects-generator".
Fix: Replace `wallpaper-effects` with `wallpaper-effects-generator` in the path.

### Fix F-0003 (S0): Root README wrong default output directory
File: `README.md`
Problem: States default output is `./wallpapers-output` but actual default is `/tmp/wallpaper-effects`.
Fix: Update default_dir references in README.md to `/tmp/wallpaper-effects`.

## After S0 fixes, proceed to synthesis
S1 findings (F-0004 through F-0009) must be covered in synthesis output.
S2 findings (F-0010 through F-0021) are stretch goals for completeness.
