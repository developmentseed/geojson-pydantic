# Contributing

To run the tests, first install the package in a virtual environment:

```sh
virtualenv venv
source venv/bin/activate
python -m pip install -e '.[test]'
```

You can then run the tests with the following command:

```sh
python -m pytest --cov geojson_pydantic --cov-report term-missing
```

This repo is set to use pre-commit to run `isort`, `flake8`, `pydocstring`, `black` ("uncompromising Python code formatter") and `mypy` when committing new code.

``` sh
pre-commit install
```


## Release

we use https://github.com/c4urself/bump2version to update the package version.

```
# Install bump2version
$ pip install --upgrade bump2version

# Update version (edit files, commit and create tag)
# this will do `0.2.1 -> 0.2.2` because we use the `patch` tag
$ bump2version patch

# Push change and tag to github
$ git push origin main --tags
```
