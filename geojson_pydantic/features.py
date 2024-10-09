"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, Iterator, List, Literal, Optional, TypeVar, Union

from pydantic.v1 import BaseModel, Field, StrictInt, StrictStr, validator
from pydantic.v1.generics import GenericModel

from geojson_pydantic.geo_interface import GeoInterfaceMixin
from geojson_pydantic.geometries import Geometry, GeometryCollection
from geojson_pydantic.types import BBox, validate_bbox

Props = TypeVar("Props", bound=Union[Dict[str, Any], BaseModel])
Geom = TypeVar("Geom", bound=Union[Geometry, GeometryCollection])


class Feature(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
    """Feature Model"""

    type: Literal["Feature"]
    geometry: Union[Geom, None] = Field(...)
    properties: Union[Props, None] = Field(...)
    id: Optional[Union[StrictInt, StrictStr]] = None
    bbox: Optional[BBox] = None

    _validate_bbox = validator("bbox", allow_reuse=True)(validate_bbox)

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__

        return geometry


class FeatureCollection(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
    """FeatureCollection Model"""

    type: Literal["FeatureCollection"]
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

    _validate_bbox = validator("bbox", allow_reuse=True)(validate_bbox)
