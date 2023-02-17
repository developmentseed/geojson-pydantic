import string
from typing import List, Tuple, TypeVar

from hypothesis import strategies as st

from geojson_pydantic.features import Feature, FeatureCollection
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


def close_ring(values: List[T]) -> List[T]:
    """Close a linear ring by adding the first coordinate to the end."""
    return values + [values[0]]


def interleave(values: Tuple[List[T], ...]) -> Tuple[T, ...]:
    """Interleave tuple of tuples together."""
    return tuple(v for t in zip(*values) for v in t)


# Custom Strategies for floats that make sense as WGS-84 Coordinates.
# These will never produce -180/180 or -90/90 in order to stay within limits once
# the decimals are added to them.
# Z limits of +/- 100,000 were just to keep the generated values from being excessive.

# Generate the integer portion of the coordinates
int_lon = st.integers(min_value=-179, max_value=179)
int_lat = st.integers(min_value=-89, max_value=89)
int_z = st.integers(min_value=-100000, max_value=100000)
# Generate decimal places for the coordinates
int_7_digit = st.integers(min_value=0, max_value=9999999)
ind_3_digit = st.integers(min_value=0, max_value=999)
# Generate values by combining the integer and decimal then mapping it to float
longitude = st.tuples(int_lon, int_7_digit).map(make_float)
latitude = st.tuples(int_lat, int_7_digit).map(make_float)
z = st.tuples(int_z, ind_3_digit).map(make_float)

# Coordinate Strategies

# Coordinates
coord_2d = st.tuples(longitude, latitude)
coord_3d = st.tuples(longitude, latitude, z)
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
multi_point = multi_point_2d | multi_point_3d
# Line
line_string_2d = st.builds(LineString, coordinates=coord_list_2d)
line_string_3d = st.builds(LineString, coordinates=coord_list_3d)
line_string = line_string_2d | line_string_3d
# Multi Line
multi_line_string_2d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_2d
)
multi_line_string_3d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_3d
)
multi_line_string = multi_line_string_2d | multi_line_string_2d
# Polygon
polygon_2d = st.builds(Polygon, coordinates=polygon_coords_2d)
polygon_3d = st.builds(Polygon, coordinates=polygon_coords_3d)
polygon = polygon_2d | polygon_3d
# Multi Polygon
multi_polygon_2d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_2d)
multi_polygon_3d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_3d)
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
geometry_collection_2d = st.builds(
    GeometryCollection, geometries=st.lists(geometry_2d, min_size=1)
)
geometry_collection_3d = st.builds(
    GeometryCollection, geometries=st.lists(geometry_3d, min_size=1)
)
geometry_collection = geometry_collection_2d | geometry_collection_3d

# Bounding Box

# Strategies which produce two unique and sorted values for each coordinate type
# For some reason mypy does not like the `map(sorted)` but it is an example in the
# hypothesis docs.
two_lon = st.lists(longitude, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_lat = st.lists(latitude, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_z = st.lists(z, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]

# Generate two lons and two lats and interleave them together
bbox_2d = st.tuples(two_lon, two_lat).map(interleave)
bbox_3d = st.tuples(two_lon, two_lat, two_z).map(interleave)
bbox = bbox_2d | bbox_3d


# Feature

# Just using positive integers and uuids for for IDs for simplicity
feature_id = st.integers(min_value=0) | st.uuids().map(str)
# Keep the strings easy to print and read without special characters for the time being
alpha_numeric = st.text(string.ascii_letters + string.digits, min_size=1)
# Starting as a dict use alpha numeric keys and then use recursive values with limited leaves
properties_dict = st.dictionaries(
    alpha_numeric,
    st.recursive(
        st.none() | st.booleans() | z | int_z | alpha_numeric,
        lambda children: st.lists(children) | st.dictionaries(alpha_numeric, children),
        max_leaves=3,
    ),
)
# This does not randomly generate a bbox since it would not correspond with the geometry.
# A composite strategy could be used to compute the bbox from the geometry.
feature_2d = st.builds(
    Feature,
    geometry=geometry_2d,
    properties=st.none() | properties_dict,
    id=st.none() | feature_id,
    bbox=st.none(),
)
feature_3d = st.builds(
    Feature,
    geometry=geometry_3d,
    properties=st.none() | properties_dict,
    id=st.none() | feature_id,
    bbox=st.none(),
)
feature = feature_2d | feature_3d

# Feature Collection

feature_collection_2d = st.builds(
    FeatureCollection, features=st.lists(feature_2d), bbox=st.none()
)
feature_collection_3d = st.builds(
    FeatureCollection, features=st.lists(feature_2d), bbox=st.none()
)
feature_collection = feature_collection_2d | feature_collection_3d


# We may not want to automatically register the default strategies on import, so we can
# hold them in an function and call that function.


def _hypothesis_setup_hook() -> None:
    """Setup hypothesis default strategies."""
    # These are the strategies for geometries which will not mix dimensionality.
    # Each geometry will be either all 2d or all 3d.
    st.register_type_strategy(Point, point)
    st.register_type_strategy(MultiPoint, multi_point)
    st.register_type_strategy(LineString, line_string)
    st.register_type_strategy(MultiLineString, multi_line_string)
    st.register_type_strategy(Polygon, polygon)
    st.register_type_strategy(MultiPolygon, multi_polygon)
    # The entire geometry collection will be either 2d or 3d geometries
    st.register_type_strategy(GeometryCollection, geometry_collection)
    # Each feature is generated with the above strategies
    st.register_type_strategy(Feature, feature)
    # The feature collection will have only 2d or 3d geometries in it
    st.register_type_strategy(FeatureCollection, feature_collection)
