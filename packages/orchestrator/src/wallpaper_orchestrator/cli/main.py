"""Main CLI entry point for wallpaper_orchestrator."""

from pathlib import Path

import typer
from layered_effects import configure as configure_effects
from layered_effects import load_effects
from layered_settings import configure, get_config
from rich.console import Console
from wallpaper_core.cli import batch as core_batch_module
from wallpaper_core.cli import show as core_show_module
from wallpaper_core.dry_run import CoreDryRun
from wallpaper_core.effects import get_package_effects_file

from wallpaper_orchestrator.cli.commands import install, uninstall
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager
from wallpaper_orchestrator.dry_run import OrchestratorDryRun

# Configure layered_settings at module import
configure(UnifiedConfig, app_name="wallpaper-effects")

# Configure layered_effects for effects discovery
configure_effects(
    package_effects_file=get_package_effects_file(),
    project_root=Path.cwd(),
)

# Create console for rich output
console = Console()

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with container orchestration",
    no_args_is_help=True,
)

# Add orchestrator-specific commands
app.command()(install)
app.command()(uninstall)

# Create process sub-app for containerized execution
process_app = typer.Typer(
    name="process",
    help="Process images with effects (runs in container)",
    no_args_is_help=True,
)


@process_app.command("effect")
def process_effect(
    input_file: Path = typer.Argument(..., help="Input image file"),  # noqa: B008
    output_file: Path = typer.Argument(..., help="Output image file"),  # noqa: B008
    effect: str = typer.Argument(..., help="Effect name to apply"),  # noqa: B008
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),  # noqa: B008
) -> None:
    """Apply single effect to image (runs in container).

    Examples:
        wallpaper-process process effect input.jpg output.jpg blur
        wallpaper-process process effect photo.png blurred.png gaussian_blur
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            image_name = manager.get_image_name()

            # Build host command string
            abs_input = input_file.absolute()
            abs_output_dir = output_file.parent.absolute()
            cmd_parts = [manager.engine, "run", "--rm"]
            if manager.engine == "podman":
                cmd_parts.append("--userns=keep-id")
            cmd_parts.extend(
                [
                    "-v",
                    f"{abs_input}:/input/image.jpg:ro",
                    "-v",
                    f"{abs_output_dir}:/output:rw",
                    image_name,
                    "process",
                    "effect",
                    "/input/image.jpg",
                    f"/output/{output_file.name}",
                    "--effect",
                    effect,
                ]
            )
            host_command = " ".join(cmd_parts)

            # Resolve inner ImageMagick command
            effects_config = load_effects()
            effect_def = effects_config.effects.get(effect)
            if effect_def:
                from wallpaper_core.cli.process import _resolve_command
                from wallpaper_core.engine.chain import ChainExecutor

                chain_exec = ChainExecutor(effects_config)
                params = chain_exec._get_params_with_defaults(effect, {})
                inner_command = _resolve_command(
                    effect_def.command,
                    Path("/input/image.jpg"),
                    Path(f"/output/{output_file.name}"),
                    params,
                )
            else:
                inner_command = f"<effect '{effect}' not found in config>"

            renderer.render_container_process(
                item_name=effect,
                item_type="effect",
                input_path=input_file,
                output_path=output_file,
                engine=manager.engine,
                image_name=image_name,
                host_command=host_command,
                inner_command=inner_command,
            )

            # Validation
            core_checks = CoreDryRun(console=console).validate_core(
                input_path=input_file,
                output_path=output_file,
                item_name=effect,
                item_type="effect",
                config=effects_config,
            )
            container_checks = renderer.validate_container(
                engine=manager.engine,
                image_name=image_name,
            )
            renderer.render_validation(core_checks + container_checks)
            raise typer.Exit(0)

        # Validate container image
        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        # Execute in container
        console.print(f"[cyan]Processing with effect:[/cyan] {effect}")
        result = manager.run_process(
            command_type="effect",
            command_name=effect,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(f"[red]Effect failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(f"[green]✓ Output written to:[/green] {output_file}")

    except typer.Exit:
        raise
    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@process_app.command("composite")
def process_composite(
    input_file: Path = typer.Argument(..., help="Input image file"),  # noqa: B008
    output_file: Path = typer.Argument(..., help="Output image file"),  # noqa: B008
    composite: str = typer.Argument(..., help="Composite name to apply"),  # noqa: B008
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),  # noqa: B008
) -> None:
    """Apply composite effect to image (runs in container).

    Examples:
        wallpaper-process process composite input.jpg output.jpg dark
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            image_name = manager.get_image_name()

            # Build host command string
            abs_input = input_file.absolute()
            abs_output_dir = output_file.parent.absolute()
            cmd_parts = [manager.engine, "run", "--rm"]
            if manager.engine == "podman":
                cmd_parts.append("--userns=keep-id")
            cmd_parts.extend(
                [
                    "-v",
                    f"{abs_input}:/input/image.jpg:ro",
                    "-v",
                    f"{abs_output_dir}:/output:rw",
                    image_name,
                    "process",
                    "composite",
                    "/input/image.jpg",
                    f"/output/{output_file.name}",
                    "--composite",
                    composite,
                ]
            )
            host_command = " ".join(cmd_parts)

            # Resolve inner commands (composite is a chain)
            effects_config = load_effects()
            composite_def = effects_config.composites.get(composite)
            if composite_def:
                from wallpaper_core.cli.process import _resolve_chain_commands

                inner_commands = _resolve_chain_commands(
                    composite_def.chain,
                    effects_config,
                    Path("/input/image.jpg"),
                    Path(f"/output/{output_file.name}"),
                )
                inner_command = (
                    " && ".join(inner_commands)
                    if inner_commands
                    else "<empty chain>"
                )
            else:
                inner_command = (
                    f"<composite '{composite}' not found in config>"
                )

            renderer.render_container_process(
                item_name=composite,
                item_type="composite",
                input_path=input_file,
                output_path=output_file,
                engine=manager.engine,
                image_name=image_name,
                host_command=host_command,
                inner_command=inner_command,
            )

            # Validation
            core_checks = CoreDryRun(console=console).validate_core(
                input_path=input_file,
                output_path=output_file,
                item_name=composite,
                item_type="composite",
                config=effects_config,
            )
            container_checks = renderer.validate_container(
                engine=manager.engine,
                image_name=image_name,
            )
            renderer.render_validation(core_checks + container_checks)
            raise typer.Exit(0)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(f"[cyan]Processing with composite:[/cyan] {composite}")
        result = manager.run_process(
            command_type="composite",
            command_name=composite,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(f"[red]Composite failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(f"[green]✓ Output written to:[/green] {output_file}")

    except typer.Exit:
        raise
    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@process_app.command("preset")
def process_preset(
    input_file: Path = typer.Argument(..., help="Input image file"),  # noqa: B008
    output_file: Path = typer.Argument(..., help="Output image file"),  # noqa: B008
    preset: str = typer.Argument(..., help="Preset name to apply"),  # noqa: B008
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),  # noqa: B008
) -> None:
    """Apply preset to image (runs in container).

    Examples:
        wallpaper-process process preset input.jpg output.jpg dark_vibrant
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            image_name = manager.get_image_name()

            # Build host command string
            abs_input = input_file.absolute()
            abs_output_dir = output_file.parent.absolute()
            cmd_parts = [manager.engine, "run", "--rm"]
            if manager.engine == "podman":
                cmd_parts.append("--userns=keep-id")
            cmd_parts.extend(
                [
                    "-v",
                    f"{abs_input}:/input/image.jpg:ro",
                    "-v",
                    f"{abs_output_dir}:/output:rw",
                    image_name,
                    "process",
                    "preset",
                    "/input/image.jpg",
                    f"/output/{output_file.name}",
                    "--preset",
                    preset,
                ]
            )
            host_command = " ".join(cmd_parts)

            # Resolve inner command (preset points to effect or composite)
            effects_config = load_effects()
            preset_def = effects_config.presets.get(preset)
            if preset_def:
                if preset_def.effect:
                    effect_def = effects_config.effects.get(preset_def.effect)
                    if effect_def:
                        from wallpaper_core.cli.process import _resolve_command
                        from wallpaper_core.engine.chain import ChainExecutor

                        chain_exec = ChainExecutor(effects_config)
                        params = chain_exec._get_params_with_defaults(
                            preset_def.effect, preset_def.params or {}
                        )
                        inner_command = _resolve_command(
                            effect_def.command,
                            Path("/input/image.jpg"),
                            Path(f"/output/{output_file.name}"),
                            params,
                        )
                    else:
                        inner_command = (
                            f"<effect '{preset_def.effect}' not found>"
                        )
                elif preset_def.composite:
                    composite_def = effects_config.composites.get(
                        preset_def.composite
                    )
                    if composite_def:
                        from wallpaper_core.cli.process import (
                            _resolve_chain_commands,
                        )

                        inner_commands = _resolve_chain_commands(
                            composite_def.chain,
                            effects_config,
                            Path("/input/image.jpg"),
                            Path(f"/output/{output_file.name}"),
                        )
                        inner_command = (
                            " && ".join(inner_commands)
                            if inner_commands
                            else "<empty chain>"
                        )
                    else:
                        inner_command = (
                            f"<composite '{preset_def.composite}' not found>"
                        )
                else:
                    inner_command = "<preset has neither effect nor composite>"
            else:
                inner_command = f"<preset '{preset}' not found in config>"

            renderer.render_container_process(
                item_name=preset,
                item_type="preset",
                input_path=input_file,
                output_path=output_file,
                engine=manager.engine,
                image_name=image_name,
                host_command=host_command,
                inner_command=inner_command,
            )

            # Validation
            core_checks = CoreDryRun(console=console).validate_core(
                input_path=input_file,
                output_path=output_file,
                item_name=preset,
                item_type="preset",
                config=effects_config,
            )
            container_checks = renderer.validate_container(
                engine=manager.engine,
                image_name=image_name,
            )
            renderer.render_validation(core_checks + container_checks)
            raise typer.Exit(0)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(f"[cyan]Processing with preset:[/cyan] {preset}")
        result = manager.run_process(
            command_type="preset",
            command_name=preset,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(f"[red]Preset failed:[/red]\n{result.stderr}")
            raise typer.Exit(result.returncode)

        console.print(f"[green]✓ Output written to:[/green] {output_file}")

    except typer.Exit:
        raise
    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


# Add process sub-app to main app
app.add_typer(process_app, name="process")


# Create batch and show sub-apps with proper context initialization
batch_app = typer.Typer(
    name="batch",
    help="Batch generate effects (runs on host)",
    no_args_is_help=True,
)

show_app = typer.Typer(
    name="show",
    help="Show available effects, composites, and presets",
    no_args_is_help=True,
)


@batch_app.callback()
def batch_callback(ctx: typer.Context) -> None:
    """Initialize context for batch commands."""
    from wallpaper_core.console.output import RichOutput

    config = get_config()
    ctx.ensure_object(dict)
    ctx.obj["output"] = RichOutput()
    ctx.obj["config"] = config.effects
    ctx.obj["settings"] = config.core


@show_app.callback()
def show_callback(ctx: typer.Context) -> None:
    """Initialize context for show commands."""
    from wallpaper_core.console.output import RichOutput

    config = get_config()
    ctx.ensure_object(dict)
    ctx.obj["output"] = RichOutput()
    ctx.obj["config"] = config.effects
    ctx.obj["settings"] = config.core


# Add core commands to the sub-apps
for cmd_info in core_batch_module.app.registered_commands:
    batch_app.command(name=cmd_info.name)(cmd_info.callback)

for cmd_info in core_show_module.app.registered_commands:
    show_app.command(name=cmd_info.name)(cmd_info.callback)

# Add the sub-apps to main app
app.add_typer(batch_app, name="batch")
app.add_typer(show_app, name="show")


@app.command()
def info() -> None:
    """Show current configuration (runs on host)."""
    from wallpaper_core.cli.main import info as core_info

    core_info()


@app.command()
def version() -> None:
    """Show version information (runs on host)."""
    from wallpaper_orchestrator import __version__

    console.print(f"wallpaper-orchestrator v{__version__}")


if __name__ == "__main__":
    app()
