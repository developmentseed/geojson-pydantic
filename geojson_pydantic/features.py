"""pydantic models for GeoJSON Feature objects."""

import json
from typing import Dict, Generic, List, Optional, TypeVar, Union

from pydantic import Field, ValidationError, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geometries import GeoInterfaceMixin, Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Dict)
Geom = TypeVar("Geom", bound=Optional[Union[Geometry, GeometryCollection]])


class Feature(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
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

    @classmethod
    def validate(cls, value):
        """Validate input."""
        try:
            value = json.loads(value)
        except TypeError:
            try:
                return cls(**value.dict())
            except (AttributeError, ValidationError):
                pass

        return cls(**value)


class FeatureCollection(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
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

    @classmethod
    def validate(cls, value):
        """Validate input."""
        try:
            value = json.loads(value)
        except TypeError:
            try:
                return cls(**value.dict())
            except (AttributeError, ValidationError):
                pass

        return cls(**value)
