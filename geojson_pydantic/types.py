"""Types for geojson_pydantic models"""

from typing import Tuple, Union

NumType = Union[float, int]
BBox = Union[
    Tuple[NumType, NumType, NumType, NumType],  # 2D bbox
    Tuple[NumType, NumType, NumType, NumType, NumType, NumType],  # 3D bbox
]
Position = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]
