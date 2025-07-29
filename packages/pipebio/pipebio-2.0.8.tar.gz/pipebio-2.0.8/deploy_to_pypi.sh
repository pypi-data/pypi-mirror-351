rm -r ./build
rm -r ./dist
rm -r ./pipebio.egg-info

# Creates a source distribution
python setup.py sdist
# Creates a wheel distribution
python setup.py bdist_wheel --universal

# pypi.org - used only for testing packaging/distribution.
# Requires an entry in you .pypirc that matches "pypi" - see https://packaging.python.org/en/latest/specifications/pypirc/
# To install from here use `pip install -i https://pypi.org/simple/ pipebio`.
twine upload -r pypi dist/*
# twine upload --repository-url https://pypi.org/legacy/ dist/* - will ask for creds on command line.
