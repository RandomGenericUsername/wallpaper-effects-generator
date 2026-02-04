# Feature Request: Wallpaper Effects Package Restructure

## Overview

**Feature**: Restructure `wallpaper-effects-generator` into two independent UV packages  
**Priority**: High  
**Status**: Proposed

## Problem Statement

The current project structure mixes core effect processing with future container orchestration needs:

- `core/` contains CLI and engine (named `wallpaper-effects-processor`)  
- `shared/` contains models and loaders (named `wallpaper-effects-shared`)  
- No container support exists
- Architecture doesn't follow our standard core/orchestrator pattern

## Goals

1. **Modular packages**: Core and orchestrator as separate, installable packages
2. **Library-first**: Core usable as both Python module and CLI tool
3. **Container isolation**: Orchestrator runs effects in containers for portability
4. **CLI consistency**: Same `wallpaper-effects` command, orchestrator takes precedence

## User Stories

### US-1: Developer Using Core as Library
> As a developer, I want to `pip install wallpaper-effects-core` and use it programmatically so I can integrate effect processing into my application.

**Acceptance Criteria**:
- `from wallpaper_effects import ConfigLoader, CommandExecutor` works
- All models and engine components are importable
- No CLI required for library usage

### US-2: End User Using Core CLI
> As an end user, I want to install only the core package and use CLI commands to process wallpapers without needing Docker.

**Acceptance Criteria**:
- `wallpaper-effects process effect input.jpg output.jpg -e blur` works
- `wallpaper-effects batch all input.jpg ./output/` works
- `wallpaper-effects show effects` lists available effects

### US-3: DevOps User Using Orchestrator
> As a DevOps engineer, I want to run effect processing in containers so I have consistent ImageMagick versions across environments.

**Acceptance Criteria**:
- `wallpaper-effects container build` creates container image
- `wallpaper-effects container run` processes images inside container
- All core commands still work (delegated)

### US-4: CI/CD Pipeline Integration
> As a CI/CD maintainer, I want portable container-based processing so builds work identically on any runner.

**Acceptance Criteria**:
- Container includes all required ImageMagick features
- Volume mounts for input/output work correctly
- Exit codes reflect processing success/failure

## Functional Requirements

### FR-1: Package Structure
| Package | PyPI Name | Import Name | CLI Command |
|---------|-----------|-------------|-------------|
| Core | `wallpaper-effects-core` | `wallpaper_effects` | `wallpaper-effects` |
| Orchestrator | `wallpaper-effects-orchestrator` | `wallpaper_effects_orchestrator` | `wallpaper-effects` |

### FR-2: Core Public API
Must export:
- `ConfigLoader` - Configuration loading and caching
- `EffectsConfig`, `Settings` - Configuration models
- `EffectDefinition`, `PresetDefinition`, etc. - Effect models
- `CommandExecutor`, `ChainExecutor`, `BatchGenerator` - Engine
- `RichOutput`, `BatchProgress` - Console utilities

### FR-3: Orchestrator Delegation
- Import and re-register core's CLI subcommands
- Add `container` subcommand group
- Override `version` command to show both versions

### FR-4: Container Requirements
- Base: Alpine Linux 3.19
- Package: `imagemagick` (ImageMagick 7)
- Required features: blur, grayscale, negate, brightness-contrast, modulate, sepia-tone, vignette, fill, colorize

### FR-5: Dependency Management
- Orchestrator depends on core (editable path for dev)
- Orchestrator depends on `container-manager` library
- Core has no dependency on orchestrator

## Non-Functional Requirements

### NFR-1: Backward Compatibility
- All existing effect definitions continue to work

### NFR-2: Test Coverage
- Migrate existing tests to new structure
- Add orchestrator-specific tests
- Maintain >80% coverage

### NFR-3: Documentation
- README.md for each package
- API documentation via docstrings
- Container usage examples

## Out of Scope

- New effect types (separate feature)
- GUI/TUI interface
- Remote container execution (Kubernetes, etc.)
- Web service mode

## Dependencies

- [container-manager](https://github.com/RandomGenericUsername/container-manager) library
- Docker or Podman runtime (for orchestrator)
