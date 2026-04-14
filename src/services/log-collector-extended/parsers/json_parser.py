"""JSON log parser."""
import json
from datetime import datetime
from .base import BaseParser, ParsedEntry


class JSONParser(BaseParser):
    """Parser for JSON-formatted log entries."""
    
    format_name = "json"
    
    # Common JSON log field names
    TIMESTAMP_FIELDS = ['timestamp', 'time', '@timestamp', 'ts', 'datetime', 'date', 'logged_at']
    LEVEL_FIELDS = ['level', 'severity', 'loglevel', 'log_level', 'priority']
    MESSAGE_FIELDS = ['message', 'msg', 'log', 'text', 'description']
    
    def parse(self, line: str) -> ParsedEntry:
        """Parse a JSON log line."""
        line = line.strip()
        if not line:
            return None
        
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        entry = ParsedEntry(raw=line, format_type=self.format_name)
        
        # Extract timestamp
        for field in self.TIMESTAMP_FIELDS:
            if field in data:
                entry.timestamp = self._parse_timestamp(data[field])
                if entry.timestamp:
                    break
        
        # Extract level
        for field in self.LEVEL_FIELDS:
            if field in data:
                entry.level = str(data[field]).upper()
                break
        
        # Extract message
        for field in self.MESSAGE_FIELDS:
            if field in data:
                entry.message = str(data[field])
                break
        
        if not entry.message:
            entry.message = json.dumps(data)
        
        # Store remaining fields as metadata
        exclude = set(self.TIMESTAMP_FIELDS + self.LEVEL_FIELDS + self.MESSAGE_FIELDS)
        entry.metadata = {k: v for k, v in data.items() if k not in exclude}
        
        return entry
    
    def _parse_timestamp(self, value) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(value)
        elif isinstance(value, str):
            for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None
