"""pydantic models for GeoJSON Feature objects."""

import json
from typing import Any, Dict, Generic, Iterator, List, Optional, TypeVar, Union

from pydantic import Field, ValidationError, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geometries import GeoInterfaceMixin, Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Dict)
Geom = TypeVar("Geom", bound=Union[Geometry, GeometryCollection])


class Feature(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
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

    @classmethod
    def validate(cls, value: Any) -> "Feature":
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

    @classmethod
    def validate(cls, value: Any) -> "FeatureCollection":
        """Validate input."""
        try:
            value = json.loads(value)
        except TypeError:
            try:
                return cls(**value.dict())
            except (AttributeError, ValidationError):
                pass

        return cls(**value)
