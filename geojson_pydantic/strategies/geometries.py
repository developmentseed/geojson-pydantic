"""Hypothesis strategies for generating geometries."""
from typing import Any, List, Literal, Optional, Protocol, cast

from hypothesis.strategies import (
    DrawFn,
    SearchStrategy,
    composite,
    floats,
    lists,
    sampled_from,
)

from geojson_pydantic import geometries, types

# Using a Literal for the number of places to round to, as it is a finite set of numbers.
Places = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# Options for the dimensionality of the coordinates or geometries. When choosing `either`
# the dimensionality will be determined in the Coordinate strategy, so all of the coordinates
# will be the same type. And when choosing `mixed` the dimensionality will be determined
# in Position and is not guaranteed to be the same for all coordinates.
Dimensionality = Optional[Literal["2d", "3d", "either", "mixed"]]
# When choosing a dimensionality randomly we want to choose either 2d or 3d geometries.
dimensionality: SearchStrategy[Dimensionality] = sampled_from(("2d", "3d"))

# Simple strategies for floats that make sense as WGS-84 Coordinates.
lon = floats(min_value=-180, max_value=180)
lat = floats(min_value=-90, max_value=90)
z = floats(min_value=-100000, max_value=100000)

# We may want to filter values which are close to zero, as they are not realistic
# coordinates, and they end up being written like 1e-05.


def close_to_zero(value: float) -> bool:
    """Filter to remove values that are close to but not equal to zero."""
    return value == 0 or abs(value) > 0.0001


lon_filtered = lon.filter(close_to_zero)
lat_filtered = lat.filter(close_to_zero)
z_filtered = z.filter(close_to_zero)


@composite
def BBox(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    **kwargs: Any,
) -> types.BBox:
    """Generate a bounding box.

    No uniqueness is enforced, as a degenerated bounding box could be allowed.
    For example: (0, 0, 0, 0)
    """
    # Draw a dimensionality if we don't have one that is either 2d or 3d.
    if dims not in ("2d", "3d"):
        dims = draw(dimensionality)

    # Draw two positions, which will be used to create the bounding box.
    positions = draw(
        lists(
            Position(dims=dims, places=places, allow_close_to_zero=allow_close_to_zero),
            min_size=2,
            max_size=2,
        )
    )
    # Zip the positions together and sort them. This will give us the min and max for
    # each dimension. [(min_lon, max_lon), (min_lat, max_lat), (min_z, max_z)]
    coordinate_pairs = (sorted(z) for z in zip(*positions))
    # Interleave the coordinate pairs back together and return them.
    # Because of the zips, mypy doesn't like the type of the return value, so we cast it.
    return cast(types.BBox, tuple(c for p in zip(*coordinate_pairs) for c in p))


@composite
def Position(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    **kwargs: Any,
) -> types.Position:
    """Generate a position."""
    # If we allow close to zero, we use the unfiltered strategies. And if we don't
    # allow close to zero, we use the filtered strategies.
    if allow_close_to_zero:
        lon_strategy = lon
        lat_strategy = lat
        z_strategy = z
    else:
        lon_strategy = lon_filtered
        lat_strategy = lat_filtered
        z_strategy = z_filtered

    # Draw a dimensionality if we don't have one that is either 2d or 3d.
    if dims not in ("2d", "3d"):
        dims = draw(dimensionality)

    # Draw a position based on the dimensionality.
    if dims == "2d":
        return (round(draw(lon_strategy), places), round(draw(lat_strategy), places))
    else:
        return (
            round(draw(lon_strategy), places),
            round(draw(lat_strategy), places),
            round(draw(z_strategy), places),
        )


@composite
def PositionList(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    **kwargs: Any,
) -> List[types.Position]:
    """Generate a list of coordinates.

    This is used for MultiPoint, LineString, and MultiLineStringCoords.
    """
    # If we get "either" as the dimensionality, we draw one.
    if dims == "either":
        dims = draw(dimensionality)
    # Draw a list of Positions.
    return draw(
        lists(
            Position(dims=dims, places=places, allow_close_to_zero=allow_close_to_zero),
            min_size=min_size,
        )
    )


@composite
def MultiLineStringCoords(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_line_size: int = 2,
    **kwargs: Any,
) -> types.MultiLineStringCoords:
    """Generate MultiLineStringCoords."""
    # If we get "either" as the dimensionality, we draw one.
    if dims == "either":
        dims = draw(dimensionality)
    # TODO: Min line size parameter?
    return draw(
        lists(
            PositionList(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_line_size,
            ),
            min_size=min_size,
        )
    )


@composite
def LinearRingCoords(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 3,
    **kwargs: Any,
) -> types.LinearRing:
    """Generate a linear ring."""
    # If we get "either" as the dimensionality, we draw one.
    if dims == "either":
        dims = draw(dimensionality)
    # Draw a list of coordinates
    coordinates = draw(
        PositionList(
            dims=dims,
            places=places,
            allow_close_to_zero=allow_close_to_zero,
            min_size=min_size,
        )
    )
    # Then add the first coordinate to the end to make it a ring.
    return coordinates + [coordinates[0]]


