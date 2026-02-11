# Contributing

Guidelines for contributing to the project.

---

## Getting Started

1. Fork the repository
2. Clone your fork
3. Set up development environment (see [Setup](setup.md))
4. Create a feature branch

```bash
git checkout -b feature/my-feature
```

---

## Development Workflow

1. Make changes
2. Write/update tests
3. Run tests and linting
4. Commit with descriptive message
5. Push and create pull request

---

## Commit Messages

Use conventional commits:

```
type(scope): description

[optional body]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance

Examples:

```
feat(effects): add sharpen effect
fix(batch): handle empty output directory
docs(guides): add extending effects guide
```

---

## Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: What and why
3. **Tests**: Include tests for changes
4. **Documentation**: Update docs if needed
5. **Single purpose**: One feature/fix per PR

---

## Code Review

- Be respectful and constructive
- Focus on code, not person
- Explain reasoning for suggestions
- Approve once concerns addressed

---

## Adding New Effects

See [Extending Effects](../guides/extending-effects.md) for adding effects via configuration.

For code changes:

1. Update `effects/effects.yaml` if adding built-in effect
2. Add tests in `tests/`
3. Update documentation

---

## See Also

- [Code Style](code-style.md)
- [Testing](testing.md)
