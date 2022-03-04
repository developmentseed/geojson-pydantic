# geojson-pydantic

<p align="center">
  <em> <a href="https://pydantic-docs.helpmanual.io" target="_blank">Pydantic</a> models for GeoJSON.</em>
</p>
<p align="center">
  <a href="https://github.com/developmentseed/geojson-pydantic/actions?query=workflow%3ACI" target="_blank">
      <img src="https://github.com/developmentseed/geojson-pydantic/workflows/CI/badge.svg" alt="Test">
  </a>
  <a href="https://codecov.io/gh/developmentseed/geojson-pydantic" target="_blank">
      <img src="https://codecov.io/gh/developmentseed/geojson-pydantic/branch/master/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/geojson-pydantic" target="_blank">
      <img src="https://img.shields.io/pypi/v/geojson-pydantic?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypistats.org/packages/geojson-pydantic" target="_blank">
      <img src="https://img.shields.io/pypi/dm/geojson-pydantic.svg" alt="Downloads">
  </a>
  <a href="https://github.com/developmentseed/geojson-pydantic/blob/master/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/developmentseed/geojson-pydantic.svg" alt="Downloads">
  </a>
  <a href="https://anaconda.org/conda-forge/geojson-pydantic" target="_blank">
      <img src="https://anaconda.org/conda-forge/geojson-pydantic/badges/installer/conda.svg" alt="Conda">
  </a>
</p>

## Description

`geojson_pydantic` provides a suite of Pydantic models matching the GeoJSON specification [rfc7946](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1). Those models can be used for creating or validating geojson data.

## Install

```bash
$ pip install -U pip
$ pip install geojson-pydantic
```

Or install from source:

```bash
$ pip install -U pip
$ pip install git+https://github.com/developmentseed/geojson-pydantic.git
```

Install with conda from [`conda-forge`](https://anaconda.org/conda-forge/geojson-pydantic):

```bash
$ conda install -c conda-forge geojson-pydantic
```

## Usage

```python
from geojson_pydantic import Feature, FeatureCollection, Point

geojson_feature = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [13.38272, 52.46385],
    },
    "properties": {
        "name": "jeff",
    },
}


feat = Feature(**geojson_feature)
assert feat.type == "Feature"
assert type(feat.geometry) == Point
assert feat.properties["name"] == "jeff"

fc = FeatureCollection(features=[geojson_feature, geojson_feature])
assert fc.type == "FeatureCollection"
assert len(fc) == 2
assert type(fc.features[0].geometry) == Point
assert fc.features[0].properties["name"] == "jeff"
```

### Advanced usage

In `geojson_pydantic` we've implemented pydantic's [Generic Models](https://pydantic-docs.helpmanual.io/usage/models/#generic-models) which allow the creation of more advanced models to validate either the geometry type or the properties.

In order to make use of this generic typing, there are two steps: first create a new model, then use that model to validate your data. To create a model using a `Generic` type, you **HAVE TO** pass `Type definitions` to the `Feature` model in form of `Feature[Geometry Type, Properties Type]`. Then pass your data to this constructor.

By default `Feature` and `FeatureCollections` are defined using `geojson_pydantic.geometries.Geometry` for the geometry and `typing.Dict` for the properties.

Here's an example where we want to validate that GeoJSON features have Polygon types, but don't do any specific property validation.

```python
from typing import Dict

from geojson_pydantic import Feature, Polygon
from pydantic import BaseModel

geojson_feature = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [13.38272, 52.46385],
    },
    "properties": {
        "name": "jeff",
    },
}

# Define a Feature model with Geometry as `Polygon` and Properties as `Dict`
MyPolygonFeatureModel = Feature[Polygon, Dict]

feat = MyPolygonFeatureModel(**geojson_feature)  # should raise Validation Error because `geojson_feature` is a polygon
>>> ValidationError: 3 validation errors for Feature[Polygon, Dict]
...
geometry -> type
  unexpected value; permitted: 'Polygon' (type=value_error.const; given=Point; permitted=['Polygon'])


geojson_feature = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [13.38272, 52.46385],
                [13.42786, 52.46385],
                [13.42786, 52.48445],
                [13.38272, 52.48445],
                [13.38272, 52.46385],
            ]
        ],
    },
    "properties": {
        "name": "jeff",
    },
}

feat = MyPolygonFeatureModel(**geojson_feature)
assert type(feature.geometry) == Polygon
```

Or with optional geometry

```python
from geojson_pydantic import Feature, Point
from typing import Optional

MyPointFeatureModel = Feature[Optional[Point], Dict]

assert MyPointFeatureModel(type="Feature", geometry=None, properties={}).geometry is None
assert MyPointFeatureModel(type="Feature", geometry=Point(coordinates=(0,0)), properties={}).geometry is not None
```

And now with constrained properties

```python
from geojson_pydantic import Feature, Point
from pydantic import BaseModel, constr

# Define a Feature model with Geometry as `Point` and Properties as a constrained Model
class MyProps(BaseModel):
    name: constr(regex=r'^(drew|vincent)$')

MyPointFeatureModel = Feature[Point, MyProps]

geojson_feature = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [13.38272, 52.46385],
    },
    "properties": {
        "name": "jeff",
    },
}

feat = MyPointFeatureModel(**geojson_feature)
>>> ValidationError: 1 validation error for Feature[Point, MyProps]
properties -> name
  string does not match regex "^(drew|vincent)$" (type=value_error.str.regex; pattern=^(drew|vincent)$)

geojson_feature["properties"]["name"] = "drew"
feat = MyPointFeatureModel(**geojson_feature)
assert feat.properties.name == "drew"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Changes

See [CHANGES.md](https://github.com/developmentseed/geojson-pydantic/blob/master/CHANGELOG.md).

## Authors

Initial implementation by @geospatial-jeff; taken liberally from https://github.com/arturo-ai/stac-pydantic/

See [contributors](hhttps://github.com/developmentseed/geojson-pydantic/graphs/contributors) for a listing of individual contributors.

## License

See [LICENSE](https://github.com/developmentseed/geojson-pydantic/blob/master/LICENSE)
