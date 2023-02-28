"""Hypothesis strategies for generating bounding boxes."""
from typing import List, Tuple, TypeVar

from hypothesis import strategies as st

from geojson_pydantic.strategies.geometries import lat, lon, z

T = TypeVar("T")


def interleave(values: Tuple[List[T], ...]) -> Tuple[T, ...]:
    """Interleave tuple of tuples together."""
    return tuple(v for t in zip(*values) for v in t)


# Bounding Box

# Strategies which produce two sorted values for each coordinate type. No uniqueness
# is enforced, as a degenerated bounding box could be allowed.

# For some reason mypy does not like the `map(sorted)` but it is an example in the
# hypothesis docs.
two_lon = st.lists(lon, min_size=2, max_size=2).map(sorted)  # type: ignore[arg-type]
two_lat = st.lists(lat, min_size=2, max_size=2).map(sorted)  # type: ignore[arg-type]
two_z = st.lists(z, min_size=2, max_size=2).map(sorted)  # type: ignore[arg-type]

# Generate two lons and two lats and interleave them together
bbox_2d = st.tuples(two_lon, two_lat).map(interleave)
bbox_3d = st.tuples(two_lon, two_lat, two_z).map(interleave)
bbox = bbox_2d | bbox_3d
