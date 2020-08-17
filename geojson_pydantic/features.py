"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from .geometries import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)
from .utils import BBox


class Feature(BaseModel):
    """Feature Model"""

    type: str = Field("Feature", const=True)
    geometry: Union[
        Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
    ]
    properties: Optional[Dict[Any, Any]]
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


class FeatureCollection(BaseModel):
    """FeatureCollection Model"""

    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]
    bbox: Optional[BBox]
