"""Batch generator for processing multiple effects."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from wallpaper_processor.engine.chain import ChainExecutor
from wallpaper_processor.engine.executor import CommandExecutor, ExecutionResult

if TYPE_CHECKING:
    from wallpaper_processor.config.schema import EffectsConfig
    from wallpaper_processor.console.output import RichOutput
    from wallpaper_processor.console.progress import BatchProgress


@dataclass
class BatchResult:
    """Result of batch generation."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    results: dict[str, ExecutionResult] = field(default_factory=dict)
    output_dir: Path | None = None

    @property
    def success(self) -> bool:
        """Check if all operations succeeded."""
        return self.failed == 0


class BatchGenerator:
    """Generate multiple effects in batch."""

    def __init__(
        self,
        config: "EffectsConfig",
        output: "RichOutput | None" = None,
        parallel: bool = True,
        strict: bool = True,
        max_workers: int = 0,
    ) -> None:
        """Initialize BatchGenerator.

        Args:
            config: Effects configuration
            output: RichOutput for logging
            parallel: Run in parallel (True) or sequential (False)
            strict: Abort on first failure
            max_workers: Max parallel workers (0 = auto)
        """
        self.config = config
        self.output = output
        self.parallel = parallel
        self.strict = strict
        self.max_workers = max_workers if max_workers > 0 else None
        self.executor = CommandExecutor(output)
        self.chain_executor = ChainExecutor(config, output)

    def generate_all_effects(
        self,
        input_path: Path,
        output_dir: Path,
        flat: bool = False,
        progress: "BatchProgress | None" = None,
    ) -> BatchResult:
        """Generate all atomic effects with default params."""
        effects = list(self.config.effects.keys())
        subdir = None if flat else "effects"
        return self._generate_batch(
            input_path, output_dir, effects, "effect", subdir, progress
        )

    def generate_all_composites(
        self,
        input_path: Path,
        output_dir: Path,
        flat: bool = False,
        progress: "BatchProgress | None" = None,
    ) -> BatchResult:
        """Generate all composite effects."""
        composites = list(self.config.composites.keys())
        subdir = None if flat else "composites"
        return self._generate_batch(
            input_path, output_dir, composites, "composite", subdir, progress
        )

    def generate_all_presets(
        self,
        input_path: Path,
        output_dir: Path,
        flat: bool = False,
        progress: "BatchProgress | None" = None,
    ) -> BatchResult:
        """Generate all presets."""
        presets = list(self.config.presets.keys())
        subdir = None if flat else "presets"
        return self._generate_batch(
            input_path, output_dir, presets, "preset", subdir, progress
        )

    def generate_all(
        self,
        input_path: Path,
        output_dir: Path,
        flat: bool = False,
        progress: "BatchProgress | None" = None,
    ) -> BatchResult:
        """Generate all effects, composites, and presets."""
        result = BatchResult(output_dir=output_dir)

        # Collect all items
        items: list[tuple[str, str]] = []  # (name, type)
        for name in self.config.effects:
            items.append((name, "effect"))
        for name in self.config.composites:
            items.append((name, "composite"))
        for name in self.config.presets:
            items.append((name, "preset"))

        result.total = len(items)
        image_name = input_path.stem
        base_dir = output_dir / image_name

        # Process items
        if self.parallel:
            result = self._process_parallel(input_path, base_dir, items, flat, progress)
        else:
            result = self._process_sequential(input_path, base_dir, items, flat, progress)

        result.output_dir = base_dir
        return result

    def _generate_batch(
        self,
        input_path: Path,
        output_dir: Path,
        names: list[str],
        item_type: str,
        subdir: str | None,
        progress: "BatchProgress | None",
    ) -> BatchResult:
        """Generate a batch of items of the same type."""
        items = [(name, item_type) for name in names]
        image_name = input_path.stem
        base_dir = output_dir / image_name
        if subdir:
            base_dir = base_dir / subdir

        if self.parallel:
            result = self._process_parallel(input_path, base_dir, items, True, progress)
        else:
            result = self._process_sequential(input_path, base_dir, items, True, progress)

        result.output_dir = base_dir
        return result

    def _process_sequential(
        self,
        input_path: Path,
        base_dir: Path,
        items: list[tuple[str, str]],
        flat: bool,
        progress: "BatchProgress | None",
    ) -> BatchResult:
        """Process items sequentially."""
        result = BatchResult(total=len(items))

        for name, item_type in items:
            output_path = self._get_output_path(base_dir, name, item_type, input_path, flat)
            exec_result = self._process_item(name, item_type, input_path, output_path)
            result.results[name] = exec_result

            if exec_result.success:
                result.succeeded += 1
            else:
                result.failed += 1
                if self.strict:
                    if self.output:
                        self.output.error(f"{item_type} '{name}' failed: {exec_result.stderr}")
                    break

            if progress:
                progress.advance(name)

        return result

    def _process_parallel(
        self,
        input_path: Path,
        base_dir: Path,
        items: list[tuple[str, str]],
        flat: bool,
        progress: "BatchProgress | None",
    ) -> BatchResult:
        """Process items in parallel."""
        result = BatchResult(total=len(items))

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for name, item_type in items:
                output_path = self._get_output_path(base_dir, name, item_type, input_path, flat)
                future = executor.submit(
                    self._process_item, name, item_type, input_path, output_path
                )
                futures[future] = (name, item_type)

            for future in as_completed(futures):
                name, item_type = futures[future]
                try:
                    exec_result = future.result()
                    result.results[name] = exec_result

                    if exec_result.success:
                        result.succeeded += 1
                    else:
                        result.failed += 1
                        if self.strict:
                            if self.output:
                                self.output.error(f"{item_type} '{name}' failed")
                            # Cancel remaining futures
                            for f in futures:
                                f.cancel()
                            break

                    if progress:
                        progress.advance(name)

                except Exception as e:
                    result.failed += 1
                    result.results[name] = ExecutionResult(
                        success=False, command="", stdout="", stderr=str(e), return_code=-1
                    )
                    if self.strict:
                        break

        return result

    def _get_output_path(
        self,
        base_dir: Path,
        name: str,
        item_type: str,
        input_path: Path,
        flat: bool,
    ) -> Path:
        """Get output path for an item."""
        suffix = input_path.suffix or ".png"
        if flat:
            return base_dir / f"{name}{suffix}"
        else:
            subdir = {"effect": "effects", "composite": "composites", "preset": "presets"}
            return base_dir / subdir.get(item_type, "") / f"{name}{suffix}"

    def _process_item(
        self,
        name: str,
        item_type: str,
        input_path: Path,
        output_path: Path,
    ) -> ExecutionResult:
        """Process a single item."""
        if item_type == "effect":
            return self._process_effect(name, input_path, output_path)
        elif item_type == "composite":
            return self._process_composite(name, input_path, output_path)
        elif item_type == "preset":
            return self._process_preset(name, input_path, output_path)
        else:
            return ExecutionResult(
                success=False, command="", stdout="", stderr=f"Unknown type: {item_type}", return_code=1
            )

    def _process_effect(self, name: str, input_path: Path, output_path: Path) -> ExecutionResult:
        """Process a single effect."""
        effect = self.config.effects.get(name)
        if effect is None:
            return ExecutionResult(
                success=False, command="", stdout="", stderr=f"Unknown effect: {name}", return_code=1
            )
        params = self.chain_executor._get_params_with_defaults(name, {})
        return self.executor.execute(effect.command, input_path, output_path, params)

    def _process_composite(self, name: str, input_path: Path, output_path: Path) -> ExecutionResult:
        """Process a composite effect."""
        composite = self.config.composites.get(name)
        if composite is None:
            return ExecutionResult(
                success=False, command="", stdout="", stderr=f"Unknown composite: {name}", return_code=1
            )
        return self.chain_executor.execute_chain(composite.chain, input_path, output_path)

    def _process_preset(self, name: str, input_path: Path, output_path: Path) -> ExecutionResult:
        """Process a preset."""
        preset = self.config.presets.get(name)
        if preset is None:
            return ExecutionResult(
                success=False, command="", stdout="", stderr=f"Unknown preset: {name}", return_code=1
            )

        if preset.composite:
            # Preset references a composite
            return self._process_composite(preset.composite, input_path, output_path)
        elif preset.effect:
            # Preset references an effect with custom params
            effect = self.config.effects.get(preset.effect)
            if effect is None:
                return ExecutionResult(
                    success=False, command="", stdout="", stderr=f"Unknown effect: {preset.effect}", return_code=1
                )
            params = self.chain_executor._get_params_with_defaults(preset.effect, preset.params)
            return self.executor.execute(effect.command, input_path, output_path, params)
        else:
            return ExecutionResult(
                success=False, command="", stdout="", stderr=f"Preset '{name}' has no effect or composite", return_code=1
            )

