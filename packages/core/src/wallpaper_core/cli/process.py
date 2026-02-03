"""Process command for applying effects to a single image."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from wallpaper_core.effects.schema import ChainStep
from wallpaper_core.engine.chain import ChainExecutor
from wallpaper_core.engine.executor import CommandExecutor

app = typer.Typer(help="Process a single image with effects")


@app.command("effect")
def apply_effect(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_file: Annotated[Path, typer.Argument(help="Output image file")],
    effect: Annotated[str, typer.Option("-e", "--effect", help="Effect to apply")],
    blur: Annotated[Optional[str], typer.Option("--blur", help="Blur geometry")] = None,
    brightness: Annotated[Optional[int], typer.Option("--brightness")] = None,
    contrast: Annotated[Optional[int], typer.Option("--contrast")] = None,
    saturation: Annotated[Optional[int], typer.Option("--saturation")] = None,
    strength: Annotated[Optional[int], typer.Option("--strength")] = None,
    color: Annotated[Optional[str], typer.Option("--color")] = None,
    opacity: Annotated[Optional[int], typer.Option("--opacity")] = None,
) -> None:
    """Apply a single effect to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    # Validate input
    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    # Get effect definition
    effect_def = config.effects.get(effect)
    if effect_def is None:
        output.error(f"Unknown effect: {effect}")
        output.info("Use 'show effects' to list available effects")
        raise typer.Exit(1)

    # Build params from CLI options
    params = {}
    if blur is not None:
        params["blur"] = blur
    if brightness is not None:
        params["brightness"] = brightness
    if contrast is not None:
        params["contrast"] = contrast
    if saturation is not None:
        params["saturation"] = saturation
    if strength is not None:
        params["strength"] = strength
    if color is not None:
        params["color"] = color
    if opacity is not None:
        params["opacity"] = opacity

    # Execute
    executor = CommandExecutor(output)
    chain_executor = ChainExecutor(config, output)
    final_params = chain_executor._get_params_with_defaults(effect, params)

    output.verbose(f"Applying effect '{effect}' to {input_file}")
    result = executor.execute(effect_def.command, input_file, output_file, final_params)

    if result.success:
        output.success(f"Created {output_file}")
    else:
        output.error(f"Failed: {result.stderr}")
        raise typer.Exit(1)


@app.command("composite")
def apply_composite(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_file: Annotated[Path, typer.Argument(help="Output image file")],
    composite: Annotated[str, typer.Option("-c", "--composite", help="Composite")],
) -> None:
    """Apply a composite effect (chain) to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    composite_def = config.composites.get(composite)
    if composite_def is None:
        output.error(f"Unknown composite: {composite}")
        raise typer.Exit(1)

    chain_executor = ChainExecutor(config, output)
    output.verbose(f"Applying composite '{composite}' to {input_file}")
    result = chain_executor.execute_chain(composite_def.chain, input_file, output_file)

    if result.success:
        output.success(f"Created {output_file}")
    else:
        output.error(f"Failed: {result.stderr}")
        raise typer.Exit(1)


@app.command("preset")
def apply_preset(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_file: Annotated[Path, typer.Argument(help="Output image file")],
    preset: Annotated[str, typer.Option("-p", "--preset", help="Preset name")],
) -> None:
    """Apply a preset to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    preset_def = config.presets.get(preset)
    if preset_def is None:
        output.error(f"Unknown preset: {preset}")
        raise typer.Exit(1)

    chain_executor = ChainExecutor(config, output)
    executor = CommandExecutor(output)

    output.verbose(f"Applying preset '{preset}' to {input_file}")

    if preset_def.composite:
        composite_def = config.composites.get(preset_def.composite)
        if composite_def is None:
            output.error(f"Preset references unknown composite: {preset_def.composite}")
            raise typer.Exit(1)
        result = chain_executor.execute_chain(composite_def.chain, input_file, output_file)
    elif preset_def.effect:
        effect_def = config.effects.get(preset_def.effect)
        if effect_def is None:
            output.error(f"Preset references unknown effect: {preset_def.effect}")
            raise typer.Exit(1)
        params = chain_executor._get_params_with_defaults(preset_def.effect, preset_def.params)
        result = executor.execute(effect_def.command, input_file, output_file, params)
    else:
        output.error(f"Preset '{preset}' has no effect or composite defined")
        raise typer.Exit(1)

    if result.success:
        output.success(f"Created {output_file}")
    else:
        output.error(f"Failed: {result.stderr}")
        raise typer.Exit(1)
