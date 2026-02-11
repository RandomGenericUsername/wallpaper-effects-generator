"""Tests for BatchProgress console class."""

from wallpaper_core.console.progress import BatchProgress


class TestBatchProgressEdgeCases:
    """Tests for BatchProgress edge cases."""

    def test_progress_advance_before_start(self) -> None:
        """Test advancing progress before starting."""
        progress = BatchProgress(10, "Testing")
        # Should not raise error when advancing before start
        progress.advance()

    def test_progress_advance_with_description(self) -> None:
        """Test advancing progress with description."""
        progress = BatchProgress(10, "Testing")
        with progress:
            progress.advance("Step 1")
            progress.advance("Step 2")

    def test_progress_completed_before_start(self) -> None:
        """Test checking completed before start."""
        progress = BatchProgress(10, "Testing")
        # Should return 0 when not started
        assert progress.completed == 0

    def test_progress_completed_after_advances(self) -> None:
        """Test checking completed after advances."""
        progress = BatchProgress(5, "Testing")
        with progress:
            progress.advance()
            progress.advance()
            assert progress.completed == 2

    def test_progress_update_description(self) -> None:
        """Test updating description."""
        progress = BatchProgress(10, "Testing")
        with progress:
            progress.update_description("Updated")

    def test_progress_update_description_before_start(self) -> None:
        """Test updating description before start."""
        progress = BatchProgress(10, "Testing")
        # Should not raise error when updating description before start
        progress.update_description("Updated")

    def test_progress_double_start(self) -> None:
        """Test calling start twice."""
        progress = BatchProgress(10, "Testing")
        progress.start()
        progress.start()  # Should not raise error or duplicate start
        progress.stop()

    def test_progress_double_stop(self) -> None:
        """Test calling stop twice."""
        progress = BatchProgress(10, "Testing")
        progress.start()
        progress.stop()
        progress.stop()  # Should not raise error

    def test_progress_context_manager_multiple_iterations(self) -> None:
        """Test context manager with multiple iterations."""
        progress = BatchProgress(3, "Processing")
        with progress:
            for i in range(3):
                progress.advance(f"Item {i+1}")

    def test_progress_zero_total(self) -> None:
        """Test progress with zero total."""
        progress = BatchProgress(0, "Empty")
        with progress:
            progress.advance()
