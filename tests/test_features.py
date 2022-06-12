from random import randint
from typing import Dict
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import Geometry, MultiPolygon, Polygon, GeometryCollection


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

geom_collection = {
    "type": "GeometryCollection",
    "geometries": [polygon, polygon]
}

test_feature = {
    "type": "Feature",
    "geometry": polygon,
    "properties": properties,
}

test_feature_geom_null = {
    "type": "Feature",
    "geometry": None,
    "properties": properties,
}

test_feature_geometry_collection = {
    "type": "Feature",
    "geometry": geom_collection,
    "properties": properties,
}


def test_feature_collection_iteration():
    """test if feature collection is iterable"""
    gc = FeatureCollection(features=[test_feature, test_feature])
    assert hasattr(gc, "__geo_interface__")
    iter(gc)


def test_geometry_collection_iteration():
    """test if feature collection is iterable"""
    gc = FeatureCollection(features=[test_feature_geometry_collection])
    assert hasattr(gc, "__geo_interface__")
    iter(gc)


def test_generic_properties_is_dict():
    feature = Feature(**test_feature)
    assert hasattr(feature, "__geo_interface__")
    assert feature.properties["id"] == test_feature["properties"]["id"]
    assert type(feature.properties) == dict
    assert not hasattr(feature.properties, "id")


def test_generic_properties_is_dict_collection():
    feature = Feature(**test_feature_geometry_collection)
    assert hasattr(feature, "__geo_interface__")
    assert feature.properties["id"] == test_feature_geometry_collection["properties"]["id"]
    assert type(feature.properties) == dict
    assert not hasattr(feature.properties, "id")


def test_generic_properties_is_object():
    feature = Feature[Geometry, GenericProperties](**test_feature)
    assert feature.properties.id == test_feature["properties"]["id"]
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")


def test_generic_geometry():
    feature = Feature[Polygon, GenericProperties](**test_feature)
    assert feature.properties.id == test_feature_geometry_collection["properties"]["id"]
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


def test_generic_geometry_collection():
    feature = Feature[GeometryCollection, GenericProperties](**test_feature_geometry_collection)
    assert feature.properties.id == test_feature_geometry_collection["properties"]["id"]
    assert type(feature.geometry) == GeometryCollection
    assert feature.geometry.wkt.startswith("GEOMETRYCOLLECTION (POLYGON ")
    assert feature.geometry.geometries[0].wkt == feature.geometry.geometries[1].wkt
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")

    feature = Feature[GeometryCollection, Dict](**test_feature_geometry_collection)
    assert type(feature.geometry) == GeometryCollection
    assert feature.properties["id"] == test_feature_geometry_collection["properties"]["id"]
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


def test_geo_interface_protocol():
    class Pointy:
        __geo_interface__ = {"type": "Point", "coordinates": (0.0, 0.0)}

    feat = Feature(geometry=Pointy())
    assert feat.geometry.dict() == Pointy.__geo_interface__


def test_feature_with_null_geometry():
    feature = Feature(**test_feature_geom_null)
    assert feature.geometry is None
