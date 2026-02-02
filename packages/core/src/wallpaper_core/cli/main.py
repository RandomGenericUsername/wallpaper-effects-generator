"""Main CLI entry point for wallpaper_core."""

import typer
from pydantic import BaseModel

from layered_settings import configure, get_config
from wallpaper_core.config.schema import CoreSettings
from wallpaper_core.effects.schema import EffectsConfig


class CoreOnlyConfig(BaseModel):
    """Configuration model for standalone core usage."""

    core: CoreSettings
    effects: EffectsConfig


# Configure layered_settings at module import
configure(CoreOnlyConfig, app_name="wallpaper-effects")

# Create Typer app
# Note: With only one command currently registered, Typer makes it the default
# (so `wallpaper-process` works instead of requiring `wallpaper-process info`).
# This behavior will change when more commands are added in Task 9.
app = typer.Typer(
    name="wallpaper-process",
    help="Wallpaper effects processor with layered configuration",
    no_args_is_help=True,
)


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
