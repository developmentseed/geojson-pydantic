from random import randint
from typing import Dict
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry, MultiPolygon, Polygon


class GenericProperties(BaseModel):
    id: str
    description: str
    size: int


properties = {
    "id": str(uuid4()),
    "description": str(uuid4()),
    "size": randint(0, 1000),
}

polygon = {
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
}

test_feature = {
    "type": "Feature",
    "geometry": polygon,
    "properties": properties,
}


def test_geometry_collection_iteration():
    """test if feature collection is iterable"""
    gc = FeatureCollection(features=[test_feature, test_feature])
    iter(gc)


def test_generic_properties_is_dict():
    feature = Feature(**test_feature)
    assert feature.properties["id"] == test_feature["properties"]["id"]
    assert type(feature.properties) == dict
    assert not hasattr(feature.properties, "id")


def test_generic_properties_is_object():
    feature = Feature[Geometry, GenericProperties](**test_feature)
    assert feature.properties.id == test_feature["properties"]["id"]
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")


def test_generic_geometry():
    feature = Feature[Polygon, GenericProperties](**test_feature)
    assert feature.properties.id == test_feature["properties"]["id"]
    assert type(feature.geometry) == Polygon
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")

    feature = Feature[Polygon, Dict](**test_feature)
    assert type(feature.geometry) == Polygon
    assert feature.properties["id"] == test_feature["properties"]["id"]
    assert type(feature.properties) == dict
    assert not hasattr(feature.properties, "id")

    with pytest.raises(ValidationError):
        Feature[MultiPolygon, Dict](**({"type": "Feature", "geometry": polygon}))


def test_generic_properties_should_raise_for_string():
    with pytest.raises(ValidationError):
        Feature(
            **({"type": "Feature", "geometry": polygon, "properties": "should raise"})
        )


def test_feature_collection_generic():
    fc = FeatureCollection[Polygon, GenericProperties](
        features=[test_feature, test_feature]
    )
    assert len(fc) == 2
    assert type(fc[0].properties) == GenericProperties
    assert type(fc[0].geometry) == Polygon
