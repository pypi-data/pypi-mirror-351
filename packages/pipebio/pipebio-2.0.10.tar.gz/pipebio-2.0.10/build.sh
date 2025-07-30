# test.pypi.org - used only for testing packaging/distribution.
# Requires an entry in you .pypirc that matches "testpypi" - see https://packaging.python.org/en/latest/specifications/pypirc/

#!/usr/bin/env bash
set -e

# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build with pyproject.toml
python -m build


# If you do not have the .pypirc file you could instead do the following:
# twine upload --repository-url https://test.pypi.org/legacy/ dist/* - will ask for creds on command line.
