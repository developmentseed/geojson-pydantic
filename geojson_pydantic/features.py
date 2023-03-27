"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, Iterator, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field, StrictInt, StrictStr, validator
from pydantic.generics import GenericModel

from geojson_pydantic.geo_interface import GeoInterfaceMixin
from geojson_pydantic.geometries import Geometry, GeometryCollection
from geojson_pydantic.types import BBox

Props = TypeVar("Props", bound=Union[Dict[str, Any], BaseModel])
Geom = TypeVar("Geom", bound=Union[Geometry, GeometryCollection])


class Feature(GenericModel, Generic[Geom, Props], GeoInterfaceMixin):
    """Feature Model"""

    type: Literal["Feature"]
    geometry: Union[Geom, None] = Field(...)
    properties: Union[Props, None] = Field(...)
    id: Optional[Union[StrictInt, StrictStr]] = None
    bbox: Optional[BBox] = None

    class Config:
        """Model configuration."""

        use_enum_values = True

    @validator("bbox", pre=True)
    def check_bbox(cls, bbox: BBox) -> BBox:
        """Check that bbox is valid."""
        if len(bbox) == 6:
            if bbox[0] > bbox[3] or bbox[1] > bbox[4] or bbox[2] > bbox[5]:  # type: ignore
                raise ValueError(
                    "BBox must be in the form [west, south, bottom, east, north, top]"
                )
        elif len(bbox) == 4:
            if bbox[0] > bbox[2] or bbox[1] > bbox[3]:
                raise ValueError("BBox must be in the form [west, south, east, north]")
        else:
            raise ValueError(
                "BBox must be in the form [west, south, east, north] or [west, south, bottom, east, north, top]"
            )
        return bbox

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
