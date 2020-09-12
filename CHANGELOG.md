# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [x.x.x]
### Changed
- date/time export format changed to separate columns <DATE> and <TIME> instead of a datetime in a single <DATE> field to make it compatible with tslab and other software
- switched logging mode to .INFO to get rid of annoying debug lines
- unpinned urltools dependency as the previous version doesn't exist

## [2.0.0] - 2020-05-10
### Added
- new market CURRENCIES_WORLD=5 (https://github.com/ffeast/finam-export/pull/9)
### Changed
- finam-downloader.py would take into account market code even if contracts are specified

## [1.0.1] - 2019-04-27
### Changed
- uploaded to PyPI https://pypi.org/project/finam-export/, now finam-export can be installed via pip install finam-export

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
