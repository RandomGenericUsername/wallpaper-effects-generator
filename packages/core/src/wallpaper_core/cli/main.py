"""Main CLI entry point for wallpaper_core."""

from typing import Annotated

import typer
from pydantic import BaseModel

from layered_settings import configure, get_config
from wallpaper_core.cli import batch, process, show
from wallpaper_core.config.schema import CoreSettings, Verbosity
from wallpaper_core.console.output import RichOutput
from wallpaper_core.effects.schema import EffectsConfig


class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    effects: EffectsConfig


# Configure layered_settings at module import
configure(CoreOnlyConfig, app_name="wallpaper-effects")

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
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
            "-v", "--verbose", count=True, help="Verbose mode (-v or -vv for debug)"
        ),
    ] = 0,
) -> None:
    """Wallpaper Effects Processor - Apply ImageMagick effects to images."""
    # Get configuration from layered_settings
    config_obj = get_config()

    # Store context for sub-commands
    ctx.ensure_object(dict)

    # Get verbosity from flags or config
    verbosity = _get_verbosity(quiet, verbose)

    ctx.obj["verbosity"] = verbosity
    ctx.obj["output"] = RichOutput(verbosity)
    ctx.obj["config"] = config_obj.effects
    ctx.obj["settings"] = config_obj.core


@app.command()
def version() -> None:
    """Show version information."""
    from wallpaper_core import __version__

    output = RichOutput()
    output.info(f"wallpaper-effects v{__version__}")


@app.command()
def info() -> None:
    """Show current configuration."""
    config = get_config()

    typer.echo("=== Core Settings ===")
    typer.echo(f"Parallel: {config.core.execution.parallel}")
    typer.echo(f"Strict: {config.core.execution.strict}")
    typer.echo(f"Max Workers: {config.core.execution.max_workers}")
    typer.echo(f"Verbosity: {config.core.output.verbosity.name}")
    typer.echo(f"Backend Binary: {config.core.backend.binary}")

    typer.echo("\n=== Effects ===")
    typer.echo(f"Version: {config.effects.version}")
    typer.echo(f"Effects defined: {len(config.effects.effects)}")

    if config.effects.effects:
        typer.echo("\nAvailable effects:")
        for effect_name in sorted(config.effects.effects.keys()):
            effect = config.effects.effects[effect_name]
            typer.echo(f"  - {effect_name}: {effect.description}")


if __name__ == "__main__":
    app()
