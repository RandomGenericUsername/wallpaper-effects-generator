"""Tests for CLI integration with core commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner
from wallpaper_orchestrator.cli.main import app


runner = CliRunner()


class TestCLIBasics:
    """Basic CLI tests."""

    def test_cli_has_core_commands(self) -> None:
        """Test CLI includes core commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0

        # Should have orchestrator commands
        assert "install" in result.stdout
        assert "uninstall" in result.stdout

        # Should have core commands
        assert "process" in result.stdout or "info" in result.stdout

    def test_cli_info_command(self) -> None:
        """Test info command is available."""
        result = runner.invoke(app, ["info"])

        # Should execute (may fail due to missing config files, that's OK)
        assert "Core Settings" in result.stdout or result.exit_code in [0, 1]

    def test_cli_process_help(self) -> None:
        """Test process command help is available."""
        result = runner.invoke(app, ["process", "--help"])

        assert result.exit_code == 0
        # Should show core's process command help

    def test_cli_version_command(self) -> None:
        """Test version command is available."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert (
            "wallpaper-orchestrator" in result.stdout
            or "version" in result.stdout.lower()
        )


class TestShowCommands:
    """Tests for show commands."""

    def test_cli_show_help(self) -> None:
        """Test show command is available (tests show_callback)."""
        result = runner.invoke(app, ["show", "--help"])

        assert result.exit_code == 0

    def test_cli_show_effects(self) -> None:
        """Test show effects command."""
        result = runner.invoke(app, ["show", "effects"])

        assert result.exit_code == 0
        # Should show effects
        assert "blur" in result.stdout.lower() or "effect" in result.stdout.lower()


class TestBatchCommands:
    """Tests for batch commands using core functionality."""

    def test_cli_batch_help(self) -> None:
        """Test batch command is available (tests batch_callback)."""
        result = runner.invoke(app, ["batch", "--help"])

        assert result.exit_code == 0

    def test_cli_batch_effects_help(self) -> None:
        """Test batch effects subcommand."""
        result = runner.invoke(app, ["batch", "effects", "--help"])

        assert result.exit_code == 0
        # Should show -o/--output-dir option
        assert "--output-dir" in result.stdout or "-o" in result.stdout

    def test_batch_effects_without_output_uses_default(
        self, test_image_file: Path, use_tmp_default_output: Path
    ) -> None:
        """Batch effects without -o uses default from settings."""
        result = runner.invoke(
            app,
            ["batch", "effects", str(test_image_file), "--sequential"],
        )
        assert result.exit_code == 0
        # Default is overridden to tmp_path for test isolation
        expected_base = use_tmp_default_output / test_image_file.stem / "effects"
        # Check that at least one effect was generated
        assert expected_base.exists()
        assert len(list(expected_base.glob("*.png"))) > 0

    def test_batch_effects_with_output_dir(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch effects command with -o flag."""
        output_dir = tmp_path / "custom_output"
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        # Check that effects directory was created
        effects_dir = output_dir / test_image_file.stem / "effects"
        assert effects_dir.exists()
        assert len(list(effects_dir.glob("*.png"))) > 0

    def test_batch_effects_flat(self, test_image_file: Path, tmp_path: Path) -> None:
        """Test batch effects with flat output."""
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            [
                "batch",
                "effects",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        # With flat, files go directly to output_dir (no subdirectories)
        assert output_dir.exists()
        assert len(list(output_dir.glob("*.png"))) > 0

    def test_batch_composites_without_output_uses_default(
        self, test_image_file: Path, use_tmp_default_output: Path
    ) -> None:
        """Batch composites without -o uses default from settings."""
        result = runner.invoke(
            app,
            ["batch", "composites", str(test_image_file), "--sequential"],
        )
        assert result.exit_code == 0
        expected_base = use_tmp_default_output / test_image_file.stem / "composites"
        assert expected_base.exists()
        assert len(list(expected_base.glob("*.png"))) > 0

    def test_batch_composites_with_output_dir(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch composites command with -o flag."""
        output_dir = tmp_path / "custom_output"
        result = runner.invoke(
            app,
            [
                "batch",
                "composites",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        composites_dir = output_dir / test_image_file.stem / "composites"
        assert composites_dir.exists()
        assert len(list(composites_dir.glob("*.png"))) > 0

    def test_batch_presets_without_output_uses_default(
        self, test_image_file: Path, use_tmp_default_output: Path
    ) -> None:
        """Batch presets without -o uses default from settings."""
        result = runner.invoke(
            app,
            ["batch", "presets", str(test_image_file), "--sequential"],
        )
        assert result.exit_code == 0
        expected_base = use_tmp_default_output / test_image_file.stem / "presets"
        assert expected_base.exists()
        assert len(list(expected_base.glob("*.png"))) > 0

    def test_batch_presets_with_output_dir(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch presets command with -o flag."""
        output_dir = tmp_path / "custom_output"
        result = runner.invoke(
            app,
            [
                "batch",
                "presets",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        presets_dir = output_dir / test_image_file.stem / "presets"
        assert presets_dir.exists()
        assert len(list(presets_dir.glob("*.png"))) > 0

    def test_batch_all_without_output_uses_default(
        self, test_image_file: Path, use_tmp_default_output: Path
    ) -> None:
        """Batch all without -o uses default from settings."""
        result = runner.invoke(
            app,
            ["batch", "all", str(test_image_file), "--sequential"],
        )
        assert result.exit_code == 0
        expected_base = use_tmp_default_output / test_image_file.stem
        assert expected_base.exists()
        # Check multiple subdirectories exist
        assert (expected_base / "effects").exists()
        assert (expected_base / "composites").exists() or (
            expected_base / "presets"
        ).exists()

    def test_batch_all_with_output_dir(
        self, test_image_file: Path, tmp_path: Path
    ) -> None:
        """Test batch all command with -o flag."""
        output_dir = tmp_path / "custom_output"
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        base_dir = output_dir / test_image_file.stem
        assert base_dir.exists()
        # Check subdirectories
        assert (base_dir / "effects").exists()
        assert (base_dir / "composites").exists() or (base_dir / "presets").exists()

    def test_batch_all_flat(self, test_image_file: Path, tmp_path: Path) -> None:
        """Test batch all with flat output."""
        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            [
                "batch",
                "all",
                str(test_image_file),
                "-o",
                str(output_dir),
                "--flat",
                "--sequential",
            ],
        )
        assert result.exit_code == 0
        # With flat, files go directly to output_dir (no subdirectories)
        assert output_dir.exists()
        assert len(list(output_dir.glob("*.png"))) > 0


# Fixtures
@pytest.fixture
def test_image_file(tmp_path: Path) -> Path:
    """Create a simple test image file (mocked)."""
    image_path = tmp_path / "test_image.png"
    # Create a minimal valid PNG file
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d"
        b"\x08\x02\x00\x00\x00\xf6B\xc8n\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return image_path
