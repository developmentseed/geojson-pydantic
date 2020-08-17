# Contributing

To run the tests, first install the package in a virtual environment:

```sh
virtualenv venv
source venv/bin/activate
pip install -e '.[test]'
```

You can then run the tests with the following command:

```sh
python -m pytest --cov geojson_pydantic --cov-report term-missing --ignore=venv
```

This repo is set to use pre-commit to run `isort`, `flake8`, `pydocstring`, `black` ("uncompromising Python code formatter") and `mypy` when committing new code.

``` sh
pre-commit install
```
