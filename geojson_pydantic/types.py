"""Types for geojson_pydantic models"""

from typing import Tuple, Union

from pydantic import conlist

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]
Position = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]

# Coordinate arrays
MultiPointCoords = conlist(Position, min_items=1)
LineStringCoords = conlist(Position, min_items=2)
MultiLineStringCoords = conlist(LineStringCoords, min_items=1)
LinearRing = conlist(Position, min_items=4)
PolygonCoords = conlist(LinearRing, min_items=1)
MultiPolygonCoords = conlist(PolygonCoords, min_items=1)
