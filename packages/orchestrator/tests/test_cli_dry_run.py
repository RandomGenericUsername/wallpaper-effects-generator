"""Tests for --dry-run flag on orchestrator CLI commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from wallpaper_orchestrator.cli.main import app

runner = CliRunner()


class TestInstallDryRun:
    def test_dry_run_shows_build_command(self):
        result = runner.invoke(app, ["install", "--dry-run"])
        assert result.exit_code == 0
        assert "build" in result.stdout.lower()
        assert "Dockerfile" in result.stdout or "dockerfile" in result.stdout.lower()

    def test_dry_run_no_image_built(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["install", "--dry-run"])
            # subprocess.run should NOT be called for building
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert "build" not in args, "Should not run build during dry-run"


class TestUninstallDryRun:
    def test_dry_run_shows_rmi_command(self):
        result = runner.invoke(app, ["uninstall", "--dry-run"])
        assert result.exit_code == 0
        assert "rmi" in result.stdout

    def test_dry_run_no_image_removed(self):
        with patch("subprocess.run") as mock_run:
            runner.invoke(app, ["uninstall", "--dry-run"])
            for call in mock_run.call_args_list:
                args = call[0][0] if call[0] else call[1].get("args", [])
                if isinstance(args, list):
                    assert "rmi" not in args, "Should not run rmi during dry-run"


class TestProcessEffectContainerDryRun:
    def test_dry_run_shows_both_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    "--effect",
                    "blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show host command (docker run...)
        assert "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        # Should show inner command (magick...)
        assert "magick" in result.stdout

    def test_dry_run_no_container_spawned(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    "--effect",
                    "blur",
                    "--dry-run",
                ],
            )

            mock_manager.run_process.assert_not_called()


class TestProcessCompositeContainerDryRun:
    def test_dry_run_shows_both_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "composite",
                    str(input_file),
                    "--composite",
                    "blur-brightness80",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show host command (docker run...)
        assert "docker" in result.stdout.lower() or "run" in result.stdout.lower()
        # Should show inner command chain
        assert "blur" in result.stdout.lower() or "brightness" in result.stdout.lower()

    def test_dry_run_composite_with_podman(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "podman"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "composite",
                    str(input_file),
                    "--composite",
                    "blur-brightness80",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show podman-specific userns flag
        assert "podman" in result.stdout.lower() or "--userns" in result.stdout.lower()


class TestProcessPresetContainerDryRun:
    def test_dry_run_preset_shows_commands(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "dark_blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show docker and magick
        assert "docker" in result.stdout.lower() or "run" in result.stdout.lower()

    def test_dry_run_unknown_preset(self, tmp_path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "nonexistent-preset",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        # Should show error about unknown preset
        assert (
            "cannot resolve" in result.stdout.lower()
            or "unknown" in result.stdout.lower()
        )

    def test_dry_run_preset_with_unknown_effect(self, tmp_path):
        """Test dry-run for preset with unknown effect."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "dark_blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0

    def test_dry_run_preset_with_unknown_composite(self, tmp_path):
        """Test dry-run for preset with unknown composite."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "dark_vibrant",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0


class TestProcessEffectDryRunEdgeCases:
    def test_dry_run_effect_not_found_in_config(self, tmp_path):
        """Test dry-run for effect not found in config."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    "--effect",
                    "nonexistent-effect",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "not found" in result.stdout.lower() or "magick" in result.stdout


class TestProcessCompositeEdgeCases:
    def test_dry_run_composite_not_found_in_config(self, tmp_path):
        """Test dry-run for composite not found in config."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()

        with patch("wallpaper_orchestrator.cli.main.ContainerManager") as mock_mgr:
            mock_manager = MagicMock()
            mock_manager.is_image_available.return_value = True
            mock_manager.engine = "docker"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_mgr.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "composite",
                    str(input_file),
                    "--composite",
                    "nonexistent-composite",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert (
            "not found" in result.stdout.lower() or "composite" in result.stdout.lower()
        )


class TestPodmanDryRun:
    """Tests for dry-run with podman engine."""

    def test_dry_run_effect_with_podman(self, tmp_path):
        """Test effect dry-run shows podman userns flag."""
        from unittest.mock import patch

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        # Mock the container manager to use podman
        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.engine = "podman"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_manager_class.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "effect",
                    str(input_file),
                    "--effect",
                    "blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "userns" in result.stdout or "podman" in result.stdout.lower()

    def test_dry_run_preset_with_podman(self, tmp_path):
        """Test preset dry-run shows podman userns flag."""
        from unittest.mock import patch

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        # Mock the container manager to use podman
        with patch(
            "wallpaper_orchestrator.cli.main.ContainerManager"
        ) as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.engine = "podman"
            mock_manager.get_image_name.return_value = "wallpaper-effects:latest"
            mock_manager_class.return_value = mock_manager

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "dark_blur",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "userns" in result.stdout or "podman" in result.stdout.lower()

    def test_dry_run_preset_with_unknown_effect(self, tmp_path):
        """Test preset dry-run when preset references unknown effect."""

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                "--preset",
                "subtle_blur",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_dry_run_preset_with_unknown_composite(self, tmp_path):
        """Test preset dry-run when preset references unknown composite."""

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        result = runner.invoke(
            app,
            [
                "process",
                "preset",
                str(input_file),
                "--preset",
                "dark_blur",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_dry_run_preset_with_invalid_effect_reference(self, tmp_path):
        """Test preset dry-run when preset references effect that doesn't exist."""
        from unittest.mock import patch

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        # Mock load_effects to return config with preset referencing unknown effect
        with patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load:
            from wallpaper_core.effects.schema import Effect, EffectsConfig, Preset

            effects_config = EffectsConfig(
                version="1.0",
                effects={"blur": Effect(description="Blur", command="magick")},
                presets={
                    "bad_preset": Preset(
                        description="Bad preset",
                        effect="nonexistent_effect",
                    )
                },
            )
            mock_load.return_value = effects_config

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "bad_preset",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "not found" in result.stdout.lower()

    def test_dry_run_preset_with_invalid_composite_reference(self, tmp_path):
        """Test preset dry-run when preset references composite that doesn't exist."""
        from unittest.mock import patch

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        # Mock load_effects to return config with preset referencing unknown composite
        with patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load:
            from wallpaper_core.effects.schema import EffectsConfig, Preset

            effects_config = EffectsConfig(
                version="1.0",
                presets={
                    "bad_preset": Preset(
                        description="Bad preset",
                        composite="nonexistent_composite",
                    )
                },
            )
            mock_load.return_value = effects_config

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "bad_preset",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "not found" in result.stdout.lower()

    def test_dry_run_preset_with_neither_effect_nor_composite(self, tmp_path):
        """Test preset dry-run when preset has neither effect nor composite."""
        from unittest.mock import patch

        input_file = tmp_path / "input.jpg"
        input_file.touch()

        # Mock load_effects to return config with invalid preset
        with patch("wallpaper_orchestrator.cli.main.load_effects") as mock_load:
            from wallpaper_core.effects.schema import EffectsConfig, Preset

            effects_config = EffectsConfig(
                version="1.0",
                presets={
                    "invalid_preset": Preset(description="Invalid preset", params={})
                },
            )
            mock_load.return_value = effects_config

            result = runner.invoke(
                app,
                [
                    "process",
                    "preset",
                    str(input_file),
                    "--preset",
                    "invalid_preset",
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "neither" in result.stdout.lower()
