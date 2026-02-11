# Contributing

Guidelines for contributing to the orchestrator.

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
2. Rebuild container if needed
3. Write/update tests
4. Run tests
5. Commit with descriptive message
6. Push and create pull request

---

## Commit Messages

Use conventional commits:

```
type(scope): description
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
feat(container): add podman support
fix(batch): handle container timeout
docs(guides): add container management guide
```

---

## Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: What and why
3. **Tests**: Include tests for changes
4. **Documentation**: Update docs if needed
5. **Container**: Rebuild and test with container

---

## Adding Container Runtime Support

To add a new container runtime:

1. Create client in `src/wallpaper_effects/container/`
2. Implement `ContainerClient` interface
3. Register in `ContainerManager`
4. Add tests
5. Update documentation

---

## See Also

- [Setup](setup.md)
- [Testing](testing.md)
