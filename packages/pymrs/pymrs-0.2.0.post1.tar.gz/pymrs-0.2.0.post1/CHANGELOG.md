# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 0.2.0 - 2025-05-21

### Fixed 

- Fixed logging levels and security concerns (#24).
- Fixed hostname handling to support flexible rest server paths. Hostname parameter now expects the complete base URL including the rest server path.

### Added

- Added timeout customiztion through AsyncMRSClient (#25).
- Added method register_entities() in Query class with URI generation (#18 #19 #20 #26)
- Added method patch_entities() in Query class (#19)

## 0.1.3 - 2025-04-07

### Fixed

- Fixed bug with `eq` field in `_QueryPartOfJSON` class that caused type error.

## 0.1.2 - 2025-02-04

### Fixed

- Incorrect error handling in some cases (#23).

## 0.1.1 - 2024-12-12

### Changed

- Module directory from mrs to pymrs to post on PyPI.

### Fixed

- Short timeout in AsyncMRSClient (#21).

## 0.1.0 - 2024-11-11

- Initial release


