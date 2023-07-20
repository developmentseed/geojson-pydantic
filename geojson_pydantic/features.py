"""pydantic models for GeoJSON Feature objects."""

from typing import Any, Dict, Generic, Iterator, List, Literal, Optional, TypeVar, Union

from pydantic import (
    BaseModel,
    Field,
    StrictInt,
    StrictStr,
    field_validator,
    model_serializer,
)

from geojson_pydantic.geo_interface import GeoInterfaceMixin
from geojson_pydantic.geometries import Geometry
from geojson_pydantic.types import BBox, validate_bbox

Props = TypeVar("Props", bound=Union[Dict[str, Any], BaseModel])
Geom = TypeVar("Geom", bound=Geometry)


class Feature(BaseModel, Generic[Geom, Props], GeoInterfaceMixin):
    """Feature Model"""

    type: Literal["Feature"]
    geometry: Union[Geom, None] = Field(...)
    properties: Union[Props, None] = Field(...)
    id: Optional[Union[StrictInt, StrictStr]] = None
    bbox: Optional[BBox] = None

    _validate_bbox = field_validator("bbox")(validate_bbox)

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        """Custom Model serializer to match the GeoJSON specification."""
        model: Dict[str, Any] = {
            "type": self.type,
            "geometry": self.geometry,
            "properties": self.properties,
        }
        if self.id is not None:
            model["id"] = self.id
        if self.bbox:
            model["bbox"] = self.bbox

        return model

    @field_validator("geometry", mode="before")
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__

        return geometry


Feat = TypeVar("Feat", bound=Feature)


class FeatureCollection(BaseModel, Generic[Feat], GeoInterfaceMixin):
    """FeatureCollection Model"""

    type: Literal["FeatureCollection"]
    features: List[Feat]
    bbox: Optional[BBox] = None

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        """Custom Model serializer to match the GeoJSON specification."""
        model: Dict[str, Any] = {
            "type": self.type,
            "features": self.features,
        }
        if self.bbox:
            model["bbox"] = self.bbox

        return model

    def __iter__(self) -> Iterator[Feat]:  # type: ignore [override]
        """iterate over features"""
        return iter(self.features)

    def __len__(self) -> int:
        """return features length"""
        return len(self.features)

    def __getitem__(self, index: int) -> Feat:
        """get feature at a given index"""
        return self.features[index]

    _validate_bbox = field_validator("bbox")(validate_bbox)
