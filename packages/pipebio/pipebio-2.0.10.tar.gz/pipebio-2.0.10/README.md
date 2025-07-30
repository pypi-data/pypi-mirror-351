# PipeBio Python SDK

This is based on the library originally created as part of the [api-examples](https://github.com/pipebio/api-examples).

## Installation

### From PyPI
```shell
pip install pipebio
```

### For Development
```shell
# Clone the repository
git clone https://github.com/pipebio/python-library.git
cd python-library

# Create and activate a conda environment (recommended)
conda create -n pipebio-dev python=3.9
conda activate pipebio-dev

# Install the package with development dependencies
python -m pip install ".[build,dev]"
```

Note: When using zsh shell, make sure to quote the `.[build,dev]` argument as shown above to prevent glob pattern interpretation.




## Testing
The package includes unit tests and integration tests located in the `tests` directory:

### Unit Tests
Located in `tests/unit/`, these tests can be run using:
```shell
pytest -v pytest tests/unit/
```

This will discover and run all test files matching the pattern `*_test.py` in the `tests` directory.

### Integration Tests
Located in `tests/integration/`, these tests verify the package's functionality:

1. **Environment Setup**
   ```shell
   # Set up required API credentials; add the following to your .env file in project root.
   # Tests will only run in intellij by default which has support for reading .env files and because
   # we have setup configs to do that.
   
   ## GCP
   # PIPE_API_URL=https://antibody-dev.com
   # PIPE_API_KEY=TODO
   
   ## AWS
   PIPE_API_URL=https://pipebio.dev-engteam1.dev.bnch.services/
   PIPE_API_KEY=TODO
   ```

2. **Running Tests**
```shell
pytest -v tests/integration/
```

### Version Compatibility
The package is tested to work with:
- All supported Python versions (see `pyproject.toml` for specific version requirements)
- Explicitly prevents installation on unsupported Python versions with clear error messages
- Tested on both Linux (Ubuntu) and macOS environments

If you're developing new features, make sure to add appropriate tests and verify that all tests pass before submitting changes.

## Versioning and Releases
To deploy a new version of this package, you'll need to:

1. Switch to either the `testpypi` or `pypi` branch (releases are only allowed from these branches)
2. Ensure your working directory is clean (all changes committed)
3. Run the release script with the appropriate version bump:

```shell
# For bug fixes and safe changes (1.0.0 → 1.0.1):
./bin/release.py patch

# For new features, backward-compatible (1.0.0 → 1.1.0):
./bin/release.py minor

# For breaking changes (1.0.0 → 2.0.0):
./bin/release.py major
```

The release script will:
- Install `bump2version` if not already installed
- Bump the version in both `pipebio/__init__.py` and `setup.py`
- Create a git tag in the format `vX.Y.Z`
- Push the changes and tag to the appropriate branch
- We will then trigger a deployment to either testpypi or pypi in github actions.

You can do a dry run first to see what would happen:
```shell
./bin/release.py patch --dry-run
```

## PyPi documentation
The documentation shown on PyPi is pulled from the `DESCRIPTION.md` file, which is configured in the setup.py file in the line:
```python
long_description=Path("DESCRIPTION.md").read_text(encoding='UTF-8'),
```

# Github actions user accounts
- In both engteam1 and antibody-dev.com we use the user sdk-tester@pipebio.com (emails go to PipeBio leadership staff)
- We have a seperate API key for each (AWS/GCP) in actions