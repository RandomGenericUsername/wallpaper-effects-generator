"""Tests for engine batch module."""

from pathlib import Path

from wallpaper_core.effects.schema import EffectsConfig
from wallpaper_core.engine.batch import BatchGenerator, BatchResult


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
        generator = BatchGenerator(config=sample_effects_config)
        assert generator.config == sample_effects_config
        assert generator.parallel is True
        assert generator.strict is True

    def test_generate_all_effects(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with effects."""
        generator = BatchGenerator(config=sample_effects_config)

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.effects)
        assert result.succeeded > 0

    def test_generate_all_effects_flat(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with flat output for effects."""
        generator = BatchGenerator(config=sample_effects_config)

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
            flat=True,
        )

        assert result.total == len(sample_effects_config.effects)

    def test_generate_all_composites(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with composites."""
        generator = BatchGenerator(config=sample_effects_config)

        result = generator.generate_all_composites(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.composites)

    def test_generate_all_presets(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with presets."""
        generator = BatchGenerator(config=sample_effects_config)

        result = generator.generate_all_presets(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.presets)

    def test_generate_all(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with all types."""
        generator = BatchGenerator(config=sample_effects_config)

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

    def test_parallel_execution_composites(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test parallel batch execution with composites."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            strict=False,
        )

        result = generator.generate_all_composites(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.composites)

    def test_parallel_execution_presets(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test parallel batch execution with presets."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            strict=False,
        )

        result = generator.generate_all_presets(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total == len(sample_effects_config.presets)

    def test_sequential_execution(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test sequential batch execution."""
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

    def test_sequential_strict_false(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test sequential execution with strict=False."""
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

    def test_parallel_strict_true(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test parallel execution with strict=True."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            strict=True,
        )

        result = generator.generate_all_presets(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total > 0

    def test_generate_all_with_max_workers(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test generate_all with custom max_workers."""
        generator = BatchGenerator(
            config=sample_effects_config,
            parallel=True,
            max_workers=2,
        )

        result = generator.generate_all_effects(
            input_path=test_image_file,
            output_dir=tmp_path,
        )

        assert result.total > 0
        assert result.succeeded > 0
