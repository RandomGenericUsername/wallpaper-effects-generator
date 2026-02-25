# Investigation Requirements

REPO_ROOT = /home/inumaki/Development/dotfiles-new-architectures/dotfiles-services/wallpaper-effects-generator
REPO_LANGUAGE = Python
REPO_TYPE = CLI tool / monorepo (4 packages)

DOCS_ROOTS =
  - README.md
  - DEVELOPMENT.md
  - packages/settings/README.md
  - packages/core/README.md
  - packages/effects/README.md
  - packages/orchestrator/README.md

INTERFACES =
  - packages/core/src (wallpaper-core CLI, public API)
  - packages/orchestrator/src (wallpaper-process CLI, public API)
  - packages/effects/src (effect/composite/preset definitions, public config)
  - packages/settings/src (settings API, used by other packages)

TEST_COMMAND = python -m pytest
TEST_CATEGORIES = unit, integration, smoke
TEST_ROOT = packages/
ENVIRONMENT_NOTES = Each package is installed as an editable package. Run `make dev` from the project root to install all packages with dependencies. Tests should be run per-package using `make test-<package>` (e.g. `make test-settings`) or all at once with `make test-all`.

CONTRACTS = (none — no OpenAPI or JSON Schema files)

ACCEPTANCE_THRESHOLDS:
  S0 = 0
  S1 <= 3
  OPEN_UNKNOWNS <= 5

OUTPUT_PROFILE = diataxis
VERIFICATION_POLICY = verified-only
PRIMARY_AUDIENCE = end-users, contributors
OUTPUT_DIR = docs/
