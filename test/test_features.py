import pytest
from pydantic import BaseModel
from uuid import uuid4
from random import randint

from geojson_pydantic.features import Feature, FeatureCollection


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
    feature = Feature[GenericProperties](**test_feature)

    assert feature.properties.id == test_feature["properties"]["id"]
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")
