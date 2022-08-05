"""Types for geojson_pydantic models"""

from typing import Tuple, Union

from pydantic import conlist

BBox = Union[
    Tuple[float, float, float, float],  # 2D bbox
    Tuple[float, float, float, float, float, float],  # 3D bbox
]
Position = Union[Tuple[float, float], Tuple[float, float, float]]

# Coordinate arrays
MultiPointCoords = conlist(Position, min_items=1)
LineStringCoords = conlist(Position, min_items=2)
MultiLineStringCoords = conlist(LineStringCoords, min_items=1)
LinearRing = conlist(Position, min_items=4)
PolygonCoords = conlist(LinearRing, min_items=1)
MultiPolygonCoords = conlist(PolygonCoords, min_items=1)
