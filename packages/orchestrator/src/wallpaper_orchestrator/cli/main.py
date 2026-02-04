"""Main CLI entry point for wallpaper_orchestrator."""

from pathlib import Path

import typer
from rich.console import Console

from layered_settings import configure, get_config
from wallpaper_orchestrator.cli.commands import install, uninstall
from wallpaper_orchestrator.config.unified import UnifiedConfig
from wallpaper_orchestrator.container.manager import ContainerManager

# Configure layered_settings at module import
configure(UnifiedConfig, app_name="wallpaper-effects")

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
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    effect: str = typer.Argument(..., help="Effect name to apply"),  # noqa: B008
) -> None:
    """Apply single effect to image (runs in container).

    Examples:
        wallpaper-process process effect input.jpg output.jpg blur
        wallpaper-process process effect photo.png blurred.png gaussian_blur
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

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

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@process_app.command("composite")
def process_composite(
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    composite: str = typer.Argument(  # noqa: B008
        ..., help="Composite name to apply"
    ),
) -> None:
    """Apply composite effect to image (runs in container).

    Examples:
        wallpaper-process process composite input.jpg output.jpg dark
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

        if not manager.is_image_available():
            console.print(
                "[red]Error:[/red] Container image not found\n\n"
                "Install the image first:\n"
                "  wallpaper-process install"
            )
            raise typer.Exit(1)

        console.print(
            f"[cyan]Processing with composite:[/cyan] {composite}"
        )
        result = manager.run_process(
            command_type="composite",
            command_name=composite,
            input_path=input_file,
            output_path=output_file,
        )

        if result.returncode != 0:
            console.print(
                f"[red]Composite failed:[/red]\n{result.stderr}"
            )
            raise typer.Exit(result.returncode)

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


@process_app.command("preset")
def process_preset(
    input_file: Path = typer.Argument(  # noqa: B008
        ..., help="Input image file"
    ),
    output_file: Path = typer.Argument(  # noqa: B008
        ..., help="Output image file"
    ),
    preset: str = typer.Argument(..., help="Preset name to apply"),  # noqa: B008
) -> None:
    """Apply preset to image (runs in container).

    Examples:
        wallpaper-process process preset input.jpg output.jpg dark_vibrant
    """
    try:
        config = get_config()
        manager = ContainerManager(config)

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

        console.print(
            f"[green]✓ Output written to:[/green] {output_file}"
        )

    except (RuntimeError, FileNotFoundError, PermissionError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None


# Add process sub-app to main app
app.add_typer(process_app, name="process")


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
