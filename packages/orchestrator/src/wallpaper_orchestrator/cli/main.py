"""Main CLI entry point for wallpaper_orchestrator."""

import typer

from layered_settings import configure
from wallpaper_core.cli import main as core_cli
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

# Import and add core commands
# Note: We import the core CLI app and add its commands
# This makes all core functionality available through orchestrator
try:
    # Get the info and version commands from core
    for cmd_info in core_cli.app.registered_commands:
        callback = cmd_info.callback
        cmd_name = cmd_info.name or callback.__name__
        if cmd_name in ["info", "version"]:
            app.command(name=cmd_name)(callback)

    # Add core sub-apps (process, batch, show)
    for group_info in core_cli.app.registered_groups:
        name = group_info.name
        typer_instance = group_info.typer_instance
        app.add_typer(typer_instance, name=name)
except (AttributeError, Exception):
    # Fallback: manually register known commands
    # This ensures compatibility even if core's internal structure changes
    from wallpaper_core.cli.main import info, version

    app.command(name="info")(info)
    app.command(name="version")(version)


if __name__ == "__main__":
    app()
