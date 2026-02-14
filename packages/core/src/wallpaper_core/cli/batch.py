"""Batch generation commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from wallpaper_core.cli.process import _resolve_chain_commands, _resolve_command
from wallpaper_core.config.schema import Verbosity
from wallpaper_core.console.progress import BatchProgress
from wallpaper_core.dry_run import CoreDryRun
from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_core.engine.batch import BatchGenerator
from wallpaper_core.engine.chain import ChainExecutor


app = typer.Typer(help="Batch generate effects")


def _get_batch_generator(
    ctx: typer.Context, parallel: bool, strict: bool
) -> BatchGenerator:
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


def _resolve_batch_items(
    config: EffectsConfig,
    batch_type: str,
    input_file: Path,
    output_dir: Path,
    flat: bool,
) -> list[dict[str, str]]:
    """Resolve all batch items with their output paths and commands."""
    suffix = input_file.suffix or ".png"
    image_name = input_file.stem
    chain_executor = ChainExecutor(config, None)

    items: list[dict[str, str]] = []

    # Collect items based on batch_type
    item_groups: list[
        tuple[str, str, str | None]
    ] = []  # (name, type, subdir_for_single_type)
    if batch_type in ("effects", "all"):
        for name in config.effects:
            item_groups.append(
                (
                    name,
                    "effect",
                    "effects" if batch_type != "all" or not flat else None,
                )
            )
    if batch_type in ("composites", "all"):
        for name in config.composites:
            item_groups.append(
                (
                    name,
                    "composite",
                    "composites" if batch_type != "all" or not flat else None,
                )
            )
    if batch_type in ("presets", "all"):
        for name in config.presets:
            item_groups.append(
                (
                    name,
                    "preset",
                    "presets" if batch_type != "all" or not flat else None,
                )
            )

    for name, item_type, single_type_subdir in item_groups:
        # Compute the output path mirroring BatchGenerator._get_output_path logic
        if batch_type == "all":
            # generate_all: base_dir = output_dir / image_name
            base_dir = output_dir / image_name
            if flat:
                out_path = base_dir / f"{name}{suffix}"
            else:
                subdir_map = {
                    "effect": "effects",
                    "composite": "composites",
                    "preset": "presets",
                }
                out_path = base_dir / subdir_map.get(item_type, "") / f"{name}{suffix}"
        else:
            # generate_batch: base_dir varies based on flat/subdir settings
            base_dir = output_dir / image_name
            if not flat and single_type_subdir:
                base_dir = base_dir / single_type_subdir
            out_path = base_dir / f"{name}{suffix}"

        # Resolve command(s)
        if item_type == "effect":
            effect_def = config.effects.get(name)
            if effect_def is not None:
                params = chain_executor._get_params_with_defaults(name, {})
                cmd = _resolve_command(effect_def.command, input_file, out_path, params)
                param_str = (
                    "  ".join(f"{k}={v}" for k, v in params.items())
                    if params
                    else "\u2014"
                )
            else:
                cmd = f"# Unknown effect: {name}"
                param_str = "\u2014"
            items.append(
                {
                    "name": name,
                    "type": "effect",
                    "output_path": str(out_path),
                    "command": cmd,
                    "params": param_str,
                }
            )

        elif item_type == "composite":
            composite_def = config.composites.get(name)
            if composite_def is not None:
                chain_cmds = _resolve_chain_commands(
                    composite_def.chain,
                    config,
                    input_file,
                    out_path,
                )
                cmd = " && ".join(chain_cmds)
                chain_str = " -> ".join(s.effect for s in composite_def.chain)
            else:
                cmd = f"# Unknown composite: {name}"
                chain_str = "\u2014"
            items.append(
                {
                    "name": name,
                    "type": "composite",
                    "output_path": str(out_path),
                    "command": cmd,
                    "params": chain_str,
                }
            )

        elif item_type == "preset":
            preset_def = config.presets.get(name)
            if preset_def is not None:
                if preset_def.composite:
                    composite_def = config.composites.get(preset_def.composite)
                    if composite_def is not None:
                        chain_cmds = _resolve_chain_commands(
                            composite_def.chain,
                            config,
                            input_file,
                            out_path,
                        )
                        cmd = " && ".join(chain_cmds)
                    else:
                        cmd = f"# Unknown composite: {preset_def.composite}"
                    items.append(
                        {
                            "name": name,
                            "type": "preset",
                            "output_path": str(out_path),
                            "command": cmd,
                            "preset_type": "composite",
                            "target": preset_def.composite,
                        }
                    )
                elif preset_def.effect:
                    effect_def = config.effects.get(preset_def.effect)
                    if effect_def is not None:
                        params = chain_executor._get_params_with_defaults(
                            preset_def.effect,
                            preset_def.params,
                        )
                        cmd = _resolve_command(
                            effect_def.command,
                            input_file,
                            out_path,
                            params,
                        )
                    else:
                        cmd = f"# Unknown effect: {preset_def.effect}"
                    items.append(
                        {
                            "name": name,
                            "type": "preset",
                            "output_path": str(out_path),
                            "command": cmd,
                            "preset_type": "effect",
                            "target": preset_def.effect,
                        }
                    )
                else:
                    items.append(
                        {
                            "name": name,
                            "type": "preset",
                            "output_path": str(out_path),
                            "command": f"# Preset '{name}' has no effect or composite",
                            "preset_type": "\u2014",
                            "target": "\u2014",
                        }
                    )
            else:
                items.append(
                    {
                        "name": name,
                        "type": "preset",
                        "output_path": str(out_path),
                        "command": f"# Unknown preset: {name}",
                        "preset_type": "\u2014",
                        "target": "\u2014",
                    }
                )

    return items


def _run_batch(
    ctx: typer.Context,
    input_file: Path,
    output_dir: Path,
    batch_type: str,
    parallel: bool,
    strict: bool,
    flat: bool,
    dry_run: bool = False,
) -> None:
    """Run batch generation."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if dry_run:
        settings = ctx.obj["settings"]
        use_parallel = parallel if parallel is not None else settings.execution.parallel
        use_strict = strict if strict is not None else settings.execution.strict
        max_workers = settings.execution.max_workers or None

        items = _resolve_batch_items(config, batch_type, input_file, output_dir, flat)

        if output.verbosity == Verbosity.QUIET:
            for item in items:
                output.console.print(item["command"])
        else:
            dry = CoreDryRun(console=output.console)
            dry.render_batch(
                input_path=input_file,
                output_dir=output_dir,
                items=items,
                parallel=use_parallel,
                max_workers=max_workers,
                strict=use_strict,
            )

        raise typer.Exit(0)

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
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Generate all effects for an image.

    Examples:
        wallpaper-core batch effects input.jpg
        wallpaper-core batch effects input.jpg -o /custom/output
        wallpaper-core batch effects input.jpg --flat
    """
    from wallpaper_core.config.schema import CoreSettings

    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    _run_batch(ctx, input_file, output_dir, "effects", parallel, strict, flat, dry_run)


@app.command("composites")
def batch_composites(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Generate all composites for an image.

    Examples:
        wallpaper-core batch composites input.jpg
        wallpaper-core batch composites input.jpg -o /custom/output
        wallpaper-core batch composites input.jpg --flat
    """
    from wallpaper_core.config.schema import CoreSettings

    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    _run_batch(
        ctx,
        input_file,
        output_dir,
        "composites",
        parallel,
        strict,
        flat,
        dry_run,
    )


