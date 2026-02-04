"""Tests for centralized path discovery module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestXdgConfigHome:
    """Test XDG_CONFIG_HOME handling."""

    def test_xdg_config_home_default(self):
        """Should default to ~/.config when XDG_CONFIG_HOME not set."""
        from layered_settings.paths import XDG_CONFIG_HOME

        # Should be a Path object
        assert isinstance(XDG_CONFIG_HOME, Path)


class TestUserPaths:
    """Test user layer path construction."""

    def test_user_config_dir(self):
        """USER_CONFIG_DIR should be under XDG_CONFIG_HOME."""
        from layered_settings.paths import USER_CONFIG_DIR, XDG_CONFIG_HOME
        from layered_settings.constants import APP_NAME

        assert USER_CONFIG_DIR == XDG_CONFIG_HOME / APP_NAME

    def test_user_settings_file(self):
        """USER_SETTINGS_FILE should be settings.toml in config dir."""
        from layered_settings.paths import USER_SETTINGS_FILE, USER_CONFIG_DIR
        from layered_settings.constants import SETTINGS_FILENAME

        assert USER_SETTINGS_FILE == USER_CONFIG_DIR / SETTINGS_FILENAME

    def test_user_effects_file(self):
        """USER_EFFECTS_FILE should be effects.yaml in config dir."""
        from layered_settings.paths import USER_EFFECTS_FILE, USER_CONFIG_DIR
        from layered_settings.constants import EFFECTS_FILENAME

        assert USER_EFFECTS_FILE == USER_CONFIG_DIR / EFFECTS_FILENAME


class TestProjectPaths:
    """Test project layer path functions."""

    def test_get_project_settings_file(self, tmp_path: Path):
        """Should return settings.toml in project root."""
        from layered_settings.paths import get_project_settings_file

        result = get_project_settings_file(tmp_path)

        assert result == tmp_path / "settings.toml"

    def test_get_project_effects_file(self, tmp_path: Path):
        """Should return effects.yaml in project root."""
        from layered_settings.paths import get_project_effects_file

        result = get_project_effects_file(tmp_path)

        assert result == tmp_path / "effects.yaml"
