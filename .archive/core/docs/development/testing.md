# Testing

Running and writing tests.

---

## Running Tests

```bash
cd core

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=wallpaper_processor --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_engine_executor.py

# Run specific test
uv run pytest tests/test_cli.py::TestProcessCommands::test_process_effect

# Verbose output
uv run pytest -v
```

---

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_cli.py           # CLI command tests
├── test_config_loader.py # Configuration loading tests
├── test_config_schema.py # Schema validation tests
├── test_config_settings.py # Settings tests
├── test_console.py       # Console output tests
├── test_engine_batch.py  # Batch generation tests
├── test_engine_chain.py  # Chain execution tests
└── test_engine_executor.py # Command execution tests
```

---

## Writing Tests

### Test File Template

```python
"""Tests for module_name."""

import pytest
from pathlib import Path


class TestClassName:
    """Tests for ClassName."""

    def test_feature(self, fixture_name: Path) -> None:
        """Test feature description."""
        # Arrange
        ...

        # Act
        result = function_under_test()

        # Assert
        assert result.expected_property == expected_value
```

### Using Fixtures

```python
def test_with_image(test_image_file: Path, tmp_path: Path) -> None:
    """Test that uses fixtures."""
    output = tmp_path / "output.png"

    # Use test_image_file as input
    result = process(test_image_file, output)

    assert output.exists()
```

---

## Key Fixtures

| Fixture | Description |
|---------|-------------|
| `test_image_file` | Path to test image |
| `tmp_path` | Temporary directory (pytest built-in) |
| `sample_effects_config` | EffectsConfig instance |
| `default_settings` | Settings instance |
| `quiet_output` | RichOutput with QUIET verbosity |
| `verbose_output` | RichOutput with VERBOSE verbosity |

---

## Coverage Requirements

Aim for:

- Overall coverage: 85%+
- Critical paths: 100%

---

## See Also

- [Setup](setup.md)
- [Contributing](contributing.md)
