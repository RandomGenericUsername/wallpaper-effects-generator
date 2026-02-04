"""Tests for show command."""

from wallpaper_effects.commands.show import (
    AVAILABLE_EFFECTS,
    AVAILABLE_PRESETS,
    run_show,
)
from wallpaper_effects.config import OrchestratorConfig


class TestAvailableEffects:
    """Tests for available effects definition."""

    def test_effects_defined(self) -> None:
        """Test that effects are defined."""
        assert len(AVAILABLE_EFFECTS) > 0

    def test_expected_effects(self) -> None:
        """Test expected effects are present."""
        expected = ["blur", "brightness", "saturation", "vignette", "grayscale"]
        for effect in expected:
            assert effect in AVAILABLE_EFFECTS

    def test_effects_have_descriptions(self) -> None:
        """Test all effects have descriptions."""
        for name, description in AVAILABLE_EFFECTS.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestAvailablePresets:
    """Tests for available presets definition."""

    def test_presets_defined(self) -> None:
        """Test that presets are defined."""
        assert len(AVAILABLE_PRESETS) > 0

    def test_expected_presets(self) -> None:
        """Test expected presets are present."""
        expected = ["dark_blur", "light_blur", "dramatic", "muted"]
        for preset in expected:
            assert preset in AVAILABLE_PRESETS


class TestRunShow:
    """Tests for run_show function."""

    def test_show_effects(self, capsys) -> None:
        """Test showing effects."""
        config = OrchestratorConfig.default()
        result = run_show(config, "effects")

        assert result == 0
        captured = capsys.readouterr()
        assert "Available Effects:" in captured.out
        assert "blur" in captured.out

    def test_show_presets(self, capsys) -> None:
        """Test showing presets."""
        config = OrchestratorConfig.default()
        result = run_show(config, "presets")

        assert result == 0
        captured = capsys.readouterr()
        assert "Available Presets:" in captured.out
        assert "dark_blur" in captured.out

    def test_show_backends(self, capsys) -> None:
        """Test showing backends."""
        config = OrchestratorConfig.default()
        result = run_show(config, "backends")

        assert result == 0
        captured = capsys.readouterr()
        assert "Available Backends:" in captured.out
        assert "imagemagick" in captured.out

    def test_show_invalid(self, capsys) -> None:
        """Test showing invalid option."""
        config = OrchestratorConfig.default()
        result = run_show(config, "invalid")

        assert result == 1
        captured = capsys.readouterr()
        assert "Unknown option" in captured.err

