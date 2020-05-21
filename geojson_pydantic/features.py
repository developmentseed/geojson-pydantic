from typing import Union, Dict, List,  Optional, Any
from pydantic import BaseModel, Field, validator

from .utils import BBox
from .geometries import Point, MultiPoint, LineString, MultiLineString, \
    Polygon, MultiPolygon

class Feature(BaseModel):
    type: str = Field("Feature", const=True)
    geometry: Union[Point, MultiPolygon, LineString,  MultiLineString, Polygon, MultiPolygon]
    properties: Optional[Dict[Any, Any]]
    id: Optional[str]
    bbox: Optional[BBox]

    class Config:
        use_enum_values = True

    @validator("geometry", pre=True, always=True)
    def set_geometry(cls, v):
        if hasattr(v, "__geo_interface__"):
            return v.__geo_interface__
        return v


class FeatureCollection(BaseModel):
    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]
    bbox: Optional[BBox]