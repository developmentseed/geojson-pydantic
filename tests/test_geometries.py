import re
from typing import Union

import pytest
from pydantic import ValidationError
from shapely.geometry import shape

from geojson_pydantic.geometries import (
    Geometry,
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    parse_geometry_obj,
)


def assert_wkt_equivalence(geom: Union[Geometry, GeometryCollection]):
    """Assert WKT equivalence with Shapely."""
    # Remove any trailing `.0` to match Shapely format
    clean_wkt = re.sub(r"\.0(\D)", r"\1", geom.wkt)
    assert shape(geom).wkt == clean_wkt


@pytest.mark.parametrize("coordinates", [(1.01, 2.01), (1.0, 2.0, 3.0), (1.0, 2.0)])
def test_point_valid_coordinates(coordinates):
    """
    Two or three number elements as coordinates should be okay
    """
    p = Point(type="Point", coordinates=coordinates)
    assert p.type == "Point"
    assert p.coordinates == coordinates
    assert hasattr(p, "__geo_interface__")
    assert_wkt_equivalence(p)


@pytest.mark.parametrize(
    "coordinates",
    [(1.0,), (1.0, 2.0, 3.0, 4.0), "Foo", (None, 2.0), (1.0, (2.0,)), (), [], None],
)
def test_point_invalid_coordinates(coordinates):
    """
    Too few or to many elements should not, nor weird data types
    """
    with pytest.raises(ValidationError):
        Point(type="Point", coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Empty array
        [],
        # No Z
        [(1.0, 2.0)],
        [(1.0, 2.0), (1.0, 2.0)],
        # Has Z
        [(1.0, 2.0, 3.0), (1.0, 2.0, 3.0)],
        # Mixed
        [(1.0, 2.0), (1.0, 2.0, 3.0)],
    ],
)
def test_multi_point_valid_coordinates(coordinates):
    """
    Two or three number elements as coordinates should be okay, as well as an empty array.
    """
    p = MultiPoint(type="MultiPoint", coordinates=coordinates)
    assert p.type == "MultiPoint"
    assert p.coordinates == coordinates
    assert hasattr(p, "__geo_interface__")
    assert_wkt_equivalence(p)


@pytest.mark.parametrize(
    "coordinates",
    [[(1.0,)], [(1.0, 2.0, 3.0, 4.0)], ["Foo"], [(None, 2.0)], [(1.0, (2.0,))], None],
)
def test_multi_point_invalid_coordinates(coordinates):
    """
    Too few or to many elements should not, nor weird data types
    """
    with pytest.raises(ValidationError):
        MultiPoint(type="MultiPoint", coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Two Points, no Z
        [(1.0, 2.0), (3.0, 4.0)],
        # Three Points, no Z
        [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)],
        # Two Points, has Z
        [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
        # Shapely doesn't like mixed here
    ],
)
def test_line_string_valid_coordinates(coordinates):
    """
    A list of two coordinates or more should be okay
    """
    linestring = LineString(type="LineString", coordinates=coordinates)
    assert linestring.type == "LineString"
    assert linestring.coordinates == coordinates
    assert hasattr(linestring, "__geo_interface__")
    assert_wkt_equivalence(linestring)


@pytest.mark.parametrize("coordinates", [None, "Foo", [], [(1.0, 2.0)], ["Foo", "Bar"]])
def test_line_string_invalid_coordinates(coordinates):
    """
    But we don't accept non-list inputs, too few coordinates, or bogus coordinates
    """
    with pytest.raises(ValidationError):
        LineString(type="LineString", coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Empty array
        [],
        # One line, two points, no Z
        [[(1.0, 2.0), (3.0, 4.0)]],
        # One line, two points, has Z
        [[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]],
        # One line, three points, no Z
        [[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]],
        # Two lines, two points each, no Z
        [[(1.0, 2.0), (3.0, 4.0)], [(0.0, 0.0), (1.0, 1.0)]],
        # Two lines, two points each, has Z
        [[(1.0, 2.0, 0.0), (3.0, 4.0, 1.0)], [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]],
        # Mixed
        [[(1.0, 2.0), (3.0, 4.0)], [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)]],
    ],
)
def test_multi_line_string_valid_coordinates(coordinates):
    """
    A list of two coordinates or more should be okay
    """
    multilinestring = MultiLineString(type="MultiLineString", coordinates=coordinates)
    assert multilinestring.type == "MultiLineString"
    assert multilinestring.coordinates == coordinates
    assert hasattr(multilinestring, "__geo_interface__")
    assert_wkt_equivalence(multilinestring)


