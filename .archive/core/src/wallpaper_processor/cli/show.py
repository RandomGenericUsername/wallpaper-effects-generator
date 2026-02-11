"""Show commands for listing effects, composites, and presets."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich.table import Table

if TYPE_CHECKING:
    from wallpaper_processor.config.schema import EffectsConfig
    from wallpaper_processor.console.output import RichOutput

show_app = typer.Typer(help="Show available effects, composites, and presets")


def _get_context(ctx: typer.Context) -> tuple[RichOutput, EffectsConfig]:
    """Get output and config from context."""
    return ctx.obj["output"], ctx.obj["config"]


@show_app.command("effects")
def show_effects(ctx: typer.Context) -> None:
    """List all available effects."""
    output, config = _get_context(ctx)

    table = Table(title="Available Effects")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Parameters", style="dim")

    for name, effect in sorted(config.effects.items()):
        params = (
            ", ".join(effect.parameters.keys()) if effect.parameters else "-"
        )
        table.add_row(name, effect.description, params)

    output.table(table)


@show_app.command("composites")
def show_composites(ctx: typer.Context) -> None:
    """List all available composite effects."""
    output, config = _get_context(ctx)

    table = Table(title="Available Composites")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Chain", style="dim")

    for name, composite in sorted(config.composites.items()):
        chain = " → ".join(step.effect for step in composite.chain)
        table.add_row(name, composite.description, chain)

    output.table(table)


@show_app.command("presets")
def show_presets(ctx: typer.Context) -> None:
    """List all available presets."""
    output, config = _get_context(ctx)

    table = Table(title="Available Presets")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Type", style="dim")
    table.add_column("Target", style="dim")

    for name, preset in sorted(config.presets.items()):
        if preset.composite:
            preset_type = "composite"
            target = preset.composite
        else:
            preset_type = "effect"
            target = preset.effect or "-"
        table.add_row(name, preset.description, preset_type, target)

    output.table(table)


@show_app.command("all")
def show_all(ctx: typer.Context) -> None:
    """List all effects, composites, and presets."""
    output, config = _get_context(ctx)

    output.rule("Effects")
    show_effects(ctx)
    output.newline()

    output.rule("Composites")
    show_composites(ctx)
    output.newline()

    output.rule("Presets")
    show_presets(ctx)
