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


## Commit messages and releases

Releases are automated with [release-please](https://github.com/googleapis/release-please), which reads the [Conventional Commit](https://www.conventionalcommits.org/) messages merged to `main`. Use them for your commits and your PR title, e.g. `fix: handle empty collections` or `feat: add a filter option`:

- `fix:`, `perf:`, `deps:`, `revert:` and `docs:` lead to a patch release, `feat:` to a minor one, and a breaking change (`feat!:` or a `BREAKING CHANGE:` footer) to a major one.
- `chore:`, `ci:`, `test:`, `build:`, `refactor:` and `style:` don't trigger a release on their own.
- release-please keeps a release PR open with the next version; merging it tags the release and publishes it.
- CHANGELOG.md is written by hand: add your change under `## [unreleased]`. For a breaking change, also mark the commit with `!` (e.g. `feat!:`), otherwise the release gets a patch or minor version.
- At release time, a maintainer adds the `## [X.Y.Z] - date` heading under `## [unreleased]` and updates the links at the bottom of CHANGELOG.md. If the version should differ from the one release-please proposes, that commit also ends with a `Release-As: X.Y.Z` line.

## Release

To release by hand instead, use https://github.com/callowayproject/bump-my-version (it also updates `.release-please-manifest.json`).

```
# Update version (edit files, commit and create tag)
# this will do `0.2.1 -> 0.2.2` because we use the `patch` tag
$ uv run --with bump-my-version bump-my-version bump patch

# Push change and tag to github
$ git push origin main --tags
```
