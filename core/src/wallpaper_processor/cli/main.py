"""Main CLI application using Typer."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from wallpaper_processor.cli.process import process_app
from wallpaper_processor.cli.batch import batch_app
from wallpaper_processor.cli.show import show_app
from wallpaper_processor.config.loader import ConfigLoader
from wallpaper_processor.config.settings import Verbosity
from wallpaper_processor.console.output import RichOutput

app = typer.Typer(
    name="wallpaper-effects-process",
    help="Apply ImageMagick effects to wallpapers",
    no_args_is_help=True,
)

# Add sub-commands
app.add_typer(process_app, name="process", help="Process a single image")
app.add_typer(batch_app, name="batch", help="Batch generate effects")
app.add_typer(show_app, name="show", help="Show available effects/presets")


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
    # Store verbosity in context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = _get_verbosity(quiet, verbose)
    ctx.obj["output"] = RichOutput(ctx.obj["verbosity"])
    ctx.obj["config"] = ConfigLoader.load_effects()
    ctx.obj["settings"] = ConfigLoader.load_settings()


@app.command()
def version() -> None:
    """Show version information."""
    from wallpaper_processor import __version__

    output = RichOutput()
    output.info(f"wallpaper-effects-processor v{__version__}")


if __name__ == "__main__":
    app()

