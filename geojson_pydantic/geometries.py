"""pydantic models for GeoJSON Geometry objects."""

import abc
from typing import Any, Dict, Iterable, Iterator, List, Protocol, Union

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.error_wrappers import ErrorWrapper
from typing_extensions import Annotated, Literal, TypeAlias

from geojson_pydantic.types import (
    LinearRing,
    LineStringCoords,
    MultiLineStringCoords,
    MultiPointCoords,
    MultiPolygonCoords,
    PolygonCoords,
    Position,
)


class DictFuncProto(Protocol):
    """Protocol to to let GeoInterfaceMixin know it has a `dict` function."""

    def dict(self) -> Dict[str, Any]:
        """A placeholder for the dict function of a BaseModel"""
        ...


class GeoInterfaceMixin:
    """Geo interface mixin class"""

    @property
    def __geo_interface__(self: DictFuncProto) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data."""
        result = self.dict()
        if "bbox" in result and result["bbox"] is None:
            del result["bbox"]
        return result


class _GeometryBase(BaseModel, GeoInterfaceMixin, abc.ABC):
    """Base class for geometry models"""

    # These are constrained in child classes
    type: str
    coordinates: Any

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
        return self.__class__.__name__.upper()

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        return f"{self._wkt_type}{self._wkt_inset}({self._wkt_coordinates})"


class Point(_GeometryBase):
    """Point Model"""

    type: Literal["Point"] = "Point"
    coordinates: Position

    @property
    def _wkt_coordinates(self) -> str:
        return " ".join(str(coordinate) for coordinate in self.coordinates)

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates) == 3 else " "


class MultiPoint(_GeometryBase):
    """MultiPoint Model"""

    type: Literal["MultiPoint"] = "MultiPoint"
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

    type: Literal["LineString"] = "LineString"
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

    type: Literal["MultiLineString"] = "MultiLineString"
    coordinates: MultiLineStringCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0][0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        lines = [LineString(coordinates=line) for line in self.coordinates]
        return ",".join(f"({line._wkt_coordinates})" for line in lines)


class Polygon(_GeometryBase):
    """Polygon Model"""

    type: Literal["Polygon"] = "Polygon"
    coordinates: PolygonCoords

    @validator("coordinates")
    def check_closure(cls, polygon: PolygonCoords) -> PolygonCoords:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any([ring[-1] != ring[0] for ring in polygon]):
            raise ValueError("All linear rings have the same start and end coordinates")

        return polygon

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
            f", ({LineString(coordinates=interior)._wkt_coordinates})"
            for interior in self.interiors
        )
        return f"({LineString(coordinates=self.exterior)._wkt_coordinates}){ic}"

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

    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: MultiPolygonCoords

    @property
    def _wkt_inset(self) -> str:
        return " Z " if len(self.coordinates[0][0][0]) == 3 else " "

    @property
    def _wkt_coordinates(self) -> str:
        polygons = [Polygon(coordinates=poly) for poly in self.coordinates]
        return ",".join(f"({poly._wkt_coordinates})" for poly in polygons)


Geometry: TypeAlias = Annotated[
    Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon],
    Field(discriminator="type"),
]


class GeometryCollection(BaseModel, GeoInterfaceMixin):
    """GeometryCollection Model"""

    type: Literal["GeometryCollection"] = "GeometryCollection"
    geometries: List[Geometry]

    def __iter__(self) -> Iterable[Geometry]:  # type: ignore [override]
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
        return self.__class__.__name__.upper()

    @property
    def _wkt_coordinates(self) -> str:
        """Encode coordinates as WKT."""
        return ", ".join(geom.wkt for geom in self.geometries)

    @property
    def wkt(self) -> str:
        """Return the Well Known Text representation."""
        return f"{self._wkt_type} ({self._wkt_coordinates})"


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
        [ErrorWrapper(ValueError("Unknown type"), "type")], _GeometryBase
    )
