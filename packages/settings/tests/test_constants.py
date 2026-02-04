"""Tests for shared constants module."""


def test_app_name_constant():
    """APP_NAME should be defined."""
    from layered_settings.constants import APP_NAME

    assert isinstance(APP_NAME, str)
    assert len(APP_NAME) > 0


def test_settings_filename_constant():
    """SETTINGS_FILENAME should be defined."""
    from layered_settings.constants import SETTINGS_FILENAME

    assert SETTINGS_FILENAME == "settings.toml"


def test_effects_filename_constant():
    """EFFECTS_FILENAME should be defined."""
    from layered_settings.constants import EFFECTS_FILENAME

    assert EFFECTS_FILENAME == "effects.yaml"
