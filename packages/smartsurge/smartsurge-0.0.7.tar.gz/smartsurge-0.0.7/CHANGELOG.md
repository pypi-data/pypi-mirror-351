# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-05-10

### Added

- Initial release
- SmartSurgeClient implementation with adaptive rate limit estimation
- Support for all common HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Streaming request functionality with resumability
- Asynchronous request support
- Comprehensive logging and error handling
- Hidden Markov Model for rate limit estimation
- Utilities for timing, logging, and request handling

## [0.0.2] - 2025-05-12

### Changed

- Requests dependency updated to version 2.32.0

## [0.0.3] - 2025-05-12

### Changed

- Bump for new release

## [0.0.4] - 2025-05-13

### Changed

- Bump for new release

## [0.0.5] - 2025-05-13

### Changed

- Enhanced HMM parameter-fitting

## [0.0.6] - 2025-05-27

### Added

- `model_disabled` parameter to RequestHistory and SmartSurgeClient for disabling HMM rate limit detection
- `disable_model()` and `enable_model()` methods to dynamically control HMM usage
- Support for operating without automatic rate limit detection while maintaining request logging

### Fixed

- StreamingState now properly includes required `chunk_size` field
- Integration tests now correctly handle client method return values

## [0.0.7] - 2025-05-28

### Changed

- Version bump to trigger rebuild and refresh package distribution