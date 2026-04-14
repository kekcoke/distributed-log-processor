# Extended Log Collector Service

A modular, feature-rich log collection service supporting multiple log formats, filtering, tagging, and structured output.

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Format Parsing** | JSON, Plain Text, Windows Event, Cisco Syslog (CE), Common Log (CLF), Extended Log (ELF), W3C Extended |
| **Regex Filtering** | Include/exclude entries based on regex patterns |
| **Level Filtering** | Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| **Rule-Based Tagging** | Categorize entries with tags (security, database, network, api, auth) |
| **Keyword Tagging** | Automatic tagging based on keyword matching |
| **Structured Output** | JSON, CSV, NDJSON formats |
| **Log Rotation Detection** | Inode and size-based rotation detection |
| **Compressed Files** | Support for .gz, .zip, .bz2 files |
| **Error Reporting** | Track parsing failures, rotation events, compression errors |
| **Metrics Collection** | Entry counts by level, format, and tag |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Extended Log Collector                        │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Parsers   │   Filters   │   Taggers   │      Writers        │
├─────────────┼─────────────┼─────────────┼─────────────────────┤
│ plaintext   │ RegexFilter │ RuleTagger  │ JSONWriter          │
│ json        │ LevelFilter │KeywordTagger│ CSVWriter           │
│ windows_event│CompositeFilter│           │ NDJSONWriter        │
│ ce          │             │             │                     │
│ clf         │             │             │                     │
│ elf         │             │             │                     │
│ w3c         │             │             │                     │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

## Requirements

- Python 3.9+
- watchdog>=2.3.1
- pyyaml>=6.0.1
- pytest>=7.4.3 (for testing)

## Installation

```bash
# Clone and setup
cd log-collector-extended

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
```

## Usage

### Quick Start

```bash
# Collect all logs (no filtering)
python log_collector.py --no-filter

# Collect only errors and above
python log_collector.py --filter-level ERROR

# Exclude debug messages
python log_collector.py --exclude-pattern "DEBUG.*heartbeat"

# Include only security-related logs
python log_collector.py --include-pattern "failed.*login" --include-pattern "unauthorized"
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-c, --config` | Config file path (default: config.yml) |
| `-f, --files` | Log files to monitor |
| `--format` | Output format (json, csv, ndjson) |
| `--filter-level` | Minimum log level to collect |
| `--exclude-pattern` | Regex patterns to exclude |
| `--include-pattern` | Regex patterns to include |
| `--no-tag` | Disable tagging |
| `--no-filter` | Disable all filtering |

### Configuration File

See `config.yml` for full configuration options:

```yaml
# Files to monitor
log_files:
  - ./sample_logs/application.log
  - ./sample_logs/access.json

# Output settings
output:
  directory: ./collected_logs
  format: ndjson

# Filtering
filtering:
  enabled: true
  level:
    min_level: WARNING
  regex:
    exclude_patterns:
      - "health.?check"

# Tagging
tagging:
  enabled: true
  rules:
    security:
      - "failed.*login"
      - "unauthorized"
```

## Supported Log Formats

### Plain Text
```
2024-01-15 10:30:45 [INFO] User logged in
2024-01-15 10:30:46 [ERROR] Connection failed
```

### JSON
```json
{"timestamp": "2024-01-15T10:30:45Z", "level": "ERROR", "message": "Connection failed"}
```

### Windows Event (XML)
```xml
<Event><System><EventID>4625</EventID><Level>2</Level><TimeCreated SystemTime="2024-01-15T10:30:45Z"/></System></Event>
```

### Cisco Syslog (CE)
```
Jan 15 10:30:45 router01 %SYS-5-CONFIG_I: Configuration saved
```

### Common Log Format (CLF)
```
127.0.0.1 - - [15/Jan/2024:10:30:45 -0700] "GET /api HTTP/1.1" 200 1234
```

### Extended Log Format (ELF)
```
2024-01-15 10:30:45 192.168.1.1 10.0.0.1 80 GET /api 200
```

### W3C Extended
```
#Fields: date time c-ip s-ip s-port cs-method cs-uri sc-status
2024-01-15 10:30:45 192.168.1.1 10.0.0.1 80 GET /api 200
```

## Project Structure

```
log-collector-extended/
├── log_collector.py           # Main service
├── config.yml                # Configuration
├── requirements.txt          # Dependencies
├── Dockerfile                # Container image
├── docker-compose.yml        # Docker Compose setup
├── sample_logs/              # Sample logs in all formats
│   ├── application.log       # Plain text
│   ├── access.json           # JSON format
│   ├── windows_event.xml     # Windows Event
│   ├── cisco_syslog.log     # Cisco Syslog
│   ├── access.clf           # Common Log Format
│   ├── access.elf           # Extended Log Format
│   └── access.w3c           # W3C Extended
├── parsers/                  # Log format parsers
│   ├── base.py
│   ├── plain_text.py
│   ├── json_parser.py
│   ├── windows_event.py
│   ├── ce_parser.py
│   ├── clf_parser.py
│   ├── elf_parser.py
│   └── w3c_parser.py
├── filters/                  # Log filters
│   ├── base.py
│   ├── regex_filter.py
│   ├── level_filter.py
│   └── composite_filter.py
├── taggers/                  # Log taggers
│   ├── base.py
│   ├── rule_tagger.py
│   └── keyword_tagger.py
├── writers/                  # Output writers
│   ├── base.py
│   ├── json_writer.py
│   ├── csv_writer.py
│   └── ndjson_writer.py
└── tests/                   # Unit tests
    ├── test_parsers.py
    ├── test_filters.py
    ├── test_taggers.py
    └── test_writers.py
```

## Docker Deployment

```bash
# Build
docker build -t log-collector-extended .

# Run specific files
docker run -v $(pwd)/logs:/app/logs:ro \
  log-collector-extended \
  --files /app/logs/app.log \
  --filter-level ERROR

# Run with docker-compose
docker-compose up -d log-collector-extended
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_parsers.py -v
```

## Modular Design

The service is designed for extensibility:

- **Add new parsers**: Inherit from `BaseParser` in `parsers/base.py`
- **Add new filters**: Inherit from `BaseFilter` in `filters/base.py`
- **Add new taggers**: Inherit from `BaseTagger` in `taggers/base.py`
- **Add new writers**: Inherit from `BaseWriter` in `writers/base.py`

## Integration with Original Collector

Both collectors can run together:

```yaml
# docker-compose.yml
services:
  log-collector:
    # Original lightweight collector
  
  log-collector-extended:
    # Full-featured collector
```

See individual READMEs for each collector's specific capabilities.

## License

MIT
