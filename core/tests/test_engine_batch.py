"""Tests for engine batch module."""

from pathlib import Path

import pytest

from wallpaper_processor.config.schema import EffectsConfig
from wallpaper_processor.config.settings import Settings, Verbosity
from wallpaper_processor.console.output import RichOutput
from wallpaper_processor.engine.batch import BatchGenerator, BatchResult


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_success_all_passed(self) -> None:
        """Test success property when all passed."""
        result = BatchResult(
            total=3,
            succeeded=3,
            failed=0,
            results=[],
            output_dir=Path("/tmp"),
        )
        assert result.success is True

    def test_success_some_failed(self) -> None:
        """Test success property when some failed."""
        result = BatchResult(
            total=3,
            succeeded=2,
            failed=1,
            results=[],
            output_dir=Path("/tmp"),
        )
        assert result.success is False

    def test_success_all_failed(self) -> None:
        """Test success property when all failed."""
        result = BatchResult(
            total=3,
            succeeded=0,
            failed=3,
            results=[],
            output_dir=Path("/tmp"),
        )
        assert result.success is False


class TestBatchGenerator:
    """Tests for BatchGenerator class."""

    def test_init(self, sample_effects_config: EffectsConfig) -> None:
        """Test BatchGenerator initialization."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            strict=False,
        )
        assert generator.config is sample_effects_config
        assert generator.parallel is True
        assert generator.strict is False

    def test_generate_all_effects(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generating all effects."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=False,
            strict=False,
        )

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.effects)
        assert result.succeeded > 0
        # Output dir includes image stem subdirectory
        assert "effects" in str(result.output_dir)

    def test_generate_all_effects_flat(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generating all effects with flat output."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=False,
            strict=False,
        )

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
            flat=True,
        )

        assert result.total == len(sample_effects_config.effects)
        # Flat output still uses image stem subdirectory
        assert result.output_dir.exists()

    def test_generate_all_composites(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generating all composites."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=False,
            strict=False,
        )

        result = generator.generate_all_composites(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.composites)
        assert "composites" in str(result.output_dir)

    def test_generate_all_presets(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generating all presets."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=False,
            strict=False,
        )

        result = generator.generate_all_presets(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.presets)
        assert "presets" in str(result.output_dir)

    def test_generate_all(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generating all effects, composites, and presets."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=False,
            strict=False,
        )

        result = generator.generate_all(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        expected_total = (
            len(sample_effects_config.effects)
            + len(sample_effects_config.composites)
            + len(sample_effects_config.presets)
        )
        assert result.total == expected_total

    def test_parallel_execution(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test parallel batch execution."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            strict=False,
        )

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.effects)
        assert result.succeeded > 0

