"""Hypothesis strategies for generating features."""
import string

from hypothesis import strategies as st

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.strategies.geometries import geometry_2d, geometry_3d, int_z, z

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
