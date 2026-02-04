# Testing

Running and writing tests.

---

## Running Tests

```bash
cd orchestrator

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=wallpaper_effects --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_container.py

# Verbose output
uv run pytest -v
```

---

## Test Categories

### Unit Tests

Test individual components without containers:

```bash
uv run pytest tests/unit/
```

### Integration Tests

Test with actual containers (requires Docker/Podman):

```bash
uv run pytest tests/integration/
```

---

## Mocking Container Runtime

For unit tests, mock the container runtime:

```python
from unittest.mock import Mock, patch

def test_process_effect():
    with patch('wallpaper_effects.container.manager.ContainerManager') as mock:
        mock_instance = Mock()
        mock_instance.run.return_value = (0, "Success", "")
        mock.return_value = mock_instance
        
        # Test code here
```

---

## Test Fixtures

```python
@pytest.fixture
def container_manager():
    """Mock container manager."""
    manager = Mock()
    manager.run.return_value = (0, "", "")
    return manager

@pytest.fixture
def test_image(tmp_path):
    """Create test image."""
    img = tmp_path / "test.png"
    # Create minimal PNG
    return img
```

---

## See Also

- [Setup](setup.md)
- [Contributing](contributing.md)

