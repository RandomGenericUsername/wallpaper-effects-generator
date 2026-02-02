"""Tests for effects.yaml schema models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wallpaper_core.effects.schema import (
    ChainStep,
    CompositeEffect,
    Effect,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    Preset,
)


class TestParameterType:
    """Tests for ParameterType model."""

    def test_string_type_with_pattern(self) -> None:
        """Should validate string type with pattern."""
        param = ParameterType(
            type="string",
            pattern=r"^\d+x\d+$",
            default="0x8",
            description="Blur geometry",
        )
        assert param.type == "string"
        assert param.pattern == r"^\d+x\d+$"
        assert param.default == "0x8"
        assert param.min is None
        assert param.max is None

    def test_integer_type_with_range(self) -> None:
        """Should validate integer type with min/max."""
        param = ParameterType(
            type="integer",
            min=-100,
            max=100,
            default=0,
            description="Percentage value",
        )
        assert param.type == "integer"
        assert param.min == -100
        assert param.max == 100
        assert param.default == 0
        assert param.pattern is None

    def test_float_type_with_range(self) -> None:
        """Should validate float type with min/max."""
        param = ParameterType(
            type="float",
            min=0.0,
            max=1.0,
            default=0.5,
            description="Opacity value",
        )
        assert param.type == "float"
        assert param.min == 0.0
        assert param.max == 1.0
        assert param.default == 0.5

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "type": "string",
            "pattern": r"^#[0-9a-fA-F]{6}$",
            "default": "#000000",
            "description": "Hex color code",
        }
        param = ParameterType(**data)
        assert param.type == "string"
        assert param.pattern == r"^#[0-9a-fA-F]{6}$"
        assert param.default == "#000000"


class TestParameterDefinition:
    """Tests for ParameterDefinition model."""

    def test_with_all_fields(self) -> None:
        """Should validate with type, cli_flag, default, and description."""
        param = ParameterDefinition(
            type="blur_geometry",
            cli_flag="--blur",
            default="0x8",
            description="Blur geometry (RADIUSxSIGMA)",
        )
        assert param.type == "blur_geometry"
        assert param.cli_flag == "--blur"
        assert param.default == "0x8"
        assert param.description == "Blur geometry (RADIUSxSIGMA)"

    def test_with_minimal_fields(self) -> None:
        """Should validate with only type and description."""
        param = ParameterDefinition(
            type="percent",
            description="Brightness adjustment percentage",
        )
        assert param.type == "percent"
        assert param.cli_flag is None
        assert param.default is None
        assert param.description == "Brightness adjustment percentage"

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "type": "percent",
            "cli_flag": "--brightness",
            "default": -20,
            "description": "Brightness adjustment percentage",
        }
        param = ParameterDefinition(**data)
        assert param.type == "percent"
        assert param.cli_flag == "--brightness"
        assert param.default == -20


class TestEffect:
    """Tests for Effect model."""

    def test_effect_with_parameters(self) -> None:
        """Should validate effect with command and parameters."""
        effect = Effect(
            description="Apply Gaussian blur",
            command='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
            parameters={
                "blur": ParameterDefinition(
                    type="blur_geometry",
                    cli_flag="--blur",
                    description="Blur geometry (RADIUSxSIGMA)",
                )
            },
        )
        assert effect.description == "Apply Gaussian blur"
        assert effect.command == 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"'
        assert "blur" in effect.parameters
        assert effect.parameters["blur"].type == "blur_geometry"

    def test_effect_without_parameters(self) -> None:
        """Should validate effect without parameters."""
        effect = Effect(
            description="Convert to grayscale",
            command='magick "$INPUT" -grayscale Average "$OUTPUT"',
        )
        assert effect.description == "Convert to grayscale"
        assert effect.command == 'magick "$INPUT" -grayscale Average "$OUTPUT"'
        assert effect.parameters == {}

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "description": "Apply Gaussian blur",
            "command": 'magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
            "parameters": {
                "blur": {
                    "type": "blur_geometry",
                    "cli_flag": "--blur",
                    "description": "Blur geometry (RADIUSxSIGMA)",
                }
            },
        }
        effect = Effect(**data)
        assert effect.description == "Apply Gaussian blur"
        assert "blur" in effect.parameters


class TestChainStep:
    """Tests for ChainStep model."""

    def test_chain_step_with_params(self) -> None:
        """Should validate chain step with effect and params."""
        step = ChainStep(
            effect="blur",
            params={"blur": "0x8"},
        )
        assert step.effect == "blur"
        assert step.params == {"blur": "0x8"}

    def test_chain_step_without_params(self) -> None:
        """Should validate chain step without params."""
        step = ChainStep(effect="blackwhite")
        assert step.effect == "blackwhite"
        assert step.params == {}

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "effect": "brightness",
            "params": {"brightness": -20},
        }
        step = ChainStep(**data)
        assert step.effect == "brightness"
        assert step.params == {"brightness": -20}


class TestCompositeEffect:
    """Tests for CompositeEffect model."""

    def test_composite_effect(self) -> None:
        """Should validate composite effect with chain."""
        composite = CompositeEffect(
            description="Blur then dim to 80% brightness",
            chain=[
                ChainStep(effect="blur", params={"blur": "0x8"}),
                ChainStep(effect="brightness", params={"brightness": -20}),
            ],
        )
        assert composite.description == "Blur then dim to 80% brightness"
        assert len(composite.chain) == 2
        assert composite.chain[0].effect == "blur"
        assert composite.chain[1].effect == "brightness"

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "description": "Blur then dim to 80% brightness",
            "chain": [
                {"effect": "blur", "params": {"blur": "0x8"}},
                {"effect": "brightness", "params": {"brightness": -20}},
            ],
        }
        composite = CompositeEffect(**data)
        assert composite.description == "Blur then dim to 80% brightness"
        assert len(composite.chain) == 2


class TestPreset:
    """Tests for Preset model."""

    def test_preset_with_composite(self) -> None:
        """Should validate preset referencing a composite."""
        preset = Preset(
            description="Dark blurred background for overlays",
            composite="blur-brightness80",
        )
        assert preset.description == "Dark blurred background for overlays"
        assert preset.composite == "blur-brightness80"
        assert preset.effect is None
        assert preset.params == {}

    def test_preset_with_effect(self) -> None:
        """Should validate preset with effect and params."""
        preset = Preset(
            description="Gentle blur effect",
            effect="blur",
            params={"blur": "0x4"},
        )
        assert preset.description == "Gentle blur effect"
        assert preset.effect == "blur"
        assert preset.params == {"blur": "0x4"}
        assert preset.composite is None

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "description": "Dark blurred background for overlays",
            "composite": "blur-brightness80",
        }
        preset = Preset(**data)
        assert preset.description == "Dark blurred background for overlays"
        assert preset.composite == "blur-brightness80"


class TestEffectsConfig:
    """Tests for EffectsConfig model."""

    def test_complete_config(self) -> None:
        """Should validate complete effects configuration."""
        config = EffectsConfig(
            version="1.0",
            parameter_types={
                "blur_geometry": ParameterType(
                    type="string",
                    pattern=r"^\d+x\d+$",
                    default="0x8",
                    description="Blur geometry",
                )
            },
            effects={
                "blur": Effect(
                    description="Apply Gaussian blur",
                    command='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
                    parameters={
                        "blur": ParameterDefinition(
                            type="blur_geometry",
                            cli_flag="--blur",
                            description="Blur geometry",
                        )
                    },
                )
            },
            composites={
                "blur-brightness80": CompositeEffect(
                    description="Blur then dim",
                    chain=[
                        ChainStep(effect="blur", params={"blur": "0x8"}),
                        ChainStep(effect="brightness", params={"brightness": -20}),
                    ],
                )
            },
            presets={
                "dark_blur": Preset(
                    description="Dark blurred background",
                    composite="blur-brightness80",
                )
            },
        )
        assert config.version == "1.0"
        assert "blur_geometry" in config.parameter_types
        assert "blur" in config.effects
        assert "blur-brightness80" in config.composites
        assert "dark_blur" in config.presets

    def test_minimal_config(self) -> None:
        """Should validate with only version and empty dicts."""
        config = EffectsConfig(version="1.0")
        assert config.version == "1.0"
        assert config.parameter_types == {}
        assert config.effects == {}
        assert config.composites == {}
        assert config.presets == {}

    def test_from_dict(self) -> None:
        """Should initialize from dictionary (YAML loading)."""
        data = {
            "version": "1.0",
            "parameter_types": {
                "percent": {
                    "type": "integer",
                    "min": -100,
                    "max": 100,
                    "default": 0,
                    "description": "Percentage value",
                }
            },
            "effects": {
                "blackwhite": {
                    "description": "Convert to grayscale",
                    "command": 'magick "$INPUT" -grayscale Average "$OUTPUT"',
                }
            },
            "composites": {},
            "presets": {},
        }
        config = EffectsConfig(**data)
        assert config.version == "1.0"
        assert "percent" in config.parameter_types
        assert "blackwhite" in config.effects
        assert config.effects["blackwhite"].description == "Convert to grayscale"
