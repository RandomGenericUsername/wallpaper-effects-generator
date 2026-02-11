"""Tests for config schema models."""


from wallpaper_processor.config.schema import (
    ChainStep,
    CompositeDefinition,
    EffectDefinition,
    EffectsConfig,
    ParameterDefinition,
    ParameterType,
    PresetDefinition,
)


class TestParameterType:
    """Tests for ParameterType model."""

    def test_minimal_creation(self) -> None:
        """Test creating with minimal required fields."""
        pt = ParameterType(type="string")
        assert pt.type == "string"
        assert pt.pattern is None
        assert pt.min is None
        assert pt.max is None
        assert pt.default is None
        assert pt.description == ""

    def test_full_creation(self) -> None:
        """Test creating with all fields."""
        pt = ParameterType(
            type="integer",
            pattern=r"^\d+$",
            min=0,
            max=100,
            default=50,
            description="A percentage value",
        )
        assert pt.type == "integer"
        assert pt.pattern == r"^\d+$"
        assert pt.min == 0
        assert pt.max == 100
        assert pt.default == 50
        assert pt.description == "A percentage value"

    def test_float_bounds(self) -> None:
        """Test float min/max values."""
        pt = ParameterType(type="float", min=0.0, max=1.0, default=0.5)
        assert pt.min == 0.0
        assert pt.max == 1.0
        assert pt.default == 0.5


class TestParameterDefinition:
    """Tests for ParameterDefinition model."""

    def test_minimal_creation(self) -> None:
        """Test creating with minimal required fields."""
        pd = ParameterDefinition(type="string", cli_flag="--value")
        assert pd.type == "string"
        assert pd.cli_flag == "--value"
        assert pd.default is None
        assert pd.description == ""

    def test_full_creation(self) -> None:
        """Test creating with all fields."""
        pd = ParameterDefinition(
            type="blur_geometry",
            cli_flag="--blur",
            default="0x8",
            description="Blur radius and sigma",
        )
        assert pd.type == "blur_geometry"
        assert pd.cli_flag == "--blur"
        assert pd.default == "0x8"


class TestEffectDefinition:
    """Tests for EffectDefinition model."""

    def test_minimal_creation(self) -> None:
        """Test creating effect with no parameters."""
        effect = EffectDefinition(
            command='magick "$INPUT" -grayscale Average "$OUTPUT"'
        )
        assert effect.description == ""
        assert effect.parameters == {}
        assert "$INPUT" in effect.command

    def test_with_parameters(self) -> None:
        """Test creating effect with parameters."""
        effect = EffectDefinition(
            description="Apply blur",
            command='magick "$INPUT" -blur "$BLUR" "$OUTPUT"',
            parameters={
                "blur": ParameterDefinition(
                    type="blur_geometry",
                    cli_flag="--blur",
                    default="0x8",
                ),
            },
        )
        assert effect.description == "Apply blur"
        assert "blur" in effect.parameters
        assert effect.parameters["blur"].default == "0x8"


class TestChainStep:
    """Tests for ChainStep model."""

    def test_minimal_creation(self) -> None:
        """Test creating step with only effect name."""
        step = ChainStep(effect="blur")
        assert step.effect == "blur"
        assert step.params == {}

    def test_with_params(self) -> None:
        """Test creating step with parameters."""
        step = ChainStep(effect="brightness", params={"brightness": -20})
        assert step.effect == "brightness"
        assert step.params["brightness"] == -20


class TestCompositeDefinition:
    """Tests for CompositeDefinition model."""

    def test_creation(self) -> None:
        """Test creating composite with chain."""
        composite = CompositeDefinition(
            description="Blur then dim",
            chain=[
                ChainStep(effect="blur"),
                ChainStep(effect="brightness", params={"brightness": -20}),
            ],
        )
        assert composite.description == "Blur then dim"
        assert len(composite.chain) == 2
        assert composite.chain[0].effect == "blur"
        assert composite.chain[1].effect == "brightness"


class TestPresetDefinition:
    """Tests for PresetDefinition model."""

    def test_effect_preset(self) -> None:
        """Test preset referencing an effect."""
        preset = PresetDefinition(
            description="Subtle blur",
            effect="blur",
            params={"blur": "0x3"},
        )
        assert preset.effect == "blur"
        assert preset.composite is None
        assert preset.params["blur"] == "0x3"

    def test_composite_preset(self) -> None:
        """Test preset referencing a composite."""
        preset = PresetDefinition(
            description="Dark blur",
            composite="blur-brightness",
        )
        assert preset.composite == "blur-brightness"
        assert preset.effect is None


class TestEffectsConfig:
    """Tests for EffectsConfig model."""

    def test_empty_config(self) -> None:
        """Test creating empty config."""
        config = EffectsConfig()
        assert config.version == "1.0"
        assert config.parameter_types == {}
        assert config.effects == {}
        assert config.composites == {}
        assert config.presets == {}

    def test_full_config(
        self,
        sample_parameter_types,
        sample_effects,
        sample_composites,
        sample_presets,
    ) -> None:
        """Test creating full config from fixtures."""
        config = EffectsConfig(
            version="2.0",
            parameter_types=sample_parameter_types,
            effects=sample_effects,
            composites=sample_composites,
            presets=sample_presets,
        )
        assert config.version == "2.0"
        assert "blur_geometry" in config.parameter_types
        assert "blur" in config.effects
        assert "blur-brightness" in config.composites
        assert "dark_blur" in config.presets

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary (like YAML load)."""
        data = {
            "version": "1.0",
            "effects": {
                "blur": {
                    "description": "Blur effect",
                    "command": 'magick "$INPUT" -blur 0x8 "$OUTPUT"',
                },
            },
        }
        config = EffectsConfig(**data)
        assert config.effects["blur"].description == "Blur effect"
