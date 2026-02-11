"""Chain executor for composite effects."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from wallpaper_core.engine.executor import CommandExecutor, ExecutionResult

if TYPE_CHECKING:
    from wallpaper_core.console.output import RichOutput
    from wallpaper_core.effects.schema import ChainStep, EffectsConfig


class ChainExecutor:
    """Execute chains of effects using temp files."""

    def __init__(
        self,
        config: EffectsConfig,
        output: RichOutput | None = None,
    ) -> None:
        """Initialize ChainExecutor.

        Args:
            config: Effects configuration
            output: RichOutput instance for logging
        """
        self.config = config
        self.output = output
        self.executor = CommandExecutor(output)

    def execute_chain(
        self,
        chain: list[ChainStep],
        input_path: Path,
        output_path: Path,
    ) -> ExecutionResult:
        """Execute a chain of effects using temp files.

        Process flow:
        - step1: input -> temp1
        - step2: temp1 -> temp2
        - ...
        - stepN: tempN-1 -> output

        Args:
            chain: List of chain steps
            input_path: Path to input image
            output_path: Path to final output

        Returns:
            ExecutionResult for the chain
        """
        if not chain:
            return ExecutionResult(
                success=False,
                command="",
                stdout="",
                stderr="Empty chain",
                return_code=1,
            )

        # Get output format from output path
        output_suffix = output_path.suffix or ".png"

        # Create temp directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            current_input = input_path
            total_duration = 0.0

            for i, step in enumerate(chain):
                is_last = i == len(chain) - 1

                # Determine output for this step
                if is_last:
                    step_output = output_path
                else:
                    step_output = temp_path / f"step_{i}{output_suffix}"

                # Get effect definition
                effect = self.config.effects.get(step.effect)
                if effect is None:
                    return ExecutionResult(
                        success=False,
                        command="",
                        stdout="",
                        stderr=f"Unknown effect in chain: {step.effect}",
                        return_code=1,
                    )

                # Merge default params with step params
                params = self._get_params_with_defaults(step.effect, step.params)

                # Execute step
                if self.output:
                    self.output.debug(f"Chain step {i + 1}/{len(chain)}: {step.effect}")

                result = self.executor.execute(
                    effect.command,
                    current_input,
                    step_output,
                    params,
                )

                total_duration += result.duration

                if not result.success:
                    error_msg = (
                        f"Chain failed at step {i + 1} ({step.effect}): "
                        f"{result.stderr}"
                    )
                    return ExecutionResult(
                        success=False,
                        command=result.command,
                        stdout=result.stdout,
                        stderr=error_msg,
                        return_code=result.return_code,
                        duration=total_duration,
                    )

                # Next step uses this output as input
                current_input = step_output

        return ExecutionResult(
            success=True,
            command=f"chain: {' -> '.join(s.effect for s in chain)}",
            stdout="",
            stderr="",
            return_code=0,
            duration=total_duration,
        )

    def _get_params_with_defaults(
        self,
        effect_name: str,
        override_params: dict,
    ) -> dict:
        """Get parameters with defaults filled in."""
        effect = self.config.effects.get(effect_name)
        if effect is None:
            return override_params

        params = {}
        for param_name, param_def in effect.parameters.items():
            if param_name in override_params:
                params[param_name] = override_params[param_name]
            elif param_def.default is not None:
                params[param_name] = param_def.default
            else:
                # Try to get default from parameter_types
                param_type = self.config.parameter_types.get(param_def.type)
                if param_type and param_type.default is not None:
                    params[param_name] = param_type.default

        return params
