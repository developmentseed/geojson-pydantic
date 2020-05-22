import pytest
from pydantic import ValidationError

from geojson_pydantic.geometries import Point

def test_point():
    coordinates = (1, 2)
    p = Point(coordinates=coordinates)
    assert p.type == "Point"
    assert p.coordinates == coordinates
    assert hasattr(p, "__geo_interface__")

def test_bad_point():
    with pytest.raises(ValidationError):
        Point(coordinates=(1, ))