"""pydantic models for GeoJSON Geometry objects."""

import abc
from typing import Any, Dict, Iterator, List, Union

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
    def _wkt_coordinates(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def _wkt_inset(self) -> str:
        """Return Z for 3 dimensional geometry or an empty string for 2 dimensions."""
        ...

    @property
    def _wkt_type(self) -> str:
        """Return the WKT name of the geometry."""
        return self.type.upper()

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        return f"{self._wkt_type}{self._wkt_inset}({self._wkt_coordinates})"


class Point(_GeometryBase):
    """Point Model"""

    type: str = Field(default="Point", const=True)
    coordinates: Position

    @property
    def _wkt_coordinates(self) -> str:
        return " ".join(str(coordinate) for coordinate in self.coordinates)

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates) == 3 else " "


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: str = Field(default="MultiPoint", const=True)
    coordinates: MultiPointCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        points = [Point(coordinates=p) for p in self.coordinates]
        return ", ".join(point._wkt_coordinates for point in points)


class LineString(_GeometryBase):
    """LineString Model"""

    type: str = Field(default="LineString", const=True)
    coordinates: LineStringCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        points = [Point(coordinates=p) for p in self.coordinates]
        return ", ".join(point._wkt_coordinates for point in points)


class MultiLineString(_GeometryBase):
    """MultiLineString Model"""

    type: str = Field(default="MultiLineString", const=True)
    coordinates: MultiLineStringCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0][0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        lines = [LineString(coordinates=line) for line in self.coordinates]
        return ",".join(f"({line._wkt_coordinates})" for line in lines)


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

    type: str = Field(default="Polygon", const=True)
    coordinates: PolygonCoords

    @validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for ring in coordinates]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return coordinates

    @property
    def exterior(self) -> LinearRing:
        """Return the exterior Linear Ring of the polygon."""
        return self.coordinates[0]

    @property
    def interiors(self) -> Iterator[LinearRing]:
        """Interiors (Holes) of the polygon."""
        yield from (
            interior for interior in self.coordinates[1:] if len(self.coordinates) > 1
        )

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0][0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        ic = "".join(
            f", ({LinearRingGeom(coordinates=interior)._wkt_coordinates})"
            for interior in self.interiors
        )
        return f"({LinearRingGeom(coordinates=self.exterior)._wkt_coordinates}){ic}"

    @classmethod
    def from_bounds(
        cls, xmin: float, ymin: float, xmax: float, ymax: float
    ) -> "Polygon":
        """Create a Polygon geometry from a boundingbox."""
        return cls(
            coordinates=[
                [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]
            ]
        )


class MultiPolygon(_GeometryBase):
    """MultiPolygon Model"""

    type: str = Field(default="MultiPolygon", const=True)
    coordinates: MultiPolygonCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0][0][0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        polygons = [Polygon(coordinates=poly) for poly in self.coordinates]
        return ",".join(f"({poly._wkt_coordinates})" for poly in polygons)


Geometry = Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]


class GeometryCollection(BaseModel):
    """GeometryCollection Model"""

    type: str = Field(default="GeometryCollection", const=True)
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
