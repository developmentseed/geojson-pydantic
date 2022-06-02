import geojson_pydantic


def test_import_namespace():
    """We have exposed all of the public objects via __all__"""
    assert sorted(geojson_pydantic.__all__) == [
        "Feature",
        "FeatureCollection",
        "GeometryCollection",
        "LineString",
        "MultiLineString",
        "MultiPoint",
        "MultiPolygon",
        "Point",
        "Polygon",
    ]
