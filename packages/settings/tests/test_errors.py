"""Tests for error hierarchy in layered_settings."""

import pytest

from layered_settings.errors import (
    SettingsError,
    SettingsFileError,
    SettingsRegistryError,
    SettingsValidationError,
)


class TestSettingsError:
    """Test the base SettingsError exception."""

    def test_inherits_from_exception(self):
        """SettingsError should inherit from Exception."""
        assert issubclass(SettingsError, Exception)

    def test_can_be_raised_with_message(self):
        """SettingsError should be raisable with a message."""
        with pytest.raises(SettingsError) as exc_info:
            raise SettingsError("test error")
        assert str(exc_info.value) == "test error"

    def test_can_be_caught_as_exception(self):
        """SettingsError should be catchable as Exception."""
        try:
            raise SettingsError("test")
        except Exception as e:
            assert isinstance(e, SettingsError)


class TestSettingsFileError:
    """Test the SettingsFileError exception."""

    def test_inherits_from_settings_error(self):
        """SettingsFileError should inherit from SettingsError."""
        assert issubclass(SettingsFileError, SettingsError)

    def test_formats_message_correctly(self):
        """SettingsFileError should format message as 'Error loading {filepath}: {reason}'."""
        error = SettingsFileError("/path/to/config.toml", "file not found")
        assert str(error) == "Error loading /path/to/config.toml: file not found"

    def test_accepts_filepath_and_reason(self):
        """SettingsFileError should accept filepath and reason parameters."""
        error = SettingsFileError(filepath="/etc/config.yaml", reason="invalid YAML")
        assert str(error) == "Error loading /etc/config.yaml: invalid YAML"

    def test_can_be_raised_and_caught(self):
        """SettingsFileError should be raisable and catchable."""
        with pytest.raises(SettingsFileError) as exc_info:
            raise SettingsFileError("/some/path", "parse error")
        assert "Error loading /some/path: parse error" in str(exc_info.value)

    def test_can_be_caught_as_settings_error(self):
        """SettingsFileError should be catchable as SettingsError."""
        try:
            raise SettingsFileError("/path", "reason")
        except SettingsError as e:
            assert isinstance(e, SettingsFileError)


class TestSettingsRegistryError:
    """Test the SettingsRegistryError exception."""

    def test_inherits_from_settings_error(self):
        """SettingsRegistryError should inherit from SettingsError."""
        assert issubclass(SettingsRegistryError, SettingsError)

    def test_formats_message_correctly(self):
        """SettingsRegistryError should format message as 'Registry error for namespace '{namespace}': {reason}'."""
        error = SettingsRegistryError("app.config", "namespace already registered")
        assert (
            str(error)
            == "Registry error for namespace 'app.config': namespace already registered"
        )

    def test_accepts_namespace_and_reason(self):
        """SettingsRegistryError should accept namespace and reason parameters."""
        error = SettingsRegistryError(namespace="core.settings", reason="duplicate key")
        assert (
            str(error) == "Registry error for namespace 'core.settings': duplicate key"
        )

    def test_can_be_raised_and_caught(self):
        """SettingsRegistryError should be raisable and catchable."""
        with pytest.raises(SettingsRegistryError) as exc_info:
            raise SettingsRegistryError("test.namespace", "conflict detected")
        assert (
            "Registry error for namespace 'test.namespace': conflict detected"
            in str(exc_info.value)
        )

    def test_can_be_caught_as_settings_error(self):
        """SettingsRegistryError should be catchable as SettingsError."""
        try:
            raise SettingsRegistryError("namespace", "reason")
        except SettingsError as e:
            assert isinstance(e, SettingsRegistryError)


class TestSettingsValidationError:
    """Test the SettingsValidationError exception."""

    def test_inherits_from_settings_error(self):
        """SettingsValidationError should inherit from SettingsError."""
        assert issubclass(SettingsValidationError, SettingsError)

    def test_formats_message_correctly(self):
        """SettingsValidationError should format message as 'Validation error for '{config_name}': {reason}'."""
        error = SettingsValidationError(
            "DatabaseConfig", "missing required field 'host'"
        )
        assert (
            str(error)
            == "Validation error for 'DatabaseConfig': missing required field 'host'"
        )

    def test_accepts_config_name_and_reason(self):
        """SettingsValidationError should accept config_name and reason parameters."""
        error = SettingsValidationError(
            config_name="AppSettings", reason="invalid type for 'port'"
        )
        assert (
            str(error) == "Validation error for 'AppSettings': invalid type for 'port'"
        )

    def test_can_be_raised_and_caught(self):
        """SettingsValidationError should be raisable and catchable."""
        with pytest.raises(SettingsValidationError) as exc_info:
            raise SettingsValidationError("MyConfig", "validation failed")
        assert "Validation error for 'MyConfig': validation failed" in str(
            exc_info.value
        )

    def test_can_be_caught_as_settings_error(self):
        """SettingsValidationError should be catchable as SettingsError."""
        try:
            raise SettingsValidationError("config", "reason")
        except SettingsError as e:
            assert isinstance(e, SettingsValidationError)


class TestErrorHierarchy:
    """Test the overall error hierarchy structure."""

    def test_all_errors_inherit_from_settings_error(self):
        """All specific errors should inherit from SettingsError."""
        errors = [SettingsFileError, SettingsRegistryError, SettingsValidationError]
        for error_class in errors:
            assert issubclass(error_class, SettingsError)

    def test_all_errors_can_be_caught_by_base_class(self):
        """All specific errors should be catchable using SettingsError."""
        errors_to_test = [
            SettingsFileError("/path", "reason"),
            SettingsRegistryError("namespace", "reason"),
            SettingsValidationError("config", "reason"),
        ]

        for error in errors_to_test:
            try:
                raise error
            except SettingsError:
                pass  # Successfully caught
            else:
                pytest.fail(f"{type(error).__name__} was not caught by SettingsError")
