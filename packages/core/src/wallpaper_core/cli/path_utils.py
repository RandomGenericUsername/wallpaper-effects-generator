"""Utilities for output path resolution."""

from pathlib import Path

from wallpaper_core.config.schema import ItemType


def resolve_output_path(
    output_dir: Path,
    input_file: Path,
    item_name: str,
    item_type: ItemType,
    flat: bool = False,
) -> Path:
    """Resolve output file path using standardized structure.

    Args:
        output_dir: Base output directory
        input_file: Input image file
        item_name: Name of effect/composite/preset
        item_type: Type of item (ItemType enum)
        flat: If True, skip type subdirectory

    Returns:
        Path: output_dir/input_stem/[type_subdir/]item_name.ext

    Examples:
        >>> resolve_output_path(
        ...     Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=False
        ... )
        Path('/out/wall/effects/blur.jpg')

        >>> resolve_output_path(
        ...     Path("/out"), Path("wall.jpg"), "blur", ItemType.EFFECT, flat=True
        ... )
        Path('/out/wall/blur.jpg')
    """
    suffix = input_file.suffix or ".png"
    base_dir = output_dir / input_file.stem

    if flat:
        return base_dir / f"{item_name}{suffix}"
    else:
        return base_dir / item_type.subdir_name / f"{item_name}{suffix}"
