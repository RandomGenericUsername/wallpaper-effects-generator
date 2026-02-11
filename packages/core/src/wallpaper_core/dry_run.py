"""Dry-run rendering for wallpaper-core commands."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from layered_settings.dry_run import DryRunBase, ValidationCheck

if TYPE_CHECKING:
    from wallpaper_core.effects.schema import EffectsConfig


class CoreDryRun(DryRunBase):
    """Dry-run renderer for wallpaper-core commands."""

    def validate_core(
        self,
        input_path: Path,
        output_path: Path | None = None,
        item_name: str | None = None,
        item_type: str | None = None,
        config: EffectsConfig | None = None,
    ) -> list[ValidationCheck]:
        """Run pre-flight validation checks."""
        checks = []

        checks.append(
            ValidationCheck(
                name="Input file exists",
                passed=input_path.exists(),
                detail=(
                    str(input_path)
                    if input_path.exists()
                    else f"not found: {input_path}"
                ),
            )
        )

        magick_path = shutil.which("magick")
        checks.append(
            ValidationCheck(
                name="magick binary found",
                passed=magick_path is not None,
                detail=magick_path or "not found on PATH",
            )
        )

        if item_name and item_type and config:
            if item_type == "effect":
                found = item_name in config.effects
            elif item_type == "composite":
                found = item_name in config.composites
            elif item_type == "preset":
                found = item_name in config.presets
            else:
                found = False
            checks.append(
                ValidationCheck(
                    name=f"{item_type.title()} '{item_name}' found in config",
                    passed=found,
                    detail="" if found else f"not found in {item_type}s",
                )
            )

        if output_path:
            output_dir = output_path.parent
            dir_exists = output_dir.exists()
            checks.append(
                ValidationCheck(
                    name="Output directory exists",
                    passed=dir_exists,
                    detail=(
                        str(output_dir)
                        if dir_exists
                        else f"would be created: {output_dir}"
                    ),
                )
            )

        return checks

    def render_process(
        self,
        item_name: str,
        item_type: str,
        input_path: Path,
        output_path: Path,
        params: dict[str, Any],
        resolved_command: str,
        chain_commands: list[str] | None = None,
        command_template: str | None = None,
    ) -> None:
        """Render single process dry-run output."""
        self.render_header(f"process {item_type}")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_path))
        self.render_field(item_type.title(), item_name)

        if params:
            param_str = "  ".join(f"{k}={v}" for k, v in params.items())
            self.render_field("Params", param_str)

        if command_template:
            self.render_command("Command template", command_template)

        if chain_commands:
            self.render_commands_list(chain_commands)
        else:
            self.render_command("Command", resolved_command)

    def render_batch(
        self,
        input_path: Path,
        output_dir: Path,
        items: list[dict[str, Any]],
        parallel: bool,
        max_workers: int | None,
        strict: bool,
    ) -> None:
        """Render batch dry-run output with table and commands."""
        effects = [i for i in items if i["type"] == "effect"]
        composites = [i for i in items if i["type"] == "composite"]
        presets = [i for i in items if i["type"] == "preset"]

        self.render_header(f"batch ({len(items)} items)")
        self.render_field("Input", str(input_path))
        self.render_field("Output", str(output_dir))
        mode = (
            f"parallel ({max_workers or 'auto'} workers)" if parallel else "sequential"
        )
        self.render_field("Mode", mode)
        self.render_field("Strict", "yes" if strict else "no")

        if effects:
            self.render_table(
                title=f"Effects ({len(effects)})",
                columns=["Name", "Output Path", "Params"],
                rows=[[e["name"], e["output_path"], e["params"]] for e in effects],
            )
        if composites:
            self.render_table(
                title=f"Composites ({len(composites)})",
                columns=["Name", "Output Path", "Chain"],
                rows=[
                    [c["name"], c["output_path"], c.get("params", "\u2014")]
                    for c in composites
                ],
            )
        if presets:
            self.render_table(
                title=f"Presets ({len(presets)})",
                columns=["Name", "Output Path", "Type", "Target"],
                rows=[
                    [
                        p["name"],
                        p["output_path"],
                        p.get("preset_type", "\u2014"),
                        p.get("target", "\u2014"),
                    ]
                    for p in presets
                ],
            )

        commands = [i["command"] for i in items]
        self.render_commands_list(commands)
