# Contributing to Speaker Diarization Project

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/speaker-diarization.git
   cd speaker-diarization
   ```
3. **Set up development environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style
- Follow PEP 8 guidelines
- Use `black` for code formatting:
  ```bash
  black src/ tests/
  ```
- Use `flake8` for linting:
  ```bash
  flake8 src/ tests/
  ```
- Use type hints and check with `mypy`:
  ```bash
  mypy src/
  ```

### Testing
- Write tests for new features
- Ensure all tests pass:
  ```bash
  pytest tests/
  ```
- Maintain test coverage above 80%:
  ```bash
  pytest --cov=src --cov-report=term
  ```

### Commit Messages
Use clear, descriptive commit messages:
```
feat: Add real-time speaker monitoring
fix: Resolve audio format conversion issue
docs: Update installation instructions
test: Add tests for identification service
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Submit pull request** with clear description

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Changelog updated

## Types of Contributions

### Bug Reports
- Use GitHub Issues
- Include reproduction steps
- Provide system information (OS, Python version, etc.)
- Include relevant logs

### Feature Requests
- Use GitHub Issues
- Describe the use case
- Explain why it's beneficial

### Code Contributions
- Bug fixes
- New features (discuss first in an issue)
- Documentation improvements
- Test coverage improvements

## Development Guidelines

### Project Structure
Follow the established structure:
```
src/
├── services/      # Core services
├── processors/    # Processing logic
├── ui/           # Streamlit UI
├── config/       # Configuration
└── utils/        # Utilities
```

### Adding Dependencies
- Update `requirements.txt`
- Update `pyproject.toml`
- Document why the dependency is needed

### Documentation
- Update relevant `.md` files in `docs/`
- Use clear, concise language
- Include code examples where helpful

## Questions?

Feel free to open an issue for any questions about contributing!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
