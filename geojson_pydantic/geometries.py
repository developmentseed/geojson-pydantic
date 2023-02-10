"""pydantic models for GeoJSON Geometry objects."""
from __future__ import annotations

import abc
from typing import Any, Dict, Iterator, List, Literal, Protocol, Union

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from typing_extensions import Annotated

from geojson_pydantic.types import (
    LinearRing,
    LineStringCoords,
    MultiLineStringCoords,
    MultiPointCoords,
    MultiPolygonCoords,
    PolygonCoords,
    Position,
)


def _position_wkt_coordinates(coordinates: Position, force_z: bool = False) -> str:
    """Converts a Position to WKT Coordinates."""
    wkt_coordinates = " ".join(str(number) for number in coordinates)
    if force_z and len(coordinates) < 3:
        wkt_coordinates += " 0.0"
    return wkt_coordinates


def _position_has_z(position: Position) -> bool:
    return len(position) == 3


def _position_list_wkt_coordinates(
    coordinates: List[Position], force_z: bool = False
) -> str:
    """Converts a list of Positions to WKT Coordinates."""
    return ", ".join(
        _position_wkt_coordinates(position, force_z) for position in coordinates
    )


def _position_list_has_z(positions: List[Position]) -> bool:
    """Checks if any position in a list has a Z."""
    return any(_position_has_z(position) for position in positions)


def _lines_wtk_coordinates(
    coordinates: List[LineStringCoords], force_z: bool = False
) -> str:
    """Converts lines to WKT Coordinates."""
    return ", ".join(
        f"({_position_list_wkt_coordinates(line, force_z)})" for line in coordinates
    )


def _lines_has_z(lines: List[LineStringCoords]) -> bool:
    """Checks if any position in a list has a Z."""
    return any(
        _position_has_z(position) for positions in lines for position in positions
    )


def _polygons_wkt_coordinates(
    coordinates: List[PolygonCoords], force_z: bool = False
) -> str:
    return ",".join(
        f"({_lines_wtk_coordinates(polygon, force_z)})" for polygon in coordinates
    )


class _WktCallable(Protocol):
    def __call__(self, coordinates: Any, force_z: bool) -> str:
        ...


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    type: str
    coordinates: Any

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        return {"type": self.type, "coordinates": self.coordinates}

    @property
    @abc.abstractmethod
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        ...

    @property
    @abc.abstractmethod
    def _wkt_coordinates(self) -> _WktCallable:
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
        has_z = self.has_z
        if self.coordinates:
            # If any of the coordinates have a Z add a "Z" to the WKT
            wkt += " Z " if has_z else " "
            # Add the rest of the WKT inside parentheses
            wkt += f"({self._wkt_coordinates(self.coordinates, force_z=has_z)})"
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
    def _wkt_coordinates(self) -> _WktCallable:
        return _position_wkt_coordinates


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: Literal["MultiPoint"]
    coordinates: MultiPointCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _position_list_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> _WktCallable:
        return _position_list_wkt_coordinates


class LineString(_GeometryBase):
    """LineString Model"""

    type: Literal["LineString"]
    coordinates: LineStringCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _position_list_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> _WktCallable:
        return _position_list_wkt_coordinates


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: Literal["MultiLineString"]
    coordinates: MultiLineStringCoords

    @property
    def has_z(self) -> bool:
        """Checks if any coordinate has a Z value."""
        return _lines_has_z(self.coordinates)

    @property
    def _wkt_coordinates(self) -> _WktCallable:
        return _lines_wtk_coordinates


class LinearRingGeom(LineString):
    """LinearRing model."""

    @validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that LinearRing is closed (first and last coordinate are the same)."""
        if coordinates[-1] != coordinates[0]:
            raise ValueError("LinearRing must have the same start and end coordinates")

        return coordinates


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
    def _wkt_coordinates(self) -> _WktCallable:
        return _lines_wtk_coordinates

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
    def _wkt_coordinates(self) -> _WktCallable:
        return _polygons_wkt_coordinates

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


class GeometryCollection(BaseModel):
    """GeometryCollection Model"""

    type: Literal["GeometryCollection"]
    geometries: List[Geometry]

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
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        coordinates = (
            f'({", ".join(geom.wkt for geom in self.geometries)})'
            if self.geometries
            else "EMPTY"
        )
        return f"{self._wkt_type} {coordinates}"

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        geometries: List[Dict[str, Any]] = []
        for geom in self.geometries:
            geometries.append(geom.__geo_interface__)

        return {"type": self.type, "geometries": self.geometries}


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
