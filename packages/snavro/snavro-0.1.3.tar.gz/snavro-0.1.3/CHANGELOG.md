# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow for automated PyPI publishing
- Continuous Integration workflow for testing and linting
- Release documentation and process

### Changed
- Improved display formatting for wide Parquet files
- Enhanced column listing with numbered format
- Better error handling and user feedback

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Snavro
- Support for reading Parquet files (.parquet, .parquet.snappy)
- Support for reading Avro files (.avro)
- Automatic file format detection
- Command-line interface (CLI)
- Python API for programmatic use
- Type hints throughout codebase
- Comprehensive test suite
- Professional packaging with pyproject.toml
- MIT license
- Documentation and examples

### Features
- `FileReader` class for object-oriented file reading
- `read_and_display_file()` convenience function
- `get_supported_files()` utility function
- Interactive CLI mode for file selection
- Direct CLI access with file path arguments
- Smart data preview with configurable row counts
- Special handling for 'msg' column in Parquet files
- Cross-platform compatibility (Windows, macOS, Linux)
- Python 3.8+ support 