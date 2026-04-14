# Changelog - Extended Log Collector

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-04-14

### Added
- **Multi-format parsing**: JSON, Plain Text, Windows Event (XML), Cisco Syslog (CE), Common Log Format (CLF), Extended Log Format (ELF), W3C Extended
- **Regex-based filtering**: Include/exclude entries based on regex patterns
- **Level-based filtering**: Filter by log level with min_level, include_levels, exclude_levels
- **Rule-based tagging**: Categorize entries with configurable rules (security, database, network, api, auth)
- **Keyword-based tagging**: Automatic tagging based on keyword matching
- **Structured output writers**: JSONWriter, CSVWriter, NDJSONWriter
- **Log rotation detection**: Inode and size-based rotation detection
- **Compressed file support**: Support for .gz, .zip, .bz2 files
- **Error reporting**: Track parsing failures, rotation events, compression errors
- **Metrics collection**: Entry counts by level, format, and tag
- **Auto-format detection**: Automatically detect log format from sample lines
- **Modular architecture**: Separable parsers, filters, taggers, and writers modules
- **Comprehensive unit tests**: 44 tests covering all components
- **Sample logs**: Test files in all supported formats

### Changed
- Complete rewrite with modular architecture
- Enhanced documentation with architecture diagrams
- Moved to src/services/ directory for project organization

### Dependencies
- watchdog>=2.3.1
- pyyaml>=6.0.1
- pytest>=7.4.3
- pytest-cov>=4.1.0

## [1.0.0] - 2026-04-11

### Added
- Initial fork from log-collector
