"""pydantic models for GeoJSON Feature objects."""

from typing import List, Optional, Generic, TypeVar

from pydantic import Field, validator
from pydantic.generics import GenericModel

from .geometries import Geometry
from .utils import BBox

T = TypeVar("T")


class Feature(GenericModel, Generic[T]):
    """Feature Model"""

    type: str = Field("Feature", const=True)
    geometry: Geometry
    properties: Optional[T]
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


class FeatureCollection(GenericModel, Generic[T]):
    """FeatureCollection Model"""

    type: str = Field("FeatureCollection", const=True)
    features: List[Feature[T]]
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
