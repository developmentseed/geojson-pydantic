"""pydantic models for GeoJSON Geometry objects."""

import abc
from typing import Any, Dict, Iterator, List, Literal, Union

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper

from geojson_pydantic.types import (
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


def _position_list_wkt_coordinates(positions: List[Position]) -> str:
    """Converts a list of Positions to WKT Coordinates."""
    return ", ".join(_position_wkt_coordinates(position) for position in positions)


def _lines_wtk_coordinates(lines: List[List[Position]]) -> str:
    """Converts lines to WKT Coordinates."""
    return ", ".join(f"({_position_list_wkt_coordinates(line)})" for line in lines)


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    type: str
    coordinates: Union[Any, None] = Field(...)

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        return {"type": self.type, "coordinates": self.coordinates}

    @property
    @abc.abstractmethod
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        ...


class Point(_GeometryBase):
    """Point Model"""

    type: Literal["Point"]
    coordinates: Union[Position, None] = Field(...)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates) == 3 else " "
        wkt_coordinates = _position_wkt_coordinates(self.coordinates)

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: Literal["MultiPoint"]
    coordinates: Union[MultiPointCoords, None] = Field(...)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates[0]) == 3 else " "
        wkt_coordinates = _position_list_wkt_coordinates(self.coordinates)

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"


class LineString(_GeometryBase):
    """LineString Model"""

    type: Literal["LineString"]
    coordinates: Union[LineStringCoords, None] = Field(...)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates[0]) == 3 else " "
        wkt_coordinates = _position_list_wkt_coordinates(self.coordinates)

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: Literal["MultiLineString"]
    coordinates: Union[MultiLineStringCoords, None] = Field(...)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates[0][0]) == 3 else " "
        wkt_coordinates = _lines_wtk_coordinates(self.coordinates)

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"


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
    coordinates: Union[PolygonCoords, None] = Field(...)

    @validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for ring in coordinates]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return coordinates

    @property
    def exterior(self) -> LinearRing:
        """Return the exterior Linear Ring of the polygon."""
        if not self.coordinates:
            return []

        return self.coordinates[0]

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        if not self.coordinates:
            return []

        yield from (
            interior for interior in self.coordinates[1:] if len(self.coordinates) > 1
        )

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates[0][0]) == 3 else " "
        wkt_coordinates = _lines_wtk_coordinates(self.coordinates)

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"

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
    coordinates: Union[MultiPolygonCoords, None] = Field(...)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        if not self.coordinates:
            return f"{self.type.upper()} EMPTY"

        wkt_inset = " Z " if len(self.coordinates[0][0][0]) == 3 else " "
        wkt_coordinates = ",".join(
            f"({_lines_wtk_coordinates(polygon)})" for polygon in self.coordinates
        )

        return f"{self.type.upper()}{wkt_inset}({wkt_coordinates})"


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


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
    def _wkt_coordinates(self) -> str:
        """Encode coordinates as WKT."""
        return ", ".join(geom.wkt for geom in self.geometries)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        return f"{self._wkt_type} ({self._wkt_coordinates})"

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
