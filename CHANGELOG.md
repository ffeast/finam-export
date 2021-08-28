# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2021-08-28
### Added
- fill_empty option support in finam.export

### Changed
- ParserError import from the right place (pandas.errors)

## [4.1.0] - 2021-06-14
### Changed
- fetcher passed to ExporterMeta https://github.com/ffeast/finam-export/pull/22

## [4.0.2] - 2021-02-06
### Fixed
- TICKS data download in some cases might miss some days (https://github.com/ffeast/finam-export/issues/16)

## [4.0.1] - 2020-10-04
### Fixed
- version in setup.py

## [4.0.0] - 2020-10-04
### Added
- automatic request split for long intervals (https://github.com/ffeast/finam-export/issues/4)
### Changed
- from now on everything needs to be exported from finam package (instead of finam.export and others)
- automatic retries when hitting the error "Система уже обрабатывает Ваш запрос. Дождитесь окончания обработки."
### Fixed
- download from time intervals that don't include any trading sessions (i.e. 2018-01-01) is now safe and would result in empty data file instead of an exception

## [3.0.1] - 2020-09-12
### Changed
- dropped python2.x support as the newest pandas doesn't support it

## [3.0.0] - 2020-09-12
### Added
- --ext option support in ./scripts/finam-download.py to enable configuration of the resulting files
### Changed
- date/time export format changed to separate columns <DATE> and <TIME> instead of a datetime in a single <DATE> field to make it compatible with tslab and other software
- switched logging mode to .INFO to get rid of annoying debug lines
- unpinned urltools dependency as the previous version doesn't exist
- upgraded dependencies to modern versions

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
