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

# Custom Strategies for floats that make sense as WGS-84 Coordinates

# Generate the integer portion of the coordinates
int_lon = st.integers(min_value=-180, max_value=180)
int_lat = st.integers(min_value=-90, max_value=90)
int_z = st.integers(min_value=-100000, max_value=100000)
# Generate decimal places for the coordinates
int_dec_7 = st.integers(min_value=0, max_value=9999999)
ind_dec_3 = st.integers(min_value=0, max_value=999)
# Generate values by combining the integer and decimal then mapping it to float
longitude = st.tuples(int_lon, int_dec_7).map(lambda x: f"{x[0]}.{x[1]}").map(float)
latitude = st.tuples(int_lat, int_dec_7).map(lambda x: f"{x[0]}.{x[1]}").map(float)
z = st.tuples(int_z, ind_dec_3).map(lambda x: f"{x[0]}.{x[1]}").map(float)

# Coordinate Strategies

# Coordinates
coord_2d = st.tuples(longitude, latitude)
coord_3d = st.tuples(longitude, latitude, z)
coord = st.one_of(coord_2d, coord_3d)
# Coordinate Lists (MultiPoint & LineString)
coord_list_2d = st.lists(coord_2d, min_size=2)
coord_list_3d = st.lists(coord_3d, min_size=2)
coord_list = st.one_of(coord_list_2d, coord_list_3d)
# MultiLineString Coordinates
multi_line_string_coords_2d = st.lists(coord_list_2d, min_size=1)
multi_line_string_coords_3d = st.lists(coord_list_3d, min_size=1)
multi_line_string_coords = st.one_of(
    multi_line_string_coords_2d, multi_line_string_coords_3d
)
# Linear Ring. At least 3 coords and append the first to the end to close it.
linear_ring_coords_2d = st.lists(coord_2d, min_size=3).map(lambda x: x + [x[0]])
linear_ring_coords_3d = st.lists(coord_3d, min_size=3).map(lambda x: x + [x[0]])
# Polygon Coordinates
polygon_coords_2d = st.lists(linear_ring_coords_2d, min_size=1)
polygon_coords_3d = st.lists(linear_ring_coords_3d, min_size=1)
polygon_coords = st.one_of(polygon_coords_2d, polygon_coords_3d)
# MultiPolygon Coordinate
multi_polygon_coords_2d = st.lists(polygon_coords_2d, min_size=1)
multi_polygon_coords_3d = st.lists(polygon_coords_3d, min_size=1)
multi_polygon_coords = st.one_of(multi_polygon_coords_2d, multi_polygon_coords_3d)

# Geometry Strategies

# Point
point_2d = st.builds(Point, coordinates=coord_2d)
point_3d = st.builds(Point, coordinates=coord_3d)
point = st.one_of(point_2d, point_3d)
# Multi Point
multi_point_2d = st.builds(MultiPoint, coordinates=coord_list_2d)
multi_point_3d = st.builds(MultiPoint, coordinates=coord_list_3d)
multi_point = st.one_of(multi_point_2d, multi_point_3d)
# Line
line_string_2d = st.builds(LineString, coordinates=coord_list_2d)
line_string_3d = st.builds(LineString, coordinates=coord_list_3d)
line_string = st.one_of(line_string_2d, line_string_3d)
# Multi Line
multi_line_string_2d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_2d
)
multi_line_string_3d = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_3d
)
multi_line_string = st.one_of(multi_line_string_2d, multi_line_string_2d)
# Polygon
polygon_2d = st.builds(Polygon, coordinates=polygon_coords_2d)
polygon_3d = st.builds(Polygon, coordinates=polygon_coords_3d)
polygon = st.one_of(polygon_2d, polygon_3d)
# Multi Polygon
multi_polygon_2d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_2d)
multi_polygon_3d = st.builds(MultiPolygon, coordinates=multi_polygon_coords_3d)
multi_polygon = st.one_of(multi_polygon_2d, multi_polygon_3d)
# Geometry
geometry_2d = st.one_of(
    point_2d,
    multi_point_2d,
    line_string_2d,
    multi_line_string_2d,
    polygon_2d,
    multi_polygon_2d,
)
geometry_3d = st.one_of(
    point_3d,
    multi_point_3d,
    line_string_3d,
    multi_line_string_3d,
    polygon_3d,
    multi_polygon_3d,
)
geometry = st.one_of(geometry_2d, geometry_3d)
# Geometry Collection
geometry_collection_2d = st.builds(
    GeometryCollection, geometries=st.lists(geometry_2d, min_size=1)
)
geometry_collection_3d = st.builds(
    GeometryCollection, geometries=st.lists(geometry_3d, min_size=1)
)
geometry_collection = st.one_of(geometry_collection_2d, geometry_collection_3d)

# Register default strategies for Geometries
st.register_type_strategy(Point, point)
st.register_type_strategy(MultiPoint, multi_point)
st.register_type_strategy(LineString, line_string)
st.register_type_strategy(MultiLineString, multi_line_string)
st.register_type_strategy(Polygon, polygon)
st.register_type_strategy(MultiPolygon, multi_polygon)
st.register_type_strategy(GeometryCollection, geometry_collection)

# Bounding Box

T = TypeVar("T")


def interleave(values: Tuple[List[T], ...]) -> Tuple[T, ...]:
    """Interleave tuple of tuples together."""
    return tuple(v for t in zip(*values) for v in t)


# Strategies which produce two unique and sorted values for each coordinate type
# For some reason mypy does not like the `map(sorted)` but it is an example in the
# hypothesis docs.
two_lon = st.lists(longitude, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_lat = st.lists(latitude, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_z = st.lists(z, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]


# Generate two lons and two lats and interleave them together
bbox_2d = st.tuples(two_lon, two_lat).map(interleave)
bbox_3d = st.tuples(two_lon, two_lat, two_z).map(interleave)
bbox = st.one_of(bbox_2d, bbox_3d)
