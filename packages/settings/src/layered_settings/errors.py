"""Error hierarchy for layered_settings package."""


class SettingsError(Exception):
    """Base exception for all settings-related errors."""

    pass


class SettingsFileError(SettingsError):
    """Exception raised when there are file loading or parsing errors."""

    def __init__(self, filepath: str, reason: str) -> None:
        """Initialize SettingsFileError.

        Args:
            filepath: Path to the file that caused the error
            reason: Description of why the error occurred
        """
        self.filepath = filepath
        self.reason = reason
        message = f"Error loading {filepath}: {reason}"
        super().__init__(message)


class SettingsRegistryError(SettingsError):
    """Exception raised when there are registration conflicts."""

    def __init__(self, namespace: str, reason: str) -> None:
        """Initialize SettingsRegistryError.

        Args:
            namespace: The namespace that caused the error
            reason: Description of why the error occurred
        """
        self.namespace = namespace
        self.reason = reason
        message = f"Registry error for namespace '{namespace}': {reason}"
        super().__init__(message)


class SettingsValidationError(SettingsError):
    """Exception raised when Pydantic validation fails."""

    def __init__(self, config_name: str, reason: str) -> None:
        """Initialize SettingsValidationError.

        Args:
            config_name: Name of the configuration that failed validation
            reason: Description of why validation failed
        """
        self.config_name = config_name
        self.reason = reason
        message = f"Validation error for '{config_name}': {reason}"
        super().__init__(message)
