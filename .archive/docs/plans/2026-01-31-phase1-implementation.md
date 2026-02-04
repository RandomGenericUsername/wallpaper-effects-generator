# Phase 1 Implementation: layered-settings Package

> **For Claude:** Use superpowers:subagent-driven-development to execute this plan.

**Goal:** Build layered_settings package as specified in `docs/plans/2026-01-31-monorepo-refactor-design.md`

**Location:** `packages/settings/`

**Approach:** TDD - write test first, run to see it fail, implement, run to see it pass, commit.

---

## Implementation Tasks

All tasks reference the architecture in the design document. Execute in order:

1. **Package Setup** - Create package structure, pyproject.toml, README
2. **Error Hierarchy** - Create errors.py with all exception classes
3. **Schema Registry** - Create registry.py with SchemaEntry and SchemaRegistry
4. **File Loader** - Create loader.py supporting TOML and YAML
5. **Merge Algorithm** - Create merger.py with deep merge logic
6. **Layer Discovery** - Create layers.py to find config files
7. **Config Builder** - Create builder.py to merge and validate
8. **Public API** - Update __init__.py with configure() and get_config()
9. **Integration Tests** - Create test_integration.py for end-to-end workflows
10. **Documentation** - Update README with examples

See design document for complete specifications and schemas.
