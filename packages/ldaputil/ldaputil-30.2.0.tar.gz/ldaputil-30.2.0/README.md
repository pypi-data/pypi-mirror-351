# ldaputil

A simple test Python package that prints "Hello World" during installation.

## Description

This is a minimal test package created to demonstrate Python packaging. The package doesn't provide any real functionality - it's designed to print a greeting message when installed and imported.

## Installation

### From PyPI (when published):
```bash
pip install ldaputil
```

### From local build:
```bash
pip install dist/ldaputil-40.0.0-py3-none-any.whl
```

## Usage

```python
import ldaputil

# The package will print "Hello World" message when imported

# You can also use the hello_world function
ldaputil.hello_world()

# Or use the greet function from main module
from ldaputil.main import greet
greet("Python Developer")
```

## Features

- Prints greeting message during installation/import
- Simple hello_world() function
- Greet function with customizable name
- Minimal dependencies

## Development

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ldaputil
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install --upgrade pip build twine pytest
   ```

### Building the Package

1. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ src/*.egg-info/
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

   This creates two files in `dist/`:
   - `ldaputil-40.0.0.tar.gz` (source distribution)
   - `ldaputil-40.0.0-py3-none-any.whl` (wheel distribution)

3. **Verify the build:**
   ```bash
   twine check dist/*
   ```

### Testing

1. **Run unit tests:**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Test local installation:**
   ```bash
   pip install dist/ldaputil-40.0.0-py3-none-any.whl
   python -c "import ldaputil; ldaputil.hello_world()"
   ```

### Publishing to PyPI

#### Option 1: Test on TestPyPI first (Recommended)

1. **Create account on TestPyPI:**
   - Go to https://test.pypi.org/account/register/
   - Verify your email address

2. **Create API token:**
   - Go to https://test.pypi.org/manage/account/#api-tokens
   - Create token with "Entire account" scope
   - Copy the token (starts with `pypi-`)

3. **Upload to TestPyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   ```
   - Enter your API token when prompted

4. **Test installation from TestPyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ ldaputil
   ```

#### Option 2: Publish to Production PyPI

1. **Create account on PyPI:**
   - Go to https://pypi.org/account/register/
   - Verify your email address

2. **Create API token:**
   - Go to https://pypi.org/manage/account/#api-tokens
   - Create token with "Entire account" scope
   - Copy the token (starts with `pypi-`)

3. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```
   - Enter your API token when prompted

4. **Verify publication:**
   - Visit https://pypi.org/project/ldaputil/
   - Install: `pip install ldaputil`

### Version Management

To release a new version:

1. **Update version in `pyproject.toml`:**
   ```toml
   version = "40.0.1"  # or next version
   ```

2. **Rebuild and republish:**
   ```bash
   rm -rf dist/
   python -m build
   twine check dist/*
   twine upload dist/*  # or --repository testpypi for testing
   ```

### Troubleshooting

**Common Issues:**

1. **"Package already exists" error:**
   - You cannot upload the same version twice
   - Increment the version number in `pyproject.toml`

2. **Authentication errors:**
   - Make sure you're using the correct API token
   - Token should start with `pypi-`

3. **Build errors:**
   - Make sure you're in the virtual environment
   - Check that all dependencies are installed

**Useful Commands:**

```bash
# Check package contents
tar -tzf dist/ldaputil-40.0.0.tar.gz

# Install in development mode
pip install -e .

# Uninstall package
pip uninstall ldaputil

# View package info
pip show ldaputil
```

## Project Structure

```
ldaputil/
├── src/ldaputil/
│   ├── __init__.py          # Main module with hello_world()
│   └── main.py              # Additional functions
├── tests/
│   ├── __init__.py
│   └── test_ldaputil.py     # Unit tests
├── dist/                    # Built packages (created by build)
├── pyproject.toml           # Package configuration
├── README.md                # This file
└── LICENSE                  # MIT License
```

## License

MIT License - see LICENSE file for details. 