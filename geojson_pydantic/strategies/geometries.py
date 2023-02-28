"""Hypothesis strategies for generating geometries."""
from typing import List, Tuple, TypeVar

from hypothesis import strategies as st

from geojson_pydantic.geometries import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

T = TypeVar("T")

# Helpers to use in strategy `.map()` functions


def make_float(values: Tuple[int, int]) -> float:
    """Concatenate a whole number part and a decimal part together to make a float."""
    return float(f"{values[0]}.{values[1]}")


def cap_lon(lon: float) -> float:
    """Cap longitude values at -180 / 180."""
    if lon < -180:
        return -180.0
    if lon > 180:
        return 180.0
    return lon


def cap_lat(lat: float) -> float:
    """Cap latitude values at -90 / 90."""
    if lat < -90:
        return -90.0
    if lat > 90:
        return 90.0
    return lat


def close_ring(values: List[T]) -> List[T]:
    """Close a linear ring by adding the first coordinate to the end."""
    return values + [values[0]]


# Custom Strategies for floats that make sense as WGS-84 Coordinates.

# Generate the integer portion of the coordinates
int_lon = st.integers(min_value=-180, max_value=180)
int_lat = st.integers(min_value=-90, max_value=90)
# Z limits of +/- 100,000 were just to keep the generated values from being excessive.
int_z = st.integers(min_value=-100000, max_value=100000)
# Generate decimal places for the coordinates
int_7_digit = st.integers(min_value=0, max_value=9999999)
ind_3_digit = st.integers(min_value=0, max_value=999)
# Generate values by combining the integer and decimal then mapping it to float
lon = st.tuples(int_lon, int_7_digit).map(make_float).map(cap_lon)
lat = st.tuples(int_lat, int_7_digit).map(make_float).map(cap_lat)
z = st.tuples(int_z, ind_3_digit).map(make_float)

# Coordinate Strategies

# Coordinates
coord_2d = st.tuples(lon, lat)
coord_3d = st.tuples(lon, lat, z)
coord = coord_2d | coord_3d
# Coordinate Lists (MultiPoint & LineString)
coord_list_2d = st.lists(coord_2d, min_size=2)
coord_list_3d = st.lists(coord_3d, min_size=2)
coord_list = coord_list_2d | coord_list_3d
# MultiLineString Coordinates
multi_line_string_coords_2d = st.lists(coord_list_2d, min_size=1)
multi_line_string_coords_3d = st.lists(coord_list_3d, min_size=1)
multi_line_string_coords = multi_line_string_coords_2d | multi_line_string_coords_3d
# Linear Ring. At least 3 coords and append the first to the end to close it.
# Not sure why mypy is unhappy here but Pyright is fine with it and it works.
linear_ring_coords_2d = st.lists(coord_2d, min_size=3).map(close_ring)  # type: ignore[arg-type]
linear_ring_coords_3d = st.lists(coord_3d, min_size=3).map(close_ring)  # type: ignore[arg-type]
linear_ring_coords = linear_ring_coords_2d | linear_ring_coords_3d
# Polygon Coordinates
polygon_coords_2d = st.lists(linear_ring_coords_2d, min_size=1)
polygon_coords_3d = st.lists(linear_ring_coords_3d, min_size=1)
polygon_coords = polygon_coords_2d | polygon_coords_3d
# MultiPolygon Coordinate
multi_polygon_coords_2d = st.lists(polygon_coords_2d, min_size=1)
multi_polygon_coords_3d = st.lists(polygon_coords_3d, min_size=1)
multi_polygon_coords = multi_polygon_coords_2d | multi_polygon_coords_3d

# Geometry Strategies

# Point
point_2d = st.builds(Point, coordinates=coord_2d)
point_3d = st.builds(Point, coordinates=coord_3d)
point = point_2d | point_3d
# Multi Point
multi_point_2d = st.builds(MultiPoint, coordinates=coord_list_2d)
multi_point_3d = st.builds(MultiPoint, coordinates=coord_list_3d)
multi_point_mixed = st.builds(MultiPoint, coordinates=coord_list)
multi_point = multi_point_2d | multi_point_3d
# Line
line_string_2d = st.builds(LineString, coordinates=coord_list_2d)
line_string_3d = st.builds(LineString, coordinates=coord_list_3d)
line_string_mixed = st.builds(LineString, coordinates=coord_list)
line_string = line_string_2d | line_string_3d
# Multi Line
multi_line_string_2d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_2d
)
multi_line_string_3d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_3d
)
multi_line_string_mixed = st.builds(
    MultiLineString, coordinates=multi_line_string_coords
)
multi_line_string = multi_line_string_2d | multi_line_string_2d
# Polygon
polygon_2d = st.builds(Polygon, coordinates=polygon_coords_2d)
polygon_3d = st.builds(Polygon, coordinates=polygon_coords_3d)
polygon_mixed = st.builds(Polygon, coordinates=polygon_coords)
polygon = polygon_2d | polygon_3d
# Multi Polygon
multi_polygon_2d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_2d)
multi_polygon_3d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_3d)
multi_polygon_mixed = st.builds(MultiPolygon, multi_polygon_coords)
multi_polygon = multi_polygon_2d | multi_polygon_3d
# Geometry
geometry_2d = (
    point_2d
    | multi_point_2d
    | line_string_2d
    | multi_line_string_2d
    | polygon_2d
    | multi_polygon_2d
)
geometry_3d = (
    point_3d
    | multi_point_3d
    | line_string_3d
    | multi_line_string_3d
    | polygon_3d
    | multi_polygon_3d
)
geometry = geometry_2d | geometry_3d
# Geometry Collection
geometry_collection_2d = st.builds(GeometryCollection, geometries=st.lists(geometry_2d))
geometry_collection_3d = st.builds(GeometryCollection, geometries=st.lists(geometry_3d))
geometry_collection_mixed = st.builds(GeometryCollection, geometries=st.lists(geometry))
geometry_collection = geometry_collection_2d | geometry_collection_3d
