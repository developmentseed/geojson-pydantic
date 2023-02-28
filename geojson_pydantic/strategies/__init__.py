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
from geojson_pydantic.strategies.features import feature, feature_collection
from geojson_pydantic.strategies.geometries import (
    geometry_collection,
    line_string,
    multi_line_string,
    multi_point,
    multi_polygon,
    point,
    polygon,
)

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
