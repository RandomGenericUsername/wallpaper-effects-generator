"""Rich console output with configurable verbosity."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from wallpaper_core.config.schema import Verbosity


class RichOutput:
    """Rich console wrapper with verbosity levels."""

    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        """Initialize RichOutput.

        Args:
            verbosity: Output verbosity level
        """
        self.console = Console()
        self.error_console = Console(stderr=True)
        self.verbosity = verbosity

    def error(self, msg: str) -> None:
        """Print error message (always shown)."""
        self.error_console.print(f"[red]✗ Error:[/red] {msg}")

    def warning(self, msg: str) -> None:
        """Print warning message (shown in normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print(f"[yellow]⚠ Warning:[/yellow] {msg}")

    def success(self, msg: str) -> None:
        """Print success message (shown in normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print(f"[green]✓[/green] {msg}")

    def info(self, msg: str) -> None:
        """Print info message (shown in normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print(msg)

    def verbose(self, msg: str) -> None:
        """Print verbose message (shown in verbose+)."""
        if self.verbosity >= Verbosity.VERBOSE:
            self.console.print(f"[dim]{msg}[/dim]")

    def debug(self, msg: str) -> None:
        """Print debug message (shown in debug only)."""
        if self.verbosity >= Verbosity.DEBUG:
            self.console.print(f"[blue][DEBUG][/blue] {msg}")

    def command(self, cmd: str) -> None:
        """Print command being executed (verbose+)."""
        if self.verbosity >= Verbosity.VERBOSE:
            self.console.print(f"[dim]$ {cmd}[/dim]")

    def panel(self, content: str, title: str = "") -> None:
        """Print a panel (normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print(Panel(content, title=title))

    def table(self, table: Table) -> None:
        """Print a table (normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print(table)

    def rule(self, title: str = "") -> None:
        """Print a horizontal rule (normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.rule(title)

    def newline(self) -> None:
        """Print a newline (normal+)."""
        if self.verbosity >= Verbosity.NORMAL:
            self.console.print()
