#!/usr/bin/env python3
"""
Extended Log Collector Service

Features:
- Multi-format parsing (JSON, Plain Text, Windows Event, CE, CLF, ELF, W3C)
- Regex-based filtering
- Rule-based and keyword-based tagging
- Structured output (JSON, CSV, NDJSON)
- Log rotation detection
- Compressed file support
- Error reporting and metrics
"""
import os
import sys
import time
import json
import yaml
import logging
import hashlib
import gzip
import zipfile
import bz2
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import modular components
from parsers import get_parser, auto_detect_format, PARSERS
from parsers.base import ParsedEntry
from filters import RegexFilter, LevelFilter, CompositeFilter
from taggers import RuleTagger, KeywordTagger
from writers import JSONWriter, CSVWriter, NDJSONWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ExtendedLogCollector')


class MetricsCollector:
    """Collect and report metrics."""
    
    def __init__(self, config: dict):
        self.config = config
        self.stats = {
            'entries_collected': 0,
            'entries_filtered': 0,
            'parsing_failures': 0,
            'rotation_events': 0,
            'compression_errors': 0,
            'entries_by_level': {},
            'entries_by_format': {},
            'entries_by_tag': {},
        }
    
    def increment(self, metric: str, value: int = 1):
        if metric in self.stats:
            if isinstance(self.stats[metric], dict):
                self.stats[metric] = self.stats.get(metric, {})
            else:
                self.stats[metric] = self.stats.get(metric, 0) + value
    
    def track_entry(self, entry: ParsedEntry, filtered: bool = False):
        self.stats['entries_collected' if not filtered else 'entries_filtered'] += 1
        if entry.level:
            self.stats['entries_by_level'][entry.level] = \
                self.stats['entries_by_level'].get(entry.level, 0) + 1
        if entry.format_type:
            self.stats['entries_by_format'][entry.format_type] = \
                self.stats['entries_by_format'].get(entry.format_type, 0) + 1
        tags = entry.metadata.get('tags', set())
        for tag in tags:
            self.stats['entries_by_tag'][tag] = \
                self.stats['entries_by_tag'].get(tag, 0) + 1
    
    def report_failure(self, failure_type: str):
        key = f"{failure_type}_failures" if 'rotation' not in failure_type else f"{failure_type}_events"
        if key not in self.stats:
            self.stats[key] = 0
        self.stats[key] += 1
    
    def to_dict(self) -> dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - getattr(self, 'start_time', time.time()),
            **self.stats
        }
    
    def save(self, output_path: str):
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class ErrorReporter:
    """Report errors to a log file."""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, error_type: str, message: str, details: dict = None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'details': details or {}
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')


class LogRotationDetector:
    """Detect log file rotation/truncation."""
    
    def __init__(self, strategies: List[str] = None):
        self.strategies = strategies or ['inode_check', 'size_threshold']
        self.file_states = {}  # path -> {inode, size, mtime, content_hash}
    
    def check_rotation(self, file_path: str) -> bool:
        """Return True if file has been rotated."""
        if not os.path.exists(file_path):
            return False
        
        stat = os.stat(file_path)
        current_state = {
            'inode': stat.st_ino,
            'size': stat.st_size,
            'mtime': stat.st_mtime
        }
        
        if file_path not in self.file_states:
            self.file_states[file_path] = current_state
            return False
        
        old_state = self.file_states[file_path]
        
        rotated = False
        
        if 'inode_check' in self.strategies:
            if current_state['inode'] != old_state['inode']:
                rotated = True
        
        if 'size_threshold' in self.strategies:
            # File shrunk significantly (truncated)
            if current_state['size'] < old_state['size'] * 0.5:
                rotated = True
        
        self.file_states[file_path] = current_state
        return rotated