@app.command("presets")
def batch_presets(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Generate all presets for an image.

    Examples:
        wallpaper-core batch presets input.jpg
        wallpaper-core batch presets input.jpg -o /custom/output
        wallpaper-core batch presets input.jpg --flat
    """
    from wallpaper_core.config.schema import CoreSettings

    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    _run_batch(ctx, input_file, output_dir, "presets", parallel, strict, flat, dry_run)


@app.command("all")
def batch_all(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory (uses settings default if not specified)",
        ),
    ] = None,
    parallel: Annotated[bool, typer.Option("--parallel/--sequential")] = True,
    strict: Annotated[bool, typer.Option("--strict/--no-strict")] = True,
    flat: Annotated[bool, typer.Option("--flat", help="Flat output structure")] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Generate all effects, composites, and presets for an image.

    Examples:
        wallpaper-core batch all input.jpg
        wallpaper-core batch all input.jpg -o /custom/output
        wallpaper-core batch all input.jpg --flat
    """
    from wallpaper_core.config.schema import CoreSettings

    settings: CoreSettings = ctx.obj["settings"]

    # Resolve output_dir
    if output_dir is None:
        output_dir = settings.output.default_dir

    _run_batch(ctx, input_file, output_dir, "all", parallel, strict, flat, dry_run)
