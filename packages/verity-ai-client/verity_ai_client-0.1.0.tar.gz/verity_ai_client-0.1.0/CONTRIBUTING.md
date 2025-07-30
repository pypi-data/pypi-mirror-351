# Contributing to Verity AI Python Client

Thank you for your interest in contributing to the Verity AI Python Client! We welcome contributions from the community and are grateful for your help in making this project better.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/verity-ai-python-client.git
   cd verity-ai-python-client
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e .[dev]
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **flake8** for linting

Run these tools before submitting:

```bash
# Format code
black .
isort .

# Type checking
mypy verity_ai_pyc

# Linting
flake8 verity_ai_pyc
```

### Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
pytest
```

For coverage reports:

```bash
pytest --cov=verity_ai_pyc --cov-report=html
```

### Pre-commit Hooks

We recommend setting up pre-commit hooks to automatically run code quality checks:

```bash
pip install pre-commit
pre-commit install
```

## 📝 Making Changes

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes**: Fix issues in the existing codebase
- **Feature additions**: Add new functionality
- **Documentation improvements**: Enhance README, docstrings, or examples
- **Performance optimizations**: Improve efficiency
- **Test coverage**: Add or improve tests

### Guidelines

1. **Keep changes focused**: One feature or fix per pull request
2. **Write clear commit messages**: Use descriptive commit messages
3. **Add tests**: Include tests for new functionality
4. **Update documentation**: Update README or docstrings as needed
5. **Follow existing patterns**: Maintain consistency with existing code

### Commit Message Format

Use clear, descriptive commit messages:

```
type(scope): brief description

Longer description if needed

- List any breaking changes
- Reference issues: Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🔍 Pull Request Process

1. **Ensure your code passes all checks**:
   ```bash
   black . && isort . && mypy verity_ai_pyc && flake8 verity_ai_pyc && pytest
   ```

2. **Update documentation** if needed

3. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Screenshots (if applicable)

4. **Respond to feedback** promptly and make requested changes

5. **Ensure CI passes** before requesting review

## 🐛 Reporting Issues

When reporting issues, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Code examples** that demonstrate the issue
- **Error messages** or stack traces

Use our issue templates when available.

## 💡 Feature Requests

For feature requests, please:

- **Check existing issues** to avoid duplicates
- **Describe the use case** and motivation
- **Provide examples** of how the feature would be used
- **Consider implementation** if you have ideas

## 📚 Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples for complex features
- Improve API documentation
- Create tutorials or guides

## 🤝 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## 📞 Getting Help

If you need help or have questions:

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: support@veritylabs.ai for direct support

## 🏆 Recognition

Contributors will be recognized in:

- The project's README
- Release notes for significant contributions
- Our contributors page

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Verity AI Python Client! 🎉 