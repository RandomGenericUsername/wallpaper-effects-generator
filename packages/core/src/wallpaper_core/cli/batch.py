"""Batch generation commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from wallpaper_core.console.progress import BatchProgress
from wallpaper_core.engine.batch import BatchGenerator

app = typer.Typer(help="Batch generate effects")


def _get_batch_generator(ctx: typer.Context, parallel: bool, strict: bool) -> BatchGenerator:
    """Create BatchGenerator with settings."""
    settings = ctx.obj["settings"]
    # CLI flags override settings
    use_parallel = parallel if parallel is not None else settings.execution.parallel
    use_strict = strict if strict is not None else settings.execution.strict
    max_workers = settings.execution.max_workers

    return BatchGenerator(
        config=ctx.obj["config"],
        output=ctx.obj["output"],
        parallel=use_parallel,
        strict=use_strict,
        max_workers=max_workers,
    )


def _run_batch(
    ctx: typer.Context,
    input_file: Path,
    output_dir: Path,
    batch_type: str,
    parallel: bool,
    strict: bool,
    flat: bool,
) -> None:
    """Run batch generation."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    generator = _get_batch_generator(ctx, parallel, strict)

    # Determine total count
    if batch_type == "effects":
        total = len(config.effects)
        method = generator.generate_all_effects
    elif batch_type == "composites":
        total = len(config.composites)
        method = generator.generate_all_composites
    elif batch_type == "presets":
        total = len(config.presets)
        method = generator.generate_all_presets
    else:  # all
        total = len(config.effects) + len(config.composites) + len(config.presets)
        method = generator.generate_all

    output.info(f"Generating {total} {batch_type}...")

    with BatchProgress(total, f"Generating {batch_type}") as progress:
        result = method(input_file, output_dir, flat=flat, progress=progress)

    output.newline()
    if result.success:
        output.success(f"Generated {result.succeeded}/{result.total} {batch_type}")
        output.info(f"Output: {result.output_dir}")
    else:
        output.error(f"Failed: {result.failed}/{result.total} {batch_type} failed")
        if strict:
            raise typer.Exit(1)


@app.command("effects")
def batch_effects(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
) -> None:
    """Generate all effects for an image."""
    _run_batch(ctx, input_file, output_dir, "effects", parallel, strict, flat)


@app.command("composites")
def batch_composites(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
) -> None:
    """Generate all composites for an image."""
    _run_batch(ctx, input_file, output_dir, "composites", parallel, strict, flat)


@app.command("presets")
def batch_presets(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
) -> None:
    """Generate all presets for an image."""
    _run_batch(ctx, input_file, output_dir, "presets", parallel, strict, flat)


@app.command("all")
def batch_all(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[Path, typer.Argument(help="Output directory")],
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
) -> None:
    """Generate all effects, composites, and presets for an image."""
    _run_batch(ctx, input_file, output_dir, "all", parallel, strict, flat)
