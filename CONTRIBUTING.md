# Contributing

Issues and pull requests are more than welcome.

We recommand using [`uv`](https://docs.astral.sh/uv) as project manager for development.

See https://docs.astral.sh/uv/getting-started/installation/ for installation 

### dev install

```sh
git clone https://github.com/developmentseed/geojson-pydantic.git
cd geojson-pydantic

uv sync
```

You can then run the tests with the following command:

```sh
uv run pytest --cov geojson_pydantic --cov-report term-missing
```

This repo is set to use pre-commit to run `isort`, `flake8`, `pydocstring`, `black` ("uncompromising Python code formatter") and `mypy` when committing new code.

``` sh
uv run pre-commit install
```


## Release

we use https://github.com/callowayproject/bump-my-version to update the package version.

```
# Update version (edit files, commit and create tag)
# this will do `0.2.1 -> 0.2.2` because we use the `patch` tag
$ uv run --with bump-my-version bump-my-version bump patch

# Push change and tag to github
$ git push origin main --tags
```
