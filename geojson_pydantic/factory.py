"""geojson-pydantic model factory"""

from typing import Type

from pydantic import BaseModel, Field, create_model

from geojson_pydantic.features import Feature
from geojson_pydantic.geometries import Geometry


def model_factory(geom: Geometry) -> Type[BaseModel]:
    """Create Feature Model."""
    return create_model(
        "Feature", geometry=(geom, Field(title="Geometry")), __base__=Feature,
    )
