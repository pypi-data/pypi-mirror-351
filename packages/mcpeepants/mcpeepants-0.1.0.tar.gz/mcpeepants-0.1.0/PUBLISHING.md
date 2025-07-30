# Publishing mcpeepants to PyPI

This guide walks you through the process of publishing mcpeepants to PyPI so it can be installed via pip/uv/poetry.

## Prerequisites

1. Create accounts:
   - **PyPI account**: https://pypi.org/account/register/
   - **TestPyPI account** (for testing): https://test.pypi.org/account/register/

2. Install build tools:
   ```bash
   pip install --upgrade build twine
   ```

## Steps to Publish

### 1. Update Package Metadata

Edit the following files with your information:

**pyproject.toml**:
- Replace `"Your Name"` and `"your.email@example.com"` with your details
- Update the GitHub URLs to point to your repository

**setup.py**:
- Replace `"Your Name"` and `"your.email@example.com"` with your details
- Update the GitHub URL to point to your repository

### 2. Verify Package Structure

Run tests to ensure everything works:
```bash
python run_self_test.py
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/mcpeepants-0.1.0.tar.gz` (source distribution)
- `dist/mcpeepants-0.1.0-py3-none-any.whl` (wheel)

### 4. Test with TestPyPI (Recommended)

First, upload to TestPyPI to verify everything works:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

Test installation from TestPyPI:
```bash
# Create a test virtual environment
python -m venv test_env
test_env\Scripts\activate  # Windows
# or
source test_env/bin/activate  # Linux/Mac

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcpeepants

# Test the installation
mcpeepants --help
python -c "from mcpeepants import create_server; print('Import successful!')"

# Deactivate and clean up
deactivate
rm -rf test_env
```

### 5. Upload to PyPI

Once testing is successful:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

### 6. Verify Installation

```bash
# Install from PyPI
pip install mcpeepants

# Or with uv
uv pip install mcpeepants

# Or with poetry
poetry add mcpeepants
```

## Using mcpeepants in a New Project

### Option 1: As a Library

```python
# my_mcp_server.py
from mcpeepants import create_server

# Create server with custom name
server = create_server("my-custom-server")

if __name__ == "__main__":
    server.run()
```

### Option 2: As a CLI Tool

```bash
# Run directly
mcpeepants

# With custom configuration
export PYTEST_PATH="./my_tests"
export MCP_PLUGIN_PATHS="/path/to/plugins"
mcpeepants --name "my-server"
```

### Option 3: In pyproject.toml

```toml
[project]
dependencies = [
    "mcpeepants>=0.1.0"
]
```

## Configuring pytest_runner for Any Project

The pytest_runner tool will work in any project as long as:

1. **pytest is installed** in the project environment
2. **PYTEST_PATH is configured** (or it will use current directory)

Example `.env` file for a project:
```bash
# .env
PYTEST_PATH=./tests
PYTEST_TIMEOUT=60
MCP_PLUGIN_PATHS=./mcp_plugins
```

Example Claude Desktop configuration:
```json
{
  "mcpServers": {
    "my-project-tests": {
      "command": "python",
      "args": ["-m", "mcpeepants.server"],
      "env": {
        "PYTEST_PATH": "C:\\Users\\YourName\\my-project\\tests",
        "PYTEST_TIMEOUT": "60"
      }
    }
  }
}
```

## Version Management

To release a new version:

1. Update version in:
   - `pyproject.toml`
   - `setup.py`
   - `src/mcpeepants/__init__.py`

2. Create git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

3. Build and upload new version:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Troubleshooting

### "pytest not found" error
- Ensure pytest is in project dependencies
- Check that the virtual environment is activated

### "Test path does not exist" error
- Verify PYTEST_PATH points to valid directory
- Use absolute paths for clarity

### Timeout issues
- Increase PYTEST_TIMEOUT environment variable
- Check for hanging tests or infinite loops

### Import errors
- Ensure PYTHONPATH includes project root
- Check that mcpeepants is properly installed

## API Token (Recommended)

For automated uploads, use an API token:

1. Generate token at https://pypi.org/manage/account/token/
2. Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-YOUR_TOKEN_HERE
   ```

## Next Steps

After publishing:

1. Add badges to README:
   ```markdown
   [![PyPI version](https://badge.fury.io/py/mcpeepants.svg)](https://badge.fury.io/py/mcpeepants)
   [![Python versions](https://img.shields.io/pypi/pyversions/mcpeepants.svg)](https://pypi.org/project/mcpeepants/)
   ```

2. Set up GitHub Actions for automated releases
3. Create documentation on Read the Docs
4. Add more built-in tools and plugins
