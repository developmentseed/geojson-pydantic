"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import Field, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geometries import Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Dict)
Geom = TypeVar("Geom", bound=Optional[Union[Geometry, GeometryCollection]])


class Feature(GenericModel, Generic[Geom, Props]):
    """Feature Model"""

    type: str = Field("Feature", const=True)
    geometry: Geom = None
    properties: Optional[Props]
    id: Optional[str]
    bbox: Optional[BBox] = None

    class Config:
        """Model configuration."""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v):
        """set geometry from geo interface or input"""
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v

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

    type: str = Field("FeatureCollection", const=True)
    features: List[Feature[Geom, Props]]
    bbox: Optional[BBox]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]

    @property
    def __geo_interface__(self) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        features = []
        for feat in self.features:
            features.append(feat.__geo_interface__)

        geo: Dict[str, Any] = {"type": self.type, "features": features}
        if self.bbox:
            geo["bbox"] = self.bbox

        return geo
