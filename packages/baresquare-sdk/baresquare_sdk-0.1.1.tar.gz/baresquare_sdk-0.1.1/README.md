# Baresquare Python Libraries

> [!CAUTION]
> This code is published publicly in PyPI - make sure you do not include proprietary information.

This monorepo hosts Baresquare's Python packages, all published to PyPI.

## Packages

The repository currently contains the following packages:

- **baresquare_core_py**: Core utilities shared across Baresquare services
- **baresquare_aws_py**: AWS-specific utilities that build upon core

## Development Guidelines

### Versioning

- All packages share the same version number
- Version is defined in each package's `__init__.py` file (`__version__ = "x.y.z"`)
- Git tags must match the version in `__init__.py` files (format: `vx.y.z`)
- CI will validate version consistency before publishing

### Package Configuration

- A single `pyproject.toml` file is used for all packages
- Package-specific settings are handled in the CI process
- Dependencies between packages are defined in `pyproject.toml` under `[project.optional-dependencies]`

### Development Setup

To set up the packages for development:

```shell
# Install in development mode with all dependencies
pip install -e ".[testing]"

# Run tests
pytest
```

> [!WARNING]  
> When introducing a new `.py` file, make sure to add it in the appropriate `__init__.py` file, otherwise it will not be
> makde available in the published package. 

### Linting

For each directory:
- Show linting issues: `ruff check . --preview`
- Fix linting issues: `ruff . --fix --preview`

### Testing

Install packages

```shell
# First in the core directory 
cd core
pip install -e .

# Then in the aws directory
cd ../aws
pip install -e .[testing]
```

Then run `pytest` in each directory

## Publishing

> [!TIP]
> Before publishing properly, check the build locally (see instructions below).

### With GitHub Action

**It is recommended to publish a new version by creating a GitHub release, as this creates release notes in the relevant 
GitHub page.**

Packages are published to PyPI through GitHub Actions when a new tag is pushed:

1. Update the `version` field in all `pyproject.toml` files (should be the same everywhere)
1. If there is optional dependency array `publishing`, update the core package version there too (e.g. in `pyproject.toml` of the AWS package)
1. Commit changes
1. Create and push a tag matching the version (assuming version to be published is 0.1.0):
   - via command line: `git tag v0.1.0 && git push origin v0.1.0`
   - via GitHub UI: Go to "Releases" → "Draft a new release" → "Choose a tag" → Enter "v0.1.0" → "Create new tag"

CI will validate versions, build packages, and publish to PyPI

### Manually

You can also use `scripts/publish_local.sh`:

1. Set environment variables:
   ```shell
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=XXX
   ``` 
1. If there is optional dependency array `publishing`, update the core package version there too (e.g. in `pyproject.toml` of the AWS package)
1. Check `pyproject.toml` files of non-core packages - they may reference the version of `baresquare-core-py`
1. Create a tag locally matching the version
1. Run `scripts/publish_local.sh`

### Check the build

When introducing a new file, ensure the file will be made available in the published package.

```shell
cd core
python -m build
mkdir -p wheel_extract
# Extract the wheel (it's just a zip file) - make sure to change the version accordingly
unzip dist/baresquare_core_py-0.1.0-py3-none-any.whl -d wheel_extract
# View the contents
ls -la wheel_extract
# Specifically check for your Python files
find wheel_extract -name "*.py"
```

then check the file exists in the output.

These instructions are for the `core` package - adjust accordingly for other packages.

## Installation


```shell
# Install core package
pip install baresquare_core_py

# Install AWS package (which includes core)
pip install baresquare_aws_py
```

## License

MIT License