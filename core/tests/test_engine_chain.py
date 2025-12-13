"""Tests for engine chain module."""

from pathlib import Path

import pytest

from wallpaper_processor.config.schema import (
    ChainStep,
    EffectsConfig,
)
from wallpaper_processor.engine.chain import ChainExecutor
from wallpaper_processor.engine.executor import ExecutionResult


class TestChainExecutor:
    """Tests for ChainExecutor class."""

    def test_init(self, sample_effects_config: EffectsConfig) -> None:
        """Test ChainExecutor initialization."""
        executor = ChainExecutor(config=sample_effects_config)
        assert executor.config is sample_effects_config
        assert executor.output is None
        assert executor.executor is not None

    def test_execute_empty_chain(
        self, sample_effects_config: EffectsConfig, tmp_path: Path
    ) -> None:
        """Test executing empty chain returns error."""
        executor = ChainExecutor(config=sample_effects_config)

        result = executor.execute_chain(
            chain=[],
            input_path=tmp_path / "input.png",
            output_path=tmp_path / "output.png",
        )

        assert result.success is False
        assert "Empty chain" in result.stderr

    def test_execute_single_step_chain(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test executing chain with single step."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        result = executor.execute_chain(
            chain=[ChainStep(effect="blur", params={"blur": "0x5"})],
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True
        assert output_path.exists()

    def test_execute_multi_step_chain(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test executing chain with multiple steps."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        result = executor.execute_chain(
            chain=[
                ChainStep(effect="blur", params={"blur": "0x3"}),
                ChainStep(effect="brightness", params={"brightness": -10}),
            ],
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True
        assert output_path.exists()
        assert "blur" in result.command
        assert "brightness" in result.command

    def test_execute_chain_unknown_effect(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test executing chain with unknown effect fails."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        result = executor.execute_chain(
            chain=[ChainStep(effect="nonexistent")],
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is False
        assert "Unknown effect" in result.stderr

    def test_execute_chain_step_failure(
        self,
        sample_effects_config: EffectsConfig,
        tmp_path: Path,
    ) -> None:
        """Test chain stops on step failure."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        result = executor.execute_chain(
            chain=[ChainStep(effect="blur")],
            input_path=tmp_path / "nonexistent.png",
            output_path=output_path,
        )

        assert result.success is False

    def test_execute_chain_uses_defaults(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test chain uses default parameter values."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        # Don't specify params - should use defaults
        result = executor.execute_chain(
            chain=[ChainStep(effect="blur")],
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True

    def test_get_params_with_defaults(
        self, sample_effects_config: EffectsConfig
    ) -> None:
        """Test _get_params_with_defaults method."""
        executor = ChainExecutor(config=sample_effects_config)

        # With override
        params = executor._get_params_with_defaults("blur", {"blur": "0x10"})
        assert params["blur"] == "0x10"

        # Without override - should use default
        params = executor._get_params_with_defaults("blur", {})
        assert "blur" in params

    def test_get_params_unknown_effect(
        self, sample_effects_config: EffectsConfig
    ) -> None:
        """Test _get_params_with_defaults with unknown effect."""
        executor = ChainExecutor(config=sample_effects_config)
        params = executor._get_params_with_defaults("unknown", {"key": "value"})
        assert params == {"key": "value"}

    def test_chain_total_duration(
        self,
        sample_effects_config: EffectsConfig,
        test_image_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test that chain tracks total duration."""
        executor = ChainExecutor(config=sample_effects_config)
        output_path = tmp_path / "output.png"

        result = executor.execute_chain(
            chain=[
                ChainStep(effect="blur"),
                ChainStep(effect="blackwhite"),
            ],
            input_path=test_image_file,
            output_path=output_path,
        )

        assert result.success is True
        assert result.duration >= 0