@pytest.mark.parametrize(
    "coordinates", [None, [None], ["Foo"], [[]], [[(1.0, 2.0)]], [["Foo", "Bar"]]]
)
def test_multi_line_string_invalid_coordinates(coordinates):
    """
    But we don't accept non-list inputs, too few coordinates, or bogus coordinates
    """
    with pytest.raises(ValidationError):
        MultiLineString(type="MultiLineString", coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Empty array
        [],
        # Polygon, no Z
        [[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (1.0, 2.0)]],
        # Polygon, has Z
        [[(0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 0.0)]],
    ],
)
def test_polygon_valid_coordinates(coordinates):
    """
    Should accept lists of linear rings
    """
    polygon = Polygon(type="Polygon", coordinates=coordinates)
    assert polygon.type == "Polygon"
    assert polygon.coordinates == coordinates
    assert hasattr(polygon, "__geo_interface__")
    if polygon.coordinates:
        assert polygon.exterior == coordinates[0]
    else:
        assert polygon.exterior is None
    assert not list(polygon.interiors)
    assert_wkt_equivalence(polygon)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Polygon with holes, no Z
        [
            [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)],
            [(2.0, 2.0), (2.0, 4.0), (4.0, 4.0), (4.0, 2.0), (2.0, 2.0)],
        ],
        # Polygon with holes, has Z
        [
            [
                (0.0, 0.0, 0.0),
                (0.0, 10.0, 0.0),
                (10.0, 10.0, 0.0),
                (10.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            ],
            [
                (2.0, 2.0, 1.0),
                (2.0, 4.0, 1.0),
                (4.0, 4.0, 1.0),
                (4.0, 2.0, 1.0),
                (2.0, 2.0, 1.0),
            ],
        ],
        # Mixed
        [
            [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)],
            [
                (2.0, 2.0, 2.0),
                (2.0, 4.0, 0.0),
                (4.0, 4.0, 0.0),
                (4.0, 2.0, 0.0),
                (2.0, 2.0, 2.0),
            ],
        ],
    ],
)
def test_polygon_with_holes(coordinates):
    """Check interior and exterior rings."""
    polygon = Polygon(type="Polygon", coordinates=coordinates)
    assert polygon.type == "Polygon"
    assert hasattr(polygon, "__geo_interface__")
    assert polygon.exterior == polygon.coordinates[0]
    assert list(polygon.interiors) == [polygon.coordinates[1]]
    assert_wkt_equivalence(polygon)


