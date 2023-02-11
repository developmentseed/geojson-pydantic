"""pydantic models for GeoJSON Geometry objects."""

import abc
from typing import Any, Iterator, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from typing_extensions import Annotated

from geojson_pydantic.geo_interface import GeoInterfaceMixin
from geojson_pydantic.types import (
    BBox,
    LinearRing,
    LineStringCoords,
    MultiLineStringCoords,
    MultiPointCoords,
    MultiPolygonCoords,
    PolygonCoords,
    Position,
)


def _position_wkt_coordinates(position: Position) -> str:
    """Converts a Position to WKT Coordinates."""
    return " ".join(str(number) for number in position)


def _position_has_z(position: Position) -> bool:
    return len(position) == 3


def _position_list_wkt_coordinates(positions: List[Position]) -> str:
    """Converts a list of Positions to WKT Coordinates."""
    return ", ".join(_position_wkt_coordinates(position) for position in positions)


def _position_list_has_z(positions: List[Position]) -> bool:
    """Checks if any position in a list has a Z."""
    return any(_position_has_z(position) for position in positions)


def _lines_wtk_coordinates(lines: List[List[Position]]) -> str:
    """Converts lines to WKT Coordinates."""
    return ", ".join(f"({_position_list_wkt_coordinates(line)})" for line in lines)


def _lines_has_z(lines: List[List[Position]]) -> bool:
    """Checks if any position in a list has a Z."""
    return any(
        _position_has_z(position) for positions in lines for position in positions
    )


class _GeometryBase(BaseModel, abc.ABC, GeoInterfaceMixin):
    """Base class for geometry models"""

    type: str
    coordinates: Any
    bbox: Optional[BBox] = None

    @property
    @abc.abstractmethod
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        ...

    @property
    @abc.abstractmethod
    def _wkt_coordinates(self) -> str:
        ...

    @property
    def _wkt_type(self) -> str:
        """Return the WKT name of the geometry."""
        return self.type.upper()

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        # Start with the WKT Type
        wkt = self._wkt_type
        if self.coordinates:
            # If any of the coordinates have a Z add a "Z" to the WKT
            wkt += " Z " if self.has_z else " "
            # Add the rest of the WKT inside parentheses
            wkt += f"({self._wkt_coordinates})"
        else:
            # Otherwise it will be "EMPTY"
            wkt += " EMPTY"

        return wkt


class Point(_GeometryBase):
    """Point Model"""

    type: Literal["Point"]
    coordinates: Position

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _position_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return _position_wkt_coordinates(self.coordinates)


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: Literal["MultiPoint"]
    coordinates: MultiPointCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _position_list_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return _position_list_wkt_coordinates(self.coordinates)


class LineString(_GeometryBase):
    """LineString Model"""

    type: Literal["LineString"]
    coordinates: LineStringCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _position_list_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return _position_list_wkt_coordinates(self.coordinates)


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: Literal["MultiLineString"]
    coordinates: MultiLineStringCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _lines_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return _lines_wtk_coordinates(self.coordinates)


class Polygon(_GeometryBase):
    """Polygon Model"""

    type: Literal["Polygon"]
    coordinates: PolygonCoords

    @validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for ring in coordinates]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return coordinates

    @property
    def exterior(self) -> Union[LinearRing, None]:
        """Return the exterior Linear Ring of the polygon."""
        return self.coordinates[0] if self.coordinates else None

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        yield from (
            interior for interior in self.coordinates[1:] if len(self.coordinates) > 1
        )

    @property
    def has_z(self) -> bool:
        """Checks if any coordinates have a Z value."""
        return _lines_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return _lines_wtk_coordinates(self.coordinates)

    @classmethod
    def from_bounds(
        cls, xmin: float, ymin: float, xmax: float, ymax: float
    ) -> "Polygon":
        """Create a Polygon geometry from a boundingbox."""
        return cls(
            type="Polygon",
            coordinates=[
                [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]
            ],
        )


class MultiPolygon(_GeometryBase):
    """MultiPolygon Model"""

    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinates have a Z value."""
        return any(_lines_has_z(polygon) for polygon in self.coordinates)

    @property
    def _wkt_coordinates(self) -> str:
        return ",".join(
            f"({_lines_wtk_coordinates(polygon)})" for polygon in self.coordinates
        )

    @validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for polygon in coordinates for ring in polygon]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return coordinates


Geometry = Annotated[
    Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon],
    Field(discriminator="type"),
]


class GeometryCollection(BaseModel, GeoInterfaceMixin):
    """GeometryCollection Model"""

    type: Literal["GeometryCollection"]
    geometries: List[Geometry]
    bbox: Optional[BBox] = None

    def __iter__(self) -> Iterator[Geometry]:  # type: ignore [override]
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self) -> int:
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index: int) -> Geometry:
        """get geometry at a given index"""
        return self.geometries[index]

    @property
    def _wkt_type(self) -> str:
        """Return the WKT name of the geometry."""
        return self.type.upper()

    @property
    def _wkt_coordinates(self) -> str:
        """Encode coordinates as WKT."""
        return ", ".join(geom.wkt for geom in self.geometries)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        return (
            self._wkt_type
            + " "
            + (f"({self._wkt_coordinates})" if self._wkt_coordinates else "EMPTY")
        )


def parse_geometry_obj(obj: Any) -> Geometry:
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
        errors=[ErrorWrapper(ValueError("Unknown type"), loc="type")],
        model=_GeometryBase,
    )
