"""Types for geojson_pydantic models"""

from typing import TYPE_CHECKING, Any, Callable, Generator, List, Tuple, Union

from pydantic import ConstrainedList, conlist


class _BBoxBase(ConstrainedList):
    """Base Class with additional Validation for order."""

    # This is needed because pydantic checks it rather than `item_type`
    __args__ = (float,)

    item_type = float

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        """Yield the validators."""
        yield from super().__get_validators__()
        yield cls.validate_bbox

    @classmethod
    def validate_bbox(cls, bbox: List[float]) -> List[float]:
        """Validate BBox values are ordered correctly."""
        if not bbox:
            return bbox

        offset = len(bbox) // 2
        errors: List[str] = []
        # Check X
        if bbox[0] > bbox[offset]:
            errors.append(f"Min X ({bbox[0]}) must be <= Max X ({bbox[offset]}).")
        # Check Y
        if bbox[1] > bbox[1 + offset]:
            errors.append(f"Min Y ({bbox[1]}) must be <= Max Y ({bbox[1 + offset]}).")
        # If 3D, check Z values.
        if offset > 2 and bbox[2] > bbox[2 + offset]:
            errors.append(f"Min Z ({bbox[2]}) must be <= Max Z ({bbox[2 + offset]}).")

        if errors:
            raise ValueError("Invalid BBox. Error(s): " + " ".join(errors))

        return bbox


class BBox2D(_BBoxBase):
    """2D Bounding Box"""

    min_items = 4
    max_items = 4


class BBox3D(_BBoxBase):
    """3D Bounding Box"""

    min_items = 6
    max_items = 6


BBox = Union[BBox3D, BBox2D]
Position = Union[Tuple[float, float], Tuple[float, float, float]]

# Coordinate arrays
if TYPE_CHECKING:
    LineStringCoords = List[Position]
    LinearRing = List[Position]
else:
    LineStringCoords = conlist(Position, min_items=2)
    LinearRing = conlist(Position, min_items=4)

MultiPointCoords = List[Position]
MultiLineStringCoords = List[LineStringCoords]
PolygonCoords = List[LinearRing]
MultiPolygonCoords = List[PolygonCoords]
