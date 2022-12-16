"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, Iterator, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geometries import Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Union[Dict[str, Any], BaseModel])
Geom = TypeVar("Geom", bound=Union[Geometry, GeometryCollection])


class Feature(GenericModel, Generic[Geom, Props]):
    """Feature Model"""

    type: str = Field(default="Feature", const=True)
    geometry: Optional[Geom] = None
    properties: Optional[Props] = None
    id: Optional[str] = None
    bbox: Optional[BBox] = None

    class Config:
        """Model configuration."""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__
        return geometry

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        geo: Dict[str, Any] = {
            "type": self.type,
            "geometry": self.geometry.__geo_interface__
            if self.geometry is not None
            else None,
        }
        if self.bbox:
            geo["bbox"] = self.bbox

        if self.id:
            geo["id"] = self.id

        if self.properties:
            geo["properties"] = self.properties

        return geo


class FeatureCollection(GenericModel, Generic[Geom, Props]):
    """FeatureCollection Model"""

    type: str = Field(default="FeatureCollection", const=True)
    features: List[Feature[Geom, Props]]
    bbox: Optional[BBox] = None

    def __iter__(self) -> Iterator[Feature]:  # type: ignore [override]
        """iterate over features"""
        return iter(self.features)

    def __len__(self) -> int:
        """return features length"""
        return len(self.features)

    def __getitem__(self, index: int) -> Feature:
        """get feature at a given index"""
        return self.features[index]

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        features: List[Dict[str, Any]] = []
        for feat in self.features:
            features.append(feat.__geo_interface__)

        geo: Dict[str, Any] = {"type": self.type, "features": features}
        if self.bbox:
            geo["bbox"] = self.bbox

        return geo
