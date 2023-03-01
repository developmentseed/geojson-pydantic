"""Hypothesis strategies for generating features."""
import string
from typing import Any

from hypothesis.strategies import (
    DrawFn,
    booleans,
    composite,
    dictionaries,
    integers,
    lists,
    none,
    recursive,
    text,
    uuids,
)

from geojson_pydantic import features
from geojson_pydantic.strategies.geometries import (
    Dimensionality,
    Geometry,
    GeometryFunction,
    Places,
    z,
)

# Just using positive integers and uuids for for IDs for simplicity
feature_id = integers(min_value=0) | uuids().map(str)
# Keep the strings easy to print and read without special characters for the time being
alpha_numeric = text(string.ascii_letters + string.digits, min_size=1)
# Starting as a dict use alpha numeric keys and then use recursive values with limited leaves
properties_dict = dictionaries(
    alpha_numeric,
    recursive(
        none() | booleans() | z | z.map(int) | alpha_numeric,
        lambda children: lists(children) | dictionaries(alpha_numeric, children),
        max_leaves=3,
    ),
)


@composite
def Feature(
    draw: DrawFn,
    *,
    dims: Dimensionality = "either",
    places: Places = 6,
    allow_close_to_zero: bool = False,
    geometry: GeometryFunction = Geometry,
    min_size: int = 1,
    **kwargs: Any,
) -> features.Feature:
    """Generate a Feature with a random Geometry.

    This does not generate a bbox since it would not correspond with the geometry.
    A future version could calculate the bbox from the geometry.
    """
    return features.Feature(
        type="Feature",
        geometry=draw(
            geometry(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
            )
        ),
        id=draw(none() | feature_id),
        properties=draw(none() | properties_dict),
        bbox=None,
    )


@composite
def FeatureCollection(
    draw: DrawFn,
    *,
    dims: Dimensionality = "either",
    places: Places = 6,
    allow_close_to_zero: bool = False,
    geometry: GeometryFunction = Geometry,
    min_size: int = 1,
    min_feature_size: int = 1,
    **kwargs: Any,
) -> features.FeatureCollection:
    """Generate a FeatureCollection with random Features.

    This does not generate a bbox since it would not correspond with the Features.
    A future version could calculate the bbox from the Features.
    """
    return features.FeatureCollection(
        type="FeatureCollection",
        features=draw(
            lists(
                Feature(
                    dims=dims,
                    places=places,
                    allow_close_to_zero=allow_close_to_zero,
                    geometry=geometry,
                    min_size=min_feature_size,
                ),
                min_size=min_size,
            )
        ),
        bbox=None,
    )
