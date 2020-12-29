
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.2.2] - 2020-12-29

### Added
- Made collections iterable (#12)
- Added `parse_geometry_obj` function (#9)

## [0.2.1] - 2020-08-07

Although the type file was added in `0.2.0` it wasn't included in the distributed package. Use this version `0.2.1` for type annotations.

## Fixed
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