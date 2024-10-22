
# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).

Note: Minor version `0.X.0` update might break the API, It's recommended to pin geojson-pydantic to minor version: `geojson-pydantic>=0.6,<0.7`

## [1.1.2] - 2024-10-22

* relax `bbox` validation and allow antimeridian crossing bboxes

## [1.1.1] - 2024-08-29

* add python 3.12 support
* switch to `flit-core` for packaging build backend

## [1.1.0] - 2024-05-10

### Added

* Add Position2D and Position3D of type NamedTuple (author @impocode, https://github.com/developmentseed/geojson-pydantic/pull/161)

## [1.0.2] - 2024-01-16

### Fixed

* Temporary workaround for surfacing model attributes in FastAPI application (author @markus-work, https://github.com/developmentseed/geojson-pydantic/pull/153)

## [1.0.1] - 2023-10-04

### Fixed

* Model serialization when using include/exclude (ref: https://github.com/developmentseed/geojson-pydantic/pull/148)

## [1.0.0] - 2023-07-24

### Fixed

* reduce validation error message verbosity when discriminating Geometry types
* MultiPoint WKT now includes parentheses around each Point

### Added

* more tests for `GeometryCollection` warnings

### Changed

* update pydantic requirement to `~=2.0`

* update pydantic `FeatureCollection` generic model to allow named features in the generated schemas.

    ```python
    # before
    FeatureCollection[Geometry, Properties]

    # now
    FeatureCollection[Feature[Geometry, Properties]]
    ```

* raise `ValueError` in `geometries.parse_geometry_obj` instead of `ValidationError`

    ```python
    # before
    parse_geometry_obj({"type": "This type", "obviously": "doesn't exist"})
    >> ValidationError

    # now
    parse_geometry_obj({"type": "This type", "obviously": "doesn't exist"})
    >> ValueError("Unknown type: This type")
    ```

* update JSON serializer to exclude null `bbox` and `id`

    ```python
    # before
    Point(type="Point", coordinates=[0, 0]).json()
    >> '{"type":"Point","coordinates":[0.0,0.0],"bbox":null}'

    # now
    Point(type="Point", coordinates=[0, 0]).model_dump_json()
    >> '{"type":"Point","coordinates":[0.0,0.0]}'
    ```

* delete `geojson_pydantic.geo_interface.GeoInterfaceMixin` and replaced by `geojson_pydantic.base._GeoJsonBase` class

* delete `geojson_pydantic.types.validate_bbox`

## [0.6.3] - 2023-07-02

* limit pydantic requirement to `~=1.0`

## [0.6.2] - 2023-05-16

### Added

* Additional bbox validation (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/122)

## [0.6.1] - 2023-05-12

### Fixed

* Fix issue with null bbox validation (author @bmschmidt, https://github.com/developmentseed/geojson-pydantic/pull/119)

## [0.6.0] - 2023-05-09

No change since 0.6.0a0

## [0.6.0a0] - 2023-04-04

### Added

- Validate order of bounding box values. (author @moradology, https://github.com/developmentseed/geojson-pydantic/pull/114)
- Enforce required keys and avoid defaults. This aim to follow the geojson specification to the letter.

    ```python
    # Before
    Feature(geometry=Point(coordinates=(0,0)))

    # Now
    Feature(
        type="Feature",
        geometry=Point(
            type="Point",
            coordinates=(0,0)
        ),
        properties=None,
    )
    ```

- Add has_z function to Geometries (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/103)
- Add optional bbox to geometries. (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/108)
- Add support for nested GeometryCollection and a corresponding warning. (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/111)

### Changed

- Refactor and simplify WKT construction (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/97)
- Support empty geometry coordinates (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/100)
- Refactored `__geo_interface__` to be a Mixin which returns `self.dict` (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/105)
- GeometryCollection containing a single geometry or geometries of only one type will now produce a warning. (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/111)

### Fixed

- Do not validates arbitrary dictionaries. Make `Type` a mandatory key for objects (author @vincentsarago, https://github.com/developmentseed/geojson-pydantic/pull/94)
- Add Geometry discriminator when parsing geometry objects (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/101)
- Mixed Dimensionality WKTs (make sure the coordinates are either all 2D or 3D) (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/107)
- Allow Feature's **id** to be either a String or a Number (author @vincentsarago, https://github.com/developmentseed/geojson-pydantic/pull/91)

### Removed

- Python 3.7 support (author @vincentsarago, https://github.com/developmentseed/geojson-pydantic/pull/94)
- Unused `LinearRing` Model (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/106)

## [0.5.0] - 2022-12-16

### Added

- python 3.11 support

### Fixed

- Derive WKT type from Geometry's type instead of class name (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/81)

### Changed

- Replace `NumType` with `float` throughout (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/83)
- `__geo_interface__` definition to not use pydantic `BaseModel.dict()` method and better match the specification
- Adjusted mypy configuration and updated type definitions to satisfy all rules (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/87)
- Updated pre-commit config to run mypy on the whole library instead of individual changed files.
- Defaults are more explicit. This keeps pyright from thinking they are required.

### Removed

- Remove `validate` classmethods used to implicitly load json strings (author @eseglem, https://github.com/developmentseed/geojson-pydantic/pull/88)

## [0.4.3] - 2022-07-18

### Fixed

- The bbox key should not be in a `__geo_interface__` object if the bbox is None (author @yellowcap, https://github.com/developmentseed/geojson-pydantic/pull/77)

## [0.4.2] - 2022-06-13

### Added

- `GeometryCollection` as optional input to geometry field in `Feature` (author @davidraleigh, https://github.com/developmentseed/geojson-pydantic/pull/72)

## [0.4.1] - 2022-06-10

### Added

- `Geometry` and `GeometryCollection` validation from dict or string (author @Vikka, https://github.com/developmentseed/geojson-pydantic/pull/69)

    ```python
    Point.validate('{"coordinates": [1.0, 2.0], "type": "Point"}')
    >> Point(coordinates=(1.0, 2.0), type='Point')
    ```

- `Feature` and `FeatureCollection` validation from dict or string

    ```python
    FeatureCollection.validate('{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"coordinates": [1.0, 2.0], "type": "Point"}}]}')
    >> FeatureCollection(type='FeatureCollection', features=[Feature(type='Feature', geometry=Point(coordinates=(1.0, 2.0), type='Point'), properties=None, id=None, bbox=None)], bbox=None)
    ```

## [0.4.0] - 2022-06-03

### Added
- `.wkt` property for Geometry object
    ```python
    from geojson_pydantic.geometries import Point

    Point(coordinates=(1, 2)).wkt
    >> 'POINT (1.0 2.0)'
    ```

- `.exterior` and `.interiors` properties for `geojson_pydantic.geometries.Polygon` object.
    ```python
    from geojson_pydantic.geometries import Polygon
    polygon = Polygon(
        coordinates=[
            [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)],
            [(2, 2), (2, 4), (4, 4), (4, 2), (2, 2)],
        ]
    )
    polygon.exterior
    >> [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (0.0, 0.0)]

    list(polygon.interiors)
    >> [[(2.0, 2.0), (2.0, 4.0), (4.0, 4.0), (4.0, 2.0), (2.0, 2.0)]]
    ```

- `__geo_interface__` to `geojson_pydantic.geometries.GeometryCollection` object
- `__geo_interface__` to `geojson_pydantic.feature.Feature` and `geojson_pydantic.feature.FeatureCollection` object
- `geojson_pydantic.__all__` to declaring public objects (author @farridav, https://github.com/developmentseed/geojson-pydantic/pull/52)

### Changed
- switch to `pyproject.toml`
- rename `geojson_pydantic.version` to `geojson_pydantic.__version__`

### Fixed
- changelog compare links

## [0.3.4] - 2022-04-28

- Fix optional geometry and bbox fields on `Feature`; allowing users to pass in `None` or even omit either field (author @moradology, https://github.com/developmentseed/geojson-pydantic/pull/56)
- Fix `Polygon.from_bounds` to respect geojson specification and return counterclockwise linear ring (author @jmfee-usgs, https://github.com/developmentseed/geojson-pydantic/pull/49)

## [0.3.3] - 2022-03-04

- Follow geojson specification and make feature geometry optional (author @yellowcap, https://github.com/developmentseed/geojson-pydantic/pull/47)
    ```python
    from geojson_pydantic import Feature
    # Before
    feature = Feature(type="Feature", geometry=None, properties={})

    >> ValidationError: 1 validation error for Feature
    geometry none is not an allowed value (type=type_error.none.not_allowed)

    # Now
    feature = Feature(type="Feature", geometry=None, properties={})
    assert feature.geometry is None
    ```

## [0.3.2] - 2022-02-21

- fix `parse_geometry_obj` potential bug (author @geospatial-jeff, https://github.com/developmentseed/geojson-pydantic/pull/45)
- improve type definition (and validation) for geometry coordinate arrays (author @geospatial-jeff, https://github.com/developmentseed/geojson-pydantic/pull/44)

## [0.3.1] - 2021-08-04

### Added
- `Polygon.from_bounds` class method to create a Polygon geometry from a bounding box.
    ```python
    from geojson_pydantic import Polygon
    print(Polygon.from_bounds((1, 2, 3, 4)).dict(exclude_none=True))
    >> {'coordinates': [[(1.0, 2.0), (1.0, 4.0), (3.0, 4.0), (3.0, 2.0), (1.0, 2.0)]], 'type': 'Polygon'}
    ```

### Fixed
- Added validation for Polygons with zero size.


## [0.3.0] - 2021-05-25

### Added
- `Feature` and `FeatureCollection` model generics to support custom geometry and/or properties validation (author @iwpnd, https://github.com/developmentseed/geojson-pydantic/pull/29)

    ```python
    from pydantic import BaseModel
    from geojson_pydantic.features import Feature
    from geojson_pydantic.geometries import Polygon

    class MyFeatureProperties(BaseModel):
        name: str
        value: int

    feature = Feature[Polygon, MyFeatureProperties](
        **{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                [
                    [13.38272,52.46385],
                    [13.42786,52.46385],
                    [13.42786,52.48445],
                    [13.38272,52.48445],
                    [13.38272,52.46385]
                ]
                ]
            },
            "properties": {
                "name": "test",
                "value": 1
            }
        }
    )
    ```

- Top level export (https://github.com/developmentseed/geojson-pydantic/pull/34)

    ```python
    # before
    from geojson_pydantic.features import Feature, FeatureCollection
    from geojson_pydantic.geometries import Polygon

    # now
    from geojson_pydantic import Feature, Polygon
    ```

### Removed
- Drop python 3.6 support
- Renamed `utils.py` to `types.py`
- Removed `Coordinate` type in `geojson_pydantic.features` (replaced by `Position`)

## [0.2.3] - 2021-05-05

### Fixed
- incorrect version number set in `__init__.py`

## [0.2.2] - 2020-12-29

### Added
- Made collections iterable (#12)
- Added `parse_geometry_obj` function (#9)

## [0.2.1] - 2020-08-07

Although the type file was added in `0.2.0` it wasn't included in the distributed package. Use this version `0.2.1` for type annotations.

### Fixed
- Correct package type information files

## [0.2.0] - 2020-08-06

### Added
- Added documentation on locally running tests (#3)
- Publish type information (#6)

### Changed
- Removed geojson dependency (#4)

### Fixed
- Include MultiPoint as a valid geometry for a Feature (#1)

## [0.1.0] - 2020-05-21

### Added
- Initial Release

[unreleased]: https://github.com/developmentseed/geojson-pydantic/compare/1.1.2...HEAD
[1.1.2]: https://github.com/developmentseed/geojson-pydantic/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/developmentseed/geojson-pydantic/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/developmentseed/geojson-pydantic/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/developmentseed/geojson-pydantic/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/developmentseed/geojson-pydantic/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.6.3...1.0.0
[0.6.3]: https://github.com/developmentseed/geojson-pydantic/compare/0.6.2...0.6.3
[0.6.2]: https://github.com/developmentseed/geojson-pydantic/compare/0.6.1...0.6.2
[0.6.1]: https://github.com/developmentseed/geojson-pydantic/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.6.0a0...0.6.0
[0.6.0a]: https://github.com/developmentseed/geojson-pydantic/compare/0.5.0...0.6.0a0
[0.5.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.4.3...0.5.0
[0.4.3]: https://github.com/developmentseed/geojson-pydantic/compare/0.4.2...0.4.3
[0.4.2]: https://github.com/developmentseed/geojson-pydantic/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/developmentseed/geojson-pydantic/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.3.4...0.4.0
[0.3.4]: https://github.com/developmentseed/geojson-pydantic/compare/0.3.3...0.3.4
[0.3.3]: https://github.com/developmentseed/geojson-pydantic/compare/0.3.2...0.3.3
[0.3.2]: https://github.com/developmentseed/geojson-pydantic/compare/0.3.1...0.3.2
[0.3.1]: https://github.com/developmentseed/geojson-pydantic/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.2.3...0.3.0
[0.2.3]: https://github.com/developmentseed/geojson-pydantic/compare/0.2.2...0.2.3
[0.2.2]: https://github.com/developmentseed/geojson-pydantic/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/developmentseed/geojson-pydantic/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/developmentseed/geojson-pydantic/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/developmentseed/geojson-pydantic/compare/005f3e57ad07272c99c54302decc63eec12175c9...0.1.0
