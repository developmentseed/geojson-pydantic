import abc
import geojson
from typing import Any, List, Tuple, Union
from pydantic import BaseModel, Field, validator

from .utils import NumType

class _GeometryBase(BaseModel, abc.ABC):
    coordinates: Any  # will be constrained in child classes

    @validator("coordinates")
    def check_coordinates(cls, coords):
        geojson_instance = getattr(geojson, cls.__name__)(coordinates=coords)

        if geojson_instance.is_valid:
            return coords
        else:
            raise ValueError(geojson_instance.errors())

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
    coordinates: List[Coordinate]

class MultiLineString(_GeometryBase):
    type: str = Field("MultiLineString", const=True)
    coordinates: List[List[Coordinate]]

class Polygon(_GeometryBase):
    type: str = Field("Polygon", const=True)
    coordinates: List[List[Coordinate]]

class MultiPolygon(_GeometryBase):
    type: str = Field("MultiPolygon", const=True)
    coordinates: List[List[List[Coordinate]]]

class GeometryCollection(BaseModel):
    type: str = Field("GeometryCollection", const=True)
    geometries: List[Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]]
