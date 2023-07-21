from typing import Set, Tuple, Union

import pytest
from pydantic import Field, ValidationError

from geojson_pydantic.base import _GeoJsonBase


@pytest.mark.parametrize(
    "values",
    (
        (100, 0, 0, 0),  # Incorrect Order
        (0, 100, 0, 0),
        (0, 0, 100, 0, 0, 0),
        (0, "a", 0, 0),  # Invalid Type
    ),
)
def test_bbox_validation(values: Tuple) -> None:
    with pytest.raises(ValidationError):
        _GeoJsonBase(bbox=values)


def test_exclude_if_none() -> None:
    model = _GeoJsonBase()
    # Included in default dump
    assert model.model_dump() == {"bbox": None}
    # Not included when in json mode
    assert model.model_dump(mode="json") == {}
    # And not included in the output json string.
    assert model.model_dump_json() == "{}"

    # Included if it has a value
    model = _GeoJsonBase(bbox=(0, 0, 0, 0))
    assert model.model_dump() == {"bbox": (0, 0, 0, 0)}
    assert model.model_dump(mode="json") == {"bbox": [0, 0, 0, 0]}
    assert model.model_dump_json() == '{"bbox":[0.0,0.0,0.0,0.0]}'

    # Since `validate_assignment` is not set, you can do this without an error.
    # The solution should handle this and not just look at if the field is set.
    model.bbox = None
    assert model.model_dump() == {"bbox": None}
    assert model.model_dump(mode="json") == {}
    assert model.model_dump_json() == "{}"


def test_exclude_if_none_subclass() -> None:
    # Create a subclass that adds a field, and ensure it works.
    class TestClass(_GeoJsonBase):
        test_field: str = None
        __exclude_if_none__: Set[str] = {"bbox", "test_field"}

    assert TestClass().model_dump_json() == "{}"
    assert TestClass(test_field="a").model_dump_json() == '{"test_field":"a"}'
    assert (
        TestClass(bbox=(0, 0, 0, 0)).model_dump_json() == '{"bbox":[0.0,0.0,0.0,0.0]}'
    )


def test_exclude_if_none_kwargs() -> None:
    # Create a subclass that adds fields and dumps it with kwargs to ensure
    # the kwargs are still being utilized.
    class TestClass(_GeoJsonBase):
        test_field: str = Field(default="test", alias="field")
        null_field: Union[str, None] = None

    model = TestClass(bbox=(0, 0, 0, 0))
    assert (
        model.model_dump_json(indent=2, by_alias=True, exclude_none=True)
        == """{
  "bbox": [
    0.0,
    0.0,
    0.0,
    0.0
  ],
  "field": "test"
}"""
    )
