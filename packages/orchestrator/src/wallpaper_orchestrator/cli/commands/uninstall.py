"""Uninstall command to remove wallpaper effects container image."""

import subprocess

import typer
from rich.console import Console

from wallpaper_orchestrator.dry_run import OrchestratorDryRun

console = Console()


def uninstall(
    yes: bool = typer.Option(  # noqa: B008
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    engine: str | None = typer.Option(  # noqa: B008
        None,
        "--engine",
        "-e",
        help="Container engine to use (docker or podman). "
        "Uses config default if not specified.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without executing"
    ),  # noqa: B008
) -> None:
    """Remove container image for wallpaper effects processing.

    This command removes the Docker/Podman image from your system.
    Use with caution as this will delete the image.

    Examples:

        # Remove image (with confirmation)
        wallpaper-process uninstall

        # Remove without confirmation
        wallpaper-process uninstall --yes

        # Use podman instead of docker
        wallpaper-process uninstall --engine podman
    """
    try:
        # Determine container engine
        if engine is None:
            container_engine = "docker"
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        image_name = "wallpaper-effects:latest"

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            cmd_str = f"{container_engine} rmi {image_name}"
            renderer.render_uninstall(
                engine=container_engine,
                image_name=image_name,
                command=cmd_str,
            )
            checks = renderer.validate_container(
                engine=container_engine, image_name=image_name
            )
            renderer.render_validation(checks)
            raise typer.Exit(0)

        # Confirm deletion
        if not yes:
            console.print(
                "[yellow]Warning:[/yellow] This will remove the image:"
            )
            console.print(f"  - {image_name}")
            console.print()

            confirm = typer.confirm("Are you sure you want to continue?")
            if not confirm:
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)

        # Remove image
        console.print(f"[cyan]Removing {image_name}...[/cyan]\n")

        cmd = [container_engine, "rmi", image_name]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Removed {image_name}[/green]")
                raise typer.Exit(0)
            else:
                # Image might not exist, which is fine
                if (
                    "no such image" in result.stderr.lower()
                    or "not found" in result.stderr.lower()
                ):
                    console.print(
                        "[dim]○ Image not found (already removed)[/dim]"
                    )
                    raise typer.Exit(0)
                else:
                    console.print("[red]✗ Failed to remove[/red]")
                    console.print(f"[dim]{result.stderr}[/dim]")
                    raise typer.Exit(1)

        except subprocess.SubprocessError as e:
            console.print(f"[red]✗ Error:[/red] {str(e)}")
            raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
