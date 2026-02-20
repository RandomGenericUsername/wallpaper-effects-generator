"""Install command to build wallpaper effects container image."""

import subprocess  # nosec: necessary for container management
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from layered_settings import get_config
from wallpaper_orchestrator.dry_run import OrchestratorDryRun

console = Console()


def install(
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
    """Build container image for wallpaper effects processing.

    This command builds a Docker/Podman image containing wallpaper_core
    plus ImageMagick and all required dependencies.

    Examples:

        # Install with default engine (docker)
        wallpaper-process install

        # Install with podman
        wallpaper-process install --engine podman
    """
    try:
        # Determine container engine
        if engine is None:
            # Load from config if not specified
            config = get_config()
            container_engine = config.orchestrator.container.engine  # type: ignore[attr-defined]
        else:
            container_engine = engine.lower()
            if container_engine not in ["docker", "podman"]:
                console.print(
                    f"[red]Error:[/red] Invalid engine '{container_engine}'. "
                    "Must be 'docker' or 'podman'."
                )
                raise typer.Exit(1)

        # Find project root (where packages/ directory is)
        # This file is at:
        # packages/orchestrator/src/wallpaper_orchestrator/cli/commands/install.py
        # Project root is: ../../../../../../..
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent.parent.parent.parent
        docker_dir = project_root / "packages" / "orchestrator" / "docker"
        dockerfile = docker_dir / "Dockerfile.imagemagick"

        if not dockerfile.exists():
            console.print(f"[red]Error:[/red] Dockerfile not found at {dockerfile}")
            raise typer.Exit(1)

        image_name = "wallpaper-effects:latest"

        console.print(
            f"[cyan]Building {image_name} using {container_engine}...[/cyan]\n"
        )

        # Build docker command
        cmd = [
            container_engine,
            "build",
            "-f",
            str(dockerfile),
            "-t",
            image_name,
            str(project_root),
        ]

        if dry_run:
            renderer = OrchestratorDryRun(console=console)
            renderer.render_install(
                engine=container_engine,
                image_name=image_name,
                dockerfile=dockerfile,
                build_command=" ".join(cmd),
            )
            # Validation
            checks = renderer.validate_container(
                engine=container_engine, image_name=image_name
            )
            # Check Dockerfile exists
            from layered_settings.dry_run import ValidationCheck

            checks.insert(
                0,
                ValidationCheck(
                    name="Dockerfile exists",
                    passed=dockerfile.exists(),
                    detail=str(dockerfile),
                ),
            )
            renderer.render_validation(checks)
            raise typer.Exit(0)

        # Show progress while building
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Building {image_name}...",
                total=None,
            )

            try:
                result = subprocess.run(  # nosec: B603
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                )

                if result.returncode == 0:
                    progress.update(task, description=f"✓ Built {image_name}")
                    console.print(f"\n[green]✓ Successfully built {image_name}[/green]")
                    raise typer.Exit(0)
                else:
                    progress.update(task, description=f"✗ Failed to build {image_name}")
                    console.print("\n[red]✗ Build failed[/red]")
                    console.print(f"[dim]{result.stderr}[/dim]")
                    raise typer.Exit(1)

            except subprocess.SubprocessError as e:
                progress.update(task, description=f"✗ Error building {image_name}")
                console.print(f"\n[red]✗ Build error:[/red] {str(e)}")
                raise typer.Exit(1) from None

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        raise typer.Exit(1) from None
