
# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.3.1] - 2021-06-30
### Fixed
Added validation for Polygons with zero size.


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
