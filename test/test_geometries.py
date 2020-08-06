import pytest
from pydantic import ValidationError

from geojson_pydantic.geometries import Point, LineString, Polygon


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
