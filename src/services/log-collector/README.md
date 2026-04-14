# Log Collector Service

A lightweight service that monitors log files in real-time and collects entries for processing.

## Architecture

```
log-generator (container)
    └── writes to: /app/logs/app.log
            ↓ (shared volume)
log-collector (container)
    └── reads from: /app/logs/app.log (read-only)
```

## Features

- **Real-time monitoring** using `watchdog` library
- **Multiple file support** via configurable file list
- **Persistent tracking** - continues from last position after restart
- **Lightweight** - minimal dependencies

## Requirements

- Python 3.9+
- watchdog>=2.3.1
- pyyaml>=6.0

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Basic usage
python log_collector.py

# Watch specific files
python log_collector.py --files /path/to/log1.log /path/to/log2.log

# With output directory
python log_collector.py --files ./logs/app.log --output-dir ./collected_logs
```

### Configuration

Edit `config.yml`:

```yaml
log_files:
  - ./sample_logs/app.log
check_interval: 0.5
```

### Docker

```bash
# Build image
docker build -t log-collector .

# Run container
docker run -v $(pwd)/logs:/app/logs:ro log-collector

# Run with docker-compose
docker-compose up -d log-collector
```

## Project Structure

```
log-collector/
├── log_collector.py      # Main service
├── config.yml           # Configuration
├── requirements.txt     # Dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Docker Compose setup
├── sample_logs/         # Sample log files for testing
└── README.md
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| log_files | ['./sample_logs/app.log'] | List of files to monitor |
| check_interval | 0.5 | Seconds between file checks |

## License

MIT
