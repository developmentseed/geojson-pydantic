"""pydantic models for GeoJSON Geometry objects."""

import abc
from typing import Any, List, Union

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper

from geojson_pydantic.types import (
    LineStringCoords,
    MultiLineStringCoords,
    MultiPointCoords,
    MultiPolygonCoords,
    NumType,
    PolygonCoords,
    Position,
)


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Any  # will be constrained in child classes

    @property
    def __geo_interface__(self):
        return self.dict()


class Point(_GeometryBase):
    """Point Model"""

    type: str = Field("Point", const=True)
    coordinates: Position


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: str = Field("MultiPoint", const=True)
    coordinates: MultiPointCoords


class LineString(_GeometryBase):
    """LineString Model"""

    type: str = Field("LineString", const=True)
    coordinates: LineStringCoords


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: str = Field("MultiLineString", const=True)
    coordinates: MultiLineStringCoords


class Polygon(_GeometryBase):
    """Polygon Model"""

    type: str = Field("Polygon", const=True)
    coordinates: PolygonCoords

    @validator("coordinates")
    def check_closure(cls, polygon):
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for ring in polygon]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return polygon

    @classmethod
    def from_bounds(
        cls, xmin: NumType, ymin: NumType, xmax: NumType, ymax: NumType
    ) -> "Polygon":
        """Create a Polygon geometry from a boundingbox."""
        return cls(
            coordinates=[
                [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]]
            ]
        )


class MultiPolygon(_GeometryBase):
    """MultiPolygon Model"""

    type: str = Field("MultiPolygon", const=True)
    coordinates: MultiPolygonCoords


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


class GeometryCollection(BaseModel):
    """GeometryCollection Model"""

    type: str = Field("GeometryCollection", const=True)
    geometries: List[Geometry]

    def __iter__(self):
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self):
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index):
        """get geometry at a given index"""
        return self.geometries[index]


def parse_geometry_obj(obj) -> Geometry:
    """
    `obj` is an object that is supposed to represent a GeoJSON geometry. This method returns the
    reads the `"type"` field and returns the correct pydantic Geometry model.
    """
    if "type" not in obj:
        raise ValidationError(
            errors=[
                ErrorWrapper(ValueError("Missing 'type' field in geometry"), loc="type")
            ],
            model=_GeometryBase,
        )
    if obj["type"] == "Point":
        return Point.parse_obj(obj)
    elif obj["type"] == "MultiPoint":
        return MultiPoint.parse_obj(obj)
    elif obj["type"] == "LineString":
        return LineString.parse_obj(obj)
    elif obj["type"] == "MultiLineString":
        return MultiLineString.parse_obj(obj)
    elif obj["type"] == "Polygon":
        return Polygon.parse_obj(obj)
    elif obj["type"] == "MultiPolygon":
        return MultiPolygon.parse_obj(obj)
    raise ValidationError(
        [ErrorWrapper(ValueError("Unknown type"), "type")], "Geometry"
    )
