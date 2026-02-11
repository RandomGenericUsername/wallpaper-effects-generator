"""Dry-run base formatting utilities.

Provides shared rendering for dry-run output across packages.
Does not contain any domain-specific logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass
class ValidationCheck:
    """Result of a single pre-flight validation check."""

    name: str
    passed: bool
    detail: str = ""


class DryRunBase:
    """Base class for dry-run rendering.

    Provides generic formatting utilities used by CoreDryRun
    and OrchestratorDryRun.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_header(self, title: str) -> None:
        """Render the dry-run header banner."""
        self.console.print(f"\n[bold cyan]Dry Run:[/bold cyan] {title}\n")

    def render_field(self, label: str, value: str) -> None:
        """Render an aligned key-value field."""
        self.console.print(
            f"  [bold]{label}:[/bold]{' ' * max(1, 12 - len(label))}{value}"
        )

    def render_command(self, label: str, command: str) -> None:
        """Render a labeled command block."""
        self.console.print(f"\n  [bold]{label}:[/bold]")
        self.console.print(f"    [dim]{command}[/dim]")

    def render_commands_list(self, commands: list[str]) -> None:
        """Render a numbered list of commands."""
        self.console.print(f"\n  [bold]Commands ({len(commands)}):[/bold]")
        for i, cmd in enumerate(commands, 1):
            self.console.print(f"    {i}. [dim]{cmd}[/dim]")

    def render_validation(self, checks: list[ValidationCheck]) -> None:
        """Render a validation checklist with pass/fail markers."""
        self.console.print("\n  [bold]Validation:[/bold]")
        for check in checks:
            if check.passed:
                detail = f" ({check.detail})" if check.detail else ""
                self.console.print(f"    [green]\u2713[/green] {check.name}{detail}")
            else:
                detail = f" ({check.detail})" if check.detail else ""
                self.console.print(f"    [red]\u2717[/red] {check.name}{detail}")

    def render_table(
        self,
        title: str,
        columns: list[str],
        rows: list[list[str]],
    ) -> None:
        """Render a Rich table with title."""
        self.console.print(f"\n  [bold]{title}[/bold]")
        table = Table(show_header=True, padding=(0, 1))
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)
