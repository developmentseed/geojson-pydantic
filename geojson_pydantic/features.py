"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, Iterable, List, Optional, TypeVar, Union

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel
from typing_extensions import Literal

from geojson_pydantic.geometries import GeoInterfaceMixin, Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Union[Dict, BaseModel])
Geom = TypeVar("Geom", bound=Union[Geometry, GeometryCollection])


class Feature(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
    """Feature Model"""

    type: Literal["Feature"] = "Feature"
    geometry: Optional[Geom] = None
    properties: Optional[Props]
    id: Optional[str]
    bbox: Optional[BBox] = None

    class Config:
        """Model configuration."""

        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v: Any) -> Any:
        """Set geometry from geo interface or input"""
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v


class FeatureCollection(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
    """FeatureCollection Model"""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[Feature[Geom, Props]]
    bbox: Optional[BBox] = None

    def __iter__(self) -> Iterable[Feature]:  # type: ignore [override]
        """iterate over features"""
        return iter(self.features)

    def __len__(self) -> int:
        """return features length"""
        return len(self.features)

    def __getitem__(self, index: int) -> Feature:
        """get feature at a given index"""
        return self.features[index]
