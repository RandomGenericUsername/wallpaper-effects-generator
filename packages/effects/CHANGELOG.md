# Changelog

All notable changes to the layered-effects package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-04

### Added
- Initial release of layered-effects package
- Layered effects.yaml configuration system with three layers:
  - Package defaults (from wallpaper-core)
  - Project-level effects (project root)
  - User-level effects (~/.config/wallpaper-effects-generator/)
- Deep merge functionality using ConfigMerger from layered-settings
- Pydantic validation using EffectsConfig schema from wallpaper-core
- EffectsLoader class for discovering and merging configuration layers
- Public API: `configure()` and `load_effects()`
- Error classes: EffectsError, EffectsLoadError, EffectsValidationError
- Configuration caching for performance
- Comprehensive test suite with 95%+ coverage
- Integration with layered-settings for path management

### Architecture
- Reuses layered-settings infrastructure (constants, paths, ConfigMerger)
- Module-level state management for configuration
- XDG Base Directory Specification compliance
- YAML configuration file format

[0.1.0]: https://github.com/yourusername/wallpaper-effects-generator/releases/tag/v0.1.0
