"""Pydantic models for effects.yaml configuration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParameterType(BaseModel):
    """Reusable parameter type definition.

    Defines a type that can be referenced by effect parameters.
    Supports validation rules like pattern matching and min/max ranges.
    """

    type: str = Field(description="Type name: string, integer, or float")
    pattern: str | None = Field(
        default=None, description="Regex pattern for string validation"
    )
    min: int | float | None = Field(
        default=None, description="Minimum value for numeric types"
    )
    max: int | float | None = Field(
        default=None, description="Maximum value for numeric types"
    )
    default: Any = Field(description="Default value for this parameter type")
    description: str | None = Field(
        default=None, description="Human-readable description of the type"
    )


class ParameterDefinition(BaseModel):
    """Parameter definition for an effect.

    References a parameter type and optionally overrides the default value.
    Can specify CLI flag for command-line interface.
    """

    type: str = Field(description="Reference to a parameter_type name")
    cli_flag: str | None = Field(
        default=None, description="Command-line flag for this parameter"
    )
    default: Any = Field(default=None, description="Override default value")
    description: str | None = Field(
        default=None, description="Human-readable description"
    )


class Effect(BaseModel):
    """Atomic effect definition (single ImageMagick command).

    Defines a single transformation that can be applied to an image.
    Parameters can use variables that will be substituted in the command.
    """

    description: str = Field(description="Human-readable description of the effect")
    command: str = Field(
        description="Shell command template with $INPUT, $OUTPUT, and parameter variables"
    )
    parameters: dict[str, ParameterDefinition] = Field(
        default_factory=dict, description="Effect parameters keyed by name"
    )


class ChainStep(BaseModel):
    """Single step in a composite effect chain.

    References an effect and provides parameter values for that effect.
    """

    effect: str = Field(description="Name of the effect to apply")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Parameter values for this effect"
    )


class CompositeEffect(BaseModel):
    """Composite effect (chain of atomic effects).

    Applies multiple effects in sequence, passing the output of each
    effect as input to the next.
    """

    description: str = Field(
        description="Human-readable description of the composite effect"
    )
    chain: list[ChainStep] = Field(
        description="Ordered list of effects to apply in sequence"
    )


class Preset(BaseModel):
    """Named preset configuration.

    A preset can reference either a composite effect or a single effect
    with specific parameter values. Provides user-friendly shortcuts.
    """

    description: str = Field(description="Human-readable description of the preset")
    composite: str | None = Field(
        default=None, description="Reference to a composite effect name"
    )
    effect: str | None = Field(
        default=None, description="Reference to a single effect name"
    )
    params: dict[str, Any] = Field(
        default_factory=dict, description="Parameter values when using single effect"
    )


class EffectsConfig(BaseModel):
    """Complete effects configuration from effects.yaml.

    Root model containing all effect definitions, parameter types,
    composite effects, and presets. This is the top-level schema
    that validates the entire effects.yaml file.
    """

    version: str = Field(description="Configuration schema version")
    parameter_types: dict[str, ParameterType] = Field(
        default_factory=dict, description="Reusable parameter type definitions"
    )
    effects: dict[str, Effect] = Field(
        default_factory=dict, description="Atomic effect definitions"
    )
    composites: dict[str, CompositeEffect] = Field(
        default_factory=dict, description="Composite effect chains"
    )
    presets: dict[str, Preset] = Field(
        default_factory=dict, description="Named preset configurations"
    )