@pytest.mark.parametrize(
    "coordinates",
    [
        "foo",
        None,
        [[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (1.0, 2.0)], "foo", None],
        [[(1.0, 2.0), (3.0, 4.0), (1.0, 2.0)]],
        [[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (7.0, 8.0)]],
    ],
)
def test_polygon_invalid_coordinates(coordinates):
    """
    Should not accept when:
    - Coordinates is not a list
    - Not all elements in coordinates are lists
    - If not all elements have four or more coordinates
    - If not all elements are linear rings
    """
    with pytest.raises(ValidationError):
        Polygon(type="Polygon", coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates",
    [
        # Empty array
        [],
        # Multipolygon, no Z
        [
            [
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],
                [(2.1, 2.1), (2.2, 2.1), (2.2, 2.2), (2.1, 2.2), (2.1, 2.1)],
            ]
        ],
        # Multipolygon, has Z
        [
            [
                [
                    (0.0, 0.0, 4.0),
                    (1.0, 0.0, 4.0),
                    (1.0, 1.0, 4.0),
                    (0.0, 1.0, 4.0),
                    (0.0, 0.0, 4.0),
                ],
                [
                    (2.1, 2.1, 4.0),
                    (2.2, 2.1, 4.0),
                    (2.2, 2.2, 4.0),
                    (2.1, 2.2, 4.0),
                    (2.1, 2.1, 4.0),
                ],
            ]
        ],
        # Mixed
        [
            [
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],
                [
                    (2.1, 2.1, 2.1),
                    (2.2, 2.1, 2.0),
                    (2.2, 2.2, 2.2),
                    (2.1, 2.2, 2.3),
                    (2.1, 2.1, 2.1),
                ],
            ]
        ],
    ],
)
def test_multi_polygon(coordinates):
    """Should accept sequence of polygons."""
    multi_polygon = MultiPolygon(type="MultiPolygon", coordinates=coordinates)

    assert multi_polygon.type == "MultiPolygon"
    assert hasattr(multi_polygon, "__geo_interface__")
    assert_wkt_equivalence(multi_polygon)


@pytest.mark.parametrize(
    "coordinates",
    [
        "foo",
        None,
        [
            [
                [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],
            ],
            [
                [(2.1, 2.1), (2.2, 2.1), (2.2, 2.2), (2.1, 4.2)],
            ],
        ],
    ],
)
def test_multipolygon_invalid_coordinates(coordinates):
    with pytest.raises(ValidationError):
        MultiPolygon(type="MultiPolygon", coordinates=coordinates)


def test_parse_geometry_obj_point():
    assert parse_geometry_obj({"type": "Point", "coordinates": [102.0, 0.5]}) == Point(
        type="Point", coordinates=(102.0, 0.5)
    )


def test_parse_geometry_obj_multi_point():
    assert parse_geometry_obj(
        {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}
    ) == MultiPoint(type="MultiPoint", coordinates=[(100.0, 0.0), (101.0, 1.0)])


def test_parse_geometry_obj_line_string():
    assert parse_geometry_obj(
        {
            "type": "LineString",
            "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]],
        }
    ) == LineString(
        type="LineString",
        coordinates=[(102.0, 0.0), (103.0, 1.0), (104.0, 0.0), (105.0, 1.0)],
    )


def test_parse_geometry_obj_multi_line_string():
    assert parse_geometry_obj(
        {
            "type": "MultiLineString",
            "coordinates": [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]],
        }
    ) == MultiLineString(
        type="MultiLineString",
        coordinates=[[(100.0, 0.0), (101.0, 1.0)], [(102.0, 2.0), (103.0, 3.0)]],
    )


def test_parse_geometry_obj_polygon():
    assert parse_geometry_obj(
        {
            "type": "Polygon",
            "coordinates": [
                [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]
            ],
        }
    ) == Polygon(
        type="Polygon",
        coordinates=[
            [(100.0, 0.0), (101.0, 0.0), (101.0, 1.0), (100.0, 1.0), (100.0, 0.0)]
        ],
    )


def test_parse_geometry_obj_multi_polygon():
    assert parse_geometry_obj(
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
        }
    ) == MultiPolygon(
        type="MultiPolygon",
        coordinates=[
            [[(102.0, 2.0), (103.0, 2.0), (103.0, 3.0), (102.0, 3.0), (102.0, 2.0)]],
            [
                [(100.0, 0.0), (101.0, 0.0), (101.0, 1.0), (100.0, 1.0), (100.0, 0.0)],
                [(100.2, 0.2), (100.8, 0.2), (100.8, 0.8), (100.2, 0.8), (100.2, 0.2)],
            ],
        ],
    )