class CompressionHandler:
    """Handle compressed log files."""
    
    def __init__(self, config: dict):
        self.config = config
        self.supported = config.get('supported', ['gz', 'zip', 'bz2'])
        self.temp_dir = Path(config.get('temp_dir', './tmp'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def is_compressed(self, file_path: str) -> bool:
        ext = file_path.lower().split('.')[-1]
        return ext in self.supported
    
    def decompress(self, file_path: str) -> Optional[str]:
        """Decompress file and return path to decompressed content."""
        try:
            if file_path.endswith('.gz'):
                output_path = self.temp_dir / Path(file_path).stem
                with gzip.open(file_path, 'rt') as f_in:
                    with open(output_path, 'w') as f_out:
                        f_out.write(f_in.read())
                return str(output_path)
            
            elif file_path.endswith('.bz2'):
                output_path = self.temp_dir / Path(file_path).stem
                with bz2.open(file_path, 'rt') as f_in:
                    with open(output_path, 'w') as f_out:
                        f_out.write(f_in.read())
                return str(output_path)
            
            elif file_path.endswith('.zip'):
                # For ZIP, extract first file
                output_path = self.temp_dir / Path(file_path).stem
                with zipfile.ZipFile(file_path, 'r') as zf:
                    first_name = zf.namelist()[0]
                    content = zf.read(first_name).decode('utf-8', errors='ignore')
                    output_path.write_text(content)
                return str(output_path)
        
        except Exception as e:
            logger.error(f"Failed to decompress {file_path}: {e}")
            return None
        
        return None


class ExtendedLogFileHandler(FileSystemEventHandler):
    """Extended handler with filtering, tagging, and structured output."""
    
    def __init__(self, file_path: str, parser, filter_obj, tagger, 
                 writer, rotation_detector, compression_handler,
                 metrics: MetricsCollector, error_reporter: ErrorReporter,
                 config: dict):
        super().__init__()
        self.file_path = file_path
        self.parser = parser
        self.filter_obj = filter_obj
        self.tagger = tagger
        self.writer = writer
        self.rotation_detector = rotation_detector
        self.compression_handler = compression_handler
        self.metrics = metrics
        self.error_reporter = error_reporter
        self.config = config
        self.last_position = 0
        self.buffer = []
        self.buffer_size = config.get('monitoring', {}).get('buffer_size', 1000)
        self.initialize_position()
    
    def initialize_position(self):
        """Start tracking from the end of existing file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                f.seek(0, os.SEEK_END)
                self.last_position = f.tell()
            logger.info(f"Tracking {self.file_path} from position {self.last_position}")
    
    def on_modified(self, event):
        if event.src_path == self.file_path:
            self.collect_new_logs()
    
    def collect_new_logs(self):
        """Read, parse, filter, tag, and output new log entries."""
        try:
            # Check for rotation
            if self.rotation_detector and self.rotation_detector.check_rotation(self.file_path):
                logger.info(f"Log rotation detected for {self.file_path}, resetting position")
                self.metrics.report_failure('rotation_events')
                self.error_reporter.log('rotation', f'Rotation detected for {self.file_path}')
                self.initialize_position()
                return
            
            # Handle compressed files
            actual_path = self.file_path
            if self.compression_handler and self.compression_handler.is_compressed(self.file_path):
                actual_path = self.compression_handler.decompress(self.file_path)
                if not actual_path:
                    self.metrics.report_failure('compression_errors')
                    return
            
            with open(actual_path, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
            
            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse
                entry = self.parser.parse(line)
                if not entry:
                    self.metrics.report_failure('parsing_failures')
                    continue
                
                # Filter
                if self.filter_obj and not self.filter_obj.should_include(entry):
                    self.metrics.track_entry(entry, filtered=True)
                    continue
                
                # Tag
                if self.tagger:
                    tags = self.tagger.tag(entry)
                    if tags:
                        if 'tags' not in entry.metadata:
                            entry.metadata['tags'] = set()
                        entry.metadata['tags'].update(tags)
                
                # Track metrics
                self.metrics.track_entry(entry)
                
                # Buffer
                self.buffer.append(entry)
                if len(self.buffer) >= self.buffer_size:
                    self.flush_buffer()
            
            # Flush buffer periodically
            if self.buffer:
                self.flush_buffer()
        
        except Exception as e:
            logger.error(f"Error collecting logs from {self.file_path}: {e}")
            self.error_reporter.log('collection_error', str(e), {'file': self.file_path})
    
    def flush_buffer(self):
        """Write buffered entries to output."""
        if self.buffer:
            try:
                self.writer.write(self.buffer)
                self.buffer.clear()
            except Exception as e:
                logger.error(f"Error writing entries: {e}")


class ExtendedLogCollectorService:
    """Extended log collector service with all features."""
    
    def __init__(self, config_path: str = "config.yml"):
        self.config_path = config_path
        self.observers = []
        self.handlers = []
        self.config = {}
        self.parser = None
        self.filter_obj = None
        self.tagger = None
        self.writer = None
        self.rotation_detector = None
        self.compression_handler = None
        self.metrics = None
        self.error_reporter = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file."""
        self.config = {
            'log_files': ['./sample_logs/*.log'],
            'output': {'directory': './collected_logs', 'format': 'ndjson'},
            'parsing': {'auto_detect': True, 'default_format': 'plaintext'},
            'filtering': {'enabled': False},
            'tagging': {'enabled': False},
            'monitoring': {'check_interval': 0.5, 'buffer_size': 1000},
            'rotation': {'enabled': False, 'strategies': ['inode_check']},
            'compression': {'enabled': False},
            'error_reporting': {'enabled': True, 'log_file': './collected_logs/errors.log'},
            'metrics': {'enabled': True, 'output_file': './collected_logs/metrics.json'}
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self._deep_update(self.config, yaml_config)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Initialize components
        self._init_components()
    
    def _deep_update(self, base: dict, update: dict):
        """Recursively update nested dictionaries."""
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def _init_components(self):
        """Initialize parser, filter, tagger, writer."""
        # Metrics
        self.metrics = MetricsCollector(self.config)
        self.metrics.start_time = time.time()
        
        # Error reporter
        err_cfg = self.config.get('error_reporting', {})
        if err_cfg.get('enabled', True):
            self.error_reporter = ErrorReporter(err_cfg.get('log_file', './collected_logs/errors.log'))
        else:
            self.error_reporter = ErrorReporter('/dev/null')
        
        # Parser
        parsing_cfg = self.config.get('parsing', {})
        if parsing_cfg.get('auto_detect', True):
            self.parser = None  # Will auto-detect per file
        else:
            format_name = parsing_cfg.get('default_format', 'plaintext')
            self.parser = get_parser(format_name)
        
        # Filter
        filter_cfg = self.config.get('filtering', {})
        if filter_cfg.get('enabled', False):
            filters = []
            
            level_cfg = filter_cfg.get('level', {})
            if level_cfg:
                level_filter = LevelFilter(
                    include_levels=level_cfg.get('include'),
                    exclude_levels=level_cfg.get('exclude'),
                    min_level=level_cfg.get('min_level')
                )
                filters.append(level_filter)
            
            regex_cfg = filter_cfg.get('regex', {})
            if regex_cfg:
                regex_filter = RegexFilter(
                    include_patterns=regex_cfg.get('include_patterns'),
                    exclude_patterns=regex_cfg.get('exclude_patterns'),
                    field=regex_cfg.get('field', 'message')
                )
                filters.append(regex_filter)
            
            if filters:
                mode = filter_cfg.get('mode', 'AND')
                self.filter_obj = CompositeFilter(filters, mode)
        
        # Tagger
        tag_cfg = self.config.get('tagging', {})
        if tag_cfg.get('enabled', False):
            rules = tag_cfg.get('rules', {})
            keywords = tag_cfg.get('keywords', {})
            
            self.tagger = RuleTagger(rules)
            if keywords:
                keyword_tagger = KeywordTagger(keywords)
                # Combine by adding keywords to rules
                for tag, kws in keywords.items():
                    self.tagger.add_rule(tag, kws)
        
        # Writer
        output_cfg = self.config.get('output', {})
        output_dir = output_cfg.get('directory', './collected_logs')
        output_format = output_cfg.get('format', 'ndjson')
        today = date.today().strftime('%Y%m%d')
        filename = output_cfg.get('filename_pattern', 'collected_{date}.{format}')
        filename = filename.format(date=today, format=output_format)
        output_path = os.path.join(output_dir, filename)
        
        if output_format == 'json':
            self.writer = JSONWriter(output_path)
        elif output_format == 'csv':
            self.writer = CSVWriter(output_path)
        else:  # ndjson
            self.writer = NDJSONWriter(output_path)
        
        # Rotation detector
        rot_cfg = self.config.get('rotation', {})
        if rot_cfg.get('enabled', False):
            self.rotation_detector = LogRotationDetector(rot_cfg.get('strategies', ['inode_check']))
        
        # Compression handler
        comp_cfg = self.config.get('compression', {})
        if comp_cfg.get('enabled', False):
            self.compression_handler = CompressionHandler(comp_cfg)
    
    def start(self):
        """Start monitoring log files."""
        log_files = self.config.get('log_files', [])
        
        for file_path in log_files:
            # Expand glob patterns
            if '*' in file_path:
                import glob
                matched_files = glob.glob(file_path)
            else:
                matched_files = [file_path]
            
            for actual_path in matched_files:
                if not os.path.exists(actual_path):
                    logger.warning(f"File not found: {actual_path}")
                    continue
                
                # Determine parser for this file
                parser = self.parser
                if parser is None:
                    # Auto-detect format
                    try:
                        with open(actual_path, 'r') as f:
                            sample = f.readline()
                        format_type = auto_detect_format(sample)
                        parser = get_parser(format_type)
                        logger.info(f"Auto-detected format '{format_type}' for {actual_path}")
                    except:
                        parser = get_parser('plaintext')
                
                # Create handler
                handler = ExtendedLogFileHandler(
                    actual_path, parser, self.filter_obj, self.tagger,
                    self.writer, self.rotation_detector, self.compression_handler,
                    self.metrics, self.error_reporter, self.config
                )
                self.handlers.append(handler)
                
                # Set up observer
                log_dir = os.path.dirname(actual_path) or '.'
                observer = Observer()
                observer.schedule(handler, log_dir, recursive=False)
                observer.start()
                self.observers.append(observer)
                
                logger.info(f"Monitoring: {actual_path}")
    
    def stop(self):
        """Stop all observers."""
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()
        logger.info("Stopped all monitoring")
    
    def run(self):
        """Run the collector service."""
        try:
            self.start()
            logger.info("Extended Log Collector is running. Press Ctrl+C to stop.")
            
            # Save metrics periodically
            metrics_cfg = self.config.get('metrics', {})
            metrics_interval = metrics_cfg.get('interval', 60)
            
            while True:
                time.sleep(1)
                # Periodically save metrics
                if self.metrics:
                    self.metrics.uptime_seconds = time.time() - self.metrics.start_time
                    if metrics_cfg.get('enabled', True):
                        output_file = metrics_cfg.get('output_file', './collected_logs/metrics.json')
                        self.metrics.save(output_file)
        
        except KeyboardInterrupt:
            logger.info("Received stop signal")
        finally:
            self.stop()
            # Final metrics save
            if self.metrics:
                metrics_cfg = self.config.get('metrics', {})
                if metrics_cfg.get('enabled', True):
                    self.metrics.save(metrics_cfg.get('output_file', './collected_logs/metrics.json'))
            logger.info("Collector stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extended Log Collector Service')
    parser.add_argument('--config', '-c', default='config.yml', help='Config file path')
    parser.add_argument('--files', '-f', nargs='+', help='Log files to monitor')
    parser.add_argument('--format', help='Output format (json, csv, ndjson)')
    parser.add_argument('--filter-level', help='Minimum log level to collect')
    parser.add_argument('--exclude-pattern', dest='exclude', action='append', help='Regex patterns to exclude')
    parser.add_argument('--include-pattern', dest='include', action='append', help='Regex patterns to include')
    parser.add_argument('--no-tag', action='store_true', help='Disable tagging')
    parser.add_argument('--no-filter', action='store_true', help='Disable filtering')
    
    args = parser.parse_args()
    
    collector = ExtendedLogCollectorService(args.config)
    
    # Override config with CLI args
    if args.files:
        collector.config['log_files'] = args.files
    if args.format:
        collector.config['output']['format'] = args.format
    if args.filter_level:
        collector.config['filtering']['enabled'] = True
        collector.config['filtering']['level'] = {'min_level': args.filter_level.upper()}
    if args.exclude:
        collector.config['filtering']['enabled'] = True
        collector.config['filtering']['regex'] = {'exclude_patterns': args.exclude}
    if args.include:
        collector.config['filtering']['enabled'] = True
        collector.config['filtering']['regex'] = {'include_patterns': args.include}
    if args.no_tag:
        collector.config['tagging']['enabled'] = False
    if args.no_filter:
        collector.config['filtering']['enabled'] = False
    
    # Reinitialize components with updated config
    collector._init_components()
    
    collector.run()
