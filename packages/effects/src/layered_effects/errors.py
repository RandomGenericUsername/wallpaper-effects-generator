"""Exception classes for the layered-effects package."""

from pathlib import Path


class EffectsError(Exception):
    """Base exception for all effects-related errors."""

    pass


class EffectsLoadError(EffectsError):
    """Raised when effects.yaml file cannot be loaded.

    Attributes:
        file_path: Path to the effects file that failed to load
        reason: Human-readable error reason
    """

    def __init__(self, file_path: Path, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to load {file_path}: {reason}")


class EffectsValidationError(EffectsError):
    """Raised when merged effects fail Pydantic validation.

    Attributes:
        message: Validation error message
        layer: Layer where validation failed (package/project/user)
    """

    def __init__(self, message: str, layer: str | None = None) -> None:
        self.message = message
        self.layer = layer

        if layer:
            super().__init__(f"Validation error in {layer} layer: {message}")
        else:
            super().__init__(f"Validation error: {message}")