def test_parse_geometry_obj_invalid_type():
    with pytest.raises(ValidationError):
        parse_geometry_obj({"type": "This type", "obviously": "doesn't exist"})
    with pytest.raises(ValidationError):
        parse_geometry_obj({"type": "", "obviously": "doesn't exist"})
    with pytest.raises(ValidationError):
        parse_geometry_obj({})


def test_parse_geometry_obj_invalid_point():
    """
    litmus test that invalid geometries don't get parsed
    """
    with pytest.raises(ValidationError):
        parse_geometry_obj(
            {"type": "Point", "coordinates": ["not", "valid", "coordinates"]}
        )


@pytest.mark.parametrize(
    "coordinates", [[[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (1.0, 2.0)]]]
)
def test_geometry_collection_iteration(coordinates):
    """test if geometry collection is iterable"""
    polygon = Polygon(type="Polygon", coordinates=coordinates)
    multipolygon = MultiPolygon(type="MultiPolygon", coordinates=[coordinates])
    gc = GeometryCollection(
        type="GeometryCollection", geometries=[polygon, multipolygon]
    )
    assert hasattr(gc, "__geo_interface__")
    assert_wkt_equivalence(gc)
    iter(gc)


@pytest.mark.parametrize(
    "coordinates", [[[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (1.0, 2.0)]]]
)
def test_len_geometry_collection(coordinates):
    """test if GeometryCollection return self leng"""
    polygon = Polygon(type="Polygon", coordinates=coordinates)
    multipolygon = MultiPolygon(type="MultiPolygon", coordinates=[coordinates])
    gc = GeometryCollection(
        type="GeometryCollection", geometries=[polygon, multipolygon]
    )
    assert_wkt_equivalence(gc)
    assert len(gc) == 2


@pytest.mark.parametrize(
    "coordinates", [[[(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (1.0, 2.0)]]]
)
def test_getitem_geometry_collection(coordinates):
    """test if GeometryCollection is subscriptable"""
    polygon = Polygon(type="Polygon", coordinates=coordinates)
    multipolygon = MultiPolygon(type="MultiPolygon", coordinates=[coordinates])
    gc = GeometryCollection(
        type="GeometryCollection", geometries=[polygon, multipolygon]
    )
    assert_wkt_equivalence(gc)
    assert polygon == gc[0]
    assert multipolygon == gc[1]


def test_wkt_mixed_geometry_collection():
    point = Point(type="Point", coordinates=(0.0, 0.0, 0.0))
    line_string = LineString(type="LineString", coordinates=[(0.0, 0.0), (1.0, 1.0)])
    gc = GeometryCollection(type="GeometryCollection", geometries=[point, line_string])
    assert_wkt_equivalence(gc)


def test_wkt_empty_geometry_collection():
    gc = GeometryCollection(type="GeometryCollection", geometries=[])
    assert_wkt_equivalence(gc)


def test_polygon_from_bounds():
    """Result from `from_bounds` class method should be the same."""
    coordinates = [[(1.0, 2.0), (3.0, 2.0), (3.0, 4.0), (1.0, 4.0), (1.0, 2.0)]]
    assert Polygon(type="Polygon", coordinates=coordinates) == Polygon.from_bounds(
        1.0, 2.0, 3.0, 4.0
    )


def test_wkt_name():
    """Make sure WKT name is derived from geometry Type."""

    class PointType(Point):
        ...

    assert (
        PointType(type="Point", coordinates=(1.01, 2.01)).wkt
        == Point(type="Point", coordinates=(1.01, 2.01)).wkt
    )


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ((0, 0), False),
        ((0, 0, 0), True),
    ],
)
def test_point_has_z(coordinates, expected):
    assert Point(type="Point", coordinates=coordinates).has_z == expected


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ([(0, 0)], False),
        ([(0, 0), (1, 1)], False),
        ([(0, 0), (1, 1, 1)], True),
        ([(0, 0, 0)], True),
        ([(0, 0, 0), (1, 1)], True),
    ],
)
def test_multipoint_has_z(coordinates, expected):
    assert MultiPoint(type="MultiPoint", coordinates=coordinates).has_z == expected


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ([(0, 0), (1, 1)], False),
        ([(0, 0), (1, 1, 1)], True),
        ([(0, 0, 0), (1, 1, 1)], True),
        ([(0, 0, 0), (1, 1)], True),
    ],
)
def test_linestring_has_z(coordinates, expected):
    assert LineString(type="LineString", coordinates=coordinates).has_z == expected


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ([[(0, 0), (1, 1)]], False),
        ([[(0, 0), (1, 1)], [(0, 0), (1, 1)]], False),
        ([[(0, 0), (1, 1)], [(0, 0, 0), (1, 1)]], True),
        ([[(0, 0), (1, 1)], [(0, 0), (1, 1, 1)]], True),
        ([[(0, 0), (1, 1, 1)]], True),
        ([[(0, 0, 0), (1, 1, 1)]], True),
        ([[(0, 0, 0), (1, 1)]], True),
        ([[(0, 0, 0), (1, 1, 1)], [(0, 0, 0), (1, 1, 1)]], True),
    ],
)
def test_multilinestring_has_z(coordinates, expected):
    assert (
        MultiLineString(type="MultiLineString", coordinates=coordinates).has_z
        == expected
    )


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ([[(0, 0), (1, 1), (2, 2), (0, 0)]], False),
        ([[(0, 0), (1, 1), (2, 2, 2), (0, 0)]], True),
        ([[(0, 0), (1, 1), (2, 2), (0, 0)], [(0, 0), (1, 1), (2, 2), (0, 0)]], False),
        (
            [[(0, 0), (1, 1), (2, 2), (0, 0)], [(0, 0), (1, 1), (2, 2, 2), (0, 0)]],
            True,
        ),
        ([[(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 0, 0)]], True),
        (
            [
                [(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 0, 0)],
                [(0, 0), (1, 1), (2, 2), (0, 0)],
            ],
            True,
        ),
    ],
)
def test_polygon_has_z(coordinates, expected):
    assert Polygon(type="Polygon", coordinates=coordinates).has_z == expected


