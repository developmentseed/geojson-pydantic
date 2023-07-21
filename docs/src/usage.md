
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

fc = FeatureCollection(type="FeatureCollection", features=[geojson_feature, geojson_feature])
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

feat = MyPolygonFeatureModel(**geojson_feature)  # should raise Validation Error because `geojson_feature` is a point
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
assert MyPointFeatureModel(type="Feature", geometry=Point(type="Point", coordinates=(0,0)), properties={}).geometry is not None
```

And now with constrained properties

```python
from geojson_pydantic import Feature, Point
from pydantic import BaseModel, constr

# Define a Feature model with Geometry as `Point` and Properties as a constrained Model
class MyProps(BaseModel):
    name: constr(pattern=r'^(drew|vincent)$')

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

## Enforced Keys

Starting with version `0.6.0`, geojson-pydantic's classes will not define default keys such has `type`, `geometry` or `properties`.
This is to make sure the library does well its first goal, which is `validating` GeoJSON object based on the [specification](https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1)

    o A GeoJSON object has a member with the name "type".  The value of
      the member MUST be one of the GeoJSON types.

    o A Feature object HAS a "type" member with the value "Feature".

    o A Feature object HAS a member with the name "geometry". The value
    of the geometry member SHALL be either a Geometry object as
    defined above or, in the case that the Feature is unlocated, a
    JSON null value.

    o A Feature object HAS a member with the name "properties". The
    value of the properties member is an object (any JSON object or a
    JSON null value).


```python
from geojson_pydantic import Point

## Before 0.6
Point(coordinates=(0,0))
>> Point(type='Point', coordinates=(0.0, 0.0), bbox=None)

## After 0.6
Point(coordinates=(0,0))
>> ValidationError: 1 validation error for Point
   type
      field required (type=value_error.missing)

Point(type="Point", coordinates=(0,0))
>> Point(type='Point', coordinates=(0.0, 0.0), bbox=None)
```
