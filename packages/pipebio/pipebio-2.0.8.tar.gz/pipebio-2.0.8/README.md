# PipeBio Python SDK

This is based on the library originally created as part of the [api-examples](https://github.com/pipebio/api-examples).

## Versioning
To deploy a new version of this package, the version number needs to be incremented, as pypi does not permit a current version to be overwritten.

The version needs to be bumped in two places:

* `pipebio/__init__.py`
* `setup.py`

These version number **must** be kept in lock step.

## PyPi documentation
The documentation shown on PyPi is pulled from the `DESCRIPTION.md` file, which is configured in the setup.py file in the line:
```python
long_description=Path("DESCRIPTION.md").read_text(encoding='UTF-8'),
```

## Developing new versions
New versions of this package can be deployed to `test.pypi.org` – a separate instance of the Python Package Index that allows you to try distribution tools and processes without affecting the real index.

To deploy to `test.pypi.org`, the shell script `deploy_to_testpypi.sh` can be used. This requires `~/.pypirc` to be configured. 

To install a package deployed to `test.pypi.org`, use 
```shell
pip install -i testpypi pipebio
```

### Example .pypirc file
```
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository=https://test.pypi.org/legacy/
username = __token__
password = <Test PyPI token>

[pypi]
repository=https://pypi.org/legacy/
username = __token__
password = <PyPI token>
```

You can get a working .pypirc file from 1password in the `PipeBio` vault, as a Secure Note called `.pypirc`.
Copy the content there to a file ~/.pypirc on your local machine.

## Deploying to pypi
To deploy to `pypi.org`, the shell script `deploy_to_pypi.sh` can be used. This requires `~/.pypirc` to be configured.
