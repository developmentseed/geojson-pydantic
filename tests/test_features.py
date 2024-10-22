import json
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


@pytest.mark.parametrize(
    "obj",
    [
        FeatureCollection,
        Feature,
    ],
)
def test_pydantic_schema(obj):
    """Test schema for Pydantic Object."""
    assert obj.model_json_schema()


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
    fc = FeatureCollection[Feature[Polygon, GenericProperties]](
        type="FeatureCollection", features=[test_feature, test_feature]
    )
    assert len(fc) == 2
    assert type(fc[0].properties) == GenericProperties
    assert type(fc[0].geometry) == Polygon


def test_geo_interface_protocol():
    class Pointy:
        __geo_interface__ = {"type": "Point", "coordinates": (0.0, 0.0)}

    feat = Feature(type="Feature", geometry=Pointy(), properties={})
    assert feat.geometry.model_dump(exclude_unset=True) == Pointy.__geo_interface__


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
    assert Feature(type="Feature", properties=None, geometry=None, bbox=None)

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

    assert Feature(
        type="Feature", properties=None, bbox=(0, 0, 100, 100), geometry=None
    )
    assert Feature(
        type="Feature", properties=None, bbox=(0, 0, 0, 100, 100, 100), geometry=None
    )

    with pytest.raises(ValidationError):
        # bad bbox2d
        Feature(type="Feature", properties=None, bbox=(0, 100, 100, 0), geometry=None)

    with pytest.raises(ValidationError):
        # bad bbox3d
        Feature(
            type="Feature",
            properties=None,
            bbox=(0, 100, 100, 100, 0, 0),
            geometry=None,
        )

    # Antimeridian
    with pytest.warns(UserWarning):
        Feature(type="Feature", properties=None, bbox=(100, 0, 0, 100), geometry=None)

    with pytest.warns(UserWarning):
        Feature(
            type="Feature",
            properties=None,
            bbox=(100, 0, 0, 0, 100, 100),
            geometry=None,
        )


def test_bbox_validation():
    # Some attempts at generic validation did not validate the types within
    # bbox before passing them to the function and resulted in TypeErrors.
    # This test exists to ensure that doesn't happen in the future.
    with pytest.raises(ValidationError):
        Feature(
            type="Feature",
            properties=None,
            bbox=(0, "a", 0, 1, 1, 1),
            geometry=None,
        )


def test_feature_validation_error_count():
    # Tests that validation does not include irrelevant errors to make them
    # easier to read. The input below used to raise 18 errors.
    # See #93 for more details.
    with pytest.raises(ValidationError):
        try:
            Feature(
                type="Feature",
                geometry=Polygon(
                    type="Polygon",
                    coordinates=[
                        [
                            (-55.9947406591177, -9.26104045526505),
                            (-55.9976752102375, -9.266589696568962),
                            (-56.00200328975916, -9.264041751931352),
                            (-55.99899921566248, -9.257935213034594),
                            (-55.99477406591177, -9.26103945526505),
                        ]
                    ],
                ),
                properties={},
            )
        except ValidationError as e:
            assert e.error_count() == 1
            raise


def test_feature_serializer():
    f = Feature(
        **{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates,
            },
            "properties": {},
            "id": "Yo",
            "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
        }
    )
    assert "bbox" in f.model_dump()
    assert "id" in f.model_dump()

    # Exclude
    assert "bbox" not in f.model_dump(exclude={"bbox"})
    assert "bbox" not in list(json.loads(f.model_dump_json(exclude={"bbox"})).keys())

    # Include
    assert ["bbox"] == list(f.model_dump(include={"bbox"}).keys())
    assert ["bbox"] == list(json.loads(f.model_dump_json(include={"bbox"})).keys())

    feat_ser = json.loads(f.model_dump_json())
    assert "bbox" in feat_ser
    assert "id" in feat_ser
    assert "bbox" not in feat_ser["geometry"]

    f = Feature(
        **{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates,
            },
            "properties": {},
        }
    )
    # BBOX Should'nt be present if `None`
    # https://github.com/developmentseed/geojson-pydantic/issues/125
    assert "bbox" in f.model_dump()

    feat_ser = json.loads(f.model_dump_json())
    assert "bbox" not in feat_ser
    assert "id" not in feat_ser
    assert "bbox" not in feat_ser["geometry"]

    f = Feature(
        **{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": coordinates,
                "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
            },
            "properties": {},
        }
    )
    feat_ser = json.loads(f.model_dump_json())
    assert "bbox" not in feat_ser
    assert "id" not in feat_ser
    assert "bbox" in feat_ser["geometry"]


def test_feature_collection_serializer():
    fc = FeatureCollection(
        **{
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": coordinates,
                        "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
                    },
                    "properties": {},
                    "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
                }
            ],
            "bbox": [13.38272, 52.46385, 13.42786, 52.48445],
        }
    )
    assert "bbox" in fc.model_dump()

    # Exclude
    assert "bbox" not in fc.model_dump(exclude={"bbox"})
    assert "bbox" not in list(json.loads(fc.model_dump_json(exclude={"bbox"})).keys())

    # Include
    assert ["bbox"] == list(fc.model_dump(include={"bbox"}).keys())
    assert ["bbox"] == list(json.loads(fc.model_dump_json(include={"bbox"})).keys())

    featcoll_ser = json.loads(fc.model_dump_json())
    assert "bbox" in featcoll_ser
    assert "bbox" in featcoll_ser["features"][0]
    assert "bbox" in featcoll_ser["features"][0]["geometry"]

    fc = FeatureCollection(
        **{
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": coordinates,
                    },
                    "properties": {},
                }
            ],
        }
    )
    assert "bbox" in fc.model_dump()

    featcoll_ser = json.loads(fc.model_dump_json())
    assert "bbox" not in featcoll_ser
    assert "bbox" not in featcoll_ser["features"][0]
    assert "bbox" not in featcoll_ser["features"][0]["geometry"]
