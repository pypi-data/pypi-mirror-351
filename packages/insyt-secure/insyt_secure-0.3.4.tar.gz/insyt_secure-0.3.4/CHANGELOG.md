# Changelog

All notable changes to the `insyt-secure` package will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and follows the format from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.3.0] - 2025-05-14

### Added
- Support for managing one or more projects simultaneously
- Independent connection management for each project (separate credential handling and reconnection)
- Shared DNS cache across all project connections
- Command-line option `--projects` for specifying project configurations
- Support for environment variable `INSYT_PROJECTS` for project configuration

### Changed
- Enhanced project identification in logs
- Improved resource management for multiple concurrent connections

### Removed
- Legacy single-project mode using separate `--project-id` and `--api-key` parameters
- Projects must now be specified using the `--projects` parameter or `INSYT_PROJECTS` environment variable

## [0.2.9] - 2025-05-13

### Added
- DNS caching mechanism to improve resilience against DNS server outages
- Cached DNS resolutions are stored for up to 24 hours and used as fallback
- Initial release of version 0.2.6 