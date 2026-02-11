"""Main CLI entry point for wallpaper_core."""

from pathlib import Path
from typing import Annotated

import typer
from layered_effects import configure as configure_effects
from layered_effects import load_effects
from layered_effects.errors import (
    EffectsError,
    EffectsLoadError,
    EffectsValidationError,
)
from layered_settings import configure, get_config
from pydantic import BaseModel

from wallpaper_core.cli import batch, process, show
from wallpaper_core.config.schema import CoreSettings, Verbosity
from wallpaper_core.console.output import RichOutput
from wallpaper_core.effects import get_package_effects_file


class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    # effects: EffectsConfig  # REMOVED - now handled by layered-effects


# Configure layered_settings at module import
configure(CoreOnlyConfig, app_name="wallpaper-effects")

# Configure layered_effects for effects configuration
configure_effects(
    package_effects_file=get_package_effects_file(), project_root=Path.cwd()
)

# Create Typer app
app = typer.Typer(
    name="wallpaper-core",
    help="Wallpaper effects processor with layered configuration",
    no_args_is_help=True,
)

# Add commands
app.add_typer(process.app, name="process")
app.add_typer(batch.app, name="batch")
app.add_typer(show.app, name="show")


def _get_verbosity(quiet: bool, verbose: int) -> Verbosity:
    """Determine verbosity level from flags."""
    if quiet:
        return Verbosity.QUIET
    if verbose >= 2:
        return Verbosity.DEBUG
    if verbose >= 1:
        return Verbosity.VERBOSE
    return Verbosity.NORMAL


@app.callback()
def main(
    ctx: typer.Context,
    quiet: Annotated[
        bool,
        typer.Option("-q", "--quiet", help="Quiet mode (errors only)"),
    ] = False,
    verbose: Annotated[
        int,
        typer.Option(
            "-v",
            "--verbose",
            count=True,
            help="Verbose mode (-v or -vv for debug)",
        ),
    ] = 0,
) -> None:
    """Wallpaper Effects Processor - Apply ImageMagick effects to images."""
    # Get core settings from layered_settings
    config_obj = get_config()

    # Get verbosity early for error output
    verbosity = _get_verbosity(quiet, verbose)
    output = RichOutput(verbosity)

    # Load effects configuration with comprehensive error handling
    try:
        effects_config = load_effects()
    except EffectsLoadError as e:
        output.error("[bold red]Failed to load effects configuration[/bold red]")
        output.error(f"Layer: {getattr(e, 'layer', 'unknown')}")
        output.error(f"File: {e.file_path}")
        output.error(f"Reason: {e.reason}")
        raise typer.Exit(1) from e
    except EffectsValidationError as e:
        output.error("[bold red]Effects configuration validation failed[/bold red]")
        output.error(f"Layer: {e.layer or 'merged'}")
        output.error(f"Problem: {e.message}")
        output.newline()
        output.error("[dim]Check your effects.yaml for:[/dim]")
        output.error("  • Undefined parameter types referenced in effects")
        output.error("  • Missing required fields (description, command)")
        output.error("  • Invalid YAML syntax")
        raise typer.Exit(1) from e
    except EffectsError as e:
        output.error(f"[bold red]Effects error:[/bold red] {e}")
        raise typer.Exit(1) from e

    # Store context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbosity
    ctx.obj["output"] = output
    ctx.obj["config"] = effects_config  # Changed from config_obj.effects
    ctx.obj["settings"] = config_obj.core  # type: ignore[attr-defined]


@app.command()
def version() -> None:
    """Show version information."""
    from wallpaper_core import __version__

    output = RichOutput()
    output.info(f"wallpaper-effects v{__version__}")


@app.command()
def info() -> None:
    """Show current configuration."""
    try:
        config = get_config()
        effects = load_effects()  # Load effects from layered-effects
    except Exception as e:  # pragma: no cover
        typer.echo(f"Error: {type(e).__name__}: {e}", err=True)
        raise typer.Exit(1) from e

    typer.echo("=== Core Settings ===")
    typer.echo(f"Parallel: {config.core.execution.parallel}")  # type: ignore[attr-defined]
    typer.echo(f"Strict: {config.core.execution.strict}")  # type: ignore[attr-defined]
    typer.echo(f"Max Workers: {config.core.execution.max_workers}")  # type: ignore[attr-defined]
    typer.echo(f"Verbosity: {config.core.output.verbosity.name}")  # type: ignore[attr-defined]
    typer.echo(f"Backend Binary: {config.core.backend.binary}")  # type: ignore[attr-defined]

    typer.echo("\n=== Effects ===")
    typer.echo(f"Version: {effects.version}")
    typer.echo(f"Effects defined: {len(effects.effects)}")

    if effects.effects:
        typer.echo("\nAvailable effects:")
        for effect_name in sorted(effects.effects.keys()):
            effect = effects.effects[effect_name]
            typer.echo(f"  - {effect_name}: {effect.description}")


if __name__ == "__main__":
    app()
