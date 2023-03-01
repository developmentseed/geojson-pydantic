"""Hypothesis strategies and entry point for geojson-pydantic."""
import hypothesis.strategies as st

from geojson_pydantic import (
    Feature,
    FeatureCollection,
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from geojson_pydantic.strategies.helpers import (
    feature_collection_either,
    feature_either,
    geometry_collection_either,
    line_string_either,
    multi_line_string_either,
    multi_point_either,
    multi_polygon_either,
    point_either,
    polygon_either,
)

# We may not want to automatically register the default strategies on import, so we can
# hold them in an function and call that function.


def _hypothesis_setup_hook() -> None:
    """Setup hypothesis default strategies."""
    # These are the strategies for geometries which will not mix dimensionality.
    # Each geometry will be either all 2d or all 3d.
    st.register_type_strategy(Point, point_either)
    st.register_type_strategy(MultiPoint, multi_point_either)
    st.register_type_strategy(LineString, line_string_either)
    st.register_type_strategy(MultiLineString, multi_line_string_either)
    st.register_type_strategy(Polygon, polygon_either)
    st.register_type_strategy(MultiPolygon, multi_polygon_either)
    # The entire geometry collection will be either 2d or 3d geometries
    st.register_type_strategy(GeometryCollection, geometry_collection_either)
    # Each feature is generated with the above strategies
    st.register_type_strategy(Feature, feature_either)
    # The feature collection will have only 2d or 3d geometries in it
    st.register_type_strategy(FeatureCollection, feature_collection_either)
