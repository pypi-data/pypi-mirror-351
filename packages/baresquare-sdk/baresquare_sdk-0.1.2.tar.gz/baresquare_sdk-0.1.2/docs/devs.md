# Developer Guide

## Development Setup

```shell
# Clone the repository
git clone https://github.com/your-org/sdk-python.git
cd sdk-python

# Install in development mode with all dependencies
pip install -e ".[dev]"
# This installs: linting, testing, and aws extras

# Check linting issues
ruff format --check src tests
ruff check src tests

# Fix linting issues
ruff format src tests
ruff check --fix src tests

# Run tests
pytest
```

## Development Guidelines

> [!WARNING]  
> When introducing a new `.py` file, make sure to add it in the appropriate `__init__.py` file, otherwise it will not be made available in the published package.

## Publishing

### Recommended: GitHub Actions

1. **Update Version**
   Edit `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. **Create PR** with the version change, then merge

3. **Create Release** using GitHub UI:
   - Go to "Releases" → "Draft a new release"
   - Choose tag → Enter "v0.2.0" → "Create new tag"
   - This triggers GitHub Action that publishes to PyPI

### Manual Publishing

Use `scripts/publish_local.sh`:

1. Set environment variables:
   ```shell
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=XXX
   ``` 
1. Update the version in `pyproject.toml`
1. Create a tag locally matching the version
1. Run `scripts/publish_local.sh`

### Verify Build

When introducing a new file, ensure the file will be made available in the published package.

```shell
python -m build
mkdir -p wheel_extract
# Extract the wheel (it's just a zip file) - make sure to change the version accordingly
unzip dist/baresquare_sdk-0.2.0-py3-none-any.whl -d wheel_extract
# View the contents
ls -la wheel_extract
# Specifically check for your Python files
find wheel_extract -name "*.py"
```