@composite
def PolygonCoords(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_ring_size: int = 3,
    **kwargs: Any,
) -> types.PolygonCoords:
    """Generate types.PolygonCoords."""
    # If we get "either" as the dimensionality, we draw one.
    if dims == "either":
        dims = draw(dimensionality)

    # TODO: Min ring size parameter?
    return draw(
        lists(
            LinearRingCoords(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_ring_size,
            ),
            min_size=min_size,
        )
    )


@composite
def MultiPolygonCoords(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_polygon_size: int = 1,
    min_ring_size: int = 3,
    **kwargs: Any,
) -> types.MultiPolygonCoords:
    """Generate types.MultiPolygonCoords."""
    # If we get "either" as the dimensionality, we draw one.
    if dims == "either":
        dims = draw(dimensionality)

    return draw(
        lists(
            PolygonCoords(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_polygon_size,
                min_ring_size=min_ring_size,
            ),
            min_size=min_size,
        )
    )


@composite
def Point(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    **kwargs: Any,
) -> geometries.Point:
    """Generate a geometries.Point."""
    return geometries.Point(
        type="Point",
        coordinates=draw(
            Position(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
            )
        ),
    )


@composite
def MultiPoint(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    **kwargs: Any,
) -> geometries.MultiPoint:
    """Generate a geometries.MultiPoint."""
    return geometries.MultiPoint(
        type="MultiPoint",
        coordinates=draw(
            PositionList(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
            )
        ),
    )


@composite
def LineString(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 2,
    **kwargs: Any,
) -> geometries.LineString:
    """Generate a LineString."""
    # We cannot have a line string with less than two points. It will not
    # validate correctly and break things. If you need invalid data, use on of the
    # Coordinate strategies directly.
    if min_size < 2:
        min_size = 2
    return geometries.LineString(
        type="LineString",
        coordinates=draw(
            PositionList(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
            )
        ),
    )


@composite
def MultiLineString(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_line_size: int = 2,
    **kwargs: Any,
) -> geometries.MultiLineString:
    """Generate a MultiLineString."""
    return geometries.MultiLineString(
        type="MultiLineString",
        coordinates=draw(
            MultiLineStringCoords(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
                min_line_size=min_line_size,
            )
        ),
    )


@composite
def Polygon(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_ring_size: int = 3,
    **kwargs: Any,
) -> geometries.Polygon:
    """Generate a Polygon."""
    # We cannot have a linear ring that starts with less than 3 points. It will not
    # validate correctly and break things. If you need invalid data, use on of the
    # Coordinate strategies directly.
    if min_ring_size < 3:
        min_ring_size = 3
    return geometries.Polygon(
        type="Polygon",
        coordinates=draw(
            PolygonCoords(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
                min_ring_size=min_ring_size,
            )
        ),
    )


@composite
def MultiPolygon(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_polygon_size: int = 1,
    min_ring_size: int = 3,
    **kwargs: Any,
) -> geometries.MultiPolygon:
    """Generate a MultiPolygon."""
    return geometries.MultiPolygon(
        type="MultiPolygon",
        coordinates=draw(
            MultiPolygonCoords(
                dims=dims,
                places=places,
                allow_close_to_zero=allow_close_to_zero,
                min_size=min_size,
                min_polygon_size=min_polygon_size,
                min_ring_size=min_ring_size,
            )
        ),
    )


class GeometryFunction(Protocol):
    """A protocol for Geometry functions."""

    def __call__(
        self,
        *,
        dims: Dimensionality,
        places: Places,
        allow_close_to_zero: bool,
        **kwargs: Any,
    ) -> SearchStrategy[geometries.Geometry]:
        """Generate the Geometry."""
        ...


geometry_function = sampled_from(
    (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)
)


@composite
def Geometry(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    **kwargs: Any,
) -> geometries.Geometry:
    """Generate a Geometry."""
    # Cast to GeometryFunction to appease mypy, we know it's a GeometryFunction
    function = cast(GeometryFunction, draw(geometry_function))
    # Draw from the function and return the result
    return draw(
        function(
            dims=dims,
            places=places,
            allow_close_to_zero=allow_close_to_zero,
            min_size=min_size,
            **kwargs,  # Pass through any extra args to the function
        )
    )


@composite
def GeometryCollection(
    draw: DrawFn,
    *,
    dims: Dimensionality = None,
    places: Places = 6,
    allow_close_to_zero: bool = False,
    min_size: int = 0,
    min_geometry_size: int = 1,
    **kwargs: Any,
) -> geometries.GeometryCollection:
    """Generate a GeometryCollection."""
    return geometries.GeometryCollection(
        type="GeometryCollection",
        geometries=draw(
            lists(
                Geometry(
                    dims=dims,
                    places=places,
                    allow_close_to_zero=allow_close_to_zero,
                    min_size=min_geometry_size,
                ),
                min_size=min_size,
            ),
        ),
    )
