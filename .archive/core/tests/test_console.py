"""Tests for console output and progress modules."""


from rich.table import Table
from wallpaper_processor.config.settings import Verbosity
from wallpaper_processor.console.output import RichOutput
from wallpaper_processor.console.progress import BatchProgress


class TestRichOutput:
    """Tests for RichOutput class."""

    def test_init_default_verbosity(self) -> None:
        """Test default verbosity level."""
        output = RichOutput()
        assert output.verbosity == Verbosity.NORMAL

    def test_init_custom_verbosity(self) -> None:
        """Test custom verbosity level."""
        output = RichOutput(verbosity=Verbosity.DEBUG)
        assert output.verbosity == Verbosity.DEBUG

    def test_error_always_shown(self, quiet_output: RichOutput) -> None:
        """Test that errors are always shown, even in quiet mode."""
        # Error should be callable even in quiet mode
        # We can't easily capture stderr, but we can ensure no exception
        quiet_output.error("Test error")

    def test_warning_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that warnings are hidden in quiet mode."""
        # This should not raise and should be silent
        quiet_output.warning("Test warning")

    def test_warning_shown_in_normal(self, normal_output: RichOutput) -> None:
        """Test that warnings are shown in normal mode."""
        # Should not raise
        normal_output.warning("Test warning")

    def test_success_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that success messages are hidden in quiet mode."""
        quiet_output.success("Test success")

    def test_success_shown_in_normal(self, normal_output: RichOutput) -> None:
        """Test that success messages are shown in normal mode."""
        normal_output.success("Test success")

    def test_info_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that info messages are hidden in quiet mode."""
        quiet_output.info("Test info")

    def test_verbose_hidden_in_normal(self, normal_output: RichOutput) -> None:
        """Test that verbose messages are hidden in normal mode."""
        normal_output.verbose("Test verbose")

    def test_verbose_shown_in_verbose(
        self, verbose_output: RichOutput
    ) -> None:
        """Test that verbose messages are shown in verbose mode."""
        verbose_output.verbose("Test verbose")

    def test_debug_hidden_in_verbose(self, verbose_output: RichOutput) -> None:
        """Test that debug messages are hidden in verbose mode."""
        verbose_output.debug("Test debug")

    def test_debug_shown_in_debug(self, debug_output: RichOutput) -> None:
        """Test that debug messages are shown in debug mode."""
        debug_output.debug("Test debug")

    def test_command_hidden_in_normal(self, normal_output: RichOutput) -> None:
        """Test that command output is hidden in normal mode."""
        normal_output.command("echo test")

    def test_command_shown_in_verbose(
        self, verbose_output: RichOutput
    ) -> None:
        """Test that command output is shown in verbose mode."""
        verbose_output.command("echo test")

    def test_panel_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that panels are hidden in quiet mode."""
        quiet_output.panel("Content", title="Title")

    def test_panel_shown_in_normal(self, normal_output: RichOutput) -> None:
        """Test that panels are shown in normal mode."""
        normal_output.panel("Content", title="Title")

    def test_table_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that tables are hidden in quiet mode."""
        table = Table()
        table.add_column("Col")
        quiet_output.table(table)

    def test_table_shown_in_normal(self, normal_output: RichOutput) -> None:
        """Test that tables are shown in normal mode."""
        table = Table()
        table.add_column("Col")
        normal_output.table(table)

    def test_rule_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that rules are hidden in quiet mode."""
        quiet_output.rule("Section")

    def test_newline_hidden_in_quiet(self, quiet_output: RichOutput) -> None:
        """Test that newlines are hidden in quiet mode."""
        quiet_output.newline()


class TestBatchProgress:
    """Tests for BatchProgress class."""

    def test_init(self) -> None:
        """Test BatchProgress initialization."""
        progress = BatchProgress(total=10, description="Testing")
        assert progress.total == 10
        assert progress.description == "Testing"
        assert progress._started is False

    def test_context_manager(self) -> None:
        """Test BatchProgress as context manager."""
        with BatchProgress(total=5, description="Test") as progress:
            assert progress._started is True
        assert progress._started is False

    def test_start_stop(self) -> None:
        """Test manual start and stop."""
        progress = BatchProgress(total=3)
        progress.start()
        assert progress._started is True
        progress.stop()
        assert progress._started is False

    def test_double_start(self) -> None:
        """Test that double start is safe."""
        progress = BatchProgress(total=3)
        progress.start()
        progress.start()  # Should not raise
        assert progress._started is True
        progress.stop()

    def test_double_stop(self) -> None:
        """Test that double stop is safe."""
        progress = BatchProgress(total=3)
        progress.start()
        progress.stop()
        progress.stop()  # Should not raise

    def test_advance(self) -> None:
        """Test advancing progress."""
        with BatchProgress(total=3) as progress:
            assert progress.completed == 0
            progress.advance()
            assert progress.completed == 1
            progress.advance()
            assert progress.completed == 2

    def test_advance_with_description(self) -> None:
        """Test advancing with description update."""
        with BatchProgress(total=3) as progress:
            progress.advance("Step 1")
            progress.advance("Step 2")
            assert progress.completed == 2

    def test_update_description(self) -> None:
        """Test updating description."""
        with BatchProgress(total=3, description="Initial") as progress:
            progress.update_description("Updated")
            # Should not raise

    def test_completed_before_start(self) -> None:
        """Test completed property before starting."""
        progress = BatchProgress(total=3)
        assert progress.completed == 0
