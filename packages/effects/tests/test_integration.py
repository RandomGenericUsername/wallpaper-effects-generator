# packages/effects/tests/test_integration.py
"""Integration tests for full layered effects system."""

from pathlib import Path

import pytest


def test_full_stack_three_layers(tmp_path: Path):
    """End-to-end test with package, project, and user layers."""
    from layered_effects import _reset, configure, load_effects

    _reset()

    # Package layer
    package_file = tmp_path / "package_effects.yaml"
    package_file.write_text(
        """
version: "1.0"
parameter_types:
  blur_geometry:
    type: string
    default: "0x8"
effects:
  blur:
    description: "Package blur"
    command: 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
    parameters:
      blur:
        type: blur_geometry
  brightness:
    description: "Package brightness"
    command: 'magick "$INPUT" -brightness-contrast "$BRIGHTNESS"% "$OUTPUT"'
composites: {}
presets: {}
"""
    )

    # Project layer
    project_root = tmp_path / "project"
    project_root.mkdir()
    project_effects = project_root / "effects.yaml"
    project_effects.write_text(
        """
version: "1.0"
effects:
  blur:
    description: "Project blur override"
    command: 'magick "$INPUT" -blur 0x12 "$OUTPUT"'
  contrast:
    description: "Project contrast"
    command: 'magick "$INPUT" -contrast "$OUTPUT"'
"""
    )

    # User layer
    user_file = tmp_path / "user_effects.yaml"
    user_file.write_text(
        """
version: "1.0"
effects:
  neon:
    description: "User neon"
    command: 'magick "$INPUT" -negate "$OUTPUT"'
"""
    )

    # Configure and load
    configure(
        package_effects_file=package_file,
        project_root=project_root,
        user_effects_file=user_file,
    )
    config = load_effects()

    # Verify merging worked correctly
    # blur: from project (overridden)
    assert "blur" in config.effects
    assert config.effects["blur"].description == "Project blur override"

    # brightness: from package (inherited)
    assert "brightness" in config.effects
    assert config.effects["brightness"].description == "Package brightness"

    # contrast: from project (new)
    assert "contrast" in config.effects
    assert config.effects["contrast"].description == "Project contrast"

    # neon: from user (new)
    assert "neon" in config.effects
    assert config.effects["neon"].description == "User neon"

    # parameter_types: from package (inherited)
    assert "blur_geometry" in config.parameter_types


def test_user_can_override_package_effect(tmp_path: Path):
    """Test user can fully override a package effect."""
    from layered_effects import _reset, configure, load_effects

    _reset()

    package_file = tmp_path / "package.yaml"
    package_file.write_text(
        """
version: "1.0"
effects:
  test:
    description: "Package version"
    command: "package command"
"""
    )

    user_file = tmp_path / "user.yaml"
    user_file.write_text(
        """
version: "1.0"
effects:
  test:
    description: "User version"
    command: "user command"
"""
    )

    configure(
        package_effects_file=package_file,
        user_effects_file=user_file,
    )
    config = load_effects()

    assert config.effects["test"].description == "User version"
    assert config.effects["test"].command == "user command"


def test_works_with_real_effects_yaml(tmp_path: Path):
    """Test with actual effects.yaml from wallpaper-core."""
    from layered_effects import _reset, configure, load_effects

    _reset()

    # Use actual package effects file
    core_effects = (
        Path(__file__).parent.parent.parent.parent
        / "core"
        / "src"
        / "wallpaper_core"
        / "effects"
        / "effects.yaml"
    )

    if not core_effects.exists():
        pytest.skip("Package effects.yaml not found")

    configure(package_effects_file=core_effects)
    config = load_effects()

    # Should have standard effects
    assert "blur" in config.effects
    assert "brightness" in config.effects
    assert "blackwhite" in config.effects
