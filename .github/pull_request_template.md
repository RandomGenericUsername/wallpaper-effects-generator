## Description

<!-- Brief description of changes (2-3 sentences) -->

## Type of Change

- [ ] Feature (new functionality)
- [ ] Bug fix (fixes an issue)
- [ ] Documentation (docs only)
- [ ] Refactor (code improvement, no behavior change)
- [ ] Performance improvement
- [ ] Hotfix (critical production issue)
- [ ] Infrastructure/tooling

## Related Issues

Closes #
Related to #

---

## Design Compliance Checklist

### Architecture

- [ ] Changes respect separation of concerns (core vs orchestrator)
- [ ] No circular dependencies introduced
- [ ] Core has zero knowledge of containers (if applicable)
- [ ] Dependencies flow: Orchestrator → Core → Settings/Effects → Libraries

### Testing

- [ ] Coverage ≥ 95% (verify: `cd packages/<pkg> && uv run pytest --cov`)
- [ ] Unit tests for new/modified code
- [ ] Integration tests for end-to-end flows (if applicable)
- [ ] All tests pass locally (`make test-all`)
- [ ] No flaky tests introduced

### Documentation

- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Public APIs have docstrings
- [ ] User documentation updated (if user-facing change)
- [ ] Development docs updated (if process changed)

### Git Workflow

- [ ] Branch name follows convention (feature/*, bugfix/*, docs/*, etc.)
- [ ] Commits follow Conventional Commits format
- [ ] No merge commits (rebased on target branch)

### Code Quality

- [ ] Code follows existing patterns and conventions
- [ ] No commented-out code or debug statements
- [ ] No TODO comments (convert to issues instead)
- [ ] Error messages are clear and actionable

### CI/CD

- [ ] All CI checks passing
- [ ] Linting passes: `make lint`
- [ ] Security scan clean: `make security`
- [ ] Tests pass with ≥95% coverage: `make test-all`

### Security

- [ ] No hardcoded secrets or credentials
- [ ] Input validation for user-provided data
- [ ] No command injection vulnerabilities
- [ ] External dependencies reviewed

---

## Verification Commands

```bash
make lint
make test-all
make pipeline
```

## Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes documented with migration guide

---

## Self-Review Checklist

- [ ] I have reviewed my own code
- [ ] I have tested this thoroughly
- [ ] I have updated CHANGELOG.md
- [ ] This PR is ready for review
