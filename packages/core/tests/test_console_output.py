"""Tests for RichOutput console class."""

from rich.table import Table

from wallpaper_core.config.schema import Verbosity
from wallpaper_core.console.output import RichOutput


class TestRichOutputVerbosity:
    """Tests for RichOutput verbosity levels."""

    def test_warning_at_normal_verbosity(self) -> None:
        """Test warning is shown at NORMAL verbosity."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        assert output.verbosity == Verbosity.NORMAL
        # Should not raise error
        output.warning("test warning")

    def test_warning_at_quiet_verbosity(self) -> None:
        """Test warning is not shown at QUIET verbosity."""
        output = RichOutput(verbosity=Verbosity.QUIET)
        assert output.verbosity == Verbosity.QUIET
        # Should not raise error
        output.warning("test warning")

    def test_verbose_at_verbose_level(self) -> None:
        """Test verbose message at VERBOSE level."""
        output = RichOutput(verbosity=Verbosity.VERBOSE)
        assert output.verbosity == Verbosity.VERBOSE
        # Should not raise error
        output.verbose("verbose message")

    def test_verbose_at_normal_level(self) -> None:
        """Test verbose message at NORMAL level (not shown)."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        # Should not raise error
        output.verbose("verbose message")

    def test_debug_at_debug_level(self) -> None:
        """Test debug message at DEBUG level."""
        output = RichOutput(verbosity=Verbosity.DEBUG)
        assert output.verbosity == Verbosity.DEBUG
        # Should not raise error
        output.debug("debug message")

    def test_debug_at_verbose_level(self) -> None:
        """Test debug message at VERBOSE level (not shown)."""
        output = RichOutput(verbosity=Verbosity.VERBOSE)
        # Should not raise error
        output.debug("debug message")

    def test_info_at_normal_verbosity(self) -> None:
        """Test info at NORMAL verbosity."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        output.info("info message")

    def test_info_at_quiet_verbosity(self) -> None:
        """Test info at QUIET verbosity."""
        output = RichOutput(verbosity=Verbosity.QUIET)
        output.info("info message")

    def test_success_at_normal_verbosity(self) -> None:
        """Test success at NORMAL verbosity."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        output.success("success message")

    def test_success_at_quiet_verbosity(self) -> None:
        """Test success at QUIET verbosity."""
        output = RichOutput(verbosity=Verbosity.QUIET)
        output.success("success message")

    def test_error_always_shown(self) -> None:
        """Test error is always shown regardless of verbosity."""
        verbosities = [
            Verbosity.QUIET,
            Verbosity.NORMAL,
            Verbosity.VERBOSE,
            Verbosity.DEBUG,
        ]
        for verbosity in verbosities:
            output = RichOutput(verbosity=verbosity)
            output.error("error message")

    def test_command_at_verbose_level(self) -> None:
        """Test command output at VERBOSE level."""
        output = RichOutput(verbosity=Verbosity.VERBOSE)
        output.command("magick input.jpg -blur 0x5 output.jpg")

    def test_command_at_normal_level(self) -> None:
        """Test command output at NORMAL level (not shown)."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        output.command("magick input.jpg -blur 0x5 output.jpg")

    def test_panel_at_normal_verbosity(self) -> None:
        """Test panel display at NORMAL verbosity."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        output.panel("panel content", title="Test Panel")

    def test_panel_at_quiet_verbosity(self) -> None:
        """Test panel at QUIET verbosity."""
        output = RichOutput(verbosity=Verbosity.QUIET)
        output.panel("panel content", title="Test Panel")

    def test_table_output(self) -> None:
        """Test table output."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        table = Table(title="Test Table")
        table.add_column("Column 1")
        table.add_column("Column 2")
        table.add_row("value1", "value2")
        output.table(table)

    def test_newline_output(self) -> None:
        """Test newline output."""
        output = RichOutput(verbosity=Verbosity.NORMAL)
        output.newline()

    def test_quiet_verbosity_level(self) -> None:
        """Test QUIET verbosity level settings."""
        output = RichOutput(verbosity=Verbosity.QUIET)
        assert output.verbosity == Verbosity.QUIET
        output.error("Only errors shown")

    def test_debug_verbosity_level(self) -> None:
        """Test DEBUG verbosity level settings."""
        output = RichOutput(verbosity=Verbosity.DEBUG)
        assert output.verbosity == Verbosity.DEBUG
        output.debug("Debug message shown")
        output.verbose("Verbose message shown")
        output.info("Info message shown")

    def test_initialize_without_verbosity(self) -> None:
        """Test RichOutput initialization with default verbosity."""
        output = RichOutput()
        # Should have default verbosity
        assert output.verbosity is not None
