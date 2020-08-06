import abc
from typing import Any, List, Tuple, Union
from pydantic import BaseModel, Field, validator

from .utils import NumType

class _GeometryBase(BaseModel, abc.ABC):
    coordinates: Any  # will be constrained in child classes

    @property
    def __geo_interface__(self):
        return self.dict()

Coordinate = Union[
    Tuple[NumType, NumType],
    Tuple[NumType, NumType, NumType]
]

Position = Coordinate

class Point(_GeometryBase):
    type: str = Field("Point", const=True)
    coordinates: Coordinate

class MultiPoint(_GeometryBase):
    type: str = Field("MultiPoint", const=True)
    coordinates: List[Coordinate]

class LineString(_GeometryBase):
    type: str = Field("LineString", const=True)
    coordinates: List[Coordinate] = Field(..., min_items=2)


class MultiLineString(_GeometryBase):
    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Coordinate]]

class Polygon(_GeometryBase):
    type: str = Field("Polygon", const=True)
    coordinates: List[List[Coordinate]]

    @validator("coordinates")
    def check_coordinates(cls, coords):
        if any([len(c) < 4 for c in coords]):
            raise ValueError("All linear rings must have four or more coordinates")
        if any([c[-1] != c[0] for c in coords]):
            raise ValueError("All linear rings have the same start and end coordinates")
        return coords


class MultiPolygon(_GeometryBase):
    type: str = Field("MultiPolygon", const=True)
    coordinates: List[List[List[Coordinate]]]

class GeometryCollection(BaseModel):
    type: str = Field("GeometryCollection", const=True)
    geometries: List[Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]]
