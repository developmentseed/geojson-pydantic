"""Types for geojson_pydantic models"""

from typing import TYPE_CHECKING, List, Tuple, Union

from pydantic import conlist

BBox = Union[
    Tuple[float, float, float, float],  # 2D bbox
    Tuple[float, float, float, float, float, float],  # 3D bbox
]
Position = Union[Tuple[float, float], Tuple[float, float, float]]

# Coordinate arrays

if TYPE_CHECKING:
    MultiPointCoords = List[Position]
    LineStringCoords = List[Position]
    LinearRing = List[Position]
    MultiLineStringCoords = List[List[Position]]
    PolygonCoords = List[List[Position]]
    MultiPolygonCoords = List[List[List[Position]]]
else:
    MultiPointCoords = conlist(Position)
    LineStringCoords = conlist(Position, min_items=2)
    LinearRing = conlist(Position, min_items=4)
    MultiLineStringCoords = conlist(LineStringCoords)
    PolygonCoords = conlist(LinearRing)
    MultiPolygonCoords = conlist(PolygonCoords)
