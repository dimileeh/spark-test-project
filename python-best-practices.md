# Python Project Best Practices Guide

## Table of Contents
1. [Project Directory Structure](#project-directory-structure)
2. [Testing Setup with pytest](#testing-setup-with-pytest)
3. [Dependency Management](#dependency-management)
4. [CI/CD Recommendations](#cicd-recommendations)
5. [Additional Best Practices](#additional-best-practices)

## Project Directory Structure

### Standard Layout

A well-structured Python project should follow these conventions:

```
my_project/
├── README.md                 # Project description and setup instructions
├── LICENSE                   # License file
├── pyproject.toml           # Modern Python project configuration
├── requirements.txt         # Optional: for backwards compatibility
├── .gitignore              # Git ignore patterns
├── .github/                # GitHub-specific files
│   └── workflows/          # GitHub Actions workflows
├── docs/                   # Documentation
│   ├── conf.py            # Sphinx configuration (if using Sphinx)
│   └── index.md           # Main documentation
├── tests/                  # Test files
│   ├── __init__.py
│   ├── conftest.py        # pytest configuration and fixtures
│   ├── test_module1.py
│   └── test_module2.py
├── src/                    # Source code (recommended for libraries)
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       ├── module1.py
│       └── subpackage/
│           ├── __init__.py
│           └── module2.py
└── scripts/                # Utility scripts
    └── setup.sh
```

### Alternative Layout (Flat Structure)

For simpler projects or applications:

```
my_project/
├── README.md
├── pyproject.toml
├── my_project/             # Main package directory
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── test_main.py
│   └── test_utils.py
└── docs/
```

### Key Directory Principles

- **Use `src/` layout for libraries**: Prevents accidental imports of uninstalled code
- **Keep tests separate**: Place all tests in a dedicated `tests/` directory
- **Documentation folder**: Centralize all documentation in `docs/`
- **Clear naming**: Use descriptive names for modules and packages
- **Flat is better than nested**: Avoid deep directory hierarchies

## Testing Setup with pytest

### Installation and Setup

```bash
# Install pytest and common plugins
pip install pytest pytest-cov pytest-mock pytest-xdist
```

### Basic pytest Configuration

Create `pyproject.toml` with pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Test Structure Best Practices

1. **Use descriptive test names**:
```python
def test_user_login_with_valid_credentials_returns_success():
    pass

def test_user_login_with_invalid_password_raises_auth_error():
    pass
```

2. **Follow the Arrange-Act-Assert pattern**:
```python
def test_calculate_total_price():
    # Arrange
    items = [{"price": 10.0, "quantity": 2}, {"price": 5.0, "quantity": 3}]
    tax_rate = 0.1
    
    # Act
    total = calculate_total_price(items, tax_rate)
    
    # Assert
    assert total == 38.5
```

3. **Use fixtures for setup**:
```python
# conftest.py
import pytest

@pytest.fixture
def sample_user():
    return {"username": "testuser", "email": "test@example.com"}

@pytest.fixture
def database_connection():
    # Setup
    conn = create_test_database()
    yield conn
    # Teardown
    conn.close()
```

4. **Parametrize tests for multiple inputs**:
```python
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square_function(input, expected):
    assert square(input) == expected
```

### Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_module.py

# Run tests matching pattern
pytest -k "test_login"

# Run tests with specific marker
pytest -m "not slow"

# Run tests in parallel
pytest -n auto
```

## Dependency Management

### Modern Approach: pyproject.toml

The modern standard for Python project configuration is `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "0.1.0"
description = "A sample Python project"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.8"
dependencies = [
    "requests>=2.28.0",
    "click>=8.0.0",
    "pydantic>=1.10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "isort>=5.10.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
]
docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
]

[project.scripts]
my-cli = "my_project.main:main"

[project.urls]
Homepage = "https://github.com/username/my-project"
Documentation = "https://my-project.readthedocs.io"
Repository = "https://github.com/username/my-project.git"
Changelog = "https://github.com/username/my-project/blob/main/CHANGELOG.md"
```

### Legacy Approach: requirements.txt

While `pyproject.toml` is preferred, `requirements.txt` is still widely used:

```txt
# requirements.txt - Production dependencies
requests>=2.28.0,<3.0.0
click>=8.0.0
pydantic>=1.10.0,<2.0.0
```

```txt
# requirements-dev.txt - Development dependencies
-r requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
isort>=5.10.0
flake8>=5.0.0
mypy>=1.0.0
```

### Dependency Management Best Practices

1. **Pin major versions**: Use `package>=1.0.0,<2.0.0` to avoid breaking changes
2. **Use lock files**: Generate `requirements-lock.txt` with exact versions
3. **Separate dev dependencies**: Keep development tools separate from production deps
4. **Regular updates**: Use tools like `pip-audit` and `safety` to check for vulnerabilities
5. **Virtual environments**: Always use virtual environments

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"  # For pyproject.toml
# or
pip install -r requirements-dev.txt  # For requirements.txt

# Generate lock file
pip freeze > requirements-lock.txt
```

## CI/CD Recommendations

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with flake8
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Format check with black
      run: black --check src tests
    
    - name: Import sort check with isort
      run: isort --check-only src tests
    
    - name: Type check with mypy
      run: mypy src
    
    - name: Test with pytest
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.11'
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
    
    - name: Run safety check
      run: safety check
    
    - name: Run bandit security check
      run: bandit -r src

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

### CI/CD Best Practices

1. **Multi-Python Testing**: Test against multiple Python versions
2. **Code Quality Gates**: Use linting, formatting, and type checking
3. **Security Scanning**: Include security vulnerability checks
4. **Code Coverage**: Maintain high test coverage (aim for >80%)
5. **Automated Releases**: Use semantic versioning and automated releases
6. **Branch Protection**: Require PR reviews and passing CI checks
7. **Caching**: Cache dependencies to speed up builds
8. **Parallel Jobs**: Run tests and quality checks in parallel

## Additional Best Practices

### Code Quality Tools

1. **Black**: Code formatting
```bash
pip install black
black src tests
```

2. **isort**: Import sorting
```bash
pip install isort
isort src tests
```

3. **flake8**: Linting
```bash
pip install flake8
flake8 src tests
```

4. **mypy**: Type checking
```bash
pip install mypy
mypy src
```

### Documentation

1. **README.md**: Clear project description, installation, and usage
2. **Docstrings**: Use Google or NumPy style docstrings
3. **API Documentation**: Use Sphinx for auto-generated docs
4. **Changelog**: Maintain a CHANGELOG.md following Keep a Changelog format

### Version Management

1. **Semantic Versioning**: Use MAJOR.MINOR.PATCH format
2. **Version Files**: Centralize version in `__init__.py` or `_version.py`
3. **Git Tags**: Tag releases in Git
4. **Automated Versioning**: Use tools like `bump2version` or `semantic-release`

### Environment and Configuration

1. **Environment Variables**: Use `.env` files for local development
2. **Configuration Management**: Use libraries like `pydantic-settings`
3. **Secrets Management**: Never commit secrets; use environment variables or secret managers
4. **Multiple Environments**: Support dev, staging, and production configurations

### Performance and Monitoring

1. **Profiling**: Use `cProfile` and `py-spy` for performance analysis
2. **Logging**: Use structured logging with the `logging` module
3. **Monitoring**: Add health checks and metrics collection
4. **Error Tracking**: Use services like Sentry for error monitoring

### Package Distribution

1. **PyPI Publishing**: Use `twine` for secure uploads
2. **Wheel Distribution**: Build both source and wheel distributions
3. **Platform Support**: Consider cross-platform compatibility
4. **Version Constraints**: Specify minimum Python version

## Conclusion

Following these best practices will help you create maintainable, scalable, and professional Python projects. Start with the basics (proper directory structure, testing, and dependency management) and gradually adopt more advanced practices like comprehensive CI/CD pipelines and automated releases.

Remember that consistency is key - choose a set of practices and apply them consistently across your projects. Adapt these recommendations to fit your specific project needs and team preferences.