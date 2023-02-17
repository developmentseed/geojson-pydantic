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

# Custom Strategies for Floats that make sense as Coordinates

# Generate the integer portion of the coordinates
int_lon = st.integers(min_value=-180, max_value=180)
int_lat = st.integers(min_value=-90, max_value=90)
int_z = st.integers(min_value=-100000, max_value=100000)
# Generate decimal places for the coordinates
int_dec_7 = st.integers(min_value=0, max_value=9999999)
ind_dec_3 = st.integers(min_value=0, max_value=999)
# Generate values by combining the integer and decimal then mapping it to float
longitude_strategy = (
    st.tuples(int_lon, int_dec_7).map(lambda x: f"{x[0]}.{x[1]}").map(float)
)
latitude_strategy = (
    st.tuples(int_lat, int_dec_7).map(lambda x: f"{x[0]}.{x[1]}").map(float)
)
z_strategy = st.tuples(int_z, ind_dec_3).map(lambda x: f"{x[0]}.{x[1]}").map(float)

# Coordinate Strategies

# Coordinates
coord_2d_strategy = st.tuples(longitude_strategy, latitude_strategy)
coord_3d_strategy = st.tuples(longitude_strategy, latitude_strategy, z_strategy)
coord_strategy = st.one_of(coord_2d_strategy, coord_3d_strategy)
# Coordinate Lists (MultiPoint & LineString)
coord_list_2d_strategy = st.lists(coord_2d_strategy, min_size=2)
coord_list_3d_strategy = st.lists(coord_3d_strategy, min_size=2)
coord_list_strategy = st.one_of(coord_list_2d_strategy, coord_list_3d_strategy)
# MultiLineString Coordinates
multi_line_string_coords_2d_strategy = st.lists(coord_list_2d_strategy, min_size=1)
multi_line_string_coords_3d_strategy = st.lists(coord_list_3d_strategy, min_size=1)
multi_line_string_coords_strategy = st.one_of(
    multi_line_string_coords_2d_strategy, multi_line_string_coords_3d_strategy
)
# Linear Ring. At least 3 coords and append the first to the end to close it.
linear_ring_coords_2d_strategy = st.lists(coord_2d_strategy, min_size=3).map(
    lambda x: x + [x[0]]
)
linear_ring_coords_3d_strategy = st.lists(coord_3d_strategy, min_size=3).map(
    lambda x: x + [x[0]]
)
# Polygon Coordinates
polygon_coords_2d_strategy = st.lists(linear_ring_coords_2d_strategy, min_size=1)
polygon_coords_3d_strategy = st.lists(linear_ring_coords_3d_strategy, min_size=1)
polygon_coords_strategy = st.one_of(
    polygon_coords_2d_strategy, polygon_coords_3d_strategy
)
# MultiPolygon Coordinate
multi_polygon_coords_2d_strategy = st.lists(polygon_coords_2d_strategy, min_size=1)
multi_polygon_coords_3d_strategy = st.lists(polygon_coords_3d_strategy, min_size=1)
multi_polygon_coords_strategy = st.one_of(
    multi_polygon_coords_2d_strategy, multi_polygon_coords_3d_strategy
)

# Geometry Strategies

# Point
point_2d_strategy = st.builds(Point, coordinates=coord_2d_strategy)
point_3d_strategy = st.builds(Point, coordinates=coord_3d_strategy)
point_strategy = st.one_of(point_2d_strategy, point_3d_strategy)
# Multi Point
multi_point_2d_strategy = st.builds(MultiPoint, coordinates=coord_list_2d_strategy)
multi_point_3d_strategy = st.builds(MultiPoint, coordinates=coord_list_3d_strategy)
multi_point_strategy = st.one_of(multi_point_2d_strategy, multi_point_3d_strategy)
# Line
line_string_2d_strategy = st.builds(LineString, coordinates=coord_list_2d_strategy)
line_string_3d_strategy = st.builds(LineString, coordinates=coord_list_3d_strategy)
line_string_strategy = st.one_of(line_string_2d_strategy, line_string_3d_strategy)
# Multi Line
multi_line_string_2d_strategy = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_2d_strategy
)
multi_line_string_3d_strategy = st.builds(
    MultiLineString, coordinates=multi_line_string_coords_3d_strategy
)
multi_line_string_strategy = st.one_of(
    multi_line_string_2d_strategy, multi_line_string_2d_strategy
)
# Polygon
polygon_2d_strategy = st.builds(Polygon, coordinates=polygon_coords_2d_strategy)
polygon_3d_strategy = st.builds(Polygon, coordinates=polygon_coords_3d_strategy)
polygon_strategy = st.one_of(polygon_2d_strategy, polygon_3d_strategy)
# Multi Polygon
multi_polygon_2d_strategy = st.builds(
    MultiPolygon, coordinates=multi_polygon_coords_2d_strategy
)
multi_polygon_3d_strategy = st.builds(
    MultiPolygon, coordinates=multi_polygon_coords_3d_strategy
)
multi_polygon_strategy = st.one_of(multi_polygon_2d_strategy, multi_polygon_3d_strategy)
# Geometry
geometry_2d_strategy = st.one_of(
    point_2d_strategy,
    multi_point_2d_strategy,
    line_string_2d_strategy,
    multi_line_string_2d_strategy,
    polygon_2d_strategy,
    multi_polygon_2d_strategy,
)
geometry_3d_strategy = st.one_of(
    point_3d_strategy,
    multi_point_3d_strategy,
    line_string_3d_strategy,
    multi_line_string_3d_strategy,
    polygon_3d_strategy,
    multi_polygon_3d_strategy,
)
geometry_strategy = st.one_of(geometry_2d_strategy, geometry_3d_strategy)
# Geometry Collection
geometry_collection_2d_strategy = st.builds(
    GeometryCollection, geometries=st.lists(geometry_2d_strategy, min_size=1)
)
geometry_collection_3d_strategy = st.builds(
    GeometryCollection, geometries=st.lists(geometry_3d_strategy, min_size=1)
)
geometry_collection_strategy = st.one_of(
    geometry_collection_2d_strategy, geometry_collection_3d_strategy
)

# Register default strategies for Geometries
st.register_type_strategy(Point, point_strategy)
st.register_type_strategy(MultiPoint, multi_point_strategy)
st.register_type_strategy(LineString, line_string_strategy)
st.register_type_strategy(MultiLineString, multi_line_string_strategy)
st.register_type_strategy(Polygon, polygon_strategy)
st.register_type_strategy(MultiPolygon, multi_polygon_strategy)
st.register_type_strategy(GeometryCollection, geometry_collection_strategy)

# Bounding Box

T = TypeVar("T")


def interleave(values: Tuple[List[T], ...]) -> Tuple[T, ...]:
    """Interleave tuple of tuples together."""
    return tuple(v for t in zip(*values) for v in t)


# Strategies which produce two unique and sorted values for each coordinate type
# For some reason mypy does not like the `map(sorted)` but it is an example in the
# hypothesis docs.
two_lon = st.lists(longitude_strategy, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_lat = st.lists(latitude_strategy, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]
two_z = st.lists(z_strategy, min_size=2, max_size=2, unique=True).map(sorted)  # type: ignore[arg-type]


# Generate two lons and two lats and interleave them together
bbox_2d_strategy = st.tuples(two_lon, two_lat).map(interleave)
bbox_3d_strategy = st.tuples(two_lon, two_lat, two_z).map(interleave)
bbox_strategy = st.one_of(bbox_2d_strategy, bbox_3d_strategy)
