"""Progress bar utilities using Rich."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

if TYPE_CHECKING:
    from rich.progress import TaskID


class BatchProgress:
    """Progress bar for batch operations."""

    def __init__(self, total: int, description: str = "Processing") -> None:
        """Initialize BatchProgress.

        Args:
            total: Total number of items to process
            description: Description for the progress bar
        """
        self.total = total
        self.description = description
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        )
        self._task: "TaskID | None" = None
        self._started = False

    def __enter__(self) -> "BatchProgress":
        """Start the progress bar."""
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        """Stop the progress bar."""
        self.stop()

    def start(self) -> None:
        """Start the progress bar."""
        if not self._started:
            self.progress.start()
            self._task = self.progress.add_task(self.description, total=self.total)
            self._started = True

    def stop(self) -> None:
        """Stop the progress bar."""
        if self._started:
            self.progress.stop()
            self._started = False

    def advance(self, description: str | None = None) -> None:
        """Advance the progress bar by one.

        Args:
            description: Optional new description
        """
        if self._task is not None:
            if description:
                self.progress.update(self._task, description=description)
            self.progress.advance(self._task)

    def update_description(self, description: str) -> None:
        """Update the progress bar description.

        Args:
            description: New description
        """
        if self._task is not None:
            self.progress.update(self._task, description=description)

    @property
    def completed(self) -> int:
        """Get number of completed items."""
        if self._task is not None:
            task = self.progress.tasks[self._task]
            return int(task.completed)
        return 0