@pytest.mark.parametrize(
    "coordinates,expected",
    [
        ([[[(0, 0), (1, 1), (2, 2), (0, 0)]]], False),
        ([[[(0, 0), (1, 1), (2, 2, 2), (0, 0)]]], True),
        (
            [[[(0, 0), (1, 1), (2, 2), (0, 0)]], [[(0, 0), (1, 1), (2, 2), (0, 0)]]],
            False,
        ),
        (
            [
                [[(0, 0), (1, 1), (2, 2), (0, 0)]],
                [
                    [(0, 0), (1, 1), (2, 2), (0, 0)],
                    [(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 0, 0)],
                ],
            ],
            True,
        ),
        (
            [[[(0, 0), (1, 1), (2, 2), (0, 0)]], [[(0, 0), (1, 1), (2, 2, 2), (0, 0)]]],
            True,
        ),
        ([[[(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 0, 0)]]], True),
        (
            [
                [[(0, 0, 0), (1, 1, 1), (2, 2, 2), (0, 0, 0)]],
                [[(0, 0), (1, 1), (2, 2), (0, 0)]],
            ],
            True,
        ),
    ],
)
def test_multipolygon_has_z(coordinates, expected):
    assert MultiPolygon(type="MultiPolygon", coordinates=coordinates).has_z == expected


@pytest.mark.parametrize(
    "shape",
    [
        MultiPoint,
        MultiLineString,
        Polygon,
        MultiPolygon,
    ],
)
def test_wkt_empty(shape):
    assert shape(type=shape.__name__, coordinates=[]).wkt.endswith(" EMPTY")


def test_wkt_empty_geometrycollection():
    assert GeometryCollection(type="GeometryCollection", geometries=[]).wkt.endswith(
        " EMPTY"
    )
