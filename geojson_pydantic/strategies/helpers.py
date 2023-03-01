"""Helper functions for strategies."""
from geojson_pydantic.strategies.features import Feature, FeatureCollection
from geojson_pydantic.strategies.geometries import (
    BBox,
    Geometry,
    GeometryCollection,
    LinearRingCoords,
    LineString,
    MultiLineString,
    MultiLineStringCoords,
    MultiPoint,
    MultiPolygon,
    MultiPolygonCoords,
    Point,
    Polygon,
    PolygonCoords,
    Position,
    PositionList,
)

# Coordinates
position_2d = Position(dims="2d")
position_3d = Position(dims="3d")
position_either = Position(dims="either")

bbox_2d = BBox(dims="2d")
bbox_3d = BBox(dims="3d")
bbox_either = BBox(dims="either")

position_list_2d = PositionList(dims="2d")
position_list_3d = PositionList(dims="3d")
position_list_either = PositionList(dims="either")
position_list_mixed = PositionList(dims="mixed")

multi_line_string_coords_2d = MultiLineStringCoords(dims="2d")
multi_line_string_coords_3d = MultiLineStringCoords(dims="3d")
multi_line_string_coords_either = MultiLineStringCoords(dims="either")
multi_line_string_coords_mixed = MultiLineStringCoords(dims="mixed")

linear_ring_coords_2d = LinearRingCoords(dims="2d")
linear_ring_coords_3d = LinearRingCoords(dims="3d")
linear_ring_coords_either = LinearRingCoords(dims="either")
linear_ring_coords_mixed = LinearRingCoords(dims="mixed")

polygon_coords_2d = PolygonCoords(dims="2d")
polygon_coords_3d = PolygonCoords(dims="3d")
polygon_coords_either = PolygonCoords(dims="either")
polygon_coords_mixed = PolygonCoords(dims="mixed")

multi_polygon_coords_2d = MultiPolygonCoords(dims="2d")
multi_polygon_coords_3d = MultiPolygonCoords(dims="3d")
multi_polygon_coords_either = MultiLineStringCoords(dims="either")
multi_polygon_coords_mixed = MultiPolygonCoords(dims="mixed")

# Geometries
point_2d = Point(dims="2d")
point_3d = Point(dims="3d")
point_either = Point(dims="either")
point_mixed = Point(dims="mixed")

multi_point_2d = MultiPoint(dims="2d")
multi_point_3d = MultiPoint(dims="3d")
multi_point_either = MultiPoint(dims="either")
multi_point_mixed = MultiPoint(dims="mixed")

line_string_2d = LineString(dims="2d")
line_string_3d = LineString(dims="3d")
line_string_either = LineString(dims="either")
line_string_mixed = LineString(dims="mixed")

multi_line_string_2d = MultiLineString(dims="2d")
multi_line_string_3d = MultiLineString(dims="3d")
multi_line_string_either = MultiLineString(dims="either")
multi_line_string_mixed = MultiLineString(dims="mixed")

polygon_2d = Polygon(dims="2d")
polygon_3d = Polygon(dims="3d")
polygon_either = Polygon(dims="either")
polygon_mixed = Polygon(dims="mixed")

multi_polygon_2d = MultiPolygon(dims="2d")
multi_polygon_3d = MultiPolygon(dims="3d")
multi_polygon_either = MultiPolygon(dims="either")
multi_polygon_mixed = MultiPolygon(dims="mixed")

geometry_2d = Geometry(dims="2d")
geometry_3d = Geometry(dims="3d")
geometry_either = Geometry(dims="either")
geometry_mixed = Geometry(dims="mixed")

geometry_collection_2d = GeometryCollection(dims="2d")
geometry_collection_3d = GeometryCollection(dims="3d")
geometry_collection_either = GeometryCollection(dims="either")
geometry_collection_mixed = GeometryCollection(dims="mixed")

# Features
feature_2d = Feature(dims="2d")
feature_3d = Feature(dims="3d")
feature_either = Feature(dims="either")
feature_mixed = Feature(dims="mixed")

feature_collection_2d = FeatureCollection(dims="2d")
feature_collection_3d = FeatureCollection(dims="3d")
feature_collection_either = FeatureCollection(dims="either")
feature_collection_mixed = FeatureCollection(dims="mixed")
