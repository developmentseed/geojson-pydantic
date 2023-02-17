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

# Use RegEx to generate strings which are plausible values for coordinates and convert them to floats.
longitude_strategy = st.from_regex(r"^(-)?((1?[1-7]?[0-9](\.[0-9]{1,8})?)|180)$").map(
    float
)
latitude_strategy = st.from_regex(r"^(-)?(([1-8]?[0-9](\.[0-9]{1,8})?)|90)$").map(float)
z_strategy = st.from_regex(r"^(-)?[0-9]{1,5}(\.[0-9]{1,2})?$").map(float)

# Strategies for coordinates
coord_2d_strategy = st.tuples(longitude_strategy, latitude_strategy)
coord_3d_strategy = st.tuples(longitude_strategy, latitude_strategy, z_strategy)
coord_strategy = st.one_of(coord_2d_strategy, coord_3d_strategy)

coords_2d_strategy = st.lists(coord_2d_strategy, min_size=2)
coords_3d_strategy = st.lists(coord_3d_strategy, min_size=2)
coords_strategy = st.one_of(coords_2d_strategy, coords_3d_strategy)

multi_line_string_2d_strategy = st.lists(coords_2d_strategy, min_size=1)
multi_line_string_3d_strategy = st.lists(coords_3d_strategy, min_size=1)
multi_line_string_strategy = st.one_of(
    multi_line_string_2d_strategy, multi_line_string_3d_strategy
)

linear_ring_2d_strategy = st.lists(coord_2d_strategy, min_size=4).map(
    lambda x: x + [x[0]]
)
linear_ring_3d_strategy = st.lists(coord_3d_strategy, min_size=4).map(
    lambda x: x + [x[0]]
)

polygon_2d_strategy = st.lists(linear_ring_2d_strategy, min_size=1)
polygon_3d_strategy = st.lists(linear_ring_3d_strategy, min_size=1)
polygon_strategy = st.one_of(polygon_2d_strategy, polygon_3d_strategy)

multi_polygon_2d_strategy = st.lists(polygon_2d_strategy, min_size=1)
multi_polygon_3d_strategy = st.lists(polygon_3d_strategy, min_size=1)
multi_polygon_strategy = st.one_of(multi_polygon_2d_strategy, multi_polygon_3d_strategy)

# Create strategies that give two of each coordinate type sorted
two_lat = (
    st.tuples(latitude_strategy, latitude_strategy)
    .filter(lambda x: x[0] != x[1])
    .map(sorted)
)
two_lon = (
    st.tuples(longitude_strategy, longitude_strategy)
    .filter(lambda x: x[0] != x[1])
    .map(sorted)
)
two_z = st.tuples(z_strategy, z_strategy).filter(lambda x: x[0] != x[1]).map(sorted)

# Generate a pair of lons and lats, then interleave them together
bbox_2d_strategy = st.tuples(two_lon, two_lat).map(
    lambda x: (x[0][0], x[1][0], x[0][1], x[1][1])
)
# Do the same but add Z coords as well
bbox_3d_strategy = st.tuples(two_lon, two_lat, two_z).map(
    lambda x: (x[0][0], x[1][0], x[0][1], x[1][1], *x[2])
)
bbox_strategy = st.one_of(bbox_2d_strategy, bbox_3d_strategy)


st.register_type_strategy(Point, st.builds(Point, coordinates=coord_strategy))
st.register_type_strategy(
    MultiPoint, st.builds(MultiPoint, coordinates=coords_strategy)
)
st.register_type_strategy(
    LineString, st.builds(LineString, coordinates=coords_strategy)
)
st.register_type_strategy(
    MultiLineString, st.builds(MultiLineString, coordinates=multi_line_string_strategy)
)
st.register_type_strategy(Polygon, st.builds(Polygon, coordinates=polygon_strategy))
st.register_type_strategy(
    MultiPolygon, st.builds(MultiPolygon, coordinates=multi_polygon_strategy)
)

st.builds(GeometryCollection).example()
