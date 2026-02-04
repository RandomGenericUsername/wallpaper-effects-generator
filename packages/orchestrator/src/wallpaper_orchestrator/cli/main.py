"""Main CLI entry point for wallpaper_orchestrator."""

import typer

from layered_settings import configure
from wallpaper_orchestrator.cli.commands import install, uninstall
from wallpaper_orchestrator.config.unified import UnifiedConfig

# Configure layered_settings at module import
configure(UnifiedConfig, app_name="wallpaper-effects")

# Create Typer app
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with container orchestration",
    no_args_is_help=True,
)

# Add orchestrator-specific commands
app.command()(install)
app.command()(uninstall)

# TODO: Add core command wrapping in next task


if __name__ == "__main__":
    app()
