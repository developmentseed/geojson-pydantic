from random import randint
from typing import Any, Dict
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import (
    Geometry,
    GeometryCollection,
    MultiPolygon,
    Polygon,
)


class GenericProperties(BaseModel):
    id: str
    description: str
    size: int


properties: Dict[str, Any] = {
    "id": str(uuid4()),
    "description": str(uuid4()),
    "size": randint(0, 1000),
}

coordinates = [
    [
        [13.38272, 52.46385],
        [13.42786, 52.46385],
        [13.42786, 52.48445],
        [13.38272, 52.48445],
        [13.38272, 52.46385],
    ]
]

polygon: Dict[str, Any] = {
    "type": "Polygon",
    "coordinates": coordinates,
}

multipolygon: Dict[str, Any] = {
    "type": "MultiPolygon",
    "coordinates": [coordinates],
}

geom_collection: Dict[str, Any] = {
    "type": "GeometryCollection",
    "geometries": [polygon, multipolygon],
}

test_feature: Dict[str, Any] = {
    "type": "Feature",
    "geometry": polygon,
    "properties": properties,
    "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
}

test_feature_geom_null: Dict[str, Any] = {
    "type": "Feature",
    "geometry": None,
    "properties": properties,
}

test_feature_geometry_collection: Dict[str, Any] = {
    "type": "Feature",
    "geometry": geom_collection,
    "properties": properties,
}


def test_feature_collection_iteration():
    """test if feature collection is iterable"""
    gc = FeatureCollection(
        type="FeatureCollection", features=[test_feature, test_feature]
    )
    assert hasattr(gc, "__geo_interface__")
    iter(gc)


def test_geometry_collection_iteration():
    """test if feature collection is iterable"""
    gc = FeatureCollection(
        type="FeatureCollection", features=[test_feature_geometry_collection]
    )
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
    assert (
        feature.properties["id"] == test_feature_geometry_collection["properties"]["id"]
    )
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
    feature = Feature[GeometryCollection, GenericProperties](
        **test_feature_geometry_collection
    )
    assert feature.properties.id == test_feature_geometry_collection["properties"]["id"]
    assert type(feature.geometry) == GeometryCollection
    assert feature.geometry.wkt.startswith("GEOMETRYCOLLECTION (POLYGON ")
    assert type(feature.properties) == GenericProperties
    assert hasattr(feature.properties, "id")

    feature = Feature[GeometryCollection, Dict](**test_feature_geometry_collection)
    assert type(feature.geometry) == GeometryCollection
    assert (
        feature.properties["id"] == test_feature_geometry_collection["properties"]["id"]
    )
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
        type="FeatureCollection", features=[test_feature, test_feature]
    )
    assert len(fc) == 2
    assert type(fc[0].properties) == GenericProperties
    assert type(fc[0].geometry) == Polygon


def test_geo_interface_protocol():
    class Pointy:
        __geo_interface__ = {"type": "Point", "coordinates": (0.0, 0.0)}

    feat = Feature(type="Feature", geometry=Pointy(), properties={})
    assert feat.geometry.dict(exclude_unset=True) == Pointy.__geo_interface__


def test_feature_with_null_geometry():
    feature = Feature(**test_feature_geom_null)
    assert feature.geometry is None


def test_feature_geo_interface_with_null_geometry():
    feature = Feature(**test_feature_geom_null)
    assert "bbox" not in feature.__geo_interface__


def test_feature_collection_geo_interface_with_null_geometry():
    fc = FeatureCollection(
        type="FeatureCollection", features=[test_feature_geom_null, test_feature]
    )
    assert "bbox" not in fc.__geo_interface__
    assert "bbox" not in fc.__geo_interface__["features"][0]
    assert "bbox" in fc.__geo_interface__["features"][1]


@pytest.mark.parametrize("id", ["a", 1, "1"])
def test_feature_id(id):
    """Test if a string stays a string and if an int stays an int."""
    feature = Feature(**test_feature, id=id)
    assert feature.id == id


@pytest.mark.parametrize("id", [True, 1.0])
def test_bad_feature_id(id):
    """make sure it raises error."""
    with pytest.raises(ValidationError):
        Feature(**test_feature, id=id)


def test_feature_validation():
    """Test default."""
    assert Feature(type="Feature", properties=None, geometry=None)

    with pytest.raises(ValidationError):
        # should be type=Feature
        Feature(type="feature", properties=None, geometry=None)

    with pytest.raises(ValidationError):
        # missing type
        Feature(properties=None, geometry=None)

    with pytest.raises(ValidationError):
        # missing properties
        Feature(type="Feature", geometry=None)

    with pytest.raises(ValidationError):
        # missing geometry
        Feature(type="Feature", properties=None)
