import pytest
from pydantic import ValidationError

from geojson_pydantic.geometries import (
    GeometryCollection,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    parse_geometry_obj,
)


@pytest.mark.parametrize("coordinates", [(1, 2), (1, 2, 3), (1.0, 2.0)])
def test_point_valid_coordinates(coordinates):
    """
    Two or three number elements as coordinates shold be okay
    """
    p = Point(coordinates=coordinates)
    assert p.type == "Point"
    assert p.coordinates == coordinates
    assert hasattr(p, "__geo_interface__")


@pytest.mark.parametrize(
    "coordinates", [(1,), (1, 2, 3, 4), "Foo", (None, 2), (1, (2,))]
)
def test_point_invalid_coordinates(coordinates):
    """
    Too few or to many elements should not, nor weird data types
    """
    with pytest.raises(ValidationError):
        Point(coordinates=coordinates)


@pytest.mark.parametrize(
    "coordinates", [[(1, 2), (3, 4)], [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0)]]
)
def test_line_string_valid_coordinates(coordinates):
    """
    A list of two coordinates or more should be okay
    """
    linestring = LineString(coordinates=coordinates)
    assert linestring.type == "LineString"
    assert linestring.coordinates == coordinates
    assert hasattr(linestring, "__geo_interface__")


@pytest.mark.parametrize("coordinates", [None, "Foo", [], [(1, 2)], ["Foo", "Bar"]])
def test_line_string_invalid_coordinates(coordinates):
    """
    But we don't accept non-list inputs, too few coordinates, or bogus coordinates
    """
    with pytest.raises(ValidationError):
        LineString(coordinates=coordinates)


@pytest.mark.parametrize("coordinates", [[[(1, 2), (3, 4), (5, 6), (1, 2)]]])
def test_polygon_valid_coordinates(coordinates):
    """
    Should accept lists of linear rings
    """
    polygon = Polygon(coordinates=coordinates)
    assert polygon.type == "Polygon"
    assert polygon.coordinates == coordinates
    assert hasattr(polygon, "__geo_interface__")


@pytest.mark.parametrize(
    "coordinates",
    [
        "foo",
        [[(1, 2), (3, 4), (5, 6), (1, 2)], "foo", None],
        [[(1, 2), (3, 4), (1, 2)]],
        [[(1, 2), (3, 4), (5, 6), (7, 8)]],
        [],
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
        Polygon(coordinates=coordinates)


def test_parse_geometry_obj_point():
    assert parse_geometry_obj({"type": "Point", "coordinates": [102.0, 0.5]}) == Point(
        coordinates=(102.0, 0.5)
    )


def test_parse_geometry_obj_multi_point():
    assert parse_geometry_obj(
        {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}
    ) == MultiPoint(coordinates=[(100.0, 0.0), (101.0, 1.0)])


def test_parse_geometry_obj_line_striing():
    assert parse_geometry_obj(
        {
            "type": "LineString",
            "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]],
        }
    ) == LineString(
        coordinates=[(102.0, 0.0), (103.0, 1.0), (104.0, 0.0), (105.0, 1.0)]
    )


def test_parse_geometry_obj_multi_line_string():
    assert parse_geometry_obj(
        {
            "type": "MultiLineString",
            "coordinates": [[[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]]],
        }
    ) == MultiLineString(
        coordinates=[[(100.0, 0.0), (101.0, 1.0)], [(102.0, 2.0), (103.0, 3.0)]]
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
        coordinates=[
            [(100.0, 0.0), (101.0, 0.0), (101.0, 1.0), (100.0, 1.0), (100.0, 0.0)]
        ]
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


def test_parse_geometry_obj_invalid_point():
    """
    litmus test that invalid geometries don't get parsed
    """
    with pytest.raises(ValidationError):
        parse_geometry_obj(
            {"type": "Point", "coordinates": ["not", "valid", "coordinates"]}
        )


@pytest.mark.parametrize("coordinates", [[[(1, 2), (3, 4), (5, 6), (1, 2)]]])
def test_geometry_collection_iteration(coordinates):
    """test if geometry collection is iterable"""
    polygon = Polygon(coordinates=coordinates)
    gc = GeometryCollection(geometries=[polygon, polygon])
    iter(gc)


@pytest.mark.parametrize("polygon", [[[(1, 2), (3, 4), (5, 6), (1, 2)]]])
def test_len_geometry_collection(polygon):
    """test if GeometryCollection return self leng"""
    polygon = Polygon(coordinates=polygon)
    gc = GeometryCollection(geometries=[polygon, polygon])
    assert len(gc) == 2


@pytest.mark.parametrize("polygon", [[[(1, 2), (3, 4), (5, 6), (1, 2)]]])
def test_getitem_geometry_collection(polygon):
    """test if GeometryCollection return self leng"""
    polygon = Polygon(coordinates=polygon)
    gc = GeometryCollection(geometries=[polygon, polygon])
    item = gc[0]
    assert item == gc[0]


def test_polygon_from_bounds():
    """Result from `from_bounds` class method should be the same."""
    coordinates = [[(1.0, 2.0), (1.0, 4.0), (3.0, 4.0), (3.0, 2.0), (1.0, 2.0)]]
    assert Polygon(coordinates=coordinates) == Polygon.from_bounds(1, 2, 3, 4)
