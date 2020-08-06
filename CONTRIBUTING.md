# Contributing

Below you'll find instructions on how to get your hands dirty in case you want
to start hacking on this library.

##  Hacking

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
