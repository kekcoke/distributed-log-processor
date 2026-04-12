# Distributed Log Processing System

This project is part of the "365-Day Distributed Log Processing System Implementation" series.

## Project Overview

We're building a distributed system for processing log data at scale. This repository contains all the code and configuration needed to run the system.

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Python 3.9+ (for local development)

### Running the Application
1. Clone this repository
2. Navigate to the project directory
3. Run `docker-compose up`

## Features

### Logger Service
- **Dual Output**: Logs are written to both console and file
- **Log Rotation**: Automatic rotation when file exceeds 1MB (keeps 5 backups)
- **Configurable Log Levels**: Separate levels for console and file output

### Web Interface
A minimal web dashboard is available at `http://localhost:8080`:
- View current configuration settings
- Display recent logs (last 100 lines)
- Raw log access via `/api/logs` endpoint

## Configuration Options

Configure the logger service by editing `src/services/logger/config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `LOG_DIR` | Directory for log files | `/app/logs` |
| `LOG_FILE` | Main log filename | `app.log` |
| `LOG_LEVEL_CONSOLE` | Console log level | `INFO` |
| `LOG_LEVEL_FILE` | File log level | `DEBUG` |
| `LOG_MAX_BYTES` | Max log file size before rotation | `1MB` |
| `LOG_BACKUP_COUNT` | Number of backup files to keep | `5` |

### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General operational messages
- `WARNING`: Potential issues
- `ERROR`: Errors that need attention

## Project Structure
- `src/services/logger/`: Logger microservice with web interface
- `logs/`: Persisted log files (created on first run)
- `config/`: Configuration files
- `data/`: Data storage (gitignored)
- `docs/`: Documentation
- `tests/`: Test suites

## Day 2 Milestones
- Implemented dual-output logging (console + file)
- Added size-based log rotation (1MB limit, 5 backups)
- Created web interface for log viewing
- Added volume mapping for log persistence on host

## Accessing Logs

### Via Web Interface
- Dashboard: http://localhost:8080
- Raw logs: http://localhost:8080/api/logs

### Via Host Filesystem
Logs are persisted to `./logs/` on your host machine:
```bash
tail -f logs/app.log
```
