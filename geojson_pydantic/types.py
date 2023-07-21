"""Types for geojson_pydantic models"""

from typing import List, Tuple, Union

from pydantic import Field
from typing_extensions import Annotated

BBox = Union[
    Tuple[float, float, float, float],  # 2D bbox
    Tuple[float, float, float, float, float, float],  # 3D bbox
]

Position = Union[Tuple[float, float], Tuple[float, float, float]]

# Coordinate arrays
LineStringCoords = Annotated[List[Position], Field(min_length=2)]
LinearRing = Annotated[List[Position], Field(min_length=4)]
MultiPointCoords = List[Position]
MultiLineStringCoords = List[LineStringCoords]
PolygonCoords = List[LinearRing]
MultiPolygonCoords = List[PolygonCoords]
