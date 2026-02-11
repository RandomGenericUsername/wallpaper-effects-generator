"""Dry-run rendering for wallpaper-orchestrator commands."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from layered_settings.dry_run import DryRunBase, ValidationCheck


class OrchestratorDryRun(DryRunBase):
    """Dry-run renderer for wallpaper-orchestrator commands."""

    def validate_container(
        self,
        engine: str,
        image_name: str | None = None,
    ) -> list[ValidationCheck]:
        """Run container pre-flight validation checks."""
        checks = []

        engine_path = shutil.which(engine)
        checks.append(
            ValidationCheck(
                name=f"{engine} binary found",
                passed=engine_path is not None,
                detail=engine_path or "not found on PATH",
            )
        )

        if image_name and engine_path:
            try:
                result = subprocess.run(
                    [engine, "inspect", image_name],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                available = result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                available = False
            checks.append(
                ValidationCheck(
                    name=f"Container image '{image_name}' available",
                    passed=available,
                    detail=(
                        ""
                        if available
                        else "not found — run: wallpaper-process install"
                    ),
                )
            )

        return checks

    def render_container_process(
        self,
        item_name: str,
        item_type: str,
        input_path: Path,
        output_path: Path,
        engine: str,
        image_name: str,
        host_command: str,
        inner_command: str,
    ) -> None:
        """Render container process dry-run with both command layers."""
        self.render_header(f"process {item_type} (container)")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_path))
        self.render_field(item_type.title(), item_name)
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_command("Host command", host_command)
        self.render_command(
            "Inner command (runs inside container)", inner_command
        )

    def render_install(
        self,
        engine: str,
        image_name: str,
        dockerfile: Path,
        build_command: str,
    ) -> None:
        """Render install dry-run output."""
        self.render_header("install")
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_field("Dockerfile", str(dockerfile))
        self.render_command("Command", build_command)

    def render_uninstall(
        self,
        engine: str,
        image_name: str,
        command: str,
    ) -> None:
        """Render uninstall dry-run output."""
        self.render_header("uninstall")
        self.render_field("Engine", engine)
        self.render_field("Image", image_name)
        self.render_command("Command", command)
