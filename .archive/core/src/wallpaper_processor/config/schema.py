"""Pydantic models for effects.yaml schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParameterType(BaseModel):
    """Definition of a reusable parameter type."""

    type: str = Field(description="Type: string, integer, float, boolean")
    pattern: str | None = Field(default=None, description="Regex pattern for validation")
    min: int | float | None = Field(default=None, description="Minimum value")
    max: int | float | None = Field(default=None, description="Maximum value")
    default: Any = Field(default=None, description="Default value")
    description: str = Field(default="", description="Human-readable description")


class ParameterDefinition(BaseModel):
    """Definition of a parameter for an effect."""

    type: str = Field(description="Reference to parameter_types or inline type")
    cli_flag: str = Field(description="CLI flag like --blur")
    default: Any = Field(default=None, description="Default value override")
    description: str = Field(default="", description="Human-readable description")


class EffectDefinition(BaseModel):
    """Definition of an atomic effect."""

    description: str = Field(default="", description="Human-readable description")
    command: str = Field(description="Shell command template with $INPUT, $OUTPUT, $PARAM")
    parameters: dict[str, ParameterDefinition] = Field(
        default_factory=dict, description="Parameter definitions"
    )


class ChainStep(BaseModel):
    """A step in a composite effect chain."""

    effect: str = Field(description="Effect name to apply")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Parameter values for this step"
    )


class CompositeDefinition(BaseModel):
    """Definition of a composite effect (chain of effects)."""

    description: str = Field(default="", description="Human-readable description")
    chain: list[ChainStep] = Field(description="Ordered list of effects to apply")


class PresetDefinition(BaseModel):
    """Definition of a preset (named configuration)."""

    description: str = Field(default="", description="Human-readable description")
    effect: str | None = Field(default=None, description="Single effect name")
    composite: str | None = Field(default=None, description="Composite effect name")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Parameter values"
    )


class EffectsConfig(BaseModel):
    """Root configuration for effects.yaml."""

    version: str = Field(default="1.0", description="Config schema version")
    parameter_types: dict[str, ParameterType] = Field(
        default_factory=dict, description="Reusable parameter type definitions"
    )
    effects: dict[str, EffectDefinition] = Field(
        default_factory=dict, description="Atomic effect definitions"
    )
    composites: dict[str, CompositeDefinition] = Field(
        default_factory=dict, description="Composite effect definitions"
    )
    presets: dict[str, PresetDefinition] = Field(
        default_factory=dict, description="Preset definitions"
    )

