# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2019-04-27
### Added
- scripts/finam-download.py now supports both --contracts and --market keys at the same time
- scripts/finam-lookup.py to quickly lookup contracts available on finam.ru

### Changed
- switched to pandas==0.24.2
- renamed scripts/download.py to scripts/finam-download.py for easier distribution
- all scripts made executable (chmod +x)

### Fixed
- https://github.com/ffeast/finam-export/issues/3: finam metadata cache file is discovered dynamically on the export page

## Older versions
Changelog was not used, see the commits history - I do my best to write meaningful commit messages https://github.com/ffeast/finam-export/commits/master
