# Publishing Guide

Simple publishing using Make commands.

## Setup (One Time)

1. **Get API Tokens**:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

2. **Configure Tokens**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env with your actual tokens
   # UV_PUBLISH_TOKEN_TEST=pypi-YOUR_TESTPYPI_TOKEN_HERE
   # UV_PUBLISH_TOKEN_PROD=pypi-YOUR_PYPI_TOKEN_HERE
   ```

## Publishing Commands

**Test PyPI (Recommended First):**
```bash
make publish-test
```

**Production PyPI:**
```bash
make publish-prod
```

**Other Commands:**
```bash
make build        # Build package
make test         # Run tests  
make clean        # Clean build artifacts
make help         # Show all commands
```

## Test Installation

After publishing to Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-kubectl
mcp-kubectl serve --help
```

## Production Installation

After publishing to PyPI:
```bash
pip install mcp-kubectl
mcp-kubectl serve --help
```

## Manual Publishing

If you prefer manual control:

```bash
# Clean and build
rm -rf dist/
uv build

# Validate
uv run twine check dist/*

# Run tests
uv run pytest

# Upload to Test PyPI
export UV_PUBLISH_TOKEN=pypi-YOUR_TESTPYPI_TOKEN_HERE
uv publish --publish-url https://test.pypi.org/legacy/

# Upload to Production PyPI
export UV_PUBLISH_TOKEN=pypi-YOUR_PYPI_TOKEN_HERE
uv publish
```

## Alternative: Using Token Flag

```bash
# Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-YOUR_TESTPYPI_TOKEN_HERE

# Production PyPI
uv publish --token pypi-YOUR_PYPI_TOKEN_HERE
```

## Version Management

Update version in `pyproject.toml` before publishing:

```toml
[project]
version = "1.2.0"  # Increment appropriately
```

Follow semantic versioning:
- `MAJOR.MINOR.PATCH`
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

## Troubleshooting

**403 Forbidden**: Check your API token and repository URL
**409 Conflict**: Version already exists, increment version number
**400 Bad Request**: Run `twine check` to validate package first