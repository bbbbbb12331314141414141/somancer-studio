# Contributing to Somancer Studio

Thank you for your interest in contributing to Sonmancer Studio! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and improve

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch**: `git checkout -b feature/my-feature`
4. **Make your changes** following [CODING_STANDARDS.md](docs/CODING_STANDARDS.md)
5. **Commit with clear messages**: `git commit -m "feat: add thing"`
6. **Push to your fork**: `git push origin feature/my-feature`
7. **Create a Pull Request** on GitHub

## Development Setup

See [SETUP.md](docs/SETUP.md) for detailed setup instructions.

## Code Quality

Before submitting a PR:

```bash
pnpm lint       # Check code style
pnpm format     # Auto-format code
pnpm type-check # Check types
pnpm test       # Run tests
```

All checks must pass before merge.

## Commit Messages

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example:**
```
feat(lyrics): Add AI-generated lyrics endpoint

Implement songwriter agent integration with support for mood
and theme customization. Uses Ollama for local inference.

Closes #42
```

## Branch Naming

- Feature: `feature/add-vocal-effects`
- Bug fix: `fix/audio-dropout-issue`
- Documentation: `docs/update-setup-guide`

## Pull Request Process

1. **Fill out the PR template** completely
2. **Link related issues** (Closes #123)
3. **Describe your changes** clearly
4. **Request reviewers** (at least one)
5. **Respond to feedback** promptly
6. **Keep commits clean** (no merge commits)

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for 80%+ code coverage
- Test cross-platform when possible

## Documentation

- Update README if user-facing changes
- Update PHASES.md if roadmap changes
- Add docstrings to complex functions
- Include examples in API documentation

## Questions?

- Check [FAQ](docs/SETUP.md#troubleshooting)
- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Open a GitHub Discussion for ideas

---

**Happy coding! 🎵**
