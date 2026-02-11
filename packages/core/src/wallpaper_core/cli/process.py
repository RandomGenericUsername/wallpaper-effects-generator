"""Process command for applying effects to a single image."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from wallpaper_core.config.schema import Verbosity
from wallpaper_core.dry_run import CoreDryRun
from wallpaper_core.effects.schema import ChainStep, EffectsConfig
from wallpaper_core.engine.chain import ChainExecutor
from wallpaper_core.engine.executor import CommandExecutor

app = typer.Typer(help="Process a single image with effects")


def _resolve_command(
    command_template: str,
    input_path: Path,
    output_path: Path,
    params: dict[str, str | int | float],
) -> str:
    """Resolve command template by substituting variables."""
    substitutions = {"INPUT": str(input_path), "OUTPUT": str(output_path)}
    for k, v in params.items():
        substitutions[k.upper()] = str(v)
    command = command_template
    for k, v in substitutions.items():
        command = command.replace(f'"${k}"', f'"{v}"')
        command = command.replace(f"${k}", v)
    return command


def _resolve_chain_commands(
    chain: list[ChainStep],
    config: EffectsConfig,
    input_path: Path,
    output_path: Path,
) -> list[str]:
    """Resolve all commands in a chain without executing them."""
    chain_executor = ChainExecutor(config, None)
    commands = []
    output_suffix = output_path.suffix or ".png"

    for i, step in enumerate(chain):
        is_last = i == len(chain) - 1

        # Determine input for this step
        if i == 0:
            step_input = input_path
        else:
            step_input = Path(f"<temp/step_{i - 1}{output_suffix}>")

        # Determine output for this step
        if is_last:
            step_output = output_path
        else:
            step_output = Path(f"<temp/step_{i}{output_suffix}>")

        effect_def = config.effects.get(step.effect)
        if effect_def is None:
            commands.append(f"# Unknown effect: {step.effect}")
            continue

        params = chain_executor._get_params_with_defaults(step.effect, step.params)
        resolved = _resolve_command(effect_def.command, step_input, step_output, params)
        commands.append(resolved)

    return commands


@app.command("effect")
def apply_effect(
    ctx: typer.Context,
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output_file: Annotated[Path, typer.Argument(help="Output image file")],
    effect: Annotated[str, typer.Option("-e", "--effect", help="Effect to apply")],
    blur: Annotated[str | None, typer.Option("--blur", help="Blur geometry")] = None,
    brightness: Annotated[int | None, typer.Option("--brightness")] = None,
    contrast: Annotated[int | None, typer.Option("--contrast")] = None,
    saturation: Annotated[int | None, typer.Option("--saturation")] = None,
    strength: Annotated[int | None, typer.Option("--strength")] = None,
    color: Annotated[str | None, typer.Option("--color")] = None,
    opacity: Annotated[int | None, typer.Option("--opacity")] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Apply a single effect to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    # Build params from CLI options
    params: dict[str, str | int] = {}
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

    if dry_run:
        dry = CoreDryRun(console=output.console)

        # Validation checks (non-fatal in dry-run mode)
        checks = dry.validate_core(
            input_path=input_file,
            output_path=output_file,
            item_name=effect,
            item_type="effect",
            config=config,
        )

        # Resolve command if effect exists
        effect_def = config.effects.get(effect)
        if effect_def is not None:
            chain_executor = ChainExecutor(config, None)
            final_params = chain_executor._get_params_with_defaults(effect, params)
            resolved = _resolve_command(
                effect_def.command, input_file, output_file, final_params
            )
        else:
            resolved = f"# Cannot resolve: unknown effect '{effect}'"

        if output.verbosity == Verbosity.QUIET:
            output.console.print(resolved)
        else:
            dry.render_process(
                item_name=effect,
                item_type="effect",
                input_path=input_file,
                output_path=output_file,
                params=params,
                resolved_command=resolved,
                command_template=effect_def.command if effect_def else None,
            )
            dry.render_validation(checks)

        raise typer.Exit(0)

    # Normal execution path
    if not input_file.exists():
        output.error(f"Input file not found: {input_file}")
        raise typer.Exit(1)

    effect_def = config.effects.get(effect)
    if effect_def is None:
        output.error(f"Unknown effect: {effect}")
        output.info("Use 'show effects' to list available effects")
        raise typer.Exit(1)

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
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Apply a composite effect (chain) to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if dry_run:
        dry = CoreDryRun(console=output.console)

        checks = dry.validate_core(
            input_path=input_file,
            output_path=output_file,
            item_name=composite,
            item_type="composite",
            config=config,
        )

        composite_def = config.composites.get(composite)
        if composite_def is not None:
            chain_commands = _resolve_chain_commands(
                composite_def.chain,
                config,
                input_file,
                output_file,
            )
        else:
            chain_commands = [f"# Cannot resolve: unknown composite '{composite}'"]

        if output.verbosity == Verbosity.QUIET:
            for cmd in chain_commands:
                output.console.print(cmd)
        else:
            dry.render_process(
                item_name=composite,
                item_type="composite",
                input_path=input_file,
                output_path=output_file,
                params={},
                resolved_command=(
                    f"chain: {' -> '.join(s.effect for s in composite_def.chain)}"
                    if composite_def
                    else ""
                ),
                chain_commands=chain_commands,
            )
            dry.render_validation(checks)

        raise typer.Exit(0)

    # Normal execution path
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
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without executing"),
    ] = False,
) -> None:
    """Apply a preset to an image."""
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    if dry_run:
        dry = CoreDryRun(console=output.console)

        checks = dry.validate_core(
            input_path=input_file,
            output_path=output_file,
            item_name=preset,
            item_type="preset",
            config=config,
        )

        preset_def = config.presets.get(preset)
        resolved = ""
        chain_commands = None

        if preset_def is not None:
            if preset_def.composite:
                composite_def = config.composites.get(preset_def.composite)
                if composite_def is not None:
                    chain_commands = _resolve_chain_commands(
                        composite_def.chain,
                        config,
                        input_file,
                        output_file,
                    )
                    chain_str = " -> ".join(s.effect for s in composite_def.chain)
                    resolved = f"chain: {chain_str}"
                else:
                    composite_name = preset_def.composite
                    resolved = f"# Cannot resolve: unknown composite '{composite_name}'"
            elif preset_def.effect:
                effect_def = config.effects.get(preset_def.effect)
                if effect_def is not None:
                    chain_executor = ChainExecutor(config, None)
                    final_params = chain_executor._get_params_with_defaults(
                        preset_def.effect,
                        preset_def.params,
                    )
                    resolved = _resolve_command(
                        effect_def.command,
                        input_file,
                        output_file,
                        final_params,
                    )
                else:
                    resolved = f"# Cannot resolve: unknown effect '{preset_def.effect}'"
            else:
                resolved = f"# Preset '{preset}' has no effect or composite defined"
        else:
            resolved = f"# Cannot resolve: unknown preset '{preset}'"

        if output.verbosity == Verbosity.QUIET:
            if chain_commands:
                for cmd in chain_commands:
                    output.console.print(cmd)
            else:
                output.console.print(resolved)
        else:
            dry.render_process(
                item_name=preset,
                item_type="preset",
                input_path=input_file,
                output_path=output_file,
                params=preset_def.params if preset_def else {},
                resolved_command=resolved,
                chain_commands=chain_commands,
            )
            dry.render_validation(checks)

        raise typer.Exit(0)

    # Normal execution path
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
        result = chain_executor.execute_chain(
            composite_def.chain, input_file, output_file
        )
    elif preset_def.effect:
        effect_def = config.effects.get(preset_def.effect)
        if effect_def is None:
            output.error(f"Preset references unknown effect: {preset_def.effect}")
            raise typer.Exit(1)
        params = chain_executor._get_params_with_defaults(
            preset_def.effect, preset_def.params
        )
        result = executor.execute(effect_def.command, input_file, output_file, params)
    else:
        output.error(f"Preset '{preset}' has no effect or composite defined")
        raise typer.Exit(1)

    if result.success:
        output.success(f"Created {output_file}")
    else:
        output.error(f"Failed: {result.stderr}")
        raise typer.Exit(1)
