import pytest

from geojson_pydantic.factory import model_factory
from geojson_pydantic.geometries import (
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)

geom_types = [
    (Point, {"type": "Point", "coordinates": [1, 2]}),
    (
        LineString,
        {
            "type": "LineString",
            "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]],
        },
    ),
    (
        Polygon,
        {
            "type": "Polygon",
            "coordinates": [
                [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]
            ],
        },
    ),
    (MultiPoint, {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}),
    (
        MultiLineString,
        {
            "type": "MultiLineString",
            "coordinates": [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]],
        },
    ),
    (
        MultiPolygon,
        {
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [102.0, 2.0],
                        [103.0, 2.0],
                        [103.0, 3.0],
                        [102.0, 3.0],
                        [102.0, 2.0],
                    ]
                ],
                [
                    [
                        [100.0, 0.0],
                        [101.0, 0.0],
                        [101.0, 1.0],
                        [100.0, 1.0],
                        [100.0, 0.0],
                    ],
                    [
                        [100.2, 0.2],
                        [100.8, 0.2],
                        [100.8, 0.8],
                        [100.2, 0.8],
                        [100.2, 0.2],
                    ],
                ],
            ],
        },
    ),
]


@pytest.mark.parametrize("geom", geom_types)
def test_factory(geom):
    """test if feature collection is iterable"""
    Feature = model_factory(geom[0])
    assert Feature(geometry=geom[1])
