"""pydantic models for GeoJSON Feature objects."""

from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import Field, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geometries import Geometry
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Dict)
Geom = TypeVar("Geom", bound=Geometry)


class Feature(GenericModel, Generic[Geom, Props]):
    """Feature Model"""

    type: str = Field("Feature", const=True)
    geometry: Geom
    properties: Optional[Props]
    id: Optional[str]
    bbox: Optional[BBox]

    class Config:
        """TODO: document"""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v):
        """set geometry from geo interface or input"""
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v


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
