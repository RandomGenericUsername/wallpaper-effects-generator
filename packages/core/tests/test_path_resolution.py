"""Tests for output path resolution."""

from pathlib import Path

from wallpaper_core.cli.path_utils import resolve_output_path
from wallpaper_core.config.schema import ItemType


def test_resolve_output_path_effect_not_flat():
    """Resolve path for effect with hierarchical structure."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall.jpg"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/wall/effects/blur.jpg")


def test_resolve_output_path_effect_flat():
    """Resolve path for effect with flat structure."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall.jpg"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=True,
    )
    assert result == Path("/out/wall/blur.jpg")


def test_resolve_output_path_composite():
    """Resolve path for composite with hierarchical structure."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall.jpg"),
        item_name="my-composite",
        item_type=ItemType.COMPOSITE,
        flat=False,
    )
    assert result == Path("/out/wall/composites/my-composite.jpg")


def test_resolve_output_path_preset():
    """Resolve path for preset with hierarchical structure."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall.jpg"),
        item_name="my-preset",
        item_type=ItemType.PRESET,
        flat=False,
    )
    assert result == Path("/out/wall/presets/my-preset.jpg")


def test_resolve_output_path_no_extension_defaults_png():
    """Resolve path defaults to .png when input has no extension."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/wall/effects/blur.png")


def test_resolve_output_path_preserves_extension():
    """Resolve path preserves input file extension."""
    result = resolve_output_path(
        output_dir=Path("/out"),
        input_file=Path("wall.png"),
        item_name="blur",
        item_type=ItemType.EFFECT,
        flat=False,
    )
    assert result == Path("/out/wall/effects/blur.png")
