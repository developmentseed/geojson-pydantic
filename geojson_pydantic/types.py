"""Types for geojson_pydantic models"""

from typing import Tuple, Union

BBox2D = Tuple[float, float, float, float]
BBox3D = Tuple[float, float, float, float, float, float]
BBox = Union[BBox2D, BBox3D]

Position2D = Tuple[float, float]
Position3D = Tuple[float, float, float]
Position = Union[Position2D, Position3D]
