# Code Style

Coding standards for the project.

---

## Python Style

Follow PEP 8 with these specifics:

- Line length: 88 characters (Black default)
- Quotes: Double quotes for strings
- Imports: Sorted with isort

---

## Type Hints

Use type hints for all functions:

```python
def process_effect(
    input_path: Path,
    output_path: Path,
    effect_name: str,
    params: dict[str, Any] | None = None,
) -> ExecutionResult:
    """Process a single effect."""
    ...
```

---

## Docstrings

Use Google-style docstrings:

```python
def execute(
    self,
    effect_name: str,
    input_path: Path,
    output_path: Path,
) -> ExecutionResult:
    """Execute an effect.

    Args:
        effect_name: Name of the effect to execute.
        input_path: Path to input image.
        output_path: Path for output image.

    Returns:
        ExecutionResult with success status and duration.

    Raises:
        ValueError: If effect_name is not found.
    """
```

---

## Class Structure

```python
class ClassName:
    """Brief class description.

    Longer description if needed.
    """

    def __init__(self, arg: Type) -> None:
        """Initialize ClassName."""
        self.arg = arg

    # Public methods first
    def public_method(self) -> ReturnType:
        """Brief description."""
        ...

    # Private methods last
    def _private_method(self) -> None:
        """Brief description."""
        ...
```

---

## Formatting Tools

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

---

## Pre-commit Hooks

Consider using pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## See Also

- [Contributing](contributing.md)
- [Testing](testing.md)